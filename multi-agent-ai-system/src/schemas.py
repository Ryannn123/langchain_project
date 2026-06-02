from typing import Literal

from pydantic import BaseModel, Field
    
class CourseDetail(BaseModel):
    # ==========================================
    # 1. ROUTING & STATUS
    # ==========================================
    is_able_to_decide: bool | None = Field(
        default=None,
        description="""Categorize the student's decision-making state:

        - True (Decided): The student selects a specific path, narrows down their list, explicitly excludes options or or accepting a fallback (e.g., "I accept foundation").
        - False (Decision Roadblock): The student understands the options but explicitly states they are stuck or unable to make a choice (e.g., "I don't know", "I can't decide", "Not sure").
        - Null (Information-Seeking): The student is asking questions, seeking clarification or comparing options (e.g., "Can I do X or Y?", "I am confused about the difference between X and Y").

        Rule:
        - DO NOT extract any info if the context is not about course
        - If the student is confused about COURSE OR PATHWAY DETAILS or DIFFERENCES (e.g., "What is the difference between A and B?", "How about B?"), classify as 'Null' because they are seeking information.
        - Only classify as 'False' if they are struggling with the ACT OF CHOOSING itself.

        <example>
        User: "I honestly cannot decide which is better for me. I dont know which one to choose"
        Reasoning: The student understands the choices but has hit a decision roadblock.
        Output: {"has_narrowed_options": false}

        User: "I want to study either business or IT."
        Reasoning: Stating multiple broad interests at the start of a conversation is exploratory, not a decision roadblock.
        Output: {"has_narrowed_options": null}

        User: "After I finish my foundation course, can I still go into event management or masscomm?"
        Reasoning: This is a feasibility question about pathways, not a struggle to make a final choice.
        Output: {"has_narrowed_options": null}

        User: "Actually, I'm still confused about what the difference is between Mass Comm and Event Management."
        Reasoning: This is an informational gap (the student needs details on the courses), not a decision roadblock.
        Output: {"has_narrowed_options": null}
        
        Assistant: "Since you cant decide a course, do you want to take Foundation first?"
        User: "Yes"
        Reasoning: The student is able to decide
        Output: {"has_narrowed_options": true}
        
        Assistant: "Do you have any preferred university in mind?"
        User: "Not sure"
        Reasoning: This is not related to course context
        Output: {"has_narrowed_options": null}
        
        Assistant: "Since you cant decide a course, do you want to take Foundation first?"
        User: "How about Diploma?"
        Reasoning: The student is seeking information
        Output: {"has_narrowed_options": null}
        </example>
        """
    )
    
    # --- Course Gates ---
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
    
    # --- Pathway Gates ---
    confirmed_pathway: str | None = Field(
        default=None, 
        description="Extract the exact Pre-U/Pathway ONLY IF the student has explicitly made a firm, final decision on a single route (e.g., 'I want to do A-Levels') or student explicitly agreed to take a fallback pathway recommendation. Leave null if they are still weighing options."
    )
    shortlisted_pathways: list[str] = Field(
        default_factory=list, 
        description="Extract any Pre-U/Pathways the student is considering but has not yet firmly chosen (e.g., ['A-Levels', 'Foundation', 'Diploma'])."
    )

    # ==========================================
    # 2. CONTEXT
    # ==========================================
    rejected_options: list[str] = Field(
        default_factory=list,
        description="List any specific courses, pathways, or subjects the student explicitly states they DO NOT want to do (e.g., 'I hate math', 'No engineering', 'Don't want A-levels')."
    )
    student_strengths: list[str] = Field(
        default_factory=list,
        description="Extract subjects, hobbies, or skills the student mentions they are good at or enjoy (e.g., 'scoring A in Biology', 'like working with computers', 'enjoy debating'). Used to suggest courses when they have no idea."
    )
    options_concerns: list[str] = Field(
        default_factory=list,
        description="Extract any explicit worries or questions the student has about a course or pathway (e.g., 'are the job prospects good?', 'is the math too hard?', 'will AI replace this job?', 'foundation or diploma is more practical?')."
    )
    options_preferences: list[str] = Field(
        default_factory=list,
        description="Extract regarding their COURSE and PATHWAY choices ONLY. ANY specific requirements or constraints for their study journey. Capture factors like location ('wants overseas', 'prefer UK', 'staying local'), duration ('fast-track 1 year'), learning style ('prefer coursework over exams'), or budget limits."
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
    
    preferred_choice: Literal['wait_upu_matriks_stpm', 'explore_alternatives'] | None = Field(
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
    
class StudentProfile(BaseModel):
    registered: bool | None = None
    qualification: str | None = None
    course_detail: CourseDetail = Field(default_factory=CourseDetail, description='Extact only info related to course, dont extract other info such as university. Context: "Foudation in Business" must extract under pathway not course')
    university_detail: UniversityDetail = Field(default_factory=UniversityDetail, description='Extact only info related to university including concern, preference about university.')
    concern_detail: list[str] = Field(default_factory=list)