from __future__ import annotations

from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models import User


def _month_key(value: date) -> tuple[int, int]:
    return value.year, value.month


async def ensure_monthly_credits(user: User, session: AsyncSession) -> None:
    if not settings.credits_enabled:
        return

    today = datetime.utcnow().date()
    if user.monthly_credits is None:
        user.monthly_credits = settings.monthly_credits_default

    if user.last_credit_reset is None or _month_key(user.last_credit_reset) != _month_key(today):
        user.credits = user.monthly_credits
        user.last_credit_reset = today
        session.add(user)
        await session.commit()
