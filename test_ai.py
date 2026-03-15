"""
ReefSync AI Layer - Quick smoke test
Run with: python test_ai.py
Requires ANTHROPIC_API_KEY env var and the FastAPI server running on localhost:8000
"""

import json
import requests

BASE = "http://localhost:8000"

# ── Test 1: site-summary ────────────────────────────────────────────────────
print("Testing POST /ai/site-summary ...")
payload = {
    "site_id": 1,
    "site_name": "Molasses Reef",
    "last_surveyed": "2024-10-01",
    "last_surveyed_by": "Reef Check Florida",
    "gap_days": 127,
    "upcoming_survey_date": "2025-02-15",
    "upcoming_survey_org": "NOAA Dive Team",
    "diver_count": 3,
    "total_surveys": 14,
    "coords": {"lat": 25.0097, "lng": -80.3762},
}
r = requests.post(f"{BASE}/ai/site-summary", json=payload)
assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
data = r.json()
assert "ai_summary" in data and len(data["ai_summary"]) > 10
print(f"  ✓ Summary: {data['ai_summary'][:80]}...")

# ── Test 2: recommend-sites ─────────────────────────────────────────────────
print("\nTesting POST /ai/recommend-sites ...")
payload = {
    "cert_level": "Advanced",
    "lat": 25.05,
    "lng": -80.40,
    "upcoming_surveys": [
        {"survey_id": 1, "site_name": "Molasses Reef", "org": "NOAA", "date": "2025-02-15",
         "cert_required": "Open Water", "gap_days": 127, "lat": 25.0097, "lng": -80.3762, "capacity": 6, "diver_count": 3},
        {"survey_id": 2, "site_name": "French Reef", "org": "Reef Check", "date": "2025-02-18",
         "cert_required": "Advanced", "gap_days": 45, "lat": 25.0255, "lng": -80.3529, "capacity": 4, "diver_count": 4},
        {"survey_id": 3, "site_name": "Sombrero Reef", "org": "Coral Restoration", "date": "2025-02-20",
         "cert_required": "Rescue", "gap_days": 200, "lat": 24.6266, "lng": -81.1102, "capacity": 8, "diver_count": 1},
        {"survey_id": 4, "site_name": "Looe Key", "org": "FKNMS", "date": "2025-02-22",
         "cert_required": "Open Water", "gap_days": 95, "lat": 24.5481, "lng": -81.4068, "capacity": 5, "diver_count": 2},
    ],
}
r = requests.post(f"{BASE}/ai/recommend-sites", json=payload)
assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
data = r.json()
recs = data["recommendations"]
assert len(recs) == 3, f"Expected 3 recommendations, got {len(recs)}"
print(f"  ✓ Got {len(recs)} recommendations:")
for rec in recs:
    print(f"    - {rec['site_name']}: {rec['reason']}")

# ── Test 3: gap-report ──────────────────────────────────────────────────────
print("\nTesting POST /ai/gap-report ...")
payload = {
    "region": "Florida Keys",
    "gap_zones": [
        {"site_name": "Sombrero Reef", "last_surveyed": "2024-08-01", "gap_days": 200},
        {"site_name": "Looe Key", "last_surveyed": "2024-11-10", "gap_days": 95},
        {"site_name": "Molasses Reef", "last_surveyed": "2024-10-01", "gap_days": 127},
        {"site_name": "French Reef", "last_surveyed": "2024-12-30", "gap_days": 45},
    ],
}
r = requests.post(f"{BASE}/ai/gap-report", json=payload)
assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
data = r.json()
assert "report_markdown" in data and "##" in data["report_markdown"]
print(f"  ✓ Gap report generated ({len(data['report_markdown'])} chars)")

# ── Test 4: follow-up Q&A ───────────────────────────────────────────────────
print("\nTesting POST /ai/follow-up ...")
payload = {
    "site_id": 1,
    "site_name": "Molasses Reef",
    "site_context": {
        "site_name": "Molasses Reef",
        "last_surveyed": "2024-10-01",
        "gap_days": 127,
        "total_surveys": 14,
    },
    "conversation": [
        {"role": "user", "content": "Why is this site considered high priority right now?"}
    ],
}
r = requests.post(f"{BASE}/ai/follow-up", json=payload)
assert r.status_code == 200, f"Failed: {r.status_code} {r.text}"
data = r.json()
assert "reply" in data and len(data["reply"]) > 10
assert len(data["conversation"]) >= 1
print(f"  ✓ Follow-up reply: {data['reply'][:80]}...")

print("\n✅ All AI endpoint tests passed!")
