from langgraph.types import Command

from src.state import AgentState
from src.types import Area
from src.nodes.pathway import get_pathway_state

AREA_PREREQUISITES: dict[Area, list[Area]] = {
    Area.PATHWAY: [Area.COURSE]
}
AREA_ORDER = [Area.COURSE, Area.PATHWAY, Area.UNI]

def journey_is_complete(state: AgentState):    
    if state.get('has_registerd', False):
        return True
    
    return False

def area_is_complete(area: Area, state: AgentState) -> bool:
    flags = state.get('flags', {})

    if area in (Area.COURSE, Area.PATHWAY):
        if flags.get('pathway_is_stuck', False):
            return True
    
    if area == Area.COURSE:
        if state.get('confirmed_course') or state.get('indecision_count', 0) >= state.get('max_indecision_count', 2):
            return True
        
    if area == Area.PATHWAY:
        if get_pathway_state(state) == '1':
            return True
            
    return False

def area_prerequisites_met(area: Area, state: AgentState) -> bool:
    required = AREA_PREREQUISITES.get(area, [])
    return all(area_is_complete(area, state) for area in required)

def get_next_area(state: AgentState):
    # 1. Check if the entire counselling journey is already over
    if journey_is_complete(state):
        return Area.FINALIZE
    
    # 2. Intent‑driven area requests
    intents = state.get('intents', [])
    requested_ares = list({i.area for i in intents if i.area != 'general' and i.intent_type == 'ask'})
    for area in requested_ares:
        if area_prerequisites_met(Area(area), state):
            return Area(area)
        
    # 3. Stay in current incomplete area
    current = state.get('current_area')
    if current and not area_is_complete(Area(current), state):
        return Area(current)
        
    # 4. Advance in ideal order
    for area in AREA_ORDER:
        if not area_is_complete(area, state) and area_prerequisites_met(area, state):
            return area 
    
    # 5. All areas are done
    return Area.FINALIZE

def route_area_node(state: AgentState):
    next_area = get_next_area(state)
    return Command(goto=next_area.value, update={'current_area': next_area.value})