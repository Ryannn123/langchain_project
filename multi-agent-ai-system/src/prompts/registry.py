from typing import TypedDict, Literal

from src.prompts.master import COURSE_MASTER_PROMPT, UNI_MASTER_PROMPT
from src.prompts.phases import COURSE_PHASE_DIRECTIVES, UNI_PHASE_DIRECTIVES

SopGates = Literal['course', 'university']

class PhaseTemplates(TypedDict):
    master: str
    phases: dict[str, str]    

PROMPT_REGISTRY: dict[SopGates, PhaseTemplates] = {
    'course': {
        'master': COURSE_MASTER_PROMPT,
        'phases': COURSE_PHASE_DIRECTIVES
    },
    
    'university': {
        'master': UNI_MASTER_PROMPT,
        'phases': UNI_PHASE_DIRECTIVES
    }
}