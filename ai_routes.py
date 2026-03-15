"""
ReefSync AI Routes
All /ai/* endpoints. These are additive - the app works without them.
Person 2 imports this router and mounts it; Person 3 never touches existing routes.
"""

import json
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ai.client import call_claude, call_claude_stream, call_claude_json, call_claude_conversation
from ai.prompts import SITE_SUMMARY_SYSTEM, RECOMMEND_SITES_SYSTEM, GAP_REPORT_SYSTEM

router = APIRouter(prefix="/ai", tags=["ai"])


# --------------------------------------------------------------------------- #
# Schemas                                                                      #
# --------------------------------------------------------------------------- #

class SiteSummaryRequest(BaseModel):
    site_id: int
    site_name: str
    last_surveyed: str | None          # ISO date string or null
    last_surveyed_by: str | None       # org name
    gap_days: int | None               # days since last survey
    upcoming_survey_date: str | None
    upcoming_survey_org: str | None
    diver_count: int
    total_surveys: int
    coords: dict | None = None         # {"lat": float, "lng": float}


class SiteSummaryResponse(BaseModel):
    site_id: int
    ai_summary: str


class RecommendRequest(BaseModel):
    cert_level: str          # e.g. "Open Water", "Advanced", "Rescue", "Divemaster"
    lat: float
    lng: float
    upcoming_surveys: list[dict]  # raw list from GET /surveys/map


class RecommendResponse(BaseModel):
    recommendations: list[dict]


class GapReportRequest(BaseModel):
    region: str
    gap_zones: list[dict]    # list of {site_name, last_surveyed, gap_days, coords}


class GapReportResponse(BaseModel):
    region: str
    report_markdown: str


class ConversationMessage(BaseModel):
    role: str   # "user" or "assistant"
    content: str


class FollowUpRequest(BaseModel):
    site_id: int
    site_name: str
    site_context: dict          # same shape as SiteSummaryRequest
    conversation: list[ConversationMessage]


class FollowUpResponse(BaseModel):
    reply: str
    conversation: list[ConversationMessage]


# --------------------------------------------------------------------------- #
# Task 3 - POST /ai/site-summary                                              #
# --------------------------------------------------------------------------- #

@router.post("/site-summary", response_model=SiteSummaryResponse)
async def site_summary(req: SiteSummaryRequest):
    """
    Generate a plain-English narrative for a reef site based on its survey history.
    Used by the place detail panel when a user clicks a reef zone.
    """
    user_msg = (
        f"Site: {req.site_name}\n"
        f"Last surveyed: {req.last_surveyed or 'Never'}"
        + (f" by {req.last_surveyed_by}" if req.last_surveyed_by else "")
        + "\n"
        f"Gap (days since last survey): {req.gap_days if req.gap_days is not None else 'unknown'}\n"
        f"Upcoming survey: {req.upcoming_survey_date or 'None scheduled'}"
        + (f" by {req.upcoming_survey_org}" if req.upcoming_survey_org else "")
        + "\n"
        f"Divers currently signed up: {req.diver_count}\n"
        f"Total historical surveys: {req.total_surveys}"
    )

    try:
        summary = call_claude(SITE_SUMMARY_SYSTEM, user_msg)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    return SiteSummaryResponse(site_id=req.site_id, ai_summary=summary)


# --------------------------------------------------------------------------- #
# Task 6 - POST /ai/site-summary/stream (SSE streaming variant)               #
# --------------------------------------------------------------------------- #

@router.post("/site-summary/stream")
async def site_summary_stream(req: SiteSummaryRequest):
    """
    Streaming version of site-summary. Returns Server-Sent Events so the UI
    can render text as it arrives. Frontend listens with EventSource or fetch+ReadableStream.
    """
    user_msg = (
        f"Site: {req.site_name}\n"
        f"Last surveyed: {req.last_surveyed or 'Never'}"
        + (f" by {req.last_surveyed_by}" if req.last_surveyed_by else "")
        + "\n"
        f"Gap (days since last survey): {req.gap_days if req.gap_days is not None else 'unknown'}\n"
        f"Upcoming survey: {req.upcoming_survey_date or 'None scheduled'}"
        + (f" by {req.upcoming_survey_org}" if req.upcoming_survey_org else "")
        + "\n"
        f"Divers currently signed up: {req.diver_count}\n"
        f"Total historical surveys: {req.total_surveys}"
    )

    def event_generator():
        try:
            for chunk in call_claude_stream(SITE_SUMMARY_SYSTEM, user_msg):
                # SSE format: "data: <payload>\n\n"
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",   # Disable nginx buffering
        },
    )


