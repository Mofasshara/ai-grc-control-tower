#!/usr/bin/env python
"""Export local database data to JSON for migration to Azure."""

import json
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(Path(__file__).parent.parent / ".env")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import SessionLocal
from models import (
    AISystem,
    ChangeRequest,
    PromptTemplate,
    PromptVersion,
    RAGSource,
    RAGSourceVersion,
    AIIncident,
)


def export_data():
    """Export all data from local database to JSON."""
    db = SessionLocal()

    try:
        data = {
            "ai_systems": [],
            "change_requests": [],
            "prompt_templates": [],
            "prompt_versions": [],
            "rag_sources": [],
            "rag_source_versions": [],
            "incidents": [],
        }

        # Export AI Systems
        for system in db.query(AISystem).all():
            data["ai_systems"].append({
                "id": str(system.id),
                "name": system.name,
                "business_purpose": system.business_purpose,
                "intended_users": system.intended_users,
                "risk_classification": system.risk_classification,
                "owner": system.owner,
                "created_by": system.created_by,
                "lifecycle_status": system.lifecycle_status,
                "created_at": system.created_at.isoformat() if system.created_at else None,
                "last_changed_at": system.last_changed_at.isoformat() if system.last_changed_at else None,
                "last_change_request_id": str(system.last_change_request_id) if system.last_change_request_id else None,
            })

        # Export Change Requests
        for cr in db.query(ChangeRequest).all():
            data["change_requests"].append({
                "id": str(cr.id),
                "ai_system_id": str(cr.ai_system_id),
                "change_type": cr.change_type,
                "description": cr.description,
                "business_justification": cr.business_justification,
                "impact_assessment": cr.impact_assessment,
                "rollback_plan": cr.rollback_plan,
                "status": cr.status,
                "requested_by": cr.requested_by,
                "approved_by": cr.approved_by,
                "created_at": cr.created_at.isoformat() if cr.created_at else None,
                "approved_at": cr.approved_at.isoformat() if cr.approved_at else None,
            })

        # Export Prompt Templates
        for template in db.query(PromptTemplate).all():
            data["prompt_templates"].append({
                "id": str(template.id),
                "name": template.name,
                "description": template.description,
                "created_at": template.created_at.isoformat() if template.created_at else None,
                "created_by": template.created_by,
            })

        # Export Prompt Versions
        for version in db.query(PromptVersion).all():
            data["prompt_versions"].append({
                "id": str(version.id),
                "prompt_template_id": str(version.prompt_template_id),
                "version": version.version,
                "prompt_text": version.prompt_text,
                "parameters_schema": version.parameters_schema,
                "status": version.status,
                "content_hash": version.content_hash,
                "diff_from_prev": version.diff_from_prev,
                "change_request_id": str(version.change_request_id) if version.change_request_id else None,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "created_by": version.created_by,
            })

        # Export RAG Sources
        for source in db.query(RAGSource).all():
            data["rag_sources"].append({
                "id": str(source.id),
                "name": source.name,
                "description": source.description,
                "source_type": source.source_type,
                "created_at": source.created_at.isoformat() if source.created_at else None,
                "created_by": source.created_by,
            })

        # Export RAG Source Versions
        for version in db.query(RAGSourceVersion).all():
            data["rag_source_versions"].append({
                "id": str(version.id),
                "rag_source_id": str(version.rag_source_id),
                "version": version.version,
                "status": version.status,
                "uri": version.uri,
                "ingestion_config": version.ingestion_config,
                "embedding_config": version.embedding_config,
                "content_hash": version.content_hash,
                "diff_from_prev": version.diff_from_prev,
                "change_request_id": str(version.change_request_id) if version.change_request_id else None,
                "created_at": version.created_at.isoformat() if version.created_at else None,
                "created_by": version.created_by,
            })

        # Export Incidents
        for incident in db.query(AIIncident).all():
            data["incidents"].append({
                "id": str(incident.id),
                "ai_system_id": str(incident.ai_system_id),
                "incident_type": incident.incident_type,
                "severity": incident.severity,
                "description": incident.description,
                "impact_area": incident.impact_area,
                "status": incident.status,
                "detected_by": incident.detected_by,
                "detection_date": incident.detection_date.isoformat() if incident.detection_date else None,
                "root_cause_description": incident.root_cause_description,
                "root_cause_category": incident.root_cause_category,
                "corrective_change_request_id": str(incident.corrective_change_request_id) if incident.corrective_change_request_id else None,
                "created_at": incident.created_at.isoformat() if incident.created_at else None,
                "created_by": incident.created_by,
            })

        # Print summary
        print(f"Exported:", file=sys.stderr)
        for key, items in data.items():
            print(f"  {key}: {len(items)} records", file=sys.stderr)

        # Output JSON
        print(json.dumps(data, indent=2))

    finally:
        db.close()


if __name__ == "__main__":
    export_data()
