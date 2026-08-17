"""Lead service with sentiment analysis."""
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead


async def create_lead(
    db: AsyncSession,
    tenant_id: UUID,
    project_id: UUID,
    call_id: str,
    **kwargs,
) -> Lead:
    """Create a new lead."""
    lead = Lead(
        tenant_id=tenant_id,
        project_id=project_id,
        call_id=call_id,
        **kwargs,
    )
    db.add(lead)
    await db.flush()
    return lead


async def get_lead_by_call_id(
    db: AsyncSession,
    call_id: str,
    tenant_id: Optional[UUID] = None,
) -> Optional[Lead]:
    """Get a lead by call_id."""
    query = select(Lead).where(Lead.call_id == call_id)
    if tenant_id:
        query = query.where(Lead.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_lead_by_id(
    db: AsyncSession,
    lead_id: UUID,
    tenant_id: Optional[UUID] = None,
) -> Optional[Lead]:
    """Get a lead by ID."""
    query = select(Lead).where(Lead.id == lead_id)
    if tenant_id:
        query = query.where(Lead.tenant_id == tenant_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def list_leads(
    db: AsyncSession,
    tenant_id: UUID,
    project_id: Optional[UUID] = None,
    status: Optional[str] = None,
    limit: int = 100,
) -> list[Lead]:
    """List leads for a tenant."""
    query = select(Lead).where(Lead.tenant_id == tenant_id)

    if project_id:
        query = query.where(Lead.project_id == project_id)
    if status:
        query = query.where(Lead.status == status)

    query = query.order_by(Lead.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_lead(
    db: AsyncSession,
    lead_id: UUID,
    tenant_id: UUID,
    **kwargs,
) -> Optional[Lead]:
    """Update a lead."""
    lead = await get_lead_by_id(db, lead_id, tenant_id)
    if lead is None:
        return None

    for key, value in kwargs.items():
        if value is not None and hasattr(lead, key):
            setattr(lead, key, value)

    await db.flush()
    return lead


def analyze_sentiment(text: str) -> dict:
    """Analyze sentiment of text. Returns score and label."""
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']

        if compound > 0.1:
            label = "positive"
        elif compound < -0.1:
            label = "negative"
        else:
            label = "neutral"

        return {"score": compound, "label": label}
    except ImportError:
        return {"score": 0.0, "label": "neutral"}


def score_lead_quality(lead: Lead, sentiment: dict) -> dict:
    """Score lead quality based on conversation data."""
    score = 50  # Base score

    # Budget clarity
    if lead.budget_min and lead.budget_max:
        score += 15

    # Timeline urgency
    timeline = (lead.timeline or "").lower()
    if "immediate" in timeline or "urgent" in timeline:
        score += 20
    elif "month" in timeline:
        score += 10

    # Sentiment
    sentiment_score = sentiment.get("score", 0)
    if sentiment_score > 0.2:
        score += 10
    elif sentiment_score < -0.2:
        score -= 10

    # Questions asked
    if lead.questions_asked and lead.questions_asked != "Not specified":
        score += 10

    score = min(100, max(0, score))

    if score >= 70:
        intent = "hot_lead"
    elif score >= 50:
        intent = "warm_lead"
    else:
        intent = "cold_lead"

    return {"score": score, "intent": intent}
