from fastapi import APIRouter
from ..schemas import AgentInput, AgentOutput, ArchitectInput
from ..agents import director_agent, cutter_agent, subtitle_agent, audio_agent, color_agent, qc_agent, architect_agent
from ..services.llm_health import get_llm_health_summary

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("/director", response_model=AgentOutput)
async def director(payload: AgentInput):
    return AgentOutput(agent="director", directives=await director_agent.run(payload.model_dump()))


@router.post("/cutter", response_model=AgentOutput)
async def cutter(payload: AgentInput):
    return AgentOutput(agent="cutter", directives=await cutter_agent.run(payload.model_dump()))


@router.post("/subtitle", response_model=AgentOutput)
async def subtitle(payload: AgentInput):
    return AgentOutput(agent="subtitle", directives=await subtitle_agent.run(payload.model_dump()))


@router.post("/audio", response_model=AgentOutput)
async def audio(payload: AgentInput):
    return AgentOutput(agent="audio", directives=await audio_agent.run(payload.model_dump()))


@router.post("/color", response_model=AgentOutput)
async def color(payload: AgentInput):
    return AgentOutput(agent="color", directives=await color_agent.run(payload.model_dump()))


@router.post("/qc", response_model=AgentOutput)
async def qc(payload: AgentInput):
    return AgentOutput(agent="qc", directives=await qc_agent.run(payload.model_dump()))


@router.post("/architect")
async def architect(payload: ArchitectInput):
    # Special case: Architect returns 'answer' instead of 'directives' or just raw dict
    result = await architect_agent.run(payload.model_dump())
    return {"agent": "architect", "data": result}


@router.get("/health")
async def llm_health():
    return {"providers": get_llm_health_summary()}
