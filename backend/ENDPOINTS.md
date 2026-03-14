## GET /health
Auth: none
Response 200: { "status": "ok" }

---

## POST /auth/login
Auth: none
Body: { "username": str, "password": str }
Response 200: { "access_token": str, "token_type": "bearer" }
Response 401: { "detail": "Invalid credentials" }

---

## GET /surveys/map
Auth: none
Query params: region (optional str), page (optional int), limit (optional int)
Response 200: GeoJSON FeatureCollection (see schemas/survey.py -> SurveyMapResponse)
Example: { "type": "FeatureCollection", "features": [...] }

---

## GET /surveys/{id}
Auth: none
Path param: id (int) — survey ID
Response 200: SurveyDetailResponse (see schemas/survey.py)
Response 404: { "detail": "Survey not found" }

---

## GET /coverage/gaps
Auth: none
Query param: days (int, default 90)
Response 200: List[GapZoneResponse] (see schemas/coverage.py)

---

## GET /surveys/overlaps
Auth: none
Response 200: List[OverlapResponse] (see schemas/survey.py)

---

## POST /surveys
Auth: require_org_admin
Body: CreateSurveyRequest (see schemas/survey.py)
Response 201: { "survey_id": int, "message": "Survey created" }
Response 409: { "detail": "Overlap conflict detected", "conflicts": [...] }

---

## POST /surveys/{id}/join
Auth: Bearer token (any role)
Path param: id (int) — survey ID
Response 200: { "survey_id": int, "divers": [...], "diver_count": int }
Response 400: { "detail": "Survey is at capacity" }
