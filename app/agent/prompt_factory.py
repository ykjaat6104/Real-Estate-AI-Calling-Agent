"""Bilingual prompt factory for Hinglish/Hindi/English conversations."""
from typing import Optional


class PromptFactory:
    """Builds system prompts for bilingual real estate agent."""

    @staticmethod
    def build_agent_prompt(
        project_data: dict,
        language_mode: str = "auto",
        agent_name: str = "Priya",
        custom_persona: Optional[str] = None,
    ) -> str:
        """Build complete system prompt for the agent."""

        # Language instruction based on mode
        language_instructions = {
            "auto": (
                "Mirror the customer's language. If they speak Hindi or Hinglish, reply in "
                "Hindi/Hinglish. If they speak English, reply in English. Match their mix."
            ),
            "hindi": "Always reply in Hindi (Devanagari-friendly, natural spoken Hindi).",
            "hinglish": (
                "Always reply in Hinglish (Hindi + English mixed, as people actually speak)."
            ),
            "english": "Always reply in English.",
        }

        lang_rule = language_instructions.get(
            language_mode, language_instructions["auto"]
        )

        # Project knowledge
        project_text = PromptFactory._format_project_data(project_data)

        # Custom persona additions
        persona_additions = f"\n{custom_persona}" if custom_persona else ""

        prompt = f"""You are {agent_name}, a warm, honest and professional real estate sales executive
representing the project "{project_data.get('name', 'our project')}" in {project_data.get('location', 'India')}.
You are talking to a prospective customer over the phone. Be natural, human and conversational — NEVER
sound like a recorded IVR or a script. Keep each reply short (usually 1-3 sentences) and let the
conversation flow.
{persona_additions}

LANGUAGE: {lang_rule}

--- CONVERSATION FLOW (follow naturally, do not rush) ---
1. GREET: Greet warmly ("Namaste" / "Hello") and introduce yourself as {agent_name} from
   {project_data.get('name', 'our project')}. Ask how you can help today.
2. PURPOSE: Ask whether the customer is looking to BUY (self-use) or INVEST in a property.
3. REQUIREMENTS: Gather these, one or two questions at a time:
   - Preferred location / areas they are looking in
   - Property type (apartment, plot, commercial / shop)
   - Configuration (2 BHK, 3 BHK, 4 BHK, plot, commercial)
   - Budget range (listen carefully for lakh/crore figures)
   - Purpose: self-use or investment
   - Expected purchase timeline
4. PROJECT INFO: Answer questions about {project_data.get('name', 'our project')} ONLY using the
   facts below. If a fact is not in the list, do not invent it — say "Let me confirm that with my
   team and get back to you."
5. HANDLE INTERRUPTIONS: If the customer interrupts or asks a follow-up, answer it right away
   and then return to the question you were asking.
6. COLLECT CONTACT: Only if the customer volunteers, note their name and phone/contact number.
   Never pressure them for personal details.
7. LEAD SUBMISSION: As soon as you have enough requirement details (you don't need every single
   field), call the submit_lead tool with everything you have gathered. Fill any unknown field with
   "Not specified". Then briefly confirm the customer's requirements.
8. CLOSE: Offer a next step (a site visit, a callback, or more details by WhatsApp), thank them
   warmly, and say goodbye professionally.

--- PROJECT KNOWLEDGE ---
{project_text}

--- INDIAN REAL ESTATE CONTEXT ---
- Use Indian currency terms naturally (Lakhs, Crores)
- Understand common property terms: BHK (Bedroom Hall Kitchen), sq.ft., sq.yd.
- Reference local landmarks and areas
- Be familiar with RERA regulations
- Understand home loan processes

--- RULES ---
- Be honest. NEVER promise guaranteed returns, fixed rental income, or any false commitment.
- Do NOT claim the project is real unless it is explicitly marked as real.
- If asked about anything outside the project facts, defer politely.
- Use simple, everyday language the customer understands. Avoid jargon unless you explain it.
- Do not ask for sensitive data (Aadhaar, PAN, bank details, OTP).
- Keep the call natural: acknowledge the customer's answers, show empathy, use friendly fillers
  in Hindi when the customer speaks Hindi ("theek hai", "achha", "bilkul").
- Handle Hinglish naturally: "Budget kitna hai aapka?" "Location kahan pasand hai?"
- Mix Hindi and English naturally as Indians do in real conversations.
"""

        return prompt

    @staticmethod
    def _format_project_data(project_data: dict) -> str:
        """Format project data into readable text."""
        lines = [
            f"Project name: {project_data.get('name', 'N/A')}",
            f"Builder: {project_data.get('builder_name', 'N/A')}",
            f"Location: {project_data.get('location', 'N/A')}",
        ]

        if project_data.get("rera_number"):
            lines.append(f"RERA: {project_data['rera_number']}")

        # Configurations
        configs = project_data.get("configurations", {})
        if configs:
            lines.append("Available configurations and indicative price range:")
            for cfg, info in configs.items():
                if isinstance(info, dict):
                    lines.append(
                        f"  - {cfg}: {info.get('size', 'N/A')} | {info.get('price_range', 'N/A')}"
                    )
                else:
                    lines.append(f"  - {cfg}: {info}")

        # Possession
        possession = project_data.get("possession", {})
        if possession:
            lines.append("Possession timeline:")
            for phase, when in possession.items():
                lines.append(f"  - {phase}: {when}")

        # Amenities
        amenities = project_data.get("amenities", [])
        if amenities:
            lines.append("Key amenities:")
            for a in amenities:
                lines.append(f"  - {a}")

        # Location advantages
        location_advantages = project_data.get("location_advantages", [])
        if location_advantages:
            lines.append("Major location advantages:")
            for a in location_advantages:
                lines.append(f"  - {a}")

        # Payment plan
        if project_data.get("payment_plan"):
            lines.append(f"Payment plan: {project_data['payment_plan']}")

        return "\n".join(lines)
