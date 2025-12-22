#!/usr/bin/env python3
"""
Export Signed Agreements with Approval and Execution Times

This script exports all signed agreements from Concord API with complete timeline data:
- Agreement creation date (from first activity in audit trail)
- First and last approval dates
- First and last signature dates

Output: Timestamped CSV file with agreement timeline data
"""

# Configuration: Set your Concord API key here
# Generate your API key at: https://secure.concordnow.com/#/automations/integrations
API_KEY = "YOUR_API_KEY_HERE"  # TODO: Replace with your actual API key

# Base URL for Concord API
BASE_URL = "https://api.concordnow.com"

import sys
import csv
import requests
from datetime import datetime, timezone


def unix_ms_to_utc_string(timestamp_ms):
    """
    Convert Unix timestamp (milliseconds) to UTC datetime string.

    Args:
        timestamp_ms: Integer milliseconds since Unix epoch (e.g., 1750172991000)

    Returns:
        UTC datetime string in format "YYYY-MM-DD HH:MM:SS"
    """
    if timestamp_ms is None or timestamp_ms <= 0:
        return ""

    try:
        # Convert milliseconds to seconds and create UTC datetime
        utc_dt = datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc)

        # Format as string without timezone indicator
        return utc_dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OSError) as e:
        print(f"ERROR: Failed to parse timestamp {timestamp_ms}: {e}")
        sys.exit(1)


def get(path):
    """
    HTTP GET wrapper with authentication and fail-fast error handling.

    Args:
        path: API endpoint path (e.g., "/api/rest/1/user/me/organizations")

    Returns:
        Parsed JSON response

    Exits:
        Exits with status code 1 on any HTTP error
    """
    url = f"{BASE_URL}{path}"
    headers = {
        "X-API-KEY": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)

        # Fail-fast error handling - exit on any non-200 status
        if response.status_code != 200:
            print(f"ERROR: API request failed: {path}")
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            sys.exit(1)

        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"ERROR: Network request failed: {path}")
        print(f"Error: {e}")
        sys.exit(1)


def get_csv_filename():
    """
    Generate Windows-compatible timestamped filename.

    Returns:
        Filename string in format: signed_agreements_execution_time_YYYYMMDD_HHMM.csv
    """
    # Use current time for timestamp (no colons for Windows compatibility)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    return f"signed_agreements_execution_time_{timestamp}.csv"


def get_organizations():
    """
    Fetch list of organizations accessible to the authenticated user.

    Returns:
        List of organization dictionaries with 'id' and 'name' fields
    """
    print("Fetching organizations...")
    response = get("/api/rest/1/user/me/organizations")
    organizations = response.get("organizations", [])

    if not organizations or len(organizations) == 0:
        print("WARNING: No organizations found for this API key")
        return []

    print(f"✓ Found {len(organizations)} organization(s)")
    return organizations


def validate_api_key():
    """
    Validate that API key has been configured (not placeholder value).

    Exits:
        Exits with status code 1 if API key is not configured
    """
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE" or API_KEY.strip() == "":
        print("ERROR: Please set your API_KEY in the script")
        print("Generate your API key at: https://secure.concordnow.com/#/automations/integrations")
        print("Then replace 'YOUR_API_KEY_HERE' on line 15 with your actual API key")
        sys.exit(1)


def get_signed_agreements(org_id):
    """
    Fetch paginated list of signed agreements for an organization.

    Uses pagination with numberOfItemsByPage=500. Page numbering starts at 0.
    Filters for all "signed" status values using multiple status parameters.
    Includes all access types (DIRECT, TAG, FOLDER, ORGANIZATION) to get complete list.

    Args:
        org_id: Organization ID

    Returns:
        List of agreement dictionaries with uuid, title, status, organizationId fields
    """
    all_agreements = []
    page = 0  # Page numbering starts at 0

    # Build status filter parameters (all signed statuses)
    # These map to the "SIGNED" stage in Concord
    status_params = [
        "statuses=UNKNOWN_CONTRACT",
        "statuses=FUTURE_CONTRACT",
        "statuses=CURRENT_CONTRACT",
        "statuses=COMPLETED_CONTRACT",
        "statuses=COMPLETED_CANCEL_CONTRACT",
        "statuses=COMPLETED_CONTRACT_RENEWABLE"
    ]

    # Build access type parameters (all types to get complete list)
    access_params = [
        "accessType=DIRECT",
        "accessType=TAG",
        "accessType=FOLDER",
        "accessType=ORGANIZATION"
    ]

    while True:
        # Construct query string with all parameters
        query_parts = status_params + access_params + [
            f"numberOfItemsByPage=500",
            f"page={page}"
        ]
        query_string = "&".join(query_parts)

        print(f"Fetching agreements (page {page})...")
        path = f"/api/rest/1/user/me/organizations/{org_id}/agreements?{query_string}"
        response = get(path)

        # API returns {"items": [...]} not a direct array
        items = response.get("items", [])

        if not items:
            break

        all_agreements.extend(items)
        print(f"  Retrieved {len(items)} agreements from page {page}")

        # Continue if we got a full page (might be more)
        if len(items) < 500:
            break

        page += 1

    return all_agreements


