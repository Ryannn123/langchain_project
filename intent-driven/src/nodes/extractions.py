from langchain_core.messages import get_buffer_string
from langchain.messages import SystemMessage
from langchain.chat_models import init_chat_model

from src.utils import area_to_schema, merge_schema, get_profile, dict_to_yaml_like
from src.state import AgentState
from src.schemas import ClassifiedIntents, CourseDetail, PathwayDetail

def extract_intents_node(state: AgentState):
    user_message = state['messages'][-1]
    
    if user_message.type != 'human':
        return {}
    
    system_prompt = SystemMessage("""Break down the user's message into a list of distinct intents. Each intent must map to one of the predefined intent types and areas. If the user says several things in one sentence, separate them. Only output intents that are explicitly expressed.

**RULES**
1. Use the <context> to get context

**EXAMPLE**
AI: 'Have you register to any uni?'
User: 'not yet, i plan to study business and IT at APU, but i dont know which couse have better job opportinuty'
Reasoning: User respond to registration first, express interest in course and uni, and express concern in course
Output: [
    {'area': 'registration', 'intent_type': 'provide'},
    {'area': 'course', 'intent_type': 'provide'},
    {'area': 'course', 'intent_type': 'ask'},
    {'area': 'university', 'intent_type': 'provide'},
]

**Final Reminder**
Carefully analyze all the area in user message from the context of <context> and separate them""")
    
    chat_history = get_buffer_string(state['messages'][-3:-1])
    context = SystemMessage(f"""
<context>
<chat_history>
{chat_history}
</chat_history>
</context>""")
    
    llm = init_chat_model(model='google_genai:gemini-3.1-flash-lite')
    intent_extractor = llm.with_structured_output(ClassifiedIntents)
    
    result = intent_extractor.invoke([system_prompt, context, user_message])
    parsed = ClassifiedIntents.model_validate(result)
    return {'intents': parsed.intents}

def extract_profile_node(state: AgentState):
	intents = state.get('intents', [])
	areas = list({i.area for i in intents if i.area != 'general' and i.intent_type != 'out_of_scope'})

	if not areas:
		return {}

	user_message = state['messages'][-1]
	if user_message.type != 'human':
		return{}

	system_prompt = SystemMessage("""You are an AI assistant designed to extract structured student profile details from conversational data.

Your primary task is to analyze the user's message to identify new choices, preferences, and concerns. Use the <chat_history> and <current_profile> to understand the context of the conversation.

### INPUTS PROVIDED:
1. <current_profile>: The student's current recorded profile json.
2. <chat_history>: The recent exchange between the AI and the student.
3. user's message: The user's most recent statement or response.

### EXTRACTION RULES:

1. STATE COMPARISON (DEDUPLICATION):
   - Always cross-reference your extractions with the <current_profile>.
   - If a course, pathway, preference, or concern is already recorded in the corresponding field of the <current_profile>, DO NOT extract it again. Leave that field empty or omit the value.
   - If a value is mentioned but is missing or incomplete in the <current_profile>, you must extract it.

2. CONTEXTUAL AGREEMENT & IMPLICIT CONFIRMATION:
   - Students often confirm suggestions made by the AI in the <chat_history> rather than repeating them.
   - If the student agrees to, accepts, or builds upon options proposed by the AI in the chat history, treat those options as active selections and extract them if they are not already in the <current_profile>.
   - Key indicators of implicit confirmation include words like "also", "too", "yes", "that's correct", "either is fine", or "sounds good".
   - Example: If the AI asks "Are you considering Business or IT?" and the student replies "I'm also considering Law", this indicates the student is considering Business, IT, and Law. Extract all three if they do not exist in the profile.

3. PREFERENCES VS. INQUIRIES:
   - Direct Choices: If the user expresses a desire to study a subject (e.g., "I want to do business"), extract it to the relevant course/pathway fields.
   - Questions/Worries: If the user asks a question about a subject (e.g., "What does the IT course cover?", "Is the math in business hard?"), DO NOT add the course to the shortlisted/confirmed lists. Instead, extract the underlying question or worry into the respective `_concerns` field.

4. REJECTIONS:
   - If the student explicitly rejects a previously mentioned option, a path, or a subject (e.g., "No engineering", "I don't want to do a Diploma"), extract it into respective `rejected_`.

### Reminder
1. DO NOT output the fields that cant be extracted
""")
    
	data = get_profile(state, CourseDetail, PathwayDetail)
	curent_profile = dict_to_yaml_like(data, exclude_empty=True)
	chat_history = get_buffer_string(state['messages'][-6:-1], format='xml') if len(state['messages']) > 1 else 'No previous history'
	context = SystemMessage(f"""
<context>
<current_profile>
{curent_profile}
</current_profile>
<chat_history>
{chat_history}
</chat_history>
</context>
""")
    
	schmeas = area_to_schema(areas)
	MergedSchema = merge_schema(*schmeas)

	llm = init_chat_model(model='google_genai:gemini-3.1-flash-lite')
	profile_extractor = llm.with_structured_output(MergedSchema)
	result = profile_extractor.invoke([system_prompt, context, user_message])
	parsed = MergedSchema.model_validate(result)
	return parsed.model_dump(exclude_unset=True)