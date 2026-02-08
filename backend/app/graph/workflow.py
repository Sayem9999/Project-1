from langgraph.graph import StateGraph, END
from .state import GraphState
from .nodes.director import director_node
from .nodes.cutter import cutter_node
from .nodes.audio import audio_node
from .nodes.visuals import visuals_node
from .nodes.compiler import compiler_node

# Define Graph
workflow = StateGraph(GraphState)

# Add Nodes
workflow.add_node("director", director_node)
workflow.add_node("cutter", cutter_node)
workflow.add_node("audio", audio_node)
workflow.add_node("visuals", visuals_node)
workflow.add_node("compiler", compiler_node)

# Define Edges
workflow.set_entry_point("director")
workflow.add_edge("director", "cutter")

# Fork: Cutter -> (Audio, Visuals)
workflow.add_edge("cutter", "audio")
workflow.add_edge("cutter", "visuals")

# Join: (Audio, Visuals) -> Compiler
workflow.add_edge("audio", "compiler")
workflow.add_edge("visuals", "compiler")

workflow.add_edge("compiler", END)

# Compile
app = workflow.compile()