def get_agreement_activities(org_id, agreement_uid):
    """
    Fetch audit trail activities for a specific agreement.

    Args:
        org_id: Organization ID
        agreement_uid: Agreement UID

    Returns:
        List of activity dictionaries with name, createdAt, and other fields
        Returns {"activities": [...]} response structure
    """
    path = f"/api/rest/1/organizations/{org_id}/agreements/{agreement_uid}/activities?type=AUDIT"
    response = get(path)

    # Return full response (contains {"activities": [...]})
    return response


def extract_creation_date(activities_response):
    """
    Extract creation date from earliest activity in audit trail.

    The creation date is the timestamp of the first (earliest) activity,
    NOT from the agreements list API (which is not always accurate).

    Args:
        activities_response: Response dict with "activities" key

    Returns:
        UTC datetime string of earliest activity, or empty string if no activities
    """
    activities = activities_response.get("activities", [])

    if not activities:
        return ""

    # Find earliest timestamp across ALL activities
    earliest_timestamp = min(activity.get("createdAt", float('inf')) for activity in activities)

    if earliest_timestamp == float('inf'):
        return ""

    return unix_ms_to_utc_string(earliest_timestamp)


def extract_created_by(activities_response):
    """
    Extract the email of the user who created the agreement from the earliest activity.

    Args:
        activities_response: Response dict with "activities" key

    Returns:
        User email address, or empty string if cannot determine
    """
    activities = activities_response.get("activities", [])

    if not activities:
        return ""

    # Find earliest activity
    earliest_activity = min(activities, key=lambda a: a.get("createdAt", float('inf')))

    # Extract user email from creator.actor structure
    creator = earliest_activity.get("creator", {})
    actor = creator.get("actor", {})

    return actor.get("email", "")


def extract_approval_dates(activities_response):
    """
    Extract first and last approval dates from audit trail.

    Filters for VALIDATION_ACCEPT activity type (workflow approvals).

    Args:
        activities_response: Response dict with "activities" key

    Returns:
        Tuple of (first_approval_utc, last_approval_utc) as strings
        Returns ("", "") if no approval activities found
    """
    activities = activities_response.get("activities", [])

    # Filter for approval activities (VALIDATION_ACCEPT)
    approval_activities = [
        activity for activity in activities
        if activity.get("name") == "VALIDATION_ACCEPT"
    ]

    if not approval_activities:
        return ("", "")

    # Get timestamps
    timestamps = [activity.get("createdAt") for activity in approval_activities if activity.get("createdAt")]

    if not timestamps:
        return ("", "")

    # Sort to find first and last
    timestamps.sort()
    first_utc = unix_ms_to_utc_string(timestamps[0])
    last_utc = unix_ms_to_utc_string(timestamps[-1])

    return (first_utc, last_utc)


def extract_detailed_approvals(activities_response, max_approvers=5):
    """
    Extract up to max_approvers approval details (email + date) from audit trail.

    Filters for VALIDATION_ACCEPT activity type (workflow approvals).

    Args:
        activities_response: Response dict with "activities" key
        max_approvers: Maximum number of approvers to return (default: 5)

    Returns:
        Tuple of (approvals_list, total_count)
        - approvals_list: List of dicts with 'email' and 'date' (up to max_approvers)
        - total_count: Total number of approvals (including those beyond max_approvers)
    """
    activities = activities_response.get("activities", [])

    # Filter for approval activities (VALIDATION_ACCEPT)
    approval_activities = [
        activity for activity in activities
        if activity.get("name") == "VALIDATION_ACCEPT"
    ]

    if not approval_activities:
        return ([], 0)

    # Sort by timestamp (earliest first)
    approval_activities.sort(key=lambda a: a.get("createdAt", 0))

    # Extract approver details
    approvals = []
    for activity in approval_activities[:max_approvers]:
        # Extract email from creator.actor structure
        creator = activity.get("creator", {})
        actor = creator.get("actor", {})
        approver_email = actor.get("email", "")
        approval_date = unix_ms_to_utc_string(activity.get("createdAt"))

        approvals.append({
            "email": approver_email,
            "date": approval_date
        })

    return (approvals, len(approval_activities))


