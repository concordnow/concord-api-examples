# Export Signed Agreements with Approval and Execution Times

A Python script that exports all signed agreements from Concord API with complete timeline data (creation date, approvals, signatures) to a timestamped CSV file.

## Overview

This script helps business analysts and contract administrators analyze agreement execution timelines by exporting:
- Agreement creation date and creator email (from first activity in audit trail)
- Detailed approval information: up to 5 approvers with email addresses and dates
- Detailed signature information: up to 5 signers with email addresses and dates
- First and last approval/signature dates
- Total counts of approvals and signatures

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

### Columns (31 total)

| Column # | Column Name | Description | Example Value | Empty If... |
|----------|-------------|-------------|---------------|-------------|
| 1 | Agreement ID | Unique identifier | `abc-123-def-456` | Never |
| 2 | Agreement Title | Agreement name | `NDA with Acme Corp` | Never |
| 3 | Agreement Link | Web URL to view | `https://secure.concordnow.com/#/...` | Never |
| 4 | Creation Date | First activity timestamp (UTC) | `2025-11-01 14:30:00` | Never |
| 5 | Created By | Email of user who created agreement | `john.doe@example.com` | Cannot determine |
| 6 | Approver 1 | First approver email | `jane.smith@example.com` | No approvals |
| 7 | Approval Date 1 | First approval timestamp (UTC) | `2025-11-02 09:15:00` | No approvals |
| 8 | Approver 2 | Second approver email | `bob.johnson@example.com` | < 2 approvals |
| 9 | Approval Date 2 | Second approval timestamp (UTC) | `2025-11-02 14:30:00` | < 2 approvals |
| 10 | Approver 3 | Third approver email | `alice.brown@example.com` | < 3 approvals |
| 11 | Approval Date 3 | Third approval timestamp (UTC) | `2025-11-02 16:45:00` | < 3 approvals |
| 12 | Approver 4 | Fourth approver email | `charlie.davis@example.com` | < 4 approvals |
| 13 | Approval Date 4 | Fourth approval timestamp (UTC) | `2025-11-03 08:00:00` | < 4 approvals |
| 14 | Approver 5 | Fifth approver email | `diana.evans@example.com` | < 5 approvals |
| 15 | Approval Date 5 | Fifth approval timestamp (UTC) | `2025-11-03 10:15:00` | < 5 approvals |
| 16 | Signer 1 | First signer email | `carol.white@example.com` | No signatures |
| 17 | Signature Date 1 | First signature timestamp (UTC) | `2025-11-04 09:00:00` | No signatures |
| 18 | Signer 2 | Second signer email | `david.green@example.com` | < 2 signatures |
| 19 | Signature Date 2 | Second signature timestamp (UTC) | `2025-11-04 14:30:00` | < 2 signatures |
| 20 | Signer 3 | Third signer email | `emily.black@example.com` | < 3 signatures |
| 21 | Signature Date 3 | Third signature timestamp (UTC) | `2025-11-04 16:45:00` | < 3 signatures |
| 22 | Signer 4 | Fourth signer email | `frank.blue@example.com` | < 4 signatures |
| 23 | Signature Date 4 | Fourth signature timestamp (UTC) | `2025-11-05 08:00:00` | < 4 signatures |
| 24 | Signer 5 | Fifth signer email | `grace.red@example.com` | < 5 signatures |
| 25 | Signature Date 5 | Fifth signature timestamp (UTC) | `2025-11-05 10:15:00` | < 5 signatures |
| 26 | First Approval Date | First approval timestamp (UTC) | `2025-11-02 09:15:00` | No approvals |
| 27 | Last Approval Date | Last approval timestamp (UTC) | `2025-11-03 10:15:00` | No approvals |
| 28 | First Signature Date | First signature timestamp (UTC) | `2025-11-04 09:00:00` | No signatures |
| 29 | Last Signature Date | Last signature timestamp (UTC) | `2025-11-05 10:15:00` | No signatures |
| 30 | Total Approvals | Count of approval activities | `5` | `0` if no approvals |
| 31 | Total Signatures | Count of signature activities | `5` | `0` if no signatures |

### Column Groups
- **Columns 1-5**: Basic agreement information
- **Columns 6-15**: Detailed approval tracking (up to 5 approvers)
- **Columns 16-25**: Detailed signature tracking (up to 5 signers)
- **Columns 26-29**: First/last dates
- **Columns 30-31**: Summary totals

### Example CSV Content

```csv
Agreement ID,Agreement Title,Agreement Link,Creation Date,Created By,Approver 1,Approval Date 1,Approver 2,Approval Date 2,Approver 3,Approval Date 3,Approver 4,Approval Date 4,Approver 5,Approval Date 5,Signer 1,Signature Date 1,Signer 2,Signature Date 2,Signer 3,Signature Date 3,Signer 4,Signature Date 4,Signer 5,Signature Date 5,First Approval Date,Last Approval Date,First Signature Date,Last Signature Date,Total Approvals,Total Signatures
abc-123,NDA with Acme,https://...,2025-11-01 14:30:00,john@example.com,jane@example.com,2025-11-02 09:15:00,bob@example.com,2025-11-02 16:45:00,,,,,,,carol@example.com,2025-11-03 10:00:00,david@example.com,2025-11-03 14:30:00,,,,,,,2025-11-02 09:15:00,2025-11-02 16:45:00,2025-11-03 10:00:00,2025-11-03 14:30:00,2,2
xyz-789,Service Agreement,https://...,2025-10-15 10:00:00,alice@example.com,,,,,,,,,,,emily@example.com,2025-10-20 15:30:00,frank@example.com,2025-10-21 11:00:00,,,,,,,,,2025-10-20 15:30:00,2025-10-21 11:00:00,0,2
```

**Notes**:
- Agreements without approvals show empty strings in approval columns (6-15, 26-27)
- Agreements without signatures show empty strings in signature columns (16-25, 28-29)
- If more than 5 approvals or signatures exist, only the first 5 are shown (see Total columns for actual count)
- Console warnings will alert you when agreements have >5 approvals or >5 signatures

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

### Maximum 5 Approvers and 5 Signers Per Agreement

The script exports **up to 5 approvers and 5 signers** per agreement.

**Rationale**: Balances comprehensive data with reasonable CSV width. Most agreements have fewer than 5 approvals/signatures.

**Impact**:
- If an agreement has more than 5 approvals or signatures, only the first 5 (chronologically) are exported to individual columns
- The "Total Approvals" and "Total Signatures" columns show the actual count, allowing you to identify agreements that exceeded the limit
- Console warnings alert you when this occurs during export

**Workaround**: Filter exported data by "Total Approvals" or "Total Signatures" > 5 to identify agreements needing special attention.

---

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
