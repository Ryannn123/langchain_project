from typing import Literal, Any

from src.state import AgentState
from src.utils import has_intent

# --- Strategy ---
def compare_course_flow(state: AgentState):
    if not state.get('course_concerns'):
        return {'current_step': 'get_concern'}
     
    return {'current_step': 'compare'}

def explore_course_flow(state: AgentState):
    flags = state.get('flags', {})
    if not flags.get('has_send_initial_course_inquiry', False):
        return {'current_step': 'ask_course_consider', 'flags': flags | {'has_send_initial_course_inquiry': True}}
    
    if not state.get('student_strengths', []) and not state.get('course_preferences', []):
        return {'current_step': 'get_strength_preference'}
    
    return {'current_step': 'suggest_course'}

# ==================================

def get_course_state(state: AgentState) -> Literal['0', '1', '>1']:
    if state.get('confirmed_course'):
        return '1'
    courses = state.get('shortlisted_courses', [])
    if len(courses) == 0:
        return '0'
    if len(courses) == 1:
        return '1'
    return '>1'

def get_course_flow(state: AgentState) -> dict[str, Any]:
    flags = state.get('flags', {})
    intents = state.get('intents', [])
    cours_state = get_course_state(state)
    
    if has_intent(intents, ['course'], ['ask']):
        return {'current_flow': '', 'current_step': ''}
    
    if cours_state == '1' and state.get('confirmed_course') is None:
        if not flags.get('has_confirm_course', False):
            return {'current_flow': 'confirm_course', 'current_step': '', 'flags': flags | {'has_confirm_course': True}}
        
        return {'current_flow': 'explore_course'} | explore_course_flow(state)
    
    if cours_state == '0':
        return {'current_flow': 'explore_course'} | explore_course_flow(state)
    
    return {'current_flow': 'compare_course'} | compare_course_flow(state)

def process_course_node(state: AgentState):
    return get_course_flow(state)