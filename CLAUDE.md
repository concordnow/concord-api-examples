# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This repository provides practical examples for using the Concord API (https://api.doc.concordnow.com/). It contains standalone scripts demonstrating various Concord API use cases, primarily focused on agreement lifecycle management and data export.

## Repository Structure

The repository is organized into two main sections:

- **`examples/`**: Contains comprehensive API walkthroughs and guides
- **`scripts/`**: Contains executable examples organized by language:
  - `scripts/javascript/`: Node.js scripts for various API operations
  - `scripts/python/`: Python scripts for data export and analysis

Each script is self-contained in its own directory with its own README, dependencies, and configuration.

## API Configuration

All scripts require a Concord API key for authentication:
- Generate API keys at: https://secure.concordnow.com/#/automations/integrations
- API keys are user-based and inherit the user's permissions
- For organization-wide data access, use an API key from a user with appropriate permissions

### Base URLs

Scripts use different Concord environments:
- **Production**: `api.concordnow.com` (default for most scripts)
- **UAT/Testing**: `uat.concordnow.com` (used in some examples)

## Common Development Tasks

### JavaScript Scripts

All JavaScript scripts use Node.js with native `https` module (no external HTTP libraries like `axios` or `node-fetch` v3+).

**Install dependencies:**
```bash
cd scripts/javascript/<script-name>
npm install
```

**Run a script:**
```bash
cd scripts/javascript/<script-name>
node index.js
```

**Configuration pattern:**
- Some scripts use inline API key configuration (e.g., `export-agreements-list`, `export-signers`): Edit `API_KEY` variable in `index.js` directly
- Newer scripts use `config.json` pattern (e.g., `simple-draft-approval`): Copy `config.example.json` to `config.json` and edit values

### Python Scripts

Python scripts are designed for data export and analysis, typically outputting CSV files.

**Setup virtual environment:**
```bash
cd scripts/python/<script-name>
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

**Install dependencies:**
```bash
pip install -r requirements.txt
```

**Run a script:**
```bash
python index.py
```

**Configuration pattern:**
- API key configured directly in `index.py` file (look for `API_KEY = "YOUR_API_KEY_HERE"`)

## Architecture Patterns

### HTTP Request Pattern (JavaScript)

All JavaScript scripts use a consistent pattern with native `https` module:

```javascript
function get(path) {
  return new Promise((resolve, reject) => {
    const options = {
      host: 'api.concordnow.com',
      port: 443,
      path: path,
      headers: { "X-API-KEY": apiKey }
    };
    https.get(options, (res) => {
      // Handle response with status checking
      // Parse JSON from chunks
    });
  });
}
```

Similar patterns exist for `post()`, `put()`, `delete()` methods where needed.

### Pagination Pattern

Concord API uses offset-based pagination. Scripts typically:
1. Set a large `numberOfItemsByPage` parameter (e.g., 5000)
2. Iterate through pages using `page` parameter (0-indexed)
3. Continue until API returns empty results or fewer items than page size

Example:
```javascript
const queryParams = [
  "numberOfItemsByPage=5000",
  `page=${pageNumber}`,
  // ... other filters
].join("&");
```

### Data Export Pattern (CSV)

Export scripts follow this flow:
1. Fetch organizations the API key has access to
2. For each organization, fetch filtered agreements (by status, access type, etc.)
3. For each agreement, fetch detailed data (activities, signatures, etc.)
4. Build in-memory data structure
5. Write timestamped CSV file with format: `export-{type}-YYYY-MM-DDTHH_MM_SS_MSZ.csv`

### Agreement Status Filtering

Concord agreements have various statuses. Key status groups:

**Signing stage statuses** (used in export scripts):
- `DRAFT`, `BROKEN`, `VALIDATION`, `NEGOTIATION`, `SIGNING`, `UNKNOWN_CONTRACT`, `FUTURE_CONTRACT`, `CURRENT_CONTRACT`, `COMPLETED_CONTRACT`, `COMPLETED_CANCEL_CONTRACT`, `COMPLETED_CONTRACT_RENEWABLE`

**Fully signed statuses** (contract stage):
- `UNKNOWN_CONTRACT`, `FUTURE_CONTRACT`, `CURRENT_CONTRACT`, `COMPLETED_CONTRACT`, `COMPLETED_CANCEL_CONTRACT`, `COMPLETED_CONTRACT_RENEWABLE`

### Access Type Filtering

When fetching agreements, scripts specify access types to control scope:
- `DIRECT`: Direct access to specific agreements
- `TAG`: Access via tags
- `FOLDER`: Access via folder membership
- `ORGANIZATION`: Full organization access

## Key API Endpoints

Based on the scripts in this repository:

**User & Organization:**
- `GET /api/rest/1/user/me` - Get current user info
- `GET /api/rest/1/user/me/organizations` - List accessible organizations

**Agreement Lifecycle:**
- `POST /api/rest/1/organizations/{orgId}/agreements` - Create draft agreement
- `POST /api/rest/1/organizations/{orgId}/auto/{templateUid}` - Create from automated template
- `GET /api/rest/1/organizations/{orgId}/agreements/{uid}/metadata` - Get agreement metadata
- `GET /api/rest/1/user/me/organizations/{orgId}/agreements` - List agreements (with filters)

**Approval Workflow:**
- `POST /api/rest/1/organizations/{orgId}/agreements/{uid}/approval` - Add custom approval
- `POST /api/rest/1/organizations/{orgId}/agreements/{uid}/approval/accept` - Accept approval

**Signatures:**
- `PUT /api/rest/1/organizations/{orgId}/agreements/{uid}/signature/slots` - Set signature slots
- `POST /api/rest/1/organizations/{orgId}/agreements/{uid}/signature/request` - Request signatures

**Activities & Audit:**
- `GET /api/rest/1/organizations/{orgId}/agreements/{uid}/activities` - Get audit trail

**Document Export:**
- `GET /api/rest/1/organizations/{orgId}/agreements/{uid}.pdf` - Download signed PDF

## Agreement UIDs

Agreements are identified by UIDs (e.g., `02yZQK4GBw1n95T9daJKx7`). These can be found:
- In the Concord web interface URL: `https://secure.concordnow.com/#/organizations/{orgId}/agreements/{agreementUid}`
- In API responses when creating or listing agreements

## Security Notes

- **Never commit API keys** - Configuration files with sensitive data are gitignored
- **Respect rate limits** - Scripts use sequential processing to avoid overwhelming the API
- **CSV output may contain sensitive data** - Secure exported files appropriately
- **API keys are user-based** - They inherit permissions from the associated user account
