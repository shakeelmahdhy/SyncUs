from datetime import datetime, UTC
def create_application() -> dict:
    return {
        "message": "create application placeholder",
        "status": "applied",
        "timestamp": datetime.now(UTC).isoformat(),
    }
def list_applications() -> dict:
    return {
        "items": [],
        "total": 0,
        "message": "list applications placeholder",
    }
def get_application(application_id: int) -> dict:
    return {
        "application_id": application_id,
        "status": "applied",
        "message": "application detail placeholder",
    }
def update_application_status(application_id: int) -> dict:
    return {
        "application_id": application_id,
        "status": "screening",
        "message": "update status placeholder",
        "updated_at": datetime.now(UTC).isoformat(),
    }

def get_job_pipeline(job_id: int) -> dict:
    return {
        "job_id": job_id,
        "candidates": [],
        "message": "pipeline placeholder",
    }
