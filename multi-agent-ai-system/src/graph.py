from langgraph.graph import StateGraph, START
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from src.state import AgentState
from src.nodes.router import route_generator_node
from src.nodes.profile_extractor import extraction_node
from src.nodes.university import university_generator_node
from src.nodes.course import course_generator_node

def build_graph():
    builder = StateGraph(AgentState)

    (
        builder
            .add_node('extraction', extraction_node)
            .add_node('route_generator', route_generator_node)
            .add_node('course_generator', course_generator_node)
            .add_node('university_generator', university_generator_node)
    )

    (
        builder
            .add_edge(START, 'extraction')
            .add_edge('extraction', 'route_generator')
    )

    serde = JsonPlusSerializer(allowed_msgpack_modules=[('src.schemas', 'StudentProfile')])

    checkpointer = InMemorySaver(serde=serde)
    return builder.compile(checkpointer=checkpointer)