# --------------------------------------------------------------------------- #
# Task 5 - POST /ai/recommend-sites                                           #
# --------------------------------------------------------------------------- #

@router.post("/recommend-sites", response_model=RecommendResponse)
async def recommend_sites(req: RecommendRequest):
    """
    Given a diver's cert level and current location, return 3 recommended
    upcoming surveys with AI reasoning.
    """
    if not req.upcoming_surveys:
        raise HTTPException(status_code=400, detail="No upcoming surveys provided")

    user_msg = (
        f"Diver cert level: {req.cert_level}\n"
        f"Diver location: lat={req.lat}, lng={req.lng}\n\n"
        f"Upcoming surveys:\n{json.dumps(req.upcoming_surveys, indent=2)}"
    )

    try:
        recommendations = call_claude_json(RECOMMEND_SITES_SYSTEM, user_msg)
    except json.JSONDecodeError:
        raise HTTPException(status_code=502, detail="AI returned invalid JSON")
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    return RecommendResponse(recommendations=recommendations)


# --------------------------------------------------------------------------- #
# Task 7 (stretch) - POST /ai/gap-report                                     #
# --------------------------------------------------------------------------- #

@router.post("/gap-report", response_model=GapReportResponse)
async def gap_report(req: GapReportRequest):
    """
    Generate a markdown coverage gap summary for org admins.
    Suitable for pasting into an email to coordinate survey scheduling.
    """
    if not req.gap_zones:
        raise HTTPException(status_code=400, detail="No gap zone data provided")

    user_msg = (
        f"Region: {req.region}\n\n"
        f"Gap zones:\n{json.dumps(req.gap_zones, indent=2)}"
    )

    try:
        report = call_claude(GAP_REPORT_SYSTEM, user_msg, max_tokens=1024)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    return GapReportResponse(region=req.region, report_markdown=report)


# --------------------------------------------------------------------------- #
# Task 8 (stretch) - POST /ai/follow-up  (multi-turn Q&A for a site)         #
# --------------------------------------------------------------------------- #

FOLLOWUP_SYSTEM = """You are ReefSync's dive site assistant. The user is viewing a specific reef site and may ask follow-up questions about its survey history, ecology, dive conditions, or how to get involved.

Be concise (under 80 words per reply), helpful, and grounded in the site data provided.
If a question is outside the scope of the data, say so briefly and suggest where to find more info."""


@router.post("/follow-up", response_model=FollowUpResponse)
async def follow_up(req: FollowUpRequest):
    """
    Multi-turn Q&A about a reef site. Maintains conversation history per session.
    The frontend keeps the conversation array and sends it with each request.
    """
    site_context_str = json.dumps(req.site_context, indent=2)

    # Inject site context as a system-level user message at the start if not already present
    messages = [m.dict() for m in req.conversation]
    if not messages or messages[0].get("role") != "user" or "Site context" not in messages[0].get("content", ""):
        context_prefix = {"role": "user", "content": f"Site context:\n{site_context_str}"}
        context_reply = {"role": "assistant", "content": f"Got it, I'm ready to answer questions about {req.site_name}."}
        messages = [context_prefix, context_reply] + messages

    try:
        reply = call_claude_conversation(FOLLOWUP_SYSTEM, messages)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"AI service error: {str(e)}")

    # Append assistant reply to conversation and return full history
    updated_conversation = list(req.conversation) + [ConversationMessage(role="assistant", content=reply)]

    return FollowUpResponse(reply=reply, conversation=updated_conversation)
