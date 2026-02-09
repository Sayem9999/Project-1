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


def should_proceed_to_compile(state: GraphState) -> str:
    """
    Conditional edge: check if QC passed before compiling.
    """
    qc_result = state.get("qc_result", {})
    validation_result = state.get("validation_result", {})
    
    # Block if validation failed
    if not validation_result.get("passed", True):
        return "abort"
    
    # Block if QC not approved
    if not qc_result.get("approved", True):
        return "abort"
    
    return "compile"


# Define Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("director", director_node)
workflow.add_node("cutter", cutter_node)
workflow.add_node("audio", audio_node)
workflow.add_node("visuals", visuals_node)
workflow.add_node("validator", validator_node)
workflow.add_node("qc_gate", qc_gate_node)
workflow.add_node("compiler", compiler_node)

# Define Edges
workflow.set_entry_point("director")
workflow.add_edge("director", "cutter")

# Fork: Cutter -> (Audio, Visuals)
workflow.add_edge("cutter", "audio")
workflow.add_edge("cutter", "visuals")

# Join: (Audio, Visuals) -> Validator
workflow.add_edge("audio", "validator")
workflow.add_edge("visuals", "validator")

# Validator -> QC Gate
workflow.add_edge("validator", "qc_gate")

# Conditional: QC Gate -> Compiler or Abort
workflow.add_conditional_edges(
    "qc_gate",
    should_proceed_to_compile,
    {
        "compile": "compiler",
        "abort": END
    }
)

workflow.add_edge("compiler", END)

# Compile
app = workflow.compile()
