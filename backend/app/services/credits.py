from __future__ import annotations

from datetime import datetime, date
from sqlalchemy.ext.asyncio import AsyncSession

from ..config import settings
from ..models import User, CreditLedger


def _month_key(value: date) -> tuple[int, int]:
    return value.year, value.month


async def ensure_monthly_credits(user: User, session: AsyncSession) -> None:
    if not settings.credits_enabled:
        return

    today = datetime.utcnow().date()
    if user.monthly_credits is None:
        user.monthly_credits = settings.monthly_credits_default

    if user.last_credit_reset is None or _month_key(user.last_credit_reset) != _month_key(today):
        previous = user.credits or 0
        user.credits = user.monthly_credits
        user.last_credit_reset = today
        delta = (user.credits or 0) - previous
        session.add(user)
        if delta != 0:
            entry = CreditLedger(
                user_id=user.id,
                delta=delta,
                balance_after=user.credits or 0,
                reason="monthly_reset",
                source="system",
            )
            session.add(entry)
        await session.commit()
