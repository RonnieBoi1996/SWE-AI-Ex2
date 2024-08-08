from agent_graph.agents import *

from langgraph.graph import END, StateGraph


# ----------------------------------------------------------
# Graph
# ----------------------------------------------------------

graph = StateGraph(MyState)


# ----------------------------------------------------------
# Nodes
# ----------------------------------------------------------

graph.add_node("Initialize", init)
graph.add_node("GenQueryProgram", generate_pq)
graph.add_node("ExecuteProgram", execute_pq)
graph.add_node("Chk4rErr", check_4_err)
graph.add_node("ReflectOnErr", reflect_on_err)
graph.add_node("ReGenQueryPgm", regenerate_pq)
graph.add_node("PrepareToTerminate", prep_2_terminate)


# ----------------------------------------------------------
# Edges
# ----------------------------------------------------------

graph.add_edge("Initialize", "GenQueryProgram")
graph.add_edge("GenQueryProgram", "ExecuteProgram")
graph.add_edge("ExecuteProgram", "Chk4rErr")
graph.add_edge("ReflectOnErr", "ReGenQueryPgm")
graph.add_edge("ReGenQueryPgm", "ExecuteProgram")
graph.add_edge("PrepareToTerminate", END)


# ----------------------------------------------------------
# Deciding Function
# ----------------------------------------------------------

def should_reflect(state):
    if ((state['errors'] == "") or (state['num_of_exe'] >= 3)):
        return "PrepareToTerminate"
    else:
        return "ReflectOnErr"


# ----------------------------------------------------------
# Conditional Edges
# ----------------------------------------------------------

graph.add_conditional_edges(
    "Chk4rErr",  # Source node
    should_reflect,  # Deciding function
    {
        "ReflectOnErr": "ReflectOnErr",
        "PrepareToTerminate": "PrepareToTerminate"
    }
)

# ----------------------------------------------------------
# Entry Point
# ----------------------------------------------------------

graph.set_entry_point("Initialize")


# ----------------------------------------------------------
# Graph Compilation
# ----------------------------------------------------------

runnable = graph.compile()
res = runnable.invoke(MyState(num_of_exe=0))