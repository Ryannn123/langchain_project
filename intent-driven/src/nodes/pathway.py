from typing import Literal, Any

from src.state import AgentState
from src.utils import has_intent

# --- Strategy ---
def compare_pathway_flow(state: AgentState):
    if not state.get('pathway_concerns', []):
        return {'current_step': 'get_concern'}
    
    return {'current_step': 'compare'}

def explore_pathway_flow(state: AgentState):
    return {'current_step': ''}

# ==================================

def get_pathway_state(state: AgentState) -> Literal['0', '1', '>1']:
    if state.get('confirmed_pathway'):
        return '1'
    pathway = state.get('shortlisted_pathways', [])
    if len(pathway) == 0:
        return '0'
    if len(pathway) == 1:
        return '1'
    return '>1'

def get_pathway_flow(state: AgentState) -> dict[str, Any]:
    pathway_state = get_pathway_state(state)
    flags = state.get('flags', {})
    
    if has_intent(state.get('intents', []), ['pathway'], ['ask']):
        return {'current_flow': 'compare_pathway'} | compare_pathway_flow(state)
    
    # state == '1' and other student - Ask international pathway question
    
    if state.get('indecision_count', 0) >= state.get('max_indecision_count', 2) and not flags.get('has_recommend_fallback', False):
        return {'current_flow': 'recommend_fallback', 'current_step': '', 'flags': flags | {'has_recommend_fallback': True}}
    
    if pathway_state == '0':
        return {'current_flow': 'explore_pathway'} | explore_pathway_flow(state)
    
    return {'current_flow': 'compare_pathway'} | compare_pathway_flow(state)

def process_pathway_node(state: AgentState):
    return get_pathway_flow(state)