from langchain.chat_models import init_chat_model
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.messages.utils import get_buffer_string

from src.state import AgentState
from src.schemas import StudentProfile
from src.prompts.master import EXTRACTION_PROMPT

def build_llm():
    llm = init_chat_model('google_genai:gemini-3.1-flash-lite')
    return llm.with_structured_output(StudentProfile)
    
def extraction_node(state: AgentState):
    latest_message = state['messages'][-1]

    if latest_message.type != 'human':
        return {}
    
    student_profile = state.get('student_profile', StudentProfile())
    history_content = get_buffer_string(state['messages'][-6:-1], format='xml') if len(state['messages']) > 1 else 'No previous history' 
    current_profile_json = student_profile.model_dump_json()
    
    sys_prompt = SystemMessage(EXTRACTION_PROMPT)

    prompt = HumanMessage(f"""
    Now, process the following:
    
    <current_profile>
    {current_profile_json}
    </current_profile>
    
    <chat_history>
    {history_content}
    </chat_history>

    <latest_message>
    {latest_message.content}
    </latest_message>
    """)

    messages = [sys_prompt, prompt]

    extractor = build_llm()
    extracted_data = extractor.invoke(messages)
    
    parsed = StudentProfile.model_validate(extracted_data)

    return {'student_profile': parsed}