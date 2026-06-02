from src.prompts.master import GLOBAL_MASTER_PROMPT
from src.prompts.registry import SopGates, PROMPT_REGISTRY
from src.schemas import StudentProfile

class PromptBuilder:
    def __init__(self, profile: StudentProfile) -> None:
        self.profile = profile
    
    @staticmethod
    def _format_list(items: list) -> str:
        return ', '.join(items) if items else "None stated yet"
    
    def build_prompt(self, sop_gate: SopGates, phase_key: str):
        gate_config = PROMPT_REGISTRY.get(sop_gate)
        if not gate_config:
            raise KeyError(f"SOP Gate '{sop_gate}' is not registered in PROMPT_REGISTRY.")
        
        phase_directive = gate_config["phases"].get(phase_key, '')
        
        student_profile_json = self.profile.model_dump_json(exclude_unset=True)
        student_profile_json = 'No profile' if student_profile_json == '{}' else student_profile_json
        
        compiled_prompt = GLOBAL_MASTER_PROMPT.format(
            student_profile_json=student_profile_json,
            sop_gate_prompt=gate_config['master'],
            phase_directive=phase_directive
        )
        
        return compiled_prompt