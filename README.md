# CreditNexus: FINOS-Compliant Financial AI Agent

A production-grade financial AI agent that extracts structured data from credit agreements using OpenAI's GPT-4o, LangChain, and the FINOS Common Domain Model (CDM). Built as a full-stack enterprise application with a React frontend and Python backend.

## Features

### AI-Powered Extraction
- **Structured Data Extraction**: Extracts FINOS CDM-compliant data from unstructured credit agreement text
- **Smart Strategy Selection**: Automatically chooses between simple and map-reduce extraction based on document length
- **Reflexion Pattern**: Automatic retry with validation error feedback for improved accuracy
- **Long Document Processing**: Map-reduce strategy for documents > 50k characters

### Enterprise Features
- **User Authentication**: Secure login with Replit OAuth2 PKCE flow
- **Document Library**: Browse, search, and manage saved documents
- **Version History**: Track all versions of a document with full audit trail
- **Workflow Management**: Draft → Under Review → Approved → Published state machine
- **Audit Logging**: Full audit trail for all user actions with timestamps and metadata
- **Dashboard Analytics**: Portfolio overview with total commitments, ESG scores, and maturity timelines
- **Export Capabilities**: Download extracted data as JSON, CSV, or Excel

### Desktop Interoperability
- **FDC3 2.0 Compliant**: Full support for Financial Desktop Connectivity standard
- **OpenFin Ready**: Pre-configured app manifests and intent declarations
- **Finsemble Ready**: Application configuration with channel bindings
- **App Channels**: Real-time communication for workflow, extraction, and portfolio events

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         CreditNexus Architecture                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Frontend Layer        │  React + TypeScript + Tailwind CSS             │
│  (Port 5000)           │  FDC3 Integration for desktop interoperability │
├─────────────────────────────────────────────────────────────────────────┤
│  API Layer             │  FastAPI REST API                              │
│  (Port 8000)           │  Authentication, CORS, Static file serving     │
├─────────────────────────────────────────────────────────────────────────┤
│  Cognitive Layer       │  OpenAI GPT-4o for semantic parsing            │
│                        │  LangChain for orchestration                   │
├─────────────────────────────────────────────────────────────────────────┤
│  Validation Layer      │  Pydantic for schema enforcement               │
│                        │  Business logic validation                     │
├─────────────────────────────────────────────────────────────────────────┤
│  Data Layer            │  PostgreSQL for persistence                    │
│                        │  SQLModel ORM                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  Ontology Layer        │  FINOS CDM for standardized representation     │
└─────────────────────────────────────────────────────────────────────────┘
```

## Project Structure

```
creditnexus/
├── app/                          # Python backend application
│   ├── api/                      # FastAPI routes
│   │   └── routes.py             # API endpoints
│   ├── core/
│   │   └── config.py             # Configuration management
│   ├── db/
│   │   ├── models.py             # SQLModel database models
│   │   └── session.py            # Database session management
│   ├── models/
│   │   ├── cdm.py                # FINOS CDM Pydantic models
│   │   └── partial_cdm.py        # Partial models for map-reduce
│   ├── chains/
│   │   ├── extraction_chain.py   # Simple extraction chain
│   │   └── map_reduce_chain.py   # Map-reduce for long documents
│   └── utils/
│       ├── document_splitter.py  # Article-based document splitting
│       └── pdf_extractor.py      # PDF text extraction
├── client/                       # React frontend application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Dashboard.tsx     # Portfolio analytics dashboard
│   │   │   ├── DocumentHistory.tsx # Document history and version management
│   │   │   ├── ReviewInterface.tsx # Extraction review UI
│   │   │   └── ui/               # Reusable UI components
│   │   ├── context/
│   │   │   └── FDC3Context.tsx   # FDC3 integration context
│   │   ├── App.tsx               # Main application component
│   │   └── main.tsx              # Application entry point
│   └── dist/                     # Built static files (production)
├── openfin/                      # OpenFin deployment configuration
│   ├── app.json                  # Application manifest
│   ├── fdc3-intents.json         # FDC3 intent declarations
│   ├── provider.json             # Service provider config
│   └── README.md                 # OpenFin deployment guide
├── finsemble/                    # Finsemble deployment configuration
│   ├── appConfig.json            # Finsemble app configuration
│   ├── channels.json             # Channel bindings
│   └── README.md                 # Finsemble deployment guide
├── server.py                     # FastAPI application entry point
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL database
- OpenAI API key

### Environment Variables

| Variable | Description |
|----------|-------------|
| `OPENAI_API_KEY` | OpenAI API key for GPT-4o access |
| `DATABASE_URL` | PostgreSQL connection string |

### Development

Both frontend and backend run concurrently:

```bash
# Backend (runs on port 8000)
uvicorn server:app --host 127.0.0.1 --port 8000 --reload

# Frontend (runs on port 5000)
cd client && npm run dev
```

The Vite frontend proxies `/api` requests to the backend automatically.

