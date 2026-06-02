from langchain.messages import SystemMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.state import AgentState
from src.schemas import StudentProfile
from src.prompt_builder import PromptBuilder

def university_generator_node(state: AgentState):
    profile = state.get('student_profile', StudentProfile())
    university = profile.university_detail 
    course_state = state.get('course_state', {})
    uni_state = state.get('university_state', {})
    history_messages = state['messages'][-6:]
    
    if university.shortlisted_public_universities and not university.preferred_choice:
        public_unis = ', '.join(university.shortlisted_public_universities)
        return {'messages': AIMessage(f"""I see, since {public_unis} are public universities, applications will need go through UPU, where placements are highly competitive and not guaranteed. What is your first choice for now?

1. Wait for UPU / Matrikulasi / STPM
2. Explore other options (Direct Intake, private, or semi-government universities)""")}
        
    if len(university.shortlisted_private_universities) == 0 and uni_state.get('step', 0) == 0:
        content = ''
        if course_state.get('is_stuck', False):
            content = 'No worries, then we can explore uni first.\n\n'
        return {
            'messages': [AIMessage(content + 'Alright, may i know what uni you are considering now? or you want me to recommend to you?')],
            'university_state': {'step': 1}
        }
    
    if len(university.shortlisted_private_universities) == 1:
        phase = 'ask_concern'
    else:
        if not university.university_preferences:
            phase = 'ask_preference'
        else:
            phase = 'ask_concern'
    
    prompt_builder = PromptBuilder(profile)
    system_prompt = SystemMessage(prompt_builder.build_prompt('university', phase))
    
    messagges = [system_prompt] + history_messages
    
    llm = ChatGoogleGenerativeAI(model='gemini-3.1-flash-lite')
    result = llm.invoke(messagges)
    
    return {'messages': [result]}