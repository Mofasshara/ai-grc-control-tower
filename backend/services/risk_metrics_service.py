from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import (
    AIIncident,
    AISystem,
    AISystemPromptBinding,
    AISystemRAGBinding,
    ChangeRequest,
    IncidentType,
    PromptVersion,
    RAGSourceVersion,
)


class RiskMetricsService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _enum_value(value):
        return getattr(value, "value", value)

    def count_incidents_by_severity(self):
        results = (
            self.db.query(AIIncident.severity, func.count(AIIncident.id))
            .group_by(AIIncident.severity)
            .all()
        )
        return {self._enum_value(severity): count for severity, count in results}

    def hallucination_rate_per_system(self):
        systems = self.db.query(AISystem).all()
        output = {}

        for system in systems:
            total = (
                self.db.query(AIIncident)
                .filter(AIIncident.ai_system_id == system.id)
                .count()
            )
            hallucinations = (
                self.db.query(AIIncident)
                .filter(
                    AIIncident.ai_system_id == system.id,
                    AIIncident.incident_type == IncidentType.HALLUCINATION,
                )
                .count()
            )
            rate = hallucinations / total if total > 0 else 0
            output[str(system.id)] = {
                "system_name": system.name,
                "hallucination_rate": rate,
                "hallucination_count": hallucinations,
                "total_incidents": total,
            }

        return output

    def changes_last_30_days(self):
        cutoff = datetime.utcnow() - timedelta(days=30)
        results = (
            self.db.query(ChangeRequest.ai_system_id, func.count(ChangeRequest.id))
            .filter(ChangeRequest.created_at >= cutoff)
            .group_by(ChangeRequest.ai_system_id)
            .all()
        )
        return {str(system_id): count for system_id, count in results}

    def hallucinations_per_week(self):
        """Count hallucination incidents in the last 7 days"""
        one_week_ago = datetime.utcnow() - timedelta(days=7)

        count = (
            self.db.query(AIIncident)
            .filter(
                AIIncident.incident_type == IncidentType.HALLUCINATION,
                AIIncident.created_at >= one_week_ago,
            )
            .count()
        )

        return {"hallucinations_last_7_days": count}

    def severity_trend(self, days=30):
        """Show incident severity distribution over time"""
        cutoff = datetime.utcnow() - timedelta(days=days)

        results = (
            self.db.query(
                func.date_trunc("day", AIIncident.created_at).label("day"),
                AIIncident.severity,
                func.count(AIIncident.id),
            )
            .filter(AIIncident.created_at >= cutoff)
            .group_by("day", AIIncident.severity)
            .order_by("day")
            .all()
        )

        trend = {}
        for day, severity, count in results:
            day_str = day.date().isoformat()
            severity_val = self._enum_value(severity)
            trend.setdefault(day_str, {})[severity_val] = count

        return trend

    def repeated_incidents(self):
        """Identify AI systems with > 3 incidents (unstable systems)"""
        results = (
            self.db.query(AIIncident.ai_system_id, func.count(AIIncident.id))
            .group_by(AIIncident.ai_system_id)
            .having(func.count(AIIncident.id) > 3)
            .all()
        )

        return {str(system_id): count for system_id, count in results}

    def prompt_drift(self):
        """Detect frequent prompt changes (>3 in 30 days) per AI system"""
        cutoff = datetime.utcnow() - timedelta(days=30)

        results = (
            self.db.query(
                AISystemPromptBinding.ai_system_id, func.count(PromptVersion.id)
            )
            .join(
                PromptVersion,
                AISystemPromptBinding.prompt_version_id == PromptVersion.id,
            )
            .filter(PromptVersion.created_at >= cutoff)
            .group_by(AISystemPromptBinding.ai_system_id)
            .all()
        )

        drift = {}
        for system_id, count in results:
            drift[str(system_id)] = {
                "prompt_changes_30d": count,
                "prompt_drift_flag": count >= 3,
            }

        return drift

    def rag_drift(self):
        """Detect frequent RAG source changes (>3 in 30 days) per AI system"""
        cutoff = datetime.utcnow() - timedelta(days=30)

        results = (
            self.db.query(
                AISystemRAGBinding.ai_system_id, func.count(RAGSourceVersion.id)
            )
            .join(
                RAGSourceVersion,
                AISystemRAGBinding.rag_source_version_id == RAGSourceVersion.id,
            )
            .filter(RAGSourceVersion.created_at >= cutoff)
            .group_by(AISystemRAGBinding.ai_system_id)
            .all()
        )

        drift = {}
        for system_id, count in results:
            drift[str(system_id)] = {
                "rag_changes_30d": count,
                "rag_drift_flag": count >= 3,
            }

        return drift

    def change_after_incident(self):
        """Find changes made within 7 days of incidents (reactive behavior)"""
        output = {}

        incidents = self.db.query(AIIncident).all()
        changes = self.db.query(ChangeRequest).all()

        for inc in incidents:
            for ch in changes:
                if ch.ai_system_id == inc.ai_system_id:
                    time_diff = (ch.created_at - inc.created_at).days
                    if 0 <= time_diff <= 7:
                        output.setdefault(str(inc.ai_system_id), []).append(
                            {
                                "incident_id": str(inc.id),
                                "change_id": str(ch.id),
                                "days_after_incident": time_diff,
                            }
                        )

        return output
