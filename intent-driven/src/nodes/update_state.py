from src.state import AgentState
from src.utils import has_intent

def update_state_node(state: AgentState):
    flags = state.get('flags', {})
    intents = state.get('intents', [])
    
    update = {}
    
    if has_intent(intents, ['course', 'pathway'], ['express_indecision']):
        updated_indecision_count = state.get('indecision_count', 0) + 1
        update['indecision_count'] = updated_indecision_count
        if updated_indecision_count >= state.get('max_indecision_count', 3) and flags.get('has_recommend_fallback'):
            update['flags'] = flags | {'pathway_is_stuck': True}
        
    if state.get('confirmed_pathway') is None and len(state.get('shortlisted_pathways', [])) == 1:
        update['confirmed_pathway'] = state.get('shortlisted_pathways', [])[0]
        
    return update