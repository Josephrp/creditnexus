"""
FDC3 API routes for CreditNexus.

Provides endpoints for FDC3 2.0 App Directory integration, allowing
OpenFin Workspace and other FDC3-compliant platforms to discover
and integrate with CreditNexus.
"""

import logging
from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import json

logger = logging.getLogger(__name__)

router = APIRouter(tags=["fdc3"])

# Path to FDC3 intents configuration file
FDC3_INTENTS_PATH = Path(__file__).parent.parent.parent / "openfin" / "fdc3-intents.json"


@router.get("/apps")
async def get_fdc3_app_directory():
    """
    Serve FDC3 2.0 App Directory JSON.
    
    This endpoint provides the app directory entry for CreditNexus,
    allowing OpenFin Workspace and other FDC3-compliant platforms
    to discover and integrate with the application.
    
    Returns:
        JSONResponse: FDC3 2.0 App Directory JSON with proper CORS headers
        
    Raises:
        HTTPException: If the app directory file is not found or invalid
    """
    try:
        # Check if file exists
        if not FDC3_INTENTS_PATH.exists():
            logger.error(f"FDC3 intents file not found: {FDC3_INTENTS_PATH}")
            raise HTTPException(
                status_code=500,
                detail="FDC3 app directory configuration not found"
            )
        
        # Read and parse JSON file
        with open(FDC3_INTENTS_PATH, 'r', encoding='utf-8') as f:
            app_directory = json.load(f)
        
        # Return with proper headers for CORS and content type
        return JSONResponse(
            content=app_directory,
            headers={
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, OPTIONS",
                "Access-Control-Allow-Headers": "Content-Type"
            }
        )
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in FDC3 intents file: {e}")
        raise HTTPException(
            status_code=500,
            detail="Invalid FDC3 app directory configuration"
        )
    except Exception as e:
        logger.error(f"Error serving FDC3 app directory: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Failed to serve FDC3 app directory"
        )


@router.options("/apps")
async def options_fdc3_app_directory():
    """
    Handle CORS preflight requests for the app directory endpoint.
    
    Returns:
        JSONResponse: Empty response with CORS headers
    """
    return JSONResponse(
        content={},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type"
        }
    )
