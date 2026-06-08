from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from src.nodes.router import route_area_node
from src.nodes.extractions import extract_intents_node, extract_profile_node
from src.nodes.update_state import update_state_node
from src.nodes.course import process_course_node
from src.nodes.pathway import process_pathway_node
from src.nodes.university import process_uni_node
from src.nodes.generations import generate_response_node
from src.state import AgentState
from src.types import Area

def build_graph():
    builder = StateGraph(AgentState)

    (
        builder
            .add_node(extract_intents_node)
            .add_node(extract_profile_node)
            .add_node(update_state_node)
            .add_node(route_area_node, destinations=(Area.COURSE.value, Area.PATHWAY.value, Area.UNI.value))
            .add_node(Area.COURSE.value, process_course_node)
            .add_node(Area.PATHWAY.value, process_pathway_node)
            .add_node(Area.UNI.value, process_uni_node)
            .add_node(generate_response_node)
    )

    (
        builder
            .add_edge(START, 'extract_intents_node')
            .add_edge('extract_intents_node', 'extract_profile_node')
            .add_edge('extract_profile_node', 'update_state_node')
            .add_edge('update_state_node', 'route_area_node')
            .add_edge(Area.COURSE.value, 'generate_response_node')
            .add_edge(Area.PATHWAY.value, 'generate_response_node')
            .add_edge(Area.UNI.value, 'generate_response_node')
    )

    serde = JsonPlusSerializer(allowed_msgpack_modules=[('src.schemas', 'IntentItem')])
    checkpointer = InMemorySaver(serde=serde)
    return builder.compile(checkpointer=checkpointer)