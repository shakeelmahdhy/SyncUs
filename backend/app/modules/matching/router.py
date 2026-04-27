from fastapi import APIRouter, Query
from modules.matching.service import MatchingService

router = APIRouter(
    prefix="/sync-us/v1/matching",
    tags=["Matching"]
)

service = MatchingService()


# 1. TOP-K JOB RECOMMENDATIONS (Candidate Side)
@router.get("/recommendations")
def get_job_recommendations(user_id: str = Query(...)):
    """
    Returns Top-K (10) job recommendations for a candidate
    """
    return service.get_job_recommendations(user_id)


# 2. TOP-N CANDIDATES FOR A JOB (Employer Side)
@router.get("/jobs/{job_id}/candidates")
def get_candidate_recommendations(job_id: str):
    """
    Returns Top-N (10) candidates for a job
    """
    return service.get_candidate_recommendations(job_id)


# 3. MATCH EXPLANATION (60/30/10 breakdown)
@router.get("/explanations/{match_id}")
def get_match_explanation(match_id: str):
    """
    Returns score breakdown for explainability
    """
    return service.get_match_explanation(match_id)


# 4. RECOMPUTE MATCHES (DEBUG / ADMIN USE)
@router.post("/recompute")
def recompute_matches(
    user_id: str = Query(None),
    job_id: str = Query(None)
):
    """
    Force recomputation of matches
    """
    return service.recompute_matches(user_id, job_id)