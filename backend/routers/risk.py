from fastapi import APIRouter, Depends

from database import get_db
from services.risk_metrics_service import RiskMetricsService

router = APIRouter(prefix="/risk", tags=["Risk"])


@router.get("/summary")
def risk_summary(db=Depends(get_db)):
    service = RiskMetricsService(db)
    hallucination_rates = service.hallucination_rate_per_system()

    return {
        "incident_severity_counts": service.count_incidents_by_severity(),
        "hallucination_rates": hallucination_rates,
        "changes_last_30_days": service.changes_last_30_days(),
        "flags": {
            "high_risk": any(
                rate.get("hallucination_rate", 0) > 0.2
                for rate in hallucination_rates.values()
            )
        },
    }


@router.get("/ai-systems/{id}")
def risk_for_system(id: str, db=Depends(get_db)):
    service = RiskMetricsService(db)

    hallucination_data = service.hallucination_rate_per_system().get(id, {})
    changes = service.changes_last_30_days().get(id, 0)

    return {
        "system_id": id,
        "hallucination_data": hallucination_data,
        "changes_last_30_days": changes,
        "flags": {
            "high_hallucination_rate": hallucination_data.get("hallucination_rate", 0)
            > 0.2,
            "high_volatility": changes > 10,
        },
    }


@router.get("/trends/hallucinations")
def hallucination_trend(db=Depends(get_db)):
    """Get hallucination incident counts per week."""
    service = RiskMetricsService(db)
    return service.hallucinations_per_week()


@router.get("/trends/severity")
def severity_trend(days: int = 30, db=Depends(get_db)):
    """Get incident severity distribution over time (default: 30 days)"""
    service = RiskMetricsService(db)
    return service.severity_trend(days=days)


@router.get("/trends/repeated-incidents")
def repeated_incidents(db=Depends(get_db)):
    """Identify AI systems with more than 3 incidents (unstable systems)"""
    service = RiskMetricsService(db)
    return service.repeated_incidents()


@router.get("/trends/incidents")
def incident_trends(db=Depends(get_db)):
    """Aggregate incident trend signals for monitoring views."""
    service = RiskMetricsService(db)
    return {
        "hallucinations_per_week": service.hallucinations_per_week(),
        "severity_trend": service.severity_trend(),
        "repeated_incidents": service.repeated_incidents(),
    }


@router.get("/drift")
def drift_signals(db=Depends(get_db)):
    """Get drift signals for all AI systems (prompt, RAG, and incident-correlated changes)"""
    service = RiskMetricsService(db)

    return {
        "prompt_drift": service.prompt_drift(),
        "rag_drift": service.rag_drift(),
        "incident_correlated_drift": service.change_after_incident(),
    }
