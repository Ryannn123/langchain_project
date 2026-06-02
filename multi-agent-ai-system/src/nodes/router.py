from typing import Literal

from langgraph.types import Command
from langgraph.graph import END
from langchain.messages import AIMessage

from src.state import AgentState
from src.schemas import StudentProfile

GotoNode = Literal['course_generator', 'university_generator', '__end__']

def route_generator_node(state: AgentState) -> Command[GotoNode]:
    profile = state.get('student_profile', StudentProfile())
    update = {}

    # --- Course ---
    course = profile.course_detail
    course_state = state.get('course_state', {})
    course_state_update = {}
    
    if course.is_able_to_decide is False:
        indecision_count = course_state.get('indecision_count', 0) + 1
        course_state_update['indecision_count'] = indecision_count
        
        if (
            indecision_count >= course_state.get('max_indecision_count', 3) and
            course_state.get('has_recommend_fallback', False) and
            not course_state.get('is_stuck', False)
        ):
            course_state_update['is_stuck'] = True
    update['course_state'] = course_state_update
    
    course_completed = (
        course.confirmed_pathway is not None and (
            course.confirmed_course is not None
            or course_state.get('has_recommend_fallback', False))
        or course_state.get('is_stuck', False)
        or course_state_update.get('is_stuck', False)
    )
        
    # --- University ---
    university = profile.university_detail
    
    university_completed = (
        university.university_questions_and_inquiries or
        university.preferred_choice == 'wait_upu_matriks_stpm'
    )
    
    # --- Routing ---
    if not course_completed:
        goto = 'course_generator'
    elif not university_completed:
        goto = 'university_generator'
    else:
        goto: GotoNode = END # type: ignore
        
        content = 'Airight no problem! we will prepare a persinalized matching report for you'
        if university.preferred_choice == 'wait_upu_matriks_stpm':
            content = """Alright you can wait for UPU / Matriks first, but if let say you didnt get the offer you want. You still have other options.
        
Plan A - Public uni direct intake
Plan B - Private uni

We can help you to explore on the other plan too, so you can ask me anytime.
"""
        update['messages'] = [AIMessage(content)]
        update['completed'] = True
    
    return Command(goto=goto, update=update)