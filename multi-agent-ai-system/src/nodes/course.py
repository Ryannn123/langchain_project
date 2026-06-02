from langchain.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.schemas import StudentProfile
from src.prompt_builder import PromptBuilder

def course_generator_node(state: AgentState):
    history_messages = state['messages'][-6:]
    profile = state.get('student_profile', StudentProfile())
    course = profile.course_detail
    course_state = state.get('course_state', {})

    course_state_update = {}
    phase = ''
    
    if not course.confirmed_course:
        if len(course.shortlisted_courses) == 0:
            phase = 'explore_course'
        else:
            phase = 'compare_course'
    
    elif not course.confirmed_pathway:
        if len(course.shortlisted_pathways) == 0:
            phase =  'explore_pathway'
        else:
            phase = 'compare_pathway'
    
    if (
        course.is_able_to_decide is False and
        course_state.get('indecision_count', 0) >= course_state.get('max_indecision_count', 3) and
        not course_state.get('has_recommend_fallback', False)
    ):
        course_state_update['has_recommend_fallback'] = True
        phase = 'recommend_fallback'
            
    prompt = PromptBuilder(profile).build_prompt('course', phase)
    system_prompt = SystemMessage(prompt)
    
    messages = [system_prompt] + history_messages
    
    llm = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')
    result = llm.invoke(messages)
        
    return {'messages': [result], 'course_state': course_state_update}