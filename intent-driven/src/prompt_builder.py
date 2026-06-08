from src.prompts.master import MASTER_PROMPT
from src.prompts.course import COURSE_PROMPT
from src.prompts.pathway import PATHWAY_PROMPT
from src.types import Area

AREA_PROMPT = {
    Area.COURSE.value: COURSE_PROMPT,
    Area.PATHWAY.value: PATHWAY_PROMPT
}

def build_prompt(area: str, flow: str, step: str):
    parts: list = [MASTER_PROMPT]
    
    area_prompt = AREA_PROMPT.get(area, {})
    if '_base' in area_prompt:
        parts.append(area_prompt['_base'])
        
    if flow and 'flows' in area_prompt:
        flow_prompt = area_prompt['flows'].get(flow, {}) # type: ignore
        if '_base' in flow_prompt:
            parts.append(flow_prompt['_base'])
            
        if step and 'steps' in flow_prompt:
            step_prompt = flow_prompt['steps'].get(step, {}) # type: ignore
            if step_prompt:
                parts.append(step_prompt)
                
    return '\n\n'.join(parts)