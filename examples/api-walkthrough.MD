# API walkthrough
This guide provides a step-by-step walkthrough for using the API to create and manage an agreement from an automated template. You'll learn how to:
- Create an agreement using an automated template
- Set up who can sign the agreement and their roles
- Request signatures, send invitations
- Check the status of the agreement
- Set up webhooks to be notified automatically when the agreement is fully signed
- Download the e-signed PDF after the agreement is fully signed

Examples will be provided as snippets of JavaScript code. The URLs contained in this guide point to the UAT environment.

For detailed reference and additional functionality, consult the complete [API documentation](https://api.doc.concordnow.com).

**Prerequisite**: you will need an API key, which can be generated directly in Concord.

## Select an automated template
To create an agreement using an automated template, you first need to pick which automated template to use in Concord.

You will need its UID, which you can find in its URL in Concord. For example, given the URL https://uat.concordnow.com/#/organizations/1/agreements/02yZQK4GBw1n95T9daJKx7 the UID is `02yZQK4GBw1n95T9daJKx7`.

You will also need to know the automated variable names, which can be configured and seen in Concord when viewing the automated template.

## Create an agreement from an automated template
Once you have identified which automated template to use, you can [create an agreement from an automated template](https://api.doc.concordnow.com/#tag/Automated-Template/operation/UseanAutomatedTemplate).
In the request body, you can set various parameters to set the automated variables, the title, the description, who to invite now or later, etc...

In the following code example, we create an agreement from an automated template and we set values for the automated variables named `VariableName1` and `VariableName2`.

We also invite several users with different permissions:
- a@corp.com the with "Editor" permission (Can edit the entire document)
- b@corp.com the with "Limited Editor" permission (Can only fill specific fields)
- c@corp.com with the "Viewer" permission (Cannot make any modifications)
```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '02yZQK4GBw1n95T9daJKx7'; // Replace with your automated template UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/auto/${agreementUid}`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            'title': 'Agreement title',
            'description': 'Agreement description',
            'tags': ['Tag1'],
            'signatureRequired': 2,
            'variables': {
                'VariableName1': 'The automated variable value',
                'VariableName2': 'Another automated variable value'
            },
            'inviteNowEmails': {
                'a@corp.com': 'FULL',
                'b@corp.com': 'LIMITED',
                'c@corp.com': 'NO_EDIT'
            },
            'inviteLaterEmails': {
                'd@corp.com': 'FULL',
                'e@corp.com': 'LIMITED',
                'f@corp.com': 'NO_EDIT'
            },
            'sendWithDocument': false,
            'customMessageTitle': 'Title of custom message',
            'customMessageContent': 'Content of custom message'
        })
    });

    const data = await response.json();
    console.log(data);
}

main();
```
The response contains the created agreement's UID which you will need for the next steps.
```json
{
    "uid": "01sp9L4YEZNcLHaSV8447N",
    "title": "Agreement title",
    "description": "Agreement description"
}
```

## Set up the agreement
### Set signers
Once the agreement has been created, you can [set up the signature slots](https://api.doc.concordnow.com/#tag/Signature/operation/SignatureSlotsUpdate).

In the following code example, we set five signature slots with different types:
- ORGANIZATION: any internal user. In that case you have to pass your organization ID along with the type in the request body.
- NOT_ORGANIZATION: any external user. In that case you also have to pass your organization ID along with the type in the request body.
- NONE: anyone
- EMAIL: a user referenced by his email, it could be an already existing user or not
- USER: a user referenced by his id, which means it's an already existing user in Concord

```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/agreements/${agreementUid}/signature/slots`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'PUT',
        headers: headers,
        body: JSON.stringify([
            {
                'reservation': {
                    'type': 'ORGANIZATION',
                    'organization': {
                        'id': 1
                    }
                }
            },
            {
                'reservation': {
                    'type': 'NOT_ORGANIZATION',
                    'organization': {
                        'id': 1
                    }
                }
            },
            {
                'reservation': {
                    'type': 'NONE'
                }
            },
            {
                'reservation': {
                    'type': 'EMAIL',
                    'email': {
                        'email': 'john@doe.com'
                    }
                }
            },
            {
                'reservation': {
                    'type': 'USER',
                    'user': {
                        'id': 5488
                    }
                }
            }
        ])
    });

    const data = await response.status();
    // Should be 204
    console.log(data);
}

main();
```

### Content edition
If you wish to edit the content of the agreement (redlining, commenting, filling fields, etc...), that must be done directly in Concord.

