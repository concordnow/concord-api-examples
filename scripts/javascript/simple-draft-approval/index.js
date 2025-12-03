/**
 * Simple Draft Approval - Concord API Example
 *
 * This script demonstrates how to:
 * 1. Create a draft agreement
 * 2. Set up a custom approval workflow
 * 3. Request approval (transitions from DRAFT to VALIDATION status)
 * 4. Accept the approval programmatically
 *
 * Prerequisites:
 * - Configure your API key and organization ID in config.json
 * - Ensure you have appropriate permissions in your Concord organization
 *
 * Usage:
 *   node index.js
 */

const https = require('https');
const fs = require('fs');
const path = require('path');

// Load configuration from config.json
const config = JSON.parse(fs.readFileSync(path.join(__dirname, 'config.json'), 'utf8'));

if (!config.apiKey) {
  console.error('Please set your API key in config.json');
  process.exit(1);
}

if (!config.organizationId) {
  console.error('Please set your organization ID in config.json');
  process.exit(1);
}

// HTTP utility functions for Concord API communication
function get(requestPath) {
  return new Promise((resolve, reject) => {
    const options = {
      host: config.baseUrl,
      port: 443,
      path: requestPath,
      headers: { 'X-API-KEY': config.apiKey }
    };

    https.get(options, res => {
      if (res.statusCode !== 200) {
        console.log('Error: Status Code', res.statusCode);
        return reject(res.statusCode);
      }
      let data = [];
      res.on('data', chunk => {
        data.push(chunk);
      });
      res.on('end', () => {
        resolve(JSON.parse(Buffer.concat(data).toString()));
      });
    }).on('error', err => {
      console.log('Error', err.message);
      reject(err.message);
    });
  });
}

