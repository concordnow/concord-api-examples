const https = require("https");
const fs = require("fs");
const { stringify } = require("csv-stringify");

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
      headers: { "X-API-KEY": apiKey },
    };

    https
      .get(options, (res) => {
        if (res.statusCode !== 200) {
          console.log("Error: Status Code", res.statusCode);
          return reject(res.statusCode);
        }
        let data = [];
        res.on("data", (chunk) => {
          data.push(chunk);
        });
        res.on("end", () => {
          resolve(JSON.parse(Buffer.concat(data).toString()));
        });
      })
      .on("error", (err) => {
        console.log("Error", err.message);
        reject(err.message);
      });
  });
}

async function getAgreementsByPage(organizationId, page) {
  console.log(`${d()} Get Agreements for ${organizationId} (page: ${page})`);
  const getSigningAgreementsQueryParams = [
    "statuses=DRAFT",
    "statuses=BROKEN",
    "statuses=VALIDATION",
    "statuses=NEGOTIATION",
    "statuses=SIGNING",
    "statuses=TEMPLATE",
    "statuses=TEMPLATE_AUTO",
    "statuses=TEMPLATE_SALESFORCE",
    "statuses=TEMPLATE_HUBSPOT",
    "statuses=UNKNOWN_CONTRACT",
    "statuses=FUTURE_CONTRACT",
    "statuses=CURRENT_CONTRACT",
    "statuses=COMPLETED_CONTRACT",
    "statuses=COMPLETED_CANCEL_CONTRACT",
    "statuses=COMPLETED_CONTRACT_RENEWABLE",
    `page=${page}`,
    `numberOfItemsByPage=${pageSize}`,
  ].join("&");
  try {
    return await get(
      `/api/rest/1/user/me/organizations/${organizationId}/agreements?${getSigningAgreementsQueryParams}`
    );
  } catch (e) {
    throw new Error(`Get Signing Agreements failed with ${e}`);
  }
}

async function getAgreements(organizationId) {
  let page = 0;
  let total = 0;
  const items = [];

  do {
    const body = await getAgreementsByPage(organizationId, page);
    items.push(...body.items);
    total = body.total;
    page++;
  } while (total > items.length);
  return items;
}

function computeAgreementStage(status) {
  switch (status) {
    case "TEMPLATE":
    case "TEMPLATE_AUTO":
    case "TEMPLATE_SALESFORCE":
    case "TEMPLATE_HUBSPOT":
      return "TEMPLATE";

    case "DRAFT":
      return "DRAFT";

    case "VALIDATION":
    case "NEGO_INVITE":
    case "NEGOTIATION":
      return "NEGOTIATION";

    case "SIGNING":
      return "SIGNING";

    case "BROKEN":
    case "TRASHED":
      return "CANCELED";

    case "UNKNOWN_CONTRACT":
    case "FUTURE_CONTRACT":
    case "CURRENT_CONTRACT":
    case "COMPLETED_CONTRACT":
    case "COMPLETED_CANCEL_CONTRACT":
    case "COMPLETED_CONTRACT_RENEWABLE":
      return "CONTRACT";
    default:
      return "UNKNOWN";
  }
}

function getStageTranslation(stage, status) {
  if (stage === "CANCELED") {
    if (status === "BROKEN") {
      return "REVIEW";
    }

    return "CANCELED";
  }
  if (stage === "NEGOTIATION") return "REVIEW";
  if (stage === "CONTRACT") return "SIGNED";
  return stage;
}

function getSubStatus(stage, status, validationRequired, signatureRequired) {
  if (
    ["TEMPLATE_AUTO", "TEMPLATE_SALESFORCE", "TEMPLATE_HUBSPOT"].includes(
      status
    )
  ) {
    return "Automated";
  }

  if (stage === "NEGOTIATION" && validationRequired) {
    return "Approval";
  }

  if (stage === "SIGNING" && signatureRequired) {
    return "Signature";
  }

  if (stage === "CANCELED" && status === "BROKEN") {
    return "Canceled";
  }

  if (stage === "CONTRACT" && status === "CURRENT_CONTRACT") {
    return "Active";
  }

  if (stage === "CONTRACT" && status === "FUTURE_CONTRACT") {
    return "Future";
  }

  if (stage === "CONTRACT" && status === "COMPLETED_CONTRACT") {
    return "Expired";
  }

  if (stage === "CONTRACT" && status === "COMPLETED_CONTRACT_RENEWABLE") {
    return "Renewed?";
  }

  if (stage === "CONTRACT" && status === "COMPLETED_CANCEL_CONTRACT") {
    return "Canceled";
  }

  return "";
}

async function getAgreementData(organization, agreementId, doc) {
  const stage = getStageTranslation(
    computeAgreementStage(doc.status),
    doc.status
  );

  const substatus = getSubStatus(
    computeAgreementStage(doc.status),
    doc.status,
    doc.validationRequired,
    doc.signatureRequired
  );

  return [
    organization.id,
    organization.name,
    doc.title,
    `https://secure.concordnow.com/#/organizations/${organization.id}/agreements/${agreementId}`,
    agreementId,
    stage,
    substatus,
  ];
}

async function getFullData(organization) {
  const documents = await getAgreements(organization.id);
  const data = [];

  for (const doc of documents) {
    try {
      data.push(await getAgreementData(organization, doc.uuid, doc));
    } catch (e) {
      console.log(`Error with agreementId: ${doc.uuid}`, e);
      retryDocs.push([organization, doc.uuid, doc]);
    }
    if (data.length % 1000 === 0) {
      console.log(
        `${d()} Get signing data in progress: ${data.length} / ${
          documents.length
        }`
      );
    }
  }
  return data;
}

async function getOrganizations() {
  const body = await get("/api/rest/1/user/me/organizations");
  return body.organizations;
}

function getCSVFilename() {
  // Replace colons and dots in the name for Windows support.
  const today = d().replaceAll(/[:.]/gi, "_");
  return `export-agreements-list-${today}.csv`;
}

async function doIt() {
  console.log(`${d()} Export starts`);
  const filename = getCSVFilename();
  const writableStream = fs.createWriteStream(filename);
  const columns = [
    "Organization ID",
    "Organization Name",
    "Title",
    "Document URL",
    "Document ID",
    "Status",
    "Substatus",
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