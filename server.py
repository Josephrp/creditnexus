"""FastAPI application entry point for CreditNexus backend."""

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from starlette.middleware.sessions import SessionMiddleware

from app.api.routes import router
from app.auth.routes import auth_router
from app.auth.jwt_auth import jwt_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    from app.core.config import settings
    
    # Initialize LLM client configuration
    try:
        from app.core.llm_client import init_llm_config
        init_llm_config(settings)
        logger.info(
            f"LLM client configured: provider={settings.LLM_PROVIDER.value}, "
            f"model={settings.LLM_MODEL}"
        )
    except Exception as e:
        logger.error(f"Failed to initialize LLM client configuration: {e}")
        raise
    
    # Initialize Policy Engine with YAML rule loading
    if settings.POLICY_ENABLED:
        try:
            from app.core.policy_config import PolicyConfigLoader
            from app.services.policy_engine_factory import create_policy_engine
            from app.services.policy_service import PolicyService
            
            # Create policy config loader
            policy_config_loader = PolicyConfigLoader(settings)
            
            # Load all rules from YAML files
            rules_yaml = policy_config_loader.load_all_rules()
            
            if not rules_yaml:
                logger.warning("No policy rules loaded - policy engine will use default allow behavior")
                rules_yaml = """
- name: default_allow
  when: {}
  action: allow
  priority: 0
  description: "Default allow for all transactions not caught by other rules"
"""
            
            # Validate rules
            policy_config_loader.validate_rules(rules_yaml)
            
            # Initialize policy engine (vendor-agnostic interface)
            policy_engine = create_policy_engine(
                vendor=settings.POLICY_ENGINE_VENDOR or "default"
            )
            
            # Load rules into engine
            policy_engine.load_rules(rules_yaml)
            
            # Create policy service instance
            policy_service = PolicyService(policy_engine)
            
            # Store in app state for dependency injection
            app.state.policy_service = policy_service
            app.state.policy_config_loader = policy_config_loader
            
            # Get metadata for logging
            metadata = policy_config_loader.get_rules_metadata()
            logger.info(
                f"Policy engine initialized: {metadata.get('rules_count', 0)} rule(s) "
                f"from {metadata.get('files_count', 0)} file(s)"
            )
            
            # Start file watcher if auto-reload enabled
            if settings.POLICY_AUTO_RELOAD:
                def reload_policy_rules():
                    """Reload policy rules from YAML files (called by file watcher)."""
                    try:
                        logger.info("Reloading policy rules...")
                        rules_yaml = policy_config_loader.load_all_rules()
                        policy_config_loader.validate_rules(rules_yaml)
                        policy_engine.load_rules(rules_yaml)
                        logger.info("Policy rules reloaded successfully")
                    except Exception as e:
                        logger.error(f"Failed to reload policy rules: {e}")
                
                policy_config_loader.start_file_watcher(reload_policy_rules)
                logger.info("Policy auto-reload enabled")
        except Exception as e:
            logger.error(f"Failed to initialize policy engine: {e}")
            if settings.POLICY_ENABLED:
                raise  # Fail fast if policy is required
    else:
        logger.info("Policy engine is disabled (POLICY_ENABLED=false)")
        app.state.policy_service = None
        app.state.policy_config_loader = None
    
    # Initialize x402 Payment Service
    if settings.X402_ENABLED:
        try:
            from app.services.x402_payment_service import X402PaymentService
            
            # Create x402 payment service instance
            payment_service = X402PaymentService(
                facilitator_url=settings.X402_FACILITATOR_URL,
                network=settings.X402_NETWORK,
                token=settings.X402_TOKEN
            )
            
            # Store in app state for dependency injection
            app.state.x402_payment_service = payment_service
            
            logger.info(
                f"x402 Payment service initialized: "
                f"facilitator={settings.X402_FACILITATOR_URL}, "
                f"network={settings.X402_NETWORK}, "
                f"token={settings.X402_TOKEN}"
            )
        except Exception as e:
            logger.error(f"Failed to initialize x402 payment service: {e}")
            if settings.X402_ENABLED:
                raise  # Fail fast if x402 is required
    else:
        logger.info("x402 Payment service is disabled (X402_ENABLED=false)")
        app.state.x402_payment_service = None
    
    # Initialize database
    if settings.DATABASE_ENABLED:
        try:
            from app.db import init_db, engine
            if engine is not None:
                init_db()
            else:
                logger.warning("Database engine is None, skipping initialization")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
    else:
        logger.info("Database is disabled (DATABASE_ENABLED=false)")
    
    yield
    
    # Cleanup
    if settings.POLICY_ENABLED and hasattr(app.state, 'policy_config_loader'):
        policy_config_loader = app.state.policy_config_loader
        if policy_config_loader:
            policy_config_loader.stop_file_watcher()
    
    # Cleanup x402 payment service
    if settings.X402_ENABLED and hasattr(app.state, 'x402_payment_service'):
        payment_service = app.state.x402_payment_service
        if payment_service:
            try:
                await payment_service.close()
                logger.info("x402 Payment service closed")
            except Exception as e:
                logger.error(f"Error closing x402 payment service: {e}")
    
    logger.info("Shutting down application...")


app = FastAPI(
    title="CreditNexus API",
    description="FINOS-Compliant Financial AI Agent for Credit Agreement Extraction",
    version="1.0.0",
    lifespan=lifespan
)

session_secret = os.environ.get("SESSION_SECRET")
is_production = os.environ.get("REPLIT_DEPLOYMENT") == "1"

if not session_secret:
    if is_production:
        raise RuntimeError("SESSION_SECRET must be set in production")
    logger.warning("SESSION_SECRET not set, generating temporary secret (not suitable for production)")
    import secrets
    session_secret = secrets.token_hex(32)

app.add_middleware(
    SessionMiddleware,
    secret_key=session_secret,
    session_cookie="creditnexus_session",
    max_age=86400 * 7,
    same_site="lax",
    https_only=is_production,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)
app.include_router(auth_router, prefix="/api")
app.include_router(jwt_router, prefix="/api")

# Serve OpenFin manifest files
openfin_dir = Path(__file__).parent / "openfin"
if openfin_dir.exists():
    @app.get("/openfin/app.json")
    async def serve_openfin_manifest():
        """Serve the OpenFin application manifest."""
        manifest_path = openfin_dir / "app.json"
        if manifest_path.exists():
            return FileResponse(str(manifest_path), media_type="application/json")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="OpenFin manifest not found")
    
    @app.get("/openfin/{filename}")
    async def serve_openfin_file(filename: str):
        """Serve other OpenFin configuration files."""
        file_path = openfin_dir / filename
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path), media_type="application/json")
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="File not found")

static_dir = Path(__file__).parent / "client" / "dist"
if static_dir.exists():
    logger.info(f"Serving static files from {static_dir}")
    app.mount("/assets", StaticFiles(directory=str(static_dir / "assets")), name="assets")
    
    @app.get("/")
    async def serve_frontend():
        """Serve the frontend application."""
        return FileResponse(str(static_dir / "index.html"))
    
    @app.get("/{full_path:path}")
    async def catch_all(full_path: str):
        """Catch-all route for SPA routing."""
        file_path = static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(static_dir / "index.html"))
else:
    logger.warning("Static files not found, running in API-only mode")
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "CreditNexus API",
            "docs": "/docs",
            "health": "/api/health"
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)
