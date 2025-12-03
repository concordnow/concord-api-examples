# Simple Draft with Approval

A minimal script that demonstrates creating a draft agreement with custom approval workflow using the Concord API.

## What This Script Does

1. **Gets Current User**: Retrieves the user ID associated with the API key
2. **Creates Draft Agreement**: Creates a new blank draft agreement
3. **Adds Custom Approval**: Configures approval workflow with:
   - `blockThirdPartySignature: true`
   - Single rule with type "ONE"
   - Single validation for the current user (USER type)
4. **Accepts Approval**: Automatically accepts the approval as the same user

## Prerequisites

- **API Key**: Generate at [Concord Settings → Automations → Integrations → Concord API](https://secure.concordnow.com)
- **Organization ID**: Integer ID of your target organization
- **Node.js**: Version 14 or higher

## Setup Instructions

### 1. Create Configuration File

Copy the example configuration:

```bash
cp config.example.json config.json
```

### 2. Configure Settings

Edit `config.json` with your details:

```json
{
  "apiKey": "YOUR_API_KEY_HERE",
  "organizationId": 123,
  "baseUrl": "api.concordnow.com"
}
```

**Configuration Options:**
- `apiKey`: Your Concord API key (required)
- `organizationId`: Target organization ID as integer (required)
- `baseUrl`: API base URL (default: "api.concordnow.com", can use "uat.concordnow.com" for testing)

## Running the Script

```bash
node index.js
```

## Expected Output

```
Getting current user...
Current user ID: 12345
Creating draft agreement...
Draft created with UID: 01sp9L4YEZNcLHaSV8447N
Adding custom approval to agreement...
Custom approval added successfully
Accepting the approval...
Approval accepted successfully
Process completed successfully
```

## API Endpoints Used

- `GET /api/rest/1/user/me` - Get current user information
- `POST /api/rest/1/organizations/{orgId}/agreements` - Create draft agreement
- `POST /api/rest/1/organizations/{orgId}/agreements/{uid}/approval` - Add custom approval
- `POST /api/rest/1/organizations/{orgId}/agreements/{uid}/approval/accept` - Accept approval

## Custom Approval Configuration

The script creates an approval workflow with this structure:

```json
{
  "blockThirdPartySignature": true,
  "rules": [
    {
      "type": "ONE",
      "validations": [
        {
          "type": "USER",
          "id": <current_user_id>
        }
      ]
    }
  ]
}
```

This means:
- Third-party signatures are blocked until approval
- Only one rule needs to be satisfied
- Only the current user can provide approval
- The user who created the approval automatically accepts it

## Error Handling

The script includes basic error handling:
- Validates API key is configured
- Validates organization ID is set
- Reports HTTP status code errors
- Exits with error code 1 on failure

## Troubleshooting

### Common Issues

1. **"Please set your API key"**: Add your API key to `config.json`
2. **"Please set your organization ID"**: Add valid organization ID to `config.json`
3. **401 Unauthorized**: Check API key is correct
4. **403 Forbidden**: Ensure you have access to the specified organization
5. **404 Not Found**: Verify organization ID exists and you have access

### Finding Your Organization ID

You can find your organization ID in the Concord web interface URL or by calling:
```bash
curl -H "X-API-KEY: YOUR_API_KEY" https://api.concordnow.com/api/rest/1/user/me/organizations
```

## Security Notes

- **Never commit config.json** to version control (already in .gitignore)
- **Use environment variables** for production deployments
- **Rotate API keys** regularly
- **Use separate configs** for different environments

## File Structure

```
simple-draft-approval/
├── index.js              # Main script
├── config.json           # Your configuration (not in git)
├── config.example.json   # Example configuration
├── package.json          # Package metadata
├── .gitignore            # Git ignore rules
└── README.md             # This file
```
