# Concord / Export Signers

This project creates a CSV file with the following columns:
- Organization ID
- Document ID
- Document URL
- Title
- Number of needed signatures
- People who need to sign
- People who signed

Each line is a document at the signing stage.

The CSV file is created in the same folder of the script and the name is:
- export-signing-documents-20YY-MM-DDTHH_MM_SS_MSZ.csv

## Prerequisite

Having Node.JS and NPM installed.

## How to execute

Initialize the project and load the node modules.

`npm install`

Insert your API key in the `index.js` file, line 5. The API key is user-based and can be created from Concord application. Pick a user who has access to all documents.

Execute the script

`node index.js`

## To go further

Concord API documentation: https://api.doc.concordnow.com/.