def extract_signature_dates(activities_response):
    """
    Extract first and last signature dates from audit trail.

    Filters for NEGOTIATION_APPROVE activity type (eSignatures),
    or AGREEMENT_SIGNATURE_FINALIZE activity type (finalize signature).

    Args:
        activities_response: Response dict with "activities" key

    Returns:
        Tuple of (first_signature_utc, last_signature_utc) as strings
        Returns ("", "") if no signature activities found
    """
    activities = activities_response.get("activities", [])

    # Filter for signature activities (NEGOTIATION_APPROVE and AGREEMENT_SIGNATURE_FINALIZE)
    signature_activities = [
        activity for activity in activities
        if activity.get("name") in ["NEGOTIATION_APPROVE", "AGREEMENT_SIGNATURE_FINALIZE"]
    ]

    if not signature_activities:
        return ("", "")

    # Get timestamps
    timestamps = [activity.get("createdAt") for activity in signature_activities if activity.get("createdAt")]

    if not timestamps:
        return ("", "")

    # Sort to find first and last
    timestamps.sort()
    first_utc = unix_ms_to_utc_string(timestamps[0])
    last_utc = unix_ms_to_utc_string(timestamps[-1])

    return (first_utc, last_utc)


def extract_detailed_signatures(activities_response, max_signers=5):
    """
    Extract up to max_signers signature details (email + date) from audit trail.

    Filters for NEGOTIATION_APPROVE and AGREEMENT_SIGNATURE_FINALIZE activity types.

    Args:
        activities_response: Response dict with "activities" key
        max_signers: Maximum number of signers to return (default: 5)

    Returns:
        Tuple of (signatures_list, total_count)
        - signatures_list: List of dicts with 'email' and 'date' (up to max_signers)
        - total_count: Total number of signatures (including those beyond max_signers)
    """
    activities = activities_response.get("activities", [])

    # Filter for signature activities
    signature_activities = [
        activity for activity in activities
        if activity.get("name") in ["NEGOTIATION_APPROVE", "AGREEMENT_SIGNATURE_FINALIZE"]
    ]

    if not signature_activities:
        return ([], 0)

    # Sort by timestamp (earliest first)
    signature_activities.sort(key=lambda a: a.get("createdAt", 0))

    # Extract signer details
    signatures = []
    for activity in signature_activities[:max_signers]:
        # Extract email from creator.actor structure
        creator = activity.get("creator", {})
        actor = creator.get("actor", {})
        signer_email = actor.get("email", "")
        signature_date = unix_ms_to_utc_string(activity.get("createdAt"))

        signatures.append({
            "email": signer_email,
            "date": signature_date
        })

    return (signatures, len(signature_activities))


def construct_agreement_url(org_id, agreement_uuid):
    """
    Build web URL for viewing agreement in Concord interface.

    Args:
        org_id: Organization ID
        agreement_uuid: Agreement UUID

    Returns:
        Full web URL string
    """
    return f"https://secure.concordnow.com/#/organizations/{org_id}/agreements/{agreement_uuid}"


