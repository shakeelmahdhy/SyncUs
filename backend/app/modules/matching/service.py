from db.supabase_client import supabase
from sentence_transformers import SentenceTransformer, util


class MatchingService:
    def __init__(self):
        # Lightweight BERT-style semantic model 
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    # UTILITY: SAFE NORMALISATION
    def _safe_list(self, value):
        if not value:
            return []
        if isinstance(value, list):
            return value
        return [value]

    # 1. NLP + SEMANTIC SKILL MATCHING (IMPROVED)
    def calculate_skill_score(self, candidate_skills, job_skills):
        candidate_skills = self._safe_list(candidate_skills)
        job_skills = self._safe_list(job_skills)

        if not candidate_skills or not job_skills:
            return 0.0

        # Semantic representation 
        candidate_text = " ".join(candidate_skills)
        job_text = " ".join(job_skills)

        embeddings = self.model.encode(
            [candidate_text, job_text],
            convert_to_tensor=True
        )

        similarity = util.cos_sim(embeddings[0], embeddings[1]).item()

        return round(similarity, 4)

    # 2. NLP EDUCATION SCORE (IMPROVED)
    def calculate_education_score(self, candidate, job):
        candidate_text = " ".join([
            candidate.get("major", ""),
            candidate.get("education", ""),
            " ".join(self._safe_list(candidate.get("academic_units")))
        ])

        job_text = " ".join([
            job.get("title", ""),
            job.get("description", ""),
            " ".join(self._safe_list(job.get("required_skills")))
        ])

        embeddings = self.model.encode(
            [candidate_text, job_text],
            convert_to_tensor=True
        )

        return round(util.cos_sim(embeddings[0], embeddings[1]).item(), 4)

    # 3. EXPERIENCE SCORE (RULE-BASED BUT OPTIMISED)
    def calculate_experience_score(self, candidate, job):
        candidate_exp = candidate.get("years_of_experience") or 0
        required_exp = job.get("experience_required") or 0

        if required_exp == 0:
            return 1.0

        return round(min(candidate_exp / required_exp, 1.0), 4)

    # 4. FINAL 60/30/10 SCORING MODEL
    def calculate_total_score(self, candidate, job):

        skill_score = self.calculate_skill_score(
            candidate.get("skills", []),
            job.get("required_skills", [])
        )

        education_score = self.calculate_education_score(candidate, job)
        experience_score = self.calculate_experience_score(candidate, job)

        total_score = (
            0.6 * skill_score +
            0.3 * education_score +
            0.1 * experience_score
        )

        return {
            "score": round(total_score, 4),
            "breakdown": {
                "skill": skill_score,
                "education": education_score,
                "experience": experience_score
            }
        }

    # 5. TOP-K JOB RECOMMENDATIONS (OPTIMISED QUERY)
    def get_job_recommendations(self, user_id: str):

        # Fetch only required columns (performance optimisation)
        candidate = supabase.table("job_seekers") \
            .select("id, skills, major, education, academic_units, years_of_experience") \
            .eq("id", user_id) \
            .single() \
            .execute().data

        jobs = supabase.table("jobs") \
            .select("id, title, description, required_skills, experience_required") \
            .eq("status", "published") \
            .execute().data

        results = []

        for job in jobs:
            result = self.calculate_total_score(candidate, job)

            results.append({
                "job_id": job["id"],
                "title": job["title"],
                "score": result["score"],
                "breakdown": result["breakdown"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:10]

    # 6. TOP-N CANDIDATES FOR EMPLOYER
    def get_candidate_recommendations(self, job_id: str):

        job = supabase.table("jobs") \
            .select("id, title, description, required_skills, experience_required") \
            .eq("id", job_id) \
            .single() \
            .execute().data

        candidates = supabase.table("job_seekers") \
            .select("id, first_name, last_name, skills, major, education, academic_units, years_of_experience") \
            .execute().data

        results = []

        for candidate in candidates:
            result = self.calculate_total_score(candidate, job)

            results.append({
                "candidate_id": candidate["id"],
                "name": f"{candidate.get('first_name', '')} {candidate.get('last_name', '')}".strip(),
                "score": result["score"],
                "breakdown": result["breakdown"]
            })

        results.sort(key=lambda x: x["score"], reverse=True)

        return results[:10]

    # 7. MATCH EXPLANATION (FOR DEMO + REPORT MARKS)
    def get_match_explanation(self, match_id: str):

        match = supabase.table("matches") \
            .select("id, score, breakdown_json") \
            .eq("id", match_id) \
            .single() \
            .execute().data

        return {
            "match_id": match["id"],
            "score": match["score"],
            "breakdown": match["breakdown_json"]
        }

    # 8. RECOMPUTE (PLACEHOLDER FOR FUTURE SCALING)
    def recompute_matches(self, user_id=None, job_id=None):
        """
        Future upgrade:
        - batch recomputation
        - trigger-based updates
        - caching layer
        """

        return {
            "status": "recomputed",
            "user_id": user_id,
            "job_id": job_id
        }