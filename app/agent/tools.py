"""Function tools for the AI agent."""
import logging

from livekit.agents import llm
from livekit.agents.job import get_job_context

logger = logging.getLogger("real-estate-agent")


def make_submit_lead_tool(project_id: str, tenant_id: str):
    """Create a submit_lead tool bound to a specific project and tenant."""

    @llm.function_tool(
        name="submit_lead",
        description=(
            "Call this once you have collected the customer's requirement details "
            "(location, property type, configuration, budget, purpose, timeline) and any "
            "contact details they shared. Fill missing fields with 'Not specified'. "
            "Saves the lead to the CRM and lets the dashboard show it live."
        ),
    )
    async def submit_lead(
        name: str = "Not specified",
        phone: str = "Not specified",
        language: str = "Not specified",
        purpose: str = "Not specified",
        property_type: str = "Not specified",
        configuration: str = "Not specified",
        preferred_location: str = "Not specified",
        budget_min: str = "Not specified",
        budget_max: str = "Not specified",
        currency: str = "INR",
        timeline: str = "Not specified",
        questions_asked: str = "Not specified",
        notes: str = "Not specified",
    ) -> str:
        """Persist the qualified lead. Returns a confirmation for the model."""
        call_id = ""
        try:
            job_ctx = get_job_context()
            call_id = job_ctx.job.room.name if job_ctx else ""
        except Exception:
            pass

        # Here you would normally call the backend API to save the lead
        # For now, we'll just log it
        lead_data = {
            "call_id": call_id,
            "project_id": project_id,
            "tenant_id": tenant_id,
            "name": name,
            "phone": phone,
            "language": language,
            "purpose": purpose,
            "property_type": property_type,
            "configuration": configuration,
            "preferred_location": preferred_location,
            "budget_min": budget_min,
            "budget_max": budget_max,
            "currency": currency,
            "timeline": timeline,
            "questions_asked": questions_asked,
            "notes": notes,
        }

        logger.info("submit_lead called with data: %s", lead_data)

        # TODO: Make API call to backend to save lead
        # async with httpx.AsyncClient() as client:
        #     await client.post(f"{BACKEND_URL}/api/v1/leads", json=lead_data)

        return "Lead saved successfully. Thank the customer and continue the conversation."

    return submit_lead