def process_agreement(org_id, agreement):
    """
    Process a single agreement to extract all timeline data.

    Orchestrates: fetch activities, extract creation/approval/signature dates,
    construct URL, and build complete timeline dictionary.

    Args:
        org_id: Organization ID
        agreement: Agreement dictionary with uuid, title fields

    Returns:
        Dictionary with all timeline fields for CSV export:
        - agreementId, agreementTitle, agreementLink
        - creationDate, createdBy
        - approver1-5, approvalDate1-5
        - signer1-5, signatureDate1-5
        - firstApprovalDate, lastApprovalDate (backward compatibility)
        - firstSignatureDate, lastSignatureDate (backward compatibility)
        - totalApprovals, totalSignatures
    """
    agreement_uuid = agreement.get("uuid")
    agreement_title = agreement.get("title", "")

    # Fetch audit trail activities
    activities_response = get_agreement_activities(org_id, agreement_uuid)

    # Extract all timeline data
    creation_date = extract_creation_date(activities_response)
    created_by = extract_created_by(activities_response)

    # Extract detailed approvals and signatures
    detailed_approvals, total_approvals = extract_detailed_approvals(activities_response)
    detailed_signatures, total_signatures = extract_detailed_signatures(activities_response)

    # Extract first/last dates for backward compatibility
    first_approval, last_approval = extract_approval_dates(activities_response)
    first_signature, last_signature = extract_signature_dates(activities_response)

    # Print warnings if more than 5 approvals or signatures
    if total_approvals > 5:
        print(f"  WARNING: Agreement '{agreement_title[:50]}' has {total_approvals} approvals (showing first 5)")
    if total_signatures > 5:
        print(f"  WARNING: Agreement '{agreement_title[:50]}' has {total_signatures} signatures (showing first 5)")

    # Construct web URL
    agreement_link = construct_agreement_url(org_id, agreement_uuid)

    # Build complete timeline dictionary with all new fields
    result = {
        "agreementId": agreement_uuid,
        "agreementTitle": agreement_title,
        "agreementLink": agreement_link,
        "creationDate": creation_date,
        "createdBy": created_by,
    }

    # Add approver details (up to 5)
    for i in range(5):
        if i < len(detailed_approvals):
            result[f"approver{i+1}"] = detailed_approvals[i]["email"]
            result[f"approvalDate{i+1}"] = detailed_approvals[i]["date"]
        else:
            result[f"approver{i+1}"] = ""
            result[f"approvalDate{i+1}"] = ""

    # Add signer details (up to 5)
    for i in range(5):
        if i < len(detailed_signatures):
            result[f"signer{i+1}"] = detailed_signatures[i]["email"]
            result[f"signatureDate{i+1}"] = detailed_signatures[i]["date"]
        else:
            result[f"signer{i+1}"] = ""
            result[f"signatureDate{i+1}"] = ""

    # Add backward compatible fields
    result["firstApprovalDate"] = first_approval
    result["lastApprovalDate"] = last_approval
    result["firstSignatureDate"] = first_signature
    result["lastSignatureDate"] = last_signature

    # Add totals
    result["totalApprovals"] = total_approvals
    result["totalSignatures"] = total_signatures

    return result


def write_csv(filename, agreement_timelines):
    """
    Write agreement timeline data to CSV file.

    CSV columns (32 total):
    - Agreement ID, Title, Link, Creation Date, Created By
    - Approver 1-5, Approval Date 1-5 (10 columns)
    - Signer 1-5, Signature Date 1-5 (10 columns)
    - First Approval Date, Last Approval Date (backward compatibility)
    - First Signature Date, Last Signature Date (backward compatibility)
    - Total Approvals, Total Signatures

    Args:
        filename: Output CSV filename
        agreement_timelines: List of timeline dictionaries
    """
    # Define CSV headers (32 columns total - must match spec exactly)
    headers = [
        # Columns 1-5: Basics
        "Agreement ID",
        "Agreement Title",
        "Agreement Link",
        "Creation Date",
        "Created By",
        # Columns 6-15: Detailed approvals (5 approvers)
        "Approver 1",
        "Approval Date 1",
        "Approver 2",
        "Approval Date 2",
        "Approver 3",
        "Approval Date 3",
        "Approver 4",
        "Approval Date 4",
        "Approver 5",
        "Approval Date 5",
        # Columns 16-25: Detailed signatures (5 signers)
        "Signer 1",
        "Signature Date 1",
        "Signer 2",
        "Signature Date 2",
        "Signer 3",
        "Signature Date 3",
        "Signer 4",
        "Signature Date 4",
        "Signer 5",
        "Signature Date 5",
        # Columns 26-29: Backward compatibility
        "First Approval Date",
        "Last Approval Date",
        "First Signature Date",
        "Last Signature Date",
        # Columns 30-31: Totals
        "Total Approvals",
        "Total Signatures"
    ]

    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            # Write header row
            writer.writerow(headers)

            # Write data rows
            for timeline in agreement_timelines:
                row = [
                    # Columns 1-5: Basics
                    timeline.get("agreementId", ""),
                    timeline.get("agreementTitle", ""),
                    timeline.get("agreementLink", ""),
                    timeline.get("creationDate", ""),
                    timeline.get("createdBy", ""),
                    # Columns 6-15: Detailed approvals
                    timeline.get("approver1", ""),
                    timeline.get("approvalDate1", ""),
                    timeline.get("approver2", ""),
                    timeline.get("approvalDate2", ""),
                    timeline.get("approver3", ""),
                    timeline.get("approvalDate3", ""),
                    timeline.get("approver4", ""),
                    timeline.get("approvalDate4", ""),
                    timeline.get("approver5", ""),
                    timeline.get("approvalDate5", ""),
                    # Columns 16-25: Detailed signatures
                    timeline.get("signer1", ""),
                    timeline.get("signatureDate1", ""),
                    timeline.get("signer2", ""),
                    timeline.get("signatureDate2", ""),
                    timeline.get("signer3", ""),
                    timeline.get("signatureDate3", ""),
                    timeline.get("signer4", ""),
                    timeline.get("signatureDate4", ""),
                    timeline.get("signer5", ""),
                    timeline.get("signatureDate5", ""),
                    # Columns 26-29: Backward compatibility
                    timeline.get("firstApprovalDate", ""),
                    timeline.get("lastApprovalDate", ""),
                    timeline.get("firstSignatureDate", ""),
                    timeline.get("lastSignatureDate", ""),
                    # Columns 30-31: Totals
                    timeline.get("totalApprovals", ""),
                    timeline.get("totalSignatures", "")
                ]
                writer.writerow(row)

        print(f"✓ CSV file written: {filename}")

    except IOError as e:
        print(f"ERROR: Failed to write CSV file: {e}")
        sys.exit(1)


