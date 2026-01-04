from datetime import datetime, timezone
import json


def log_security_event(user_id, action, details=None) -> None:
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": user_id,
        "action": action,
        "details": details or {},
    }
    try:
        with open("audit_security.log", "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry) + "\n")
    except OSError:
        pass
