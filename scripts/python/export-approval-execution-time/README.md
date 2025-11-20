# Export Signed Agreements with Approval and Execution Times

A Python script that exports all signed agreements from Concord API with complete timeline data (creation date, approvals, signatures) to a timestamped CSV file.

## Overview

This script helps business analysts and contract administrators analyze agreement execution timelines by exporting:
- Agreement creation date (from first activity in audit trail)
- First and last approval dates
- First and last signature dates

The output is a timestamped CSV file ready for analysis in Excel, Google Sheets, or other spreadsheet applications.

## Prerequisites

### Required

1. **Python 3.8 or higher**
   - Check your version: `python3 --version`
   - Download from: https://www.python.org/downloads/

2. **Concord API Key**
   - Log in to Concord: https://secure.concordnow.com
   - Navigate to Settings → Automations → Integrations → Concord API
   - Click "Generate a new API Key"
   - Copy the key

3. **Access to Signed Agreements**
   - Your API key must have permission to access agreements in your organization
   - You must have at least one signed agreement to export

## Installation

### Step 1: Navigate to Script Directory

```bash
cd scripts/python/export-approval-execution-time/
```

### Step 2: Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- `requests>=2.31.0` - for HTTP API calls

## Configuration

### Set Your API Key

Open `index.py` in a text editor and find line 15:

```python
API_KEY = "YOUR_API_KEY_HERE"  # TODO: Replace with your actual API key
```

Replace `YOUR_API_KEY_HERE` with your actual API key:

```python
API_KEY = "abc123def456..."
```

**⚠️ Security Note**: Never commit your API key to git. The `.gitignore` file is configured to exclude `.env` files if you prefer environment variable configuration.

## Usage

Run the script:

```bash
python index.py
```

**Expected output:**
```
Export Signed Agreements - Approval & Execution Time
======================================================

✓ API key configured

Fetching organizations...
✓ Found 1 organization(s)

Processing organization: My Company
Fetching agreements (page 0)...
  Retrieved 45 agreements from page 0
✓ Found 45 signed agreement(s)

Processing agreements:
  [1/45] NDA with Acme Corporation...
  [2/45] Service Agreement with Beta Inc...
  ...
  [45/45] Master Services Agreement...

Writing CSV output...
✓ CSV file written: signed_agreements_execution_time_20251120_1430.csv

✓ Export complete!

Output file: signed_agreements_execution_time_20251120_1430.csv
Total agreements exported: 45
Agreements with approvals: 38
Agreements without approvals: 7
Agreements with signatures: 45
Agreements without signatures: 0

You can now open the CSV file in Excel, Google Sheets, or any spreadsheet application.
```

## CSV Output Format

### Columns

| Column | Description | Example Value | Empty If... |
|--------|-------------|---------------|-------------|
| Agreement ID | Unique identifier | `abc-123-def-456` | Never empty |
| Agreement Title | Agreement name | `NDA with Acme Corp` | Never empty |
| Agreement Link | Web URL to view | `https://secure.concordnow.com/#/organizations/{organizationId}/agreements/{agreementID}` | Never empty |
| Creation Date | First activity timestamp from audit trail (UTC) | `2025-11-01 14:30:00` | Never empty |
| First Approval Date | First approval timestamp (UTC) | `2025-11-02 09:15:00` | No approvals in workflow |
| Last Approval Date | Last approval timestamp (UTC) | `2025-11-02 16:45:00` | No approvals in workflow |
| First Signature Date | First signature timestamp (UTC) | `2025-11-03 10:00:00` | No signatures recorded |
| Last Signature Date | Last signature timestamp (UTC) | `2025-11-03 14:30:00` | No signatures recorded |

### Example CSV Content

```csv
Agreement ID,Agreement Title,Agreement Link,Creation Date,First Approval Date,Last Approval Date,First Signature Date,Last Signature Date
abc-123-def-456,NDA with Acme Corp,https://secure.concordnow.com/#/organizations/org-123/agreements/abc-123-def-456,2025-11-01 14:30:00,2025-11-02 09:15:00,2025-11-02 16:45:00,2025-11-03 10:00:00,2025-11-03 14:30:00
xyz-789-ghi-012,Service Agreement with Beta Inc,https://secure.concordnow.com/#/organizations/org-123/agreements/xyz-789-ghi-012,2025-10-15 10:00:00,,,2025-10-20 15:30:00,2025-10-21 11:00:00
```

**Note**: Agreements without approval steps show empty strings in the approval date columns. This is expected behavior for agreements that skip the approval phase.

## Troubleshooting

### API Key Not Configured

