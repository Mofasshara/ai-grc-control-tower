import ast
from datetime import datetime, timedelta
from pathlib import Path

import yaml
from sqlalchemy.orm import Session

from models import AIIncident, AISystem
from services.risk_metrics_service import RiskMetricsService


class IncidentTriageService:
    def __init__(self, db: Session):
        self.db = db
        self.rules = self._load_rules()
        self.root_cause_map = self._load_root_cause_map()

    @staticmethod
    def _rules_path() -> Path:
        return Path(__file__).resolve().parent.parent / "triage" / "triage_rules.yaml"

    def _load_rules(self) -> dict:
        with self._rules_path().open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def _load_root_cause_map(self) -> dict:
        path = Path(__file__).resolve().parent.parent / "triage" / "root_cause_map.yaml"
        with path.open("r", encoding="utf-8") as handle:
            return yaml.safe_load(handle) or {}

    def suggest(self, incident: AIIncident) -> dict:
        ai_system = (
            self.db.query(AISystem)
            .filter(AISystem.id == incident.ai_system_id)
            .first()
        )
        risk = (
            getattr(ai_system.risk_classification, "value", None)
            if ai_system
            else "low"
        )
        incident_type = getattr(incident.incident_type, "value", incident.incident_type)

        risk_service = RiskMetricsService(self.db)
        drift_flag = self._check_drift(incident.ai_system_id, risk_service)
        incidents_last_30_days = self._incident_count_last_30_days(incident.ai_system_id)
        volatility = risk_service.changes_last_30_days().get(str(incident.ai_system_id), 0)

        context = {
            "risk": risk,
            "type": incident_type,
            "drift_flag": drift_flag,
            "incidents_last_30_days": incidents_last_30_days,
            "volatility": volatility,
        }

        suggestion = {
            "severity": "Medium",
            "owner_role": "AI_OWNER",
            "root_cause": "Unclassified",
            "reason": "Default rule applied",
        }

        for rule in self.rules.get("severity_rules", []):
            if self._match_condition(rule.get("condition"), context):
                suggestion = {
                    "severity": rule.get("suggested_severity", "Medium"),
                    "owner_role": rule.get("owner_role", "AI_OWNER"),
                    "root_cause": rule.get("root_cause", "Unclassified"),
                    "reason": rule.get("reason", "Rule matched"),
                }
                break

        context["severity"] = suggestion["severity"]

        for esc in self.rules.get("escalation_rules", []):
            if self._match_condition(esc.get("condition"), context):
                levels = int(esc.get("escalate_by", 0))
                suggestion["severity"] = self._escalate(suggestion["severity"], levels)
                suggestion["reason"] += f" | Escalation: {esc.get('reason', 'rule')}"
                context["severity"] = suggestion["severity"]

        for dr in self.rules.get("drift_rules", []):
            if self._match_condition(dr.get("condition"), context):
                suggestion["severity"] = dr.get("suggested_severity", suggestion["severity"])
                suggestion["owner_role"] = dr.get("owner_role", suggestion["owner_role"])
                suggestion["root_cause"] = dr.get("root_cause", suggestion["root_cause"])
                suggestion["reason"] += f" | Drift rule: {dr.get('reason', 'rule')}"

        root_cause_category, root_cause_explanation = self._suggest_root_cause(
            incident_type
        )
        if suggestion["root_cause"] == "Unclassified":
            suggestion["root_cause"] = root_cause_category
        suggestion["root_cause_explanation"] = root_cause_explanation

        return suggestion

    def _incident_count_last_30_days(self, system_id: str) -> int:
        cutoff = datetime.utcnow() - timedelta(days=30)
        return (
            self.db.query(AIIncident)
            .filter(
                AIIncident.ai_system_id == system_id,
                AIIncident.created_at >= cutoff,
            )
            .count()
        )

    @staticmethod
    def _check_drift(system_id: str, risk_service: RiskMetricsService) -> bool:
        prompt = risk_service.prompt_drift().get(str(system_id), {})
        rag = risk_service.rag_drift().get(str(system_id), {})
        incident_links = risk_service.change_after_incident().get(str(system_id), [])

        return (
            prompt.get("prompt_drift_flag", False)
            or rag.get("rag_drift_flag", False)
            or len(incident_links) > 0
        )

    def _suggest_root_cause(self, incident_type: str) -> tuple[str, str]:
        options = self.root_cause_map.get(incident_type, [])
        if not options:
            return ("Unclassified", "No root cause mapping available.")

        first = options[0]
        return (
            first.get("category", "Unclassified"),
            first.get("explanation", "No explanation provided."),
        )

    @staticmethod
    def _escalate(severity: str, levels: int) -> str:
        order = ["Low", "Medium", "High"]
        if severity not in order:
            return severity
        idx = min(order.index(severity) + levels, len(order) - 1)
        return order[idx]

    @staticmethod
    def _match_condition(condition: str | None, context: dict) -> bool:
        if not condition:
            return False
        tree = ast.parse(condition, mode="eval")
        return IncidentTriageService._eval_node(tree.body, context)

    @staticmethod
    def _eval_node(node: ast.AST, context: dict):
        if isinstance(node, ast.BoolOp):
            values = [IncidentTriageService._eval_node(v, context) for v in node.values]
            if isinstance(node.op, ast.And):
                return all(values)
            if isinstance(node.op, ast.Or):
                return any(values)
        if isinstance(node, ast.Compare):
            left = IncidentTriageService._eval_node(node.left, context)
            for op, comparator in zip(node.ops, node.comparators):
                right = IncidentTriageService._eval_node(comparator, context)
                if isinstance(op, ast.Eq):
                    if left != right:
                        return False
                elif isinstance(op, ast.NotEq):
                    if left == right:
                        return False
                elif isinstance(op, ast.Gt):
                    if left <= right:
                        return False
                elif isinstance(op, ast.GtE):
                    if left < right:
                        return False
                elif isinstance(op, ast.Lt):
                    if left >= right:
                        return False
                elif isinstance(op, ast.LtE):
                    if left > right:
                        return False
                elif isinstance(op, ast.In):
                    if left not in right:
                        return False
                elif isinstance(op, ast.NotIn):
                    if left in right:
                        return False
                else:
                    raise ValueError("Unsupported operator")
                left = right
            return True
        if isinstance(node, ast.Name):
            return context.get(node.id)
        if isinstance(node, ast.Constant):
            return node.value
        if isinstance(node, ast.Tuple):
            return tuple(IncidentTriageService._eval_node(elt, context) for elt in node.elts)
        raise ValueError("Unsupported condition expression")
