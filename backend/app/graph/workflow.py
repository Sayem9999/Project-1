"""
LangGraph Workflow - Unified AI decision DAG.
Flow: director → cutter → audio/visuals → validator → qc_gate → compiler
"""
from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes.director import director_node
from .nodes.cutter import cutter_node
from .nodes.audio import audio_node
from .nodes.visuals import visuals_node
from .nodes.validator import validator_node
from .nodes.qc_gate import qc_gate_node
from .nodes.compiler import compiler_node
from .nodes.hook import hook_node
from .nodes.platform import platform_node
from .nodes.brand_safety import brand_safety_node
from .nodes.ab_test import ab_test_node
from .nodes.media_intelligence import media_intelligence_node
from .nodes.subtitle import subtitle_node
from .nodes.scout import scout_node


from .iteration_controller import create_iteration_node, should_revise


def should_proceed_to_compile(state: GraphState) -> str:
    """
    Conditional edge: check if QC passed before compiling.
    """
    qc_result = state.get("qc_result", {})
    validation_result = state.get("validation_result", {})
    
    # Block if validation failed
    if not validation_result.get("passed", True):
        return "abort"
    
    # If QC not approved, check if we should iterate
    if not qc_result.get("approved", True):
        return "check_iteration"
    
    return "compile"


# Define Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("media_intelligence", media_intelligence_node)
workflow.add_node("director", director_node)
workflow.add_node("cutter", cutter_node)
workflow.add_node("audio", audio_node)
workflow.add_node("visuals", visuals_node)
workflow.add_node("validator", validator_node)
workflow.add_node("qc_gate", qc_gate_node)
workflow.add_node("iteration_control", create_iteration_node())
workflow.add_node("compiler", compiler_node)
workflow.add_node("hook", hook_node)
workflow.add_node("platform", platform_node)
workflow.add_node("brand_safety", brand_safety_node)
workflow.add_node("ab_test", ab_test_node)
workflow.add_node("subtitle", subtitle_node)
workflow.add_node("scout", scout_node)

# Define Edges
workflow.set_entry_point("media_intelligence")
workflow.add_edge("media_intelligence", "director")
workflow.add_edge("director", "platform")
workflow.add_edge("platform", "cutter")

# Fork: Cutter -> (Audio, Visuals)
workflow.add_edge("cutter", "audio")
workflow.add_edge("cutter", "visuals")

# Visuals -> Hook
workflow.add_edge("visuals", "hook")

# Parallel: Platform -> Scout
workflow.add_edge("platform", "scout")

# Join: (Audio, Hook) -> Subtitle
workflow.add_edge("audio", "subtitle")
workflow.add_edge("hook", "subtitle")

# Subtitle -> Validator
workflow.add_edge("subtitle", "validator")
workflow.add_edge("scout", "validator")

# Validator -> Brand Safety
workflow.add_edge("validator", "brand_safety")

# Brand Safety -> QC Gate
workflow.add_edge("brand_safety", "qc_gate")

# Conditional: QC Gate -> Compiler or Iteration Check
workflow.add_conditional_edges(
    "qc_gate",
    should_proceed_to_compile,
    {
        "compile": "compiler",
        "check_iteration": "iteration_control",
        "abort": END
    }
)

# Conditional: Iteration Check -> Director (Revise) or Compile (Best Effort)
workflow.add_conditional_edges(
    "iteration_control",
    should_revise,
    {
        "revise": "director",
        "proceed": "compiler"  # Max iterations reached or no improvement -> Compile anyway
    }
)

workflow.add_edge("compiler", "ab_test")
workflow.add_edge("ab_test", END)

from langgraph.checkpoint.memory import MemorySaver

# ... existing code ...

# Compile
checkpointer = MemorySaver()
app = workflow.compile(checkpointer=checkpointer)
