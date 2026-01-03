#!/usr/bin/env python
"""Import data to Azure via API endpoints."""

import json
import sys
import httpx
from pathlib import Path


AZURE_BASE_URL = "https://ai-grc-api-dev-h7dchcdad7c6bmdh.switzerlandnorth-01.azurewebsites.net"
HEADERS = {
    "Content-Type": "application/json",
    "accept": "application/json",
    "x-user-id": "migration-script",  # For audit logs
}


def import_data(data_file: str, dry_run: bool = False):
    """Import data to Azure via API."""

    with open(data_file, 'r') as f:
        data = json.load(f)

    print(f"{'[DRY RUN] ' if dry_run else ''}Starting import...")
    print(f"Data to import:")
    for key, items in data.items():
        print(f"  {key}: {len(items)} records")

    if dry_run:
        print("\nDry run - no actual API calls will be made.")
        return

    client = httpx.Client(timeout=30.0, follow_redirects=True)
    results = {
        "ai_systems": {"success": 0, "failed": 0},
        "change_requests": {"success": 0, "failed": 0},
        "prompt_templates": {"success": 0, "failed": 0},
        "prompt_versions": {"success": 0, "failed": 0},
        "rag_sources": {"success": 0, "failed": 0},
        "rag_source_versions": {"success": 0, "failed": 0},
        "incidents": {"success": 0, "failed": 0},
    }

    try:
        # 1. Import AI Systems first (base dependency)
        print("\n=== Importing AI Systems ===")
        for system in data["ai_systems"]:
            try:
                # Remove fields that shouldn't be in POST
                post_data = {
                    "name": system["name"],
                    "business_purpose": system["business_purpose"],
                    "intended_users": system["intended_users"],
                    "risk_classification": system["risk_classification"],
                    "owner": system["owner"],
                    "created_by": system["created_by"],
                }

                response = client.post(
                    f"{AZURE_BASE_URL}/ai-systems",
                    json=post_data,
                    headers=HEADERS
                )

                if response.status_code in [200, 201]:
                    results["ai_systems"]["success"] += 1
                    print(f"  ✓ Created: {system['name']}")
                else:
                    results["ai_systems"]["failed"] += 1
                    print(f"  ✗ Failed: {system['name']} - {response.status_code}: {response.text}")

            except Exception as e:
                results["ai_systems"]["failed"] += 1
                print(f"  ✗ Error: {system['name']} - {str(e)}")

        # 2. Import Change Requests (depends on AI Systems)
        print("\n=== Importing Change Requests ===")
        for cr in data["change_requests"]:
            try:
                post_data = {
                    "change_type": cr["change_type"],
                    "description": cr["description"],
                    "business_justification": cr["business_justification"],
                    "impact_assessment": cr["impact_assessment"],
                    "rollback_plan": cr["rollback_plan"],
                    "requested_by": cr["requested_by"],
                }

                response = client.post(
                    f"{AZURE_BASE_URL}/ai-systems/{cr['ai_system_id']}/changes",
                    json=post_data,
                    headers=HEADERS
                )

                if response.status_code in [200, 201]:
                    results["change_requests"]["success"] += 1
                    print(f"  ✓ Created change request")
                else:
                    results["change_requests"]["failed"] += 1
                    print(f"  ✗ Failed - {response.status_code}: {response.text}")

            except Exception as e:
                results["change_requests"]["failed"] += 1
                print(f"  ✗ Error - {str(e)}")

        # 3. Import Prompt Templates
        print("\n=== Importing Prompt Templates ===")
        for template in data["prompt_templates"]:
            try:
                post_data = {
                    "name": template["name"],
                    "description": template["description"],
                }

                response = client.post(
                    f"{AZURE_BASE_URL}/prompts/templates",
                    json=post_data,
                    headers=HEADERS
                )

                if response.status_code in [200, 201]:
                    results["prompt_templates"]["success"] += 1
                    print(f"  ✓ Created: {template['name']}")
                else:
                    results["prompt_templates"]["failed"] += 1
                    print(f"  ✗ Failed: {template['name']} - {response.status_code}: {response.text}")

            except Exception as e:
                results["prompt_templates"]["failed"] += 1
                print(f"  ✗ Error: {template['name']} - {str(e)}")

        # 4. Import RAG Sources
        print("\n=== Importing RAG Sources ===")
        for source in data["rag_sources"]:
            try:
                post_data = {
                    "name": source["name"],
                    "description": source["description"],
                    "source_type": source["source_type"],
                }

                response = client.post(
                    f"{AZURE_BASE_URL}/rag/sources",
                    json=post_data,
                    headers=HEADERS
                )

                if response.status_code in [200, 201]:
                    results["rag_sources"]["success"] += 1
                    print(f"  ✓ Created: {source['name']}")
                else:
                    results["rag_sources"]["failed"] += 1
                    print(f"  ✗ Failed: {source['name']} - {response.status_code}: {response.text}")

            except Exception as e:
                results["rag_sources"]["failed"] += 1
                print(f"  ✗ Error: {source['name']} - {str(e)}")

        # Print summary
        print("\n" + "="*50)
        print("IMPORT SUMMARY")
        print("="*50)
        for entity, stats in results.items():
            total = stats["success"] + stats["failed"]
            if total > 0:
                print(f"{entity}:")
                print(f"  ✓ Success: {stats['success']}/{total}")
                print(f"  ✗ Failed:  {stats['failed']}/{total}")

    finally:
        client.close()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python import_to_azure.py <data.json> [--dry-run]")
        sys.exit(1)

    data_file = sys.argv[1]
    dry_run = "--dry-run" in sys.argv

    import_data(data_file, dry_run)