function post(requestPath, body) {
  return new Promise((resolve, reject) => {
    const options = {
      host: config.baseUrl,
      port: 443,
      path: requestPath,
      method: 'POST',
      headers: {
        'X-API-KEY': config.apiKey,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = https.request(options, res => {
      if (res.statusCode < 200 || res.statusCode >= 300) {
        console.log('Error: Status Code', res.statusCode);
        return reject(res.statusCode);
      }
      let data = [];
      res.on('data', chunk => {
        data.push(chunk);
      });
      res.on('end', () => {
        const responseBody = Buffer.concat(data).toString();
        try {
          resolve(JSON.parse(responseBody));
        } catch (e) {
          resolve(responseBody);
        }
      });
    });

    req.on('error', err => {
      console.log('Error', err.message);
      reject(err.message);
    });

    req.write(body);
    req.end();
  });
}

function patch(requestPath, body) {
  return new Promise((resolve, reject) => {
    const options = {
      host: config.baseUrl,
      port: 443,
      path: requestPath,
      method: 'PATCH',
      headers: {
        'X-API-KEY': config.apiKey,
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(body)
      }
    };

    const req = https.request(options, res => {
      if (res.statusCode < 200 || res.statusCode >= 300) {
        console.log('Error: Status Code', res.statusCode);
        return reject(res.statusCode);
      }
      let data = [];
      res.on('data', chunk => {
        data.push(chunk);
      });
      res.on('end', () => {
        const responseBody = Buffer.concat(data).toString();
        try {
          resolve(JSON.parse(responseBody));
        } catch (e) {
          resolve(responseBody);
        }
      });
    });

    req.on('error', err => {
      console.log('Error', err.message);
      reject(err.message);
    });

    req.write(body);
    req.end();
  });
}

// Business logic functions
/**
 * Get current authenticated user information
 * @returns {Object} User object with id, name, email, etc.
 */
async function getCurrentUser() {
  console.log('Getting current user...');
  const response = await get('/api/rest/1/user/me');
  return response;
}

/**
 * Create a new draft agreement
 * @returns {string} The UID of the created agreement
 */
async function createDraft() {
  console.log('Creating draft agreement...');

  const requestBody = JSON.stringify({
    title: 'Draft Agreement',
    description: 'Draft agreement with custom approval',
    status: 'DRAFT'
  });

  const response = await post(`/api/rest/1/organizations/${config.organizationId}/agreements`, requestBody);
  return response.uid;
}

/**
 * Add a custom approval configuration to the agreement
 * Sets up the current user as the approver with a "ONE" rule (one approval needed)
 * @param {string} agreementUid - The UID of the agreement
 * @param {Object} user - User object containing the approver's ID
 */
async function addCustomApproval(agreementUid, user) {
  console.log('Adding custom approval to agreement...');

  const approvalConfig = {
    autoNotificationEnabled: true,        // Send notifications when approval is requested
    blockThirdPartySignature: true,       // Prevent external users from signing until approved
    rules: [
      {
        blockThirdPartySignature: true,
        type: "ONE",                      // Only one approval needed from the validations list
        validations: [
          {
            type: "USER",                 // Specific user approval (vs GROUP or other types)
            user: {
              id: user.id                 // Only the user ID is required
            }
          }
        ]
      }
    ]
  };

  const requestBody = JSON.stringify(approvalConfig);

  await post(`/api/rest/1/organizations/${config.organizationId}/agreements/${agreementUid}/approval`, requestBody);
}

/**
 * Check the current status of an agreement
 * @param {string} agreementUid - The UID of the agreement
 * @returns {Object} Agreement object with metadata including status
 */
async function checkAgreementStatus(agreementUid) {
  const response = await get(`/api/rest/1/organizations/${config.organizationId}/agreements/${agreementUid}`);
  console.log('Agreement status:', response.metadata.status);
  return response;
}

/**
 * Get the approval configuration for an agreement
 * @param {string} agreementUid - The UID of the agreement
 * @returns {Object|null} Approval configuration or null if not found
 */
async function checkApprovalConfiguration(agreementUid) {
  try {
    const response = await get(`/api/rest/1/organizations/${config.organizationId}/agreements/${agreementUid}/approval`);
    return response;
  } catch (error) {
    return null;
  }
}

// Approval workflow functions
/**
 * Request approval for an agreement
 * This action triggers the transition from DRAFT to VALIDATION status
 * @param {string} agreementUid - The UID of the agreement
 * @param {Object} approvalConfig - The approval configuration containing rules
 */
async function requestApproval(agreementUid, approvalConfig) {
  console.log('Requesting approval...');

  if (approvalConfig && approvalConfig.rules && approvalConfig.rules[0]) {
    const ruleId = approvalConfig.rules[0].id;
    const requestBody = JSON.stringify({ action: 'ASK' });  // ASK action initiates approval workflow
    await patch(`/api/rest/1/organizations/${config.organizationId}/agreements/${agreementUid}/rules/${ruleId}`, requestBody);
  } else {
    throw new Error('No approval rules found to request');
  }
}

/**
 * Accept an approval for an agreement
 * This completes the approval process for the specified rule
 * @param {string} agreementUid - The UID of the agreement
 * @param {Object} approvalConfig - The approval configuration containing rules
 */
async function acceptApproval(agreementUid, approvalConfig) {
  console.log('Accepting approval...');

  if (approvalConfig && approvalConfig.rules && approvalConfig.rules[0]) {
    const ruleId = approvalConfig.rules[0].id;
    const requestBody = JSON.stringify({ action: 'ACCEPT' });  // ACCEPT action completes the approval
    await patch(`/api/rest/1/organizations/${config.organizationId}/agreements/${agreementUid}/rules/${ruleId}`, requestBody);
  } else {
    throw new Error('No approval rules found to accept');
  }
}

/**
 * Main function that orchestrates the complete approval workflow
 *
 * Workflow steps:
 * 1. Get current user (who will be the approver)
 * 2. Create a draft agreement
 * 3. Configure custom approval with the current user as approver
 * 4. Request approval (triggers DRAFT → VALIDATION status change)
 * 5. Accept the approval (completes the approval process)
 * 6. Verify approval status changes
 */
async function main() {
  try {
    // Step 1: Get current user information
    const user = await getCurrentUser();

    // Step 2: Create a new draft agreement
    const agreementUid = await createDraft();

    // Step 3: Set up approval configuration
    await addCustomApproval(agreementUid, user);
    await checkAgreementStatus(agreementUid);  // Should show DRAFT status

    // Get the approval configuration to extract rule IDs
    const approvalConfig = await checkApprovalConfiguration(agreementUid);

    // Step 4: Request approval (initiates the approval workflow)
    await requestApproval(agreementUid, approvalConfig);
    await checkAgreementStatus(agreementUid);  // Should show VALIDATION status

    // Step 5: Accept the approval (completes the approval process)
    await acceptApproval(agreementUid, approvalConfig);
    await checkAgreementStatus(agreementUid);  // Should remain VALIDATION status but approved

    // Check approval configuration after acceptance to see status changes
    const finalApprovalConfig = await checkApprovalConfiguration(agreementUid);
    if (finalApprovalConfig && finalApprovalConfig.rules && finalApprovalConfig.rules[0]) {
      console.log('Final approval status:', finalApprovalConfig.rules[0].status);
    }

    console.log('Process completed successfully');
  } catch (error) {
    console.error('Error:', error);
    process.exit(1);
  }
}

// Execute the main workflow
main();
