from typing import Literal
from pydantic import BaseModel, Field

IntentType = Literal['provide', 'confirm', 'reject', 'ask', 'express_indecision', 'accept_fallback', 'out_of_scope']
Area = Literal['registration', 'qualification', 'course', 'pathway', 'university', 'general']

# =========================================
# Intent
# =========================================

class IntentItem(BaseModel):
    intent_type: IntentType = Field(
        ..., 
        description="""The specific action the user is performing in this segment
        
- provide: user gives information (shortlists, preferences, status)
- confirm: user makes a final decision on a single item
- reject: user explicitly excludes an option
- express_indecision: ONLY if student explicitly cannot make decision, or having "no idea" when respond to a question
- ask: user asks a question, seeking information or expresses concern
- accept_fallback: user agrees to a system-suggested fallback
- out_of_scope: every other non related intent
        """)
    
    area: Area = Field(
        ..., 
        description="""The counselling area this intent belongs to
- 'registration' - Register, apply, pay registration fee related topic
- 'qualification': Result, qualification, entry requirement related topic
- 'course': course / major related topic
- 'pathway': Academic pathway (e.g., foundation, diploma, alevel, etc) related topic
- 'university': University related topic
- 'general': Other topic not related to area above
        """)
    
class ClassifiedIntents(BaseModel):
    reasoning: str = Field(..., description='a one sentence reasoning thought about the intent of the user message')
    intents: list[IntentItem] = Field(default_factory=list, description='List of all intents detected in the user message. Can be empty if no clear intent')
    
# =========================================
# Student Profile
# =========================================

class RegistrationDetail(BaseModel):
    has_registerd: bool = Field(
        default=False,
        description="If student explicitly mentioned has registered, extract 'true'"
    )
    
class CourseDetail(BaseModel):
    confirmed_course: str | None = Field(
        default=None, 
        description="""Extract the exact course/major ONLY IF the student has explicitly made a firm, final decision on a single choice (e.g., 'I will definitely do Computer Science'). Or there only 1 course left after narrow down.
        
        Example:
        AI: So between business and IT, you're leaning more towards dropping IT from your list?
        User: Yes
        Reasoning: Student have eliminated IT from the list, there are only Business left
        Output: "confirmed_course": Business
        """
    )
    
    shortlisted_courses: list[str] = Field(
        default_factory=list, 
        description="""Extract any courses or fields of study the student is interested in but has not yet firmly chosen. If they mention 2 or more options they are considering, list them all here.
        
        CRITICAL: Include courses from the chat history that the user implicitly confirms or adds to in the latest message (e.g., if the AI suggested 'Business' and the user says 'I am also considering Law', extract both ['Business', 'Law'] if they are not already in the current_profile).
        """
    )
    
    student_strengths: list[str] = Field(
        default_factory=list,
        description="Extract subjects, hobbies, or skills the student mentions they are good at or enjoy (e.g., 'scoring A in Biology', 'like working with computers', 'enjoy debating')."
    )
    
    rejected_courses: list[str] = Field(
        default_factory=list,
        description="List any specific courses or subjects the student explicitly states they DO NOT want to do (e.g., 'I hate math', 'No engineering')."
    )
    
    course_concerns: list[str] = Field(
        default_factory=list,
        description="Extract any explicit worries or questions the student has about a course (e.g., 'are the job prospects good?', 'is the math too hard?', 'will AI replace this job?')."
    )
    
    course_preferences: list[str] = Field(
        default_factory=list,
        description="Extract regarding their COURSE choices ONLY. ANY specific requirements or constraints for their study journey. (e.g., 'I want job with flexible woking time', 'I prefer talk to people')"
    )
    
class PathwayDetail(BaseModel):
    confirmed_pathway: str | None = Field(
        default=None, 
        description="Extract the exact Pre-U/Pathway ONLY IF the student has explicitly made a firm, final decision on a single route (e.g., 'I want to do A-Levels') or student explicitly agreed to take a fallback pathway recommendation. Leave null if they are still weighing options."
    )
    
    shortlisted_pathways: list[str] = Field(
        default_factory=list, 
        description="Extract any Pre-U/Pathways the student is considering but has not yet firmly chosen (e.g., ['A-Levels', 'Foundation', 'Diploma'])."
    )

    rejected_pathways: list[str] = Field(
        default_factory=list,
        description="List any specific pathways the student explicitly states they DO NOT want to do (e.g., 'Don't want A-levels')."
    )
    
    pathway_concerns: list[str] = Field(
        default_factory=list,
        description="Extract any explicit worries or questions the student has about a pathway (e.g., 'foundation or diploma is more practical?')."
    )
    
    pathway_preferences: list[str] = Field(
        default_factory=list,
        description="Extract regarding their PATHWAY choices ONLY. ANY specific requirements or constraints for their study journey. Capture factors like location ('wants overseas', 'prefer UK', 'staying local'), duration ('fast-track 1 year'), learning style ('prefer coursework over exams')."
    )
    
class UniversityDetail(BaseModel):
    shortlisted_private_universities: list[str] = Field(
        default_factory=list,
        description="Extract any PRIVATE university the student is considering"
    )
    
    shortlisted_public_universities: list[str] = Field(
        default_factory=list,
        description="Extract any PUBLIC university the student is considering"
    )
    
    admission_strategy: Literal['wait_upu_matriks_stpm', 'explore_alternatives'] | None = Field(
        default=None,
        description="""The student's explicitly stated primary admission strategy.
        CRITICAL: Only extract this value if the student has been directly asked about their preference and has provided a clear, explicit answer. Do not infer, guess, or assume this preference prior to a direct question-and-answer exchange. Keep as None if the topic has not been explicitly raised and answered
        
        - 'wait_upu_matriks_stpm' if they prefer to wait for standard government channels (UPU, Matrikulasi, or STPM results).
        - 'explore_alternatives' if they want to look into other options immediately (such as public university direct intake, private universities, or semi-government institutions).
"""
    )
    
    university_preferences: list[str] = Field(
        default_factory=list,
        description="""
        Extract regarding their UNIVERSITY choices ONLY. ANY specific requirements or constraints for their university choice. Capture factors like location ('I want KL / Selangor area'), university type ('I prefer ranking', 'i prefer budget'), environment ('I want uni with rich campus life').
        
        RULES:
        - Do NOT extract general status updates, statements of intent (e.g., 'I have some universities in mind')
        """
    )
    
    university_questions_and_inquiries: list[str] = Field(
        default_factory=list,
        description="""
        Extract specific, factual questions or information requests the student has about university details (e.g., queries about tuition fees, accommodation/hostel, transportation, facilities).

        RULES:
        - Do NOT extract general status updates, statements of intent (e.g., 'I have some universities in mind', 'no uni in mind', 'recommend uni to me'), or preferences.
        - Do NOT extract general recommendation requests(e.g., 'recommend some universities to me', 'which uni is good?')
        - DO NOT assume any question, MUST be explicitly mentioned by student
        - If the student explicitly mentioned no qustion, return 'No question'.
        
        <example>
        User: "No uni in mind"
        Reasoning: This is a general statement, status update. Not a question or inquiry
        Output: {"university_questions_and_inquiries": []}
        
        User: "Recommend uni to me"
        User: "List the uni for me"
        Reasoning: This is a recommendation requests, not specific factual inquiries about university
        Output: {"university_questions_and_inquiries": []}
        </example>
        """        
    )