def main():
    """
    Main execution function.

    Orchestrates:
    1. Validate API key
    2. Get organizations
    3. Fetch signed agreements (with pagination)
    4. Process each agreement sequentially (extract timeline data)
    5. Write CSV output
    6. Display success summary
    """
    print("Export Signed Agreements - Approval & Execution Time")
    print("=" * 54)
    print()

    # Validate API key
    validate_api_key()
    print("✓ API key configured")
    print()

    # Get organizations
    organizations = get_organizations()

    if not organizations:
        print("No organizations found. Exiting.")
        sys.exit(0)

    print()

    # Collect all agreement timelines
    all_timelines = []

    # Process each organization
    for org in organizations:
        org_id = org.get("id")
        org_name = org.get("name", "Unknown")

        print(f"Processing organization: {org_name}")

        # Fetch signed agreements for this organization
        agreements = get_signed_agreements(org_id)

        if not agreements:
            print(f"  No signed agreements found for {org_name}")
            continue

        print(f"✓ Found {len(agreements)} signed agreement(s)")
        print()

        # Process each agreement sequentially
        print(f"Processing agreements:")
        for i, agreement in enumerate(agreements, 1):
            agreement_title = agreement.get("title", "Untitled")
            print(f"  [{i}/{len(agreements)}] {agreement_title[:50]}...")

            # Extract timeline data
            timeline = process_agreement(org_id, agreement)
            all_timelines.append(timeline)

        print()

    # Generate CSV output
    if not all_timelines:
        print("No agreements to export. Exiting.")
        sys.exit(0)

    print("Writing CSV output...")
    filename = get_csv_filename()
    write_csv(filename, all_timelines)

    # Summary statistics
    print()
    print("✓ Export complete!")
    print()
    print(f"Output file: {filename}")
    print(f"Total agreements exported: {len(all_timelines)}")

    # Count agreements with/without approvals and signatures
    with_approvals = sum(1 for t in all_timelines if t.get("firstApprovalDate"))
    without_approvals = len(all_timelines) - with_approvals
    with_signatures = sum(1 for t in all_timelines if t.get("firstSignatureDate"))
    without_signatures = len(all_timelines) - with_signatures

    print(f"Agreements with approvals: {with_approvals}")
    print(f"Agreements without approvals: {without_approvals}")
    print(f"Agreements with signatures: {with_signatures}")
    print(f"Agreements without signatures: {without_signatures}")
    print()
    print("You can now open the CSV file in Excel, Google Sheets, or any spreadsheet application.")


if __name__ == "__main__":
    main()
