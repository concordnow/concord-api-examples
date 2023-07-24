const https = require('https');
const fs = require('fs');
const { stringify } = require('csv-stringify');

const apiKey = ''; // Insert your API key here
const pageSize = 5000;
const retryDocs = [];

function d() {
  return new Date().toISOString();
}

function get(path) {
  return new Promise((resolve, reject) => {
    const options = {
      host: 'api.concordnow.com',
      port: 443,
      path: path,
      headers: { 'X-API-KEY': apiKey }
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

async function getSigningAgreementsByPage(organizationId, page) {
  console.log(`${d()} Get Signing Agreements for ${organizationId} (${page})`);
  const getSigningAgreementsQueryParams = [
    'statuses=SIGNING',
    `page=${page}`,
    'directAccessOnly=false',
    `numberOfItemsByPage=${pageSize}`
  ].join('&');
  try {
    return await get(`/api/rest/1/user/me/organizations/${organizationId}/agreements?${getSigningAgreementsQueryParams}`);
  } catch (e) {
    throw new Error(`Get Signing Agreements failed with ${e}`);
  }
}

async function getSigningAgreements(organizationId) {
  let page = 0;
  let total = 0;
  const items = [];

  do {
    const body = await getSigningAgreementsByPage(organizationId, page);
    items.push(...body.items);
    total = body.total;
    page++;
  } while (total > items.length);
  return items;
}

async function getSignatureAgreement(organizationId, agreementId) {
  const body = await get(`/api/rest/1/organizations/${organizationId}/agreements/${agreementId}/signature`);

  return body.slots;
}

async function getAgreementData(organization, agreementId, doc) {
  const slots = await getSignatureAgreement(organization.id, agreementId);
  const needToSign = slots
    .filter(s => !s.signature)
    .map(s => s.reservation)
    .map(n => {
      if (n.type === 'USER') {
        return n.user.email;
      } else if (n.type === 'ORGANIZATION') {
        return 'Someone from the company: ' + n.organization.name;
      } else if (n.type === 'NOT_ORGANIZATION') {
        return 'Anyone outside of the company: ' + n.organization.name;
      } else if (n.type === 'EMAIL') {
        return n.email.email;
      } else {
        throw new Error(`Unsupported type: ${n.type}`);
      }
    });
  const whoSigned = slots
    .filter(s => s.signature)
    .map(s => s.signature.info.email);

  return [
    organization.id,
    organization.name,
    agreementId,
    `https://secure.concordnow.com/#/organizations/${organization.id}/agreements/${agreementId}`,
    doc.title,
    doc.signatureRequired - doc.signatureCount,
    needToSign.join(','),
    whoSigned.join(',')
  ];
}

async function getFullData(organization) {
  const documents = await getSigningAgreements(organization.id);
  const data = [];

  for (const doc of documents) {
    try {
      data.push(await getAgreementData(organization, doc.uuid, doc));
    } catch (e) {
      console.log(`Error with agreementId: ${doc.uuid}`, e);
      retryDocs.push([organization, doc.uuid, doc]);
    }
    if (data.length % 1000 === 0) {
      console.log(`${d()} Get signing data in progress: ${data.length} / ${documents.length}`);
    }
  }
  return data;
}

async function getOrganizations() {
  const body = await get('/api/rest/1/user/me/organizations');

  return body.organizations;
}

function getCSVFilename() {
  // Replace colons and dots in the name for Windows support.
  const today = d().replaceAll(/[:.]/ig, '_');
  return `export-signing-documents-${today}.csv`;
}

async function doIt() {
  console.log(`${d()} Export starts`);
  const filename = getCSVFilename();
  const writableStream = fs.createWriteStream(filename);
  const columns = [
    'Organization ID',
    'Organization Name',
    'Document ID',
    'Document URL',
    'Title',
    'Number of needed signatures',
    'People who need to sign',
    'People who signed'
    ];
  const stringifier = stringify({ header: true, columns: columns });
  const organizations = await getOrganizations();

  for (const organization of organizations) {
    const data = await getFullData(organization);
    for (const d of data) {
      stringifier.write(d);
    }
  }
  console.log(`${d()} Retry ${retryDocs.length} documents in error`);
  for (const d of retryDocs) {
    try {
      stringifier.write(await getAgreementData(d[0], d[1], d[2]));
    } catch (e) {
      console.log(`Error (2) with agreementId: ${d[1]}`, e);
    }
  }
  stringifier.pipe(writableStream);
  console.log(`${d()} Export ends`);
}

doIt();
