from typing import Annotated, Any, TypedDict

from langgraph.graph import MessagesState

from src.schemas import CourseDetail, UniversityDetail, StudentProfile

class CourseState(TypedDict, total=False):
    max_indecision_count: int
    indecision_count: int
    is_stuck: bool
    has_recommend_fallback: bool
    
class UniversityState(TypedDict, total=False):
    step: int

def merge_unique_lists(existing: list[Any], new: list[Any]) -> list[Any]:
    """
    Merges two lists preserving order and ensuring unique values.
    """
    
    merged = list(existing)
    for item in new:
        if item not in merged:
            merged.append(item)
    
    return merged

def merge_course_detail(existing: CourseDetail, update: CourseDetail | dict[str, Any]) -> CourseDetail:
    update_dict = update.model_dump(exclude_unset=True) if isinstance(update, CourseDetail) else update
    existing_dict = existing.model_dump()
    
    for key, value in update_dict.items():
        if key == 'is_able_to_decide':
            existing_dict[key] = value
        
        if value is None:
            continue
        
        if isinstance(value, list):
            existing_dict[key] = merge_unique_lists(existing_dict.get(key, []), value)
        else:
            existing_dict[key] = value
    
    return CourseDetail(**existing_dict)

def merge_uni_detail(existing: UniversityDetail, update: UniversityDetail | dict[str, Any]) -> UniversityDetail:
    update_dict = update.model_dump(exclude_unset=True) if isinstance(update, UniversityDetail) else update
    existing_dict = existing.model_dump()
    
    for key, value in update_dict.items():
        if value is None:
            continue
        
        if isinstance(value, list):
            existing_dict[key] = merge_unique_lists(existing_dict.get(key, []), value)
        else:
            existing_dict[key] = value
    
    return UniversityDetail(**existing_dict)

def reduce_student_profile(existing: StudentProfile | None, update: StudentProfile | dict[str, Any] | None) -> StudentProfile:
    if existing is None:
        existing = StudentProfile()
    if not update:
        return existing
    
    if isinstance(update, StudentProfile):
        update_dict = update.model_dump(exclude_unset=True)
        if 'course_detail' in update_dict:
            update_dict['course_detail']['is_able_to_decide'] = update.course_detail.is_able_to_decide
    else:
        update_dict = update
    existing_dict = existing.model_dump()
    
    for key, value in update_dict.items():
        if value is None:
            continue
        
        if key == 'course_detail':
            existing_dict[key] = merge_course_detail(existing.course_detail, value).model_dump()
        elif key == 'university_detail':
            existing_dict[key] = merge_uni_detail(existing.university_detail, value).model_dump()
        elif isinstance(value, list):
            existing_dict[key] = merge_unique_lists(existing_dict.get(key, []), value)
        elif isinstance(value, dict) and isinstance(existing_dict.get(key), dict):
            existing_dict[key] = {**existing_dict[key], **value}
        else:
            existing_dict[key] = value
    
    return StudentProfile(**existing_dict)

def reduce_course_state(existing: CourseState | None, new: CourseState | dict[str, Any] | None):
    if existing is None:
        existing = {'max_indecision_count': 3, 'indecision_count': 0, 'has_recommend_fallback': False, 'is_stuck': False}
    if not new:
        return existing
    
    for key, value in new.items():          
        if value is None:
            continue
        
        existing[key] = value
    
    return existing

class AgentState(MessagesState, total=False):
    student_profile: Annotated[StudentProfile, reduce_student_profile]
    course_state: Annotated[CourseState, reduce_course_state]
    university_state: UniversityState
    