# Tracking module: recommended minimal implementation order

Start with a minimal “contract then persistence” flow.

1. Implement request/response models in `backend/app/modules/tracking/schema.py`
2. Implement routes in `backend/app/modules/tracking/router.py` using typed UUID path params
3. Keep `backend/app/modules/tracking/service.py` placeholders until wiring is stable
4. Add `backend/app/modules/tracking/repository.py` (recommended) to perform Supabase reads/writes
5. Replace placeholders in service/repository with real Supabase queries
6. Enforce status transition rules in `service.py` and validate DB constraints in migrations

## Quick smoke tests (before merge)

For each tracking endpoint:
1. Open `/docs` and confirm OpenAPI models appear correctly
2. Test one happy path request (create application)
3. Test one failure path (invalid status transition)
4. Confirm unauthorized access returns 401/403 depending on your auth strategy

