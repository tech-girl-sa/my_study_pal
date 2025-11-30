from pydantic import BaseModel
from django.core.exceptions import ImproperlyConfigured
from my_study_pal.ai_utilities.models import AiModel
from my_study_pal.ai_utilities.vector_store_utils import VectorStoreManager
from my_study_pal.courses.models import Course, Chunk, Message
from my_study_pal.subjects.models import Subject
from google.genai import types
import os
from typing import Optional




OPEN_AI_KEY = os.environ.get('OPENAI_API_KEY')
GEMINI_KEY = os.environ.get('GEMINI_API_KEY')

class QuestionOrganizer(BaseModel):
    existing_subject_id: int
    existing_course_id: int
    existing_section_id: int
    suggested_subject_title: str
    suggested_course_title: str
    suggested_section_title: str

class CourseOrganizer(BaseModel):
    existing_subject_id: Optional[int] = None
    suggested_subject_title: Optional[str] = None
    suggested_subject_description: Optional[str] = None

class QuestionWithinCourseOrganizer(BaseModel):
    relevant: bool
    question_scope: str
    question_action: str

class retrieval_mode(BaseModel):
    retrieval_mode: str

class SubjectDescription(BaseModel):
    description: str


def get_current_sections_structures(query:str, user_id) -> list:
    """Get subjects/courses and sections structure with titles along with their ids.
        A filtering phase is performed on topics using similarity search to avoid
        overloading the prompt with unnecessary data.
        Args:
            query: user query
        Returns:
            A list containing the results.
    """

    subjects = VectorStoreManager(Subject().vector_store_name).get_similar_topics(query, user_id)
    courses = VectorStoreManager(Course().vector_store_name).get_similar_topics(query, user_id)
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

def get_similar_chunks_data(query:str, document_id, section_id) -> list:
    """Get subjects/courses and sections structure with titles along with their ids.
        A filtering phase is performed on topics using similarity search to avoid
        overloading the prompt with unnecessary data.
        Args:
            query: user query
        Returns:
            A list containing the results.
    """

    chunks = VectorStoreManager(Chunk().vector_store_name).get_similar_chunks(query, document_id)
    data = [chunk.content for chunk in chunks]
    return  data


