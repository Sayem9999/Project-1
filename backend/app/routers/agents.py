from fastapi import APIRouter
from ..schemas import AgentInput, AgentOutput
from ..agents import director_agent, cutter_agent, subtitle_agent, audio_agent, color_agent, qc_agent

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
