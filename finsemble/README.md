# Finsemble Deployment Guide for CreditNexus

This directory contains the Finsemble platform configuration files for deploying CreditNexus as a Finsemble component with FDC3 2.0 interoperability support.

## Overview

CreditNexus integrates with Finsemble to provide:
- Component-based architecture for enterprise desktop deployment
- FDC3 2.0 interoperability with other financial applications
- Channel-based communication for workflow orchestration
- Intent-based actions for credit agreement processing

## Configuration Files

### appConfig.json

Main Finsemble application configuration file containing:
- **Component Definition**: Window settings, preloads, and workspace integration
- **FDC3 App Definition**: FDC3 2.0 compliant application metadata
- **Intent Declarations**: Supported intents with context types
- **User Channel Configuration**: Broadcast and listen settings
- **Custom Context Types**: Schema definitions for CreditNexus contexts

### channels.json

Channel binding configuration for inter-application communication:
- **System Channels**: Standard FDC3 user channels (1-4)
- **App Channels**: CreditNexus-specific workflow channels
- **Channel Bindings**: Default routing for context types
- **Context Handlers**: Action mappings for each context type

## Deployment Steps

### 1. Configure Environment Variables

Replace `${APP_URL}` placeholder with your deployed CreditNexus URL:

```bash
# Example for production
export APP_URL=https://josephrp.github.io/creditnexus

# Replace in config files
sed -i 's|\${APP_URL}|'"$APP_URL"'|g' finsemble/appConfig.json
```

### 2. Add to Finsemble Configuration

Copy the app configuration to your Finsemble configs directory:

```bash
cp finsemble/appConfig.json $FINSEMBLE_ROOT/configs/application/apps/creditnexus.json
```

### 3. Register Channels

Add channel definitions to your Finsemble channel configuration:

```bash
# Merge channels.json with your existing channel config
cat finsemble/channels.json >> $FINSEMBLE_ROOT/configs/application/channels.json
```

### 4. Update App Directory

Add CreditNexus to your Finsemble app directory for the App Launcher:

```json
{
  "apps": [
    {
      "appId": "creditnexus",
      "name": "CreditNexus",
      "manifest": "configs/application/apps/creditnexus.json",
      "manifestType": "finsemble"
    }
  ]
}
```

### 5. Configure CORS (if needed)

Ensure your CreditNexus deployment allows requests from the Finsemble container:

```python
# In server.py, add Finsemble origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://your-finsemble-container.com",
        "http://localhost:3375"  # Finsemble default
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Supported FDC3 Intents

| Intent | Description | Input Context | Output Context |
|--------|-------------|---------------|----------------|
| `ViewLoanAgreement` | View credit agreement details | `finos.creditnexus.agreement` | `finos.creditnexus.agreement` |
| `ApproveLoanAgreement` | Approve or reject agreement | `finos.creditnexus.agreement` | `finos.creditnexus.approvalResult` |
| `ViewESGAnalytics` | View ESG scores and metrics | `finos.creditnexus.portfolio` | `finos.creditnexus.esgData` |
| `ExtractCreditAgreement` | Extract data from document | `finos.creditnexus.document` | `finos.creditnexus.agreement` |
| `ViewPortfolio` | View portfolio overview | `finos.creditnexus.portfolio` | `finos.creditnexus.portfolio` |

## App Channels

| Channel | Purpose | Broadcasts | Listens For |
|---------|---------|------------|-------------|
| `creditnexus.workflow` | Workflow state updates | `agreement`, `approvalResult` | `approvalResult` |
| `creditnexus.extraction` | Document extraction events | `agreement` | `document` |
| `creditnexus.portfolio` | Portfolio analytics | `portfolio`, `esgData` | `portfolio` |

## Custom Context Types

### finos.creditnexus.agreement
Credit agreement context with borrower, facilities, and parties data.

```javascript
{
  type: "finos.creditnexus.agreement",
  id: { agreementId: "AGR-2024-001", version: 1 },
  name: "Acme Corp Credit Facility",
  borrower: "Acme Corporation",
  agreementDate: "2024-01-15",
  totalCommitment: { amount: 100000000, currency: "USD" },
  workflowStatus: "approved"
}
```

### finos.creditnexus.document
Document for AI-powered extraction.

```javascript
{
  type: "finos.creditnexus.document",
  id: { documentId: "DOC-001" },
  name: "Credit Agreement.pdf",
  content: "...",  // Raw text content
  mimeType: "text/plain"
}
```

### finos.creditnexus.approvalResult
Result of approval workflow action.

```javascript
{
  type: "finos.creditnexus.approvalResult",
  agreementId: "AGR-2024-001",
  approved: true,
  approver: "John Smith",
  timestamp: "2024-01-20T14:30:00Z",
  comments: "Approved with standard terms",
  newStatus: "approved"
}
```

## Integration Examples

### Broadcasting Agreement Context

```javascript
import { fdc3 } from '@finsemble/finsemble-ui';

// Get app channel
const workflowChannel = await fdc3.getOrCreateChannel("creditnexus.workflow");

// Broadcast agreement context
await workflowChannel.broadcast({
  type: "finos.creditnexus.agreement",
  id: { agreementId: agreement.id },
  name: agreement.name,
  borrower: agreement.borrower,
  totalCommitment: agreement.totalCommitment
});
```

### Raising an Intent

```javascript
import { fdc3 } from '@finsemble/finsemble-ui';

// Raise intent to approve agreement
const result = await fdc3.raiseIntent("ApproveLoanAgreement", {
  type: "finos.creditnexus.agreement",
  id: { agreementId: "AGR-2024-001" }
});
```

### Adding Intent Listener

```javascript
import { fdc3 } from '@finsemble/finsemble-ui';

// Listen for ViewLoanAgreement intent
const listener = await fdc3.addIntentListener("ViewLoanAgreement", (context) => {
  const agreementId = context.id.agreementId;
  // Navigate to agreement view
  navigateToAgreement(agreementId);
  
  // Return result context
  return {
    type: "finos.creditnexus.agreement",
    id: { agreementId },
    // ... full agreement data
  };
});
```

## Troubleshooting

### Component Not Loading
1. Verify `${APP_URL}` is correctly replaced
2. Check CORS configuration allows Finsemble origin
3. Ensure CreditNexus server is running and accessible

### Intents Not Working
1. Confirm intent handlers are registered in the app
2. Check channel subscriptions are active
3. Verify context type matches exactly (case-sensitive)

### Channel Communication Issues
1. Ensure both apps are joined to the same channel
2. Verify context type schemas match
3. Check for JavaScript console errors

## Support

For issues with:
- **Finsemble Configuration**: Refer to [Finsemble Documentation](https://documentation.finsemble.com/)
- **FDC3 Interop**: Refer to [FDC3 Specification](https://fdc3.finos.org/)
- **CreditNexus Application**: Check the main project README
