from typing import Annotated, Any, TypedDict

from langgraph.graph import MessagesState

from src.schemas import IntentItem

def merge_unique_lists(existing: list[Any], new: list[Any]) -> list[Any]:
    merged = list(existing)
    for item in new:
        if item not in merged:
            merged.append(item)
    
    return merged

AppendUniqueStringList = Annotated[list[str], merge_unique_lists]

class Flags(TypedDict, total=False):
    # --- Course ---
    has_send_initial_course_inquiry: bool
    has_confirm_course: bool
    
    # --- Pathway ---
    pathway_is_stuck: bool
    has_recommend_fallback: bool

class AgentState(MessagesState, total=False):
    # --- Registration Detail ---
    has_registerd: bool
    
    # --- Qualification Detail ---
    highest_qualification: str
    
    # --- Course Detail ---
    confirmed_course: str
    shortlisted_courses: AppendUniqueStringList
    student_strengths: AppendUniqueStringList
    rejected_courses: AppendUniqueStringList
    course_concerns: AppendUniqueStringList
    course_preferences: AppendUniqueStringList
    
    # --- Pathway Detail ---
    confirmed_pathway: str
    shortlisted_pathways: AppendUniqueStringList
    rejected_pathways: AppendUniqueStringList
    pathway_concerns: AppendUniqueStringList
    pathway_preferences: AppendUniqueStringList
    
    # --- University Detail ---
    shortlisted_private_universities: AppendUniqueStringList
    shortlisted_public_universities: AppendUniqueStringList
    admission_strategy: str
    university_preferences: AppendUniqueStringList
    university_questions_and_inquiries: AppendUniqueStringList
    
    # --- Meta ---
    current_area: str
    current_flow: str
    current_step: str
    intents: list[IntentItem]
    max_indecision_count: int
    indecision_count: int
    
    # --- Flags ---
    flags: Flags