## Send invitations and request signatures
Once the agreement has been configured, you may want to send invitations and request signatures.
### Send invitations
You may have already sent invitations when creating the agreement from the template. If you haven't, or if you want to send more invitations, you can [invite users to join the agreement](https://api.doc.concordnow.com/#tag/Agreement/operation/InviteaMember).

In the following code example, we invite three users with different permissions on the agreement:
- viewer@example.com with the "Viewer" permission (Cannot make any modifications)
- limited@example.com the with "Limited Editor" permission (Can only fill specific fields)
- editor@example.com the with "Editor" permission (Can edit the entire document)
```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/agreements/${agreementUid}/members`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            "invitations": {
                "viewer@example.com": {
                    "permission": "NO_EDIT"
                },
                "limited@example.com": {
                    "permission": "LIMITED"
                },
                "EDITOR@example.com": {
                    "permission": "FULL"
                }
            },
            "message": {
                "subject": "Invitation to sign",
                "content": "Hello, this is an invite for a Non-Disclosure Agreement."
            }
        })
    });

    const data = await response.json();
    console.log(data);
}

main();
```
### Request signatures
In order to be able to request signatures, the agreement must meet certain pre-requisites, such as having all tracked changes resolved and having a signature field for each signer. That can only be set in Concord, not via API.

If you do not wish to add a signature field for each signer, you can enable legacy signature blocks by [updating the signature metadata](https://api.doc.concordnow.com/#tag/Signature/operation/SignatureUpdate) and setting `signatureBlockEnabled` to `true`.


When your agreement is ready to sign, you can [request signatures](https://api.doc.concordnow.com/#tag/Signature/operation/RequestSignature).

```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/agreements/${agreementUid}/signature/request`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'POST',
        headers: headers,
    });

    const data = await response.json();
    console.log(data);
}

main();
```

## Check the agreement's status
You may want to know when the agreement is fully signed. You can either manually check its status or set up a webhook to be notified when the agreement is fully signed.

### Manual status check
You can manually check the agreement's status by [getting the agreement's metadata](https://api.doc.concordnow.com/#tag/Agreement/operation/GetMetadata)

In the following code example, we retrieve the agreement's metadata.
```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/agreements/${agreementUid}/metadata`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'GET',
        headers: headers,
    });

    const data = await response.json();
    console.log(data);
}

main();
```

The agreement's status can be found in the `summaryStatus` field in the response.
```jsonc
{
    "summaryStatus": "SIGNING"
    // Other attributes ommitted
}
```
The following statuses indicate that the agreement is in the contract stage and has been fully signed: 
- `UNKNOWN_CONTRACT`
- `FUTURE_CONTRACT`
- `CURRENT_CONTRACT`
- `COMPLETED_CONTRACT`
- `COMPLETED_CANCEL_CONTRACT`
- `COMPLETED_CONTRACT_RENEWABLE`

### Set up a webhook
If you wish to be automatically notified when an agreement is fully signed, you can [set up a webhook](https://api.doc.concordnow.com/#tag/Webhooks).

In the following code example, we create a webhook that will be triggered every time an agreement is fully signed. A POST request will be sent to the configured URL, with the request body as described [here](https://api.doc.concordnow.com/#tag/Webhooks/operation/postAgreementEvent).
```javascript
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/users/me/integrations/webhooks`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'POST',
        headers: headers,
        body: JSON.stringify({
            "events": [
                "AGREEMENT_EXECUTED"
            ],
            "name": "My webhook",
            "url": "https://test.com"
        })
    });

    const data = await response.json();
    console.log(data);
}

main();
```

## Download the e-signed PDF once the agreement has been signed
Once the agreement has been fully signed, you can [download the e-signed PDF](https://api.doc.concordnow.com/#tag/Agreement/operation/GetPDF).

The following code example calls the endpoint to download the PDF and saves it in the current path.
```javascript
const fs = require('fs');
const organizationId = '1'; // Replace with your organization ID
const agreementUid = '01sp9L4YEZNcLHaSV8447N'; // Replace with your agreement UID
const apiUrl = `https://uat.concordnow.com/api/rest/1/organizations/${organizationId}/agreements/${agreementUid}.pdf`;
const headers = {
    'X-API-KEY': 'YOUR-API-KEY', // Replace with your API Key
    'Content-Type': 'application/json'
};
async function main() {
    const response = await fetch(`${apiUrl}`, {
        method: 'GET',
        headers: headers
    });
    const filePath = `${agreementUid}.pdf`;
    const fileStream = fs.createWriteStream(filePath);
    for await (const chunk of response.body) {
        fileStream.write(chunk);
    }
    fileStream.end();
}

main();
```