**Error:**
```
ERROR: Please set your API_KEY in the script
```

**Solution**: Edit `index.py` line 15 and replace `YOUR_API_KEY_HERE` with your actual API key.

---

### No Organizations Found

**Warning:**
```
WARNING: No organizations found for this API key
```

**Possible Causes**:
- API key is invalid or expired
- API key doesn't have permission to access any organizations

**Solution**: Generate a new API key from Concord settings and ensure you have organization access.

---

### API Request Failed

**Error:**
```
ERROR: API request failed: /api/rest/1/...
Status code: 401
```

**Possible Causes**:
- API key is invalid
- API key has been revoked

**Solution**: Generate a new API key and update the script.

---

### Empty CSV (No Agreements Found)

**Output:**
```
No signed agreements found for Organization Name
```

**Possible Causes**:
- Organization has no signed agreements
- API key doesn't have permission to view agreements
- Agreements are in draft or negotiation status (not signed)

**Solution**: Verify you have signed agreements in your Concord account and that your API key has appropriate permissions.

---

### Network Timeout

**Error:**
```
ERROR: Network request failed: /api/rest/1/...
```

**Possible Causes**:
- No internet connection
- Concord API is temporarily unavailable
- Corporate firewall blocking API access

**Solution**: Check your internet connection and try again. If the problem persists, check Concord's status page.

## Performance Notes

- **Sequential Processing**: The script processes agreements one at a time (no concurrency) to respect API rate limits
- **Expected Performance**: 3-5 minutes for 1000 agreements
- **Pagination**: Uses `numberOfItemsByPage=5000` for efficient bulk retrieval
- **Memory Usage**: Loads all agreement data into memory before writing CSV (suitable for up to 10,000 agreements)

## Security Best Practices

⚠️ **Important Security Notes**:

1. **Never commit API keys to version control**
   - The `.gitignore` file excludes common secret files
   - Consider using environment variables for API keys

2. **Use separate API keys for testing**
   - Generate a dedicated API key for testing/development
   - Revoke test keys when no longer needed

3. **Secure CSV output files**
   - CSV files may contain sensitive agreement data
   - Store exported files in secure locations
   - Delete old exports when no longer needed

4. **Rotate API keys regularly**
   - Generate new keys periodically
   - Revoke old keys after rotation

## Known Limitations

### Fail-Fast Behavior

The script uses fail-fast error handling: **any API error causes immediate exit** with no partial CSV output.

**Rationale**: Partial exports could mislead analysts about timeline metrics. If you need 100% of signed agreements (per spec), incomplete data is worse than no data.

**Impact**: If the script fails on agreement #50 of 100, no CSV is created. You must fix the error and re-run.

---

### Sequential Processing

The script processes agreements **one at a time** (no concurrent requests).

**Rationale**: Respects API rate limits and simplifies error handling.

**Impact**: Slower than concurrent processing, but more reliable. For 1000 agreements, expect 3-5 minutes.

---

### Creation Date Source

The creation date comes from the **first activity in the audit trail**, NOT from the agreements list API.

**Rationale**: The `createdAt` field in the agreements list is not always accurate in the context of this analysis.

**Impact**: The script must fetch the full audit trail for every agreement, which adds processing time but ensures accurate dates.

---

### No Retry Logic

Failed API requests do **not retry** automatically.

**Rationale**: The repository constitution requires retry logic, but this script deviates intentionally for data integrity (see plan.md).

**Impact**: Temporary network glitches will cause the script to exit. You must re-run manually.

## API Endpoints Used

This script uses 3 Concord API endpoints:

1. **GET /api/rest/1/user/me/organizations**
   - Fetch organizations accessible to the authenticated user

2. **GET /api/rest/1/user/me/organizations/{orgId}/agreements**
   - Fetch paginated list of signed agreements
   - Filters: multiple `statuses` parameters for all signed statuses
   - Access types: DIRECT, TAG, FOLDER, ORGANIZATION

3. **GET /api/rest/1/organizations/{orgId}/agreements/{agreementUid}/activities**
   - Fetch audit trail for a specific agreement
   - Filters for: VALIDATION_ACCEPT (approvals), NEGOTIATION_APPROVE (signatures)
   - Used to extract creation date (earliest activity timestamp)

For complete API documentation, see: https://api.doc.concordnow.com/

## License

This script is part of the Concord API Examples repository and is provided as-is for educational and demonstration purposes.

## Support

For issues or questions:
- Review the Troubleshooting section above
- Check the Concord API documentation: https://api.doc.concordnow.com/
- Contact Concord support for API-related questions