class AIAgentClientManager:

    def __init__(self, ai_agent_token:str ="", model:str="",name:str="", ai_agent: AiModel=None):
        """
        Class to handle api calls to AI agents can be initialized using a token, both model and name
        or a model instance.
        #TODO add user information to prompt for a better customized responses
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


    def make_call(self, call_parameters:dict, parsed=True):
        if self.agent.name == AiModel.AiAgentNameChoices.OPEN_AI:
            response = self.client.responses.parse(**call_parameters)
            if parsed:
                return response.output_parsed.dict()
            return response.output[0].content[0].text
        if self.agent.name == AiModel.AiAgentNameChoices.GEMINI:
            response = self.client.models.generate_content(**call_parameters)
            if parsed:
                return response.parsed.dict()
            return response.text


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

    def get_massage_classification_data(self, user_message, user_id):
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

    def get_course_subject_title(self, course_title, user_id):
        subjects = VectorStoreManager(Subject().vector_store_name).get_similar_topics(course_title, user_id)
        data = [
            {"subject_id": subject.id,
             "subject_title": subject.title,
             } for subject in subjects
        ]
        message = ("You are responsible for managing course creation in a study helping app. "
                   f"A new course titled {course_title} needs to be categorized."
                   f"list of existing subjects currently existing in db {data}"
                    "If the course clearly belongs semantically to one of the existing subjects exclusively from the list, "
                   "return its id in existing_subject_id."
                    "If none of the existing subjects are a good fit—due to language, topic, "
                   "or academic focus—then do not return an id rather suggest a new subject by providing a suggested_subject_title "
                   "and a short description. existing_subject_id should be empty in that case"
                    "Do not pick a subject that refers to a different language or unrelated field."
                   "ex: spanish related courses cannot be part of english related subjects")

        parameters = self.build_parameters([message], structured_output=CourseOrganizer)
        return self.make_call(parameters)

    def get_question_scope(self, course, user_query):

        message = ("You are responsible for detecting the scope of user's question in a study helping app. "
                   f"the course that the user is asking about is named {course.title} ({course.description}), "
                   f"if the question is irrelevant to the course set relevant to false else to true. "
                   f"If the user is asking to perform an action like summarizing,translating or explaining "
                   f"the current section itself set the question_scope to section, if the question requires"
                   f"an action for the whole course set the question_scope to whole_course. else set it to similarity_search."
                   f"set question_action according to the action the user wants to perform.Possible values are:"
                   f"summarize, translate, explain_more or respond")

        parameters = self.build_parameters([user_query],instructions=message, structured_output=QuestionWithinCourseOrganizer)
        return self.make_call(parameters)

    def get_retrieval_mode(self, docs, user_query):

        message = (f"are the following information {docs} relevant to answer the user questions "
                   f"if yes set retrieval_mode to retrieval. if no and a web search is needed (set "
                   f"it to web) if you can answer it without a search (set it to llm) ")

        parameters = self.build_parameters([user_query], instructions=message,
                                           structured_output=retrieval_mode)
        return self.make_call(parameters)


    def get_response_based_on_documents(self, user_message,user , documents, retrieval_mode, section_id=0):
        if retrieval_mode=="retrieval":
            instructions = (f" based on the following informations respond to the users question {documents}")
        elif retrieval_mode=="web":
            instructions = (f"A web search is performed to answer this question here are the search results {documents}")
        else:
            instructions = "respond to user's message."
        if section_id:
            instructions += self.construct_history_prompt(user_message, user, section_id)
        print(instructions)
        parameters = self.build_parameters([user_message], instructions=instructions)
        return self.make_call(parameters, parsed=False)

    def get_messages_history(self, user, section_id):
        last_messages =  Message.objects.select_related("related_message").filter( section_id=section_id,
                                                sender=Message.SenderChoices.user, user=user, ai_response__isnull=False).order_by("created_at")[:10]
        print(user,section_id, last_messages)
        if last_messages:
            return [{"user": message.content, "AI": getattr(message.ai_response, "content", "")} for message in last_messages]
        return []

    def get_similar_messages(self, query, user,  section_id):
        similar_messages = VectorStoreManager(Message().vector_store_name).get_similar_user_messages(query,user,  section_id)
        print(similar_messages)
        return [{"user": message.content, "AI": getattr(message.ai_response, "content", "")} for message in similar_messages]

    def construct_history_prompt(self, query, user, section_id):
        return (f"Those are the last 20 messages: {self.get_messages_history(user,section_id)} "
                f"and those messages may or not be relevant to our query: "
                f"{self.get_similar_messages(query, user,  section_id)}, Inform the user in case question is repeated and "
                f"that you are going to provide simpler more detailed answers.In case the last 20 messages array is empty that"
                f"means the question never had been asked before"
                f"if it is not clear what is the user referring to assume "
                f"he is asking about the last ai response.")

    def summarize(self, user_message, scope , documents):
        instructions = (f" summarize the following {scope}: {documents} taking into account the users request")
        parameters = self.build_parameters([user_message], instructions=instructions)
        return self.make_call(parameters, parsed=False)

    def translate(self, user_message, scope , documents, language):
        instructions = (f" translate the following {scope}: {documents}. if the user didn't specify a language to translate"
                        f"translate to {language}")
        parameters = self.build_parameters([user_message], instructions=instructions)
        return self.make_call(parameters, parsed=False)

    def explain_more(self, user_message, scope, documents):
        instructions = (f" explain more the following {scope}: {documents} taking into account the users request")
        parameters = self.build_parameters([user_message], instructions=instructions)
        return self.make_call(parameters, parsed=False)

    def get_subject_description(self, subject_title):

        message = (f"We need to add a new Subject into our educational app database and we need to fill the description"
                   f"field the Subject name is {subject_title}. Provide a short description of one or two phrases maximum ")

        parameters = self.build_parameters([message],
                                           structured_output=SubjectDescription)
        return self.make_call(parameters)





