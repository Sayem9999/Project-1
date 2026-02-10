# Integration Guide

Always verify new code against existing APIs and styles.

## Backend Rules
- **Schema First**: Any changes to Agent outputs must be reflected in `backend/app/agents/schemas.py` and subsequently in `backend/app/models.py`.
- **JSON Robustness**: Use `parse_json_response` from `backend/app/agents/base.py` for all LLM interactions.
- **Dependency Audit**: Before adding a new library, check `requirements.txt` to see if existing tools (like MoviePy or FFmpeg) already provide the functionality.

## Frontend Rules
- **Component Consistency**: Use Vanilla CSS and Lucide-React for consistency with the "Cinematic Studio" aesthetic.
- **Glassmorphism**: Follow the `glass-panel` and `shadow-glow` classes for new UI elements.
- **Data Bento**: Ensure new specialist insights are added as modular cards in the `Job Status` bento grid.

## Verification Checklist
- [ ] Run `pytest` for backend logic.
- [ ] Run `npx playwright test` for frontend E2E flows.
- [ ] Verify database migrations using `alembic current`.