### Production Build

```bash
# Build frontend
cd client && npm run build

# Start production server (serves both API and static files)
uvicorn server:app --host 0.0.0.0 --port 5000
```

## API Reference

### Extraction

| Endpoint | Method | Description |
|----------|--------|-------------|
| `POST /api/extract` | POST | Extract structured data from credit agreement text |
| `GET /api/health` | GET | Health check endpoint |

### Documents

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/documents` | GET | List all documents |
| `GET /api/documents/{id}` | GET | Get document by ID |
| `POST /api/documents` | POST | Create new document |
| `PUT /api/documents/{id}` | PUT | Update document |
| `DELETE /api/documents/{id}` | DELETE | Delete document |
| `GET /api/documents/{id}/versions` | GET | Get document version history |
| `GET /api/documents/{id}/export` | GET | Export document (format: json, csv, excel) |

### Workflows

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/workflows/{document_id}` | GET | Get workflow state |
| `POST /api/workflows/{document_id}/transition` | POST | Transition workflow state |

### Analytics

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/analytics/portfolio` | GET | Get portfolio analytics |

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /api/auth/login` | GET | Initiate OAuth login |
| `GET /api/auth/callback` | GET | OAuth callback handler |
| `GET /api/auth/me` | GET | Get current user |
| `POST /api/auth/logout` | POST | Logout user |

## Data Models (FINOS CDM)

All extracted data conforms to the FINOS Common Domain Model:

```python
CreditAgreement
├── agreement_date: date
├── effective_date: date (optional)
├── governing_law: str
├── parties: List[Party]
│   ├── name: str
│   ├── role: PartyRole (Borrower, Lender, AdministrativeAgent, etc.)
│   └── jurisdiction: str (optional)
├── facilities: List[LoanFacility]
│   ├── facility_type: FacilityType (Revolving, TermLoan, etc.)
│   ├── commitment_amount: Money
│   ├── maturity_date: date
│   └── interest_rate_payout: InterestRatePayout
│       ├── rate_type: str (Floating, Fixed)
│       ├── floating_rate_option: FloatingRateOption
│       │   ├── benchmark: str (SOFR, LIBOR, etc.)
│       │   └── spread_bps: Decimal (basis points)
│       └── payment_frequency: str
└── covenants: List[Covenant] (optional)
```

## Validation Rules

The system enforces strict validation:

- **Type Safety**: All fields must match declared types
- **Business Logic**:
  - Agreement date cannot be in the future
  - Maturity date must be after agreement date
  - All facilities must use the same currency
  - At least one party must have role "Borrower"
- **Spread Normalization**: Percentages automatically converted to basis points (3.5% → 350.0)
- **Precision**: All monetary amounts use Decimal for financial precision

## FDC3 Integration

### Supported Intents

| Intent | Description |
|--------|-------------|
| `ViewLoanAgreement` | View credit agreement details |
| `ApproveLoanAgreement` | Approve or reject agreements |
| `ViewESGAnalytics` | View ESG scores and metrics |
| `ExtractCreditAgreement` | Extract data from documents |
| `ViewPortfolio` | View portfolio overview |

### Custom Context Types

| Context Type | Description |
|--------------|-------------|
| `finos.creditnexus.agreement` | Credit agreement context |
| `finos.creditnexus.document` | Document for extraction |
| `finos.creditnexus.portfolio` | Portfolio context |
| `finos.creditnexus.approvalResult` | Approval workflow result |
| `finos.creditnexus.esgData` | ESG analytics data |

### App Channels

| Channel | Purpose |
|---------|---------|
| `creditnexus.workflow` | Workflow state updates and approvals |
| `creditnexus.extraction` | Document extraction events |
| `creditnexus.portfolio` | Portfolio analytics and updates |

## Desktop Deployment

### OpenFin

See [openfin/README.md](openfin/README.md) for detailed OpenFin deployment instructions.

```bash
# Install OpenFin CLI
npm install -g openfin-cli

# Launch application
openfin -l -c openfin/app.json
```

### Finsemble

See [finsemble/README.md](finsemble/README.md) for detailed Finsemble deployment instructions.

1. Copy `finsemble/appConfig.json` to your Finsemble configs directory
2. Update the `url` field with your deployed application URL
3. Restart Finsemble to load the new component

## Security

- OAuth2 PKCE authentication flow
- Role-based access control (Viewer, Analyst, Reviewer, Admin)
- API keys stored as encrypted secrets
- Session management with secure cookies
- Full audit logging for compliance

## References

- [FINOS Common Domain Model](https://cdm.finos.org/)
- [FDC3 Specification](https://fdc3.finos.org/)
- [OpenFin Documentation](https://developers.openfin.co/)
- [Finsemble Documentation](https://documentation.finsemble.com/)
- [LangChain Documentation](https://docs.langchain.com/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This project implements the FINOS Common Domain Model (CDM) for financial data interoperability.
