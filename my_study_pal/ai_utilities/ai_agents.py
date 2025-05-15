from pydantic import BaseModel
from django.core.exceptions import ImproperlyConfigured
from my_study_pal.ai_utilities.models import AiModel
from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
from my_study_pal.courses.models import Course
from my_study_pal.subjects.models import Subject
from google.genai import types
import os




OPEN_AI_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

class QuestionOrganizer(BaseModel):
    existing_subject_id: int
    existing_course_id: int
    existing_section_id: int
    suggested_subject_title: str
    suggested_course_title: str
    suggested_section_title: str


def get_current_sections_structures(query:str) -> list:
    """Get subjects/courses and sections structure with titles along with their ids.
        A filtering phase is performed on topics using similarity search to avoid
        overloading the prompt with unnecessary data.
        Args:
            query: user query
        Returns:
            A list containing the results.
    """

    subjects = VectorStoreManager(Subject().vector_store_name).get_similar_topics(query)
    courses = VectorStoreManager(Course().vector_store_name).get_similar_topics(query)
    data = [
        {"subject_id":subject.id,
         "subject_title": subject.title,
         "courses": [{"course_id":  course.id,
                      "course_title": course.title,
                      "sections":[{"section_id": section.id,
                                   "section_title":section.title} for section in course.sections.all()]
                      } for course in subject.courses.filter(id__in=[course.id for course in courses])]
         } for subject in subjects
    ]
    return  data


class AIAgentClientManager:

    def __init__(self, ai_agent_token:str ="", model:str="",name:str="", ai_agent: AiModel=None):
        """
        Class to handle api calls to AI agents can be initialized using a token, both model and name
        or a model instance.
        """
        try:
            if ai_agent and type(ai_agent) == AiModel:
                self.agent = ai_agent
            elif ai_agent_token:
                self.agent = AiModel.objects.get(token=ai_agent_token)
            elif model and name:
                self.agent = AiModel.objects.get(model=model, name=name)
            else:
                raise ImproperlyConfigured("Wrong usage of parameters.")
            self.client = self.agent.client
        except Exception:
            raise ImproperlyConfigured("Wrong usage of parameters.")


    def make_call(self, call_parameters:dict):
        if self.agent.name == AiModel.AiAgentNameChoices.OPEN_AI:
            response = self.client.responses.parse(**call_parameters)
            return response.output_parsed.dict()
        if self.agent.name == AiModel.AiAgentNameChoices.GEMINI:
            response = self.client.models.generate_content(**call_parameters)
            return response.parsed.dict()


    def build_parameters(self, messages, instructions="", structured_output = None):
        parameters_mapping= {
            AiModel.AiAgentNameChoices.OPEN_AI: self.build_open_ai_parameters,
            AiModel.AiAgentNameChoices.GEMINI: self.build_gemini_parameters
        }
        return parameters_mapping[self.agent.name](messages, instructions, structured_output)


    def build_open_ai_parameters(self, messages, instructions="", structured_output = None):
        parameters = {"model": self.agent.model}
        user_messages = [{
            "role": "user",
            "content": message
        } for message in messages]
        parameters.update(input=user_messages)
        if instructions:
            parameters.update(instructions=instructions)
        if structured_output:
            parameters.update(text_format=structured_output)
        return parameters

    def build_gemini_parameters(self, messages, instructions="", structured_output= None):
        parameters = {"model": self.agent.model}
        user_messages = [
            types.Content(
                role="user", parts=[types.Part(text=message)]
            ) for message in messages
        ]
        parameters.update(contents=user_messages)
        config_params = {}
        if instructions:
            config_params.update(system_instruction=instructions)
        if structured_output:
            config_params.update(response_mime_type="application/json", response_schema=structured_output)
        if config_params:
            parameters.update(config=types.GenerateContentConfig(**config_params))
        return parameters

    def get_massage_classification_data(self, user_message):
        topics_structure = get_current_sections_structures(user_message)
        instructions = ("you are an assistant your role is to help the user identify where to look for the answer "
                        "to his question in the database."
                        f"Here is the current structure {str(topics_structure)}"
                        "use it to identify which  subjects/courses and sections titles "
                        "are related semantically to the users question respond with the following:"
                        "if an existing subject is relevant return his id else suggest a title for a new subject"
                        "if an existing course is relevant return his id else suggest a title for a new course"
                        "if an existing section is relevant return his id else suggest a title for a new section."
                        "existing_subject_id or suggested_subject_title are not allowed to be both empty or both non empty"
                        "existing_course_id or suggested_course_title are not allowed to be both empty or both non empty"
                        "existing_section_id or suggested_section_title are not allowed to be both empty or both non empty")

        parameters = self.build_parameters([user_message], instructions=instructions,
                                           structured_output=QuestionOrganizer)
        return self.make_call(parameters)







