from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage

from src.state import AgentState
from src.prompt_builder import build_prompt
from src.utils import get_profile, dict_to_yaml_like
from src.schemas import CourseDetail, PathwayDetail, UniversityDetail
from src.types import Area

PROFILE_SCHEMAS = {
    Area.COURSE.value: [CourseDetail, PathwayDetail],
    Area.PATHWAY.value: [CourseDetail, PathwayDetail],
    Area.UNI.value: [UniversityDetail]
}

def generate_response_node(state: AgentState):
    area = state.get('current_area', '')
    flow = state.get('current_flow', '')
    step = state.get('current_step', '')
    history_messages = state['messages'][-6:]
    profile_dict = get_profile(state, *PROFILE_SCHEMAS[area])
    current_student_profile = dict_to_yaml_like(profile_dict, exclude_empty=True)
    
    system_prompt = SystemMessage(build_prompt(area, flow, step))
    context = SystemMessage(f"""
<context>
<current_student_profile>
{current_student_profile}
</current_student_profile>
</context>
""")
    messages = [system_prompt, context] + history_messages
    
    llm = init_chat_model('google_genai:gemini-3.1-flash-lite')
    response = llm.invoke(messages)
    return {'messages': [response]}