from langgraph.graph import StateGraph, START, END
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import os
from my_study_pal.ai_utilities.ai_agents import AIAgentClientManager, get_similar_chunks_data
from langchain_community.tools import TavilySearchResults

from my_study_pal.courses.models import Course, Section
from my_study_pal.users.models import User, UserInfo

TAVILY_API_KEY = os.environ.get('TAVILY_API_KEY')

@dataclass
class StudyPalState:
    user_input: str
    user_id: int
    course_id: int
    section_id: int
    user_info:Optional[ str] = None
    agent_manager:Optional[ AIAgentClientManager] =None
    translation_language: Optional[str] = None
    course_has_docs: bool = True
    relevant: Optional[bool] = None
    question_scope: Optional[str] = None
    question_action: str = None
    retrieved_docs: List[Any] = field(default_factory=list)
    llm_response: Optional[str] = None
    retrieval_mode: str = "llm"




def input_node(state: StudyPalState) -> StudyPalState:
    """
    Normalize input and enrich state with metadata (like course_has_docs).
    """
    state.user_input = state.user_input.strip()
    user=User.objects.get(id=state.user_id)
    user_info:UserInfo = user.user_info
    state.user_info =  (f"the user is {user.username} from {user_info.country}, {user_info.age} years old studies at "
                        f"{user_info.current_year} at {user_info.academic_level} at {user_info.institution_name}")
    ai_model = user.settings.ai_model
    state.agent_manager= AIAgentClientManager(ai_agent=ai_model)
    state.course_has_docs = bool(getattr(Course.objects.get(id=state.course_id),"document", ""))
    state.translation_language = user.settings.translation_language
    print(f"[input_node] user_input='{state.user_input}', has_docs={state.course_has_docs}")
    return state


def determine_scope_node(state:StudyPalState):
    """
    Decide if question is about the section, the whole course, or irrelevant.
    """
    user = User.objects.get(id=state.user_id)
    user_query = state.user_input.lower()
    course = Course.objects.get(id=state.course_id)
    response = state.agent_manager.get_question_scope(course=course, user_query=user_query)
    state.relevant = response['relevant']
    state.question_scope = response['question_scope']
    state.question_action = response['question_action']
    print(f"[determine_scope_node] scope={state.question_scope}, relevant={state.relevant}, question_action={state.question_action}")
    return state


def decide_retrieval_node(state:StudyPalState):
    """
    Decide whether retrieval is needed, and what type (local/web).
    """
    if state.course_has_docs:
        if state.question_scope=="section":
            state.retrieved_docs = [chunk.content for chunk in Section.objects.get(id=state.section_id).chunks.all()]
        elif state.question_scope == "similarity_search":
            document_id= Course.objects.get(id=state.course_id).document.id
            state.retrieved_docs = get_similar_chunks_data(state.user_input, document_id=document_id,
                                                           section_id=state.section_id)
        else:
            #TODO work with summaries here
            state.retrieved_docs =  [chunk.content for section in Course.objects.get(id=state.course_id).sections.all()
                                     for chunk in  section.chunks.all()]

    if state.question_action in ["respond", "explain_more"]:
        response=state.agent_manager.get_retrieval_mode(state.retrieved_docs,state.user_input)
        state.retrieval_mode = response['retrieval_mode']
    print(f"[decide_retrieval_node] retrieval_mode={state.retrieval_mode}")

    return state



def llm_answer_node(state:StudyPalState):
    """
    Compose final prompt and call LLM
    """
    if not state.relevant:
        state.llm_response = ("Sorry the question you asked is not part of the scope of the current course."
                              "please refer to the course corresponding to it or create a new one if not existant")
        return state
    if state.question_action == "summarize":
        response = state.agent_manager.summarize(state.user_input, state.question_scope, state.retrieved_docs)
    elif state.question_action == "translate":
        response = state.agent_manager.translate(state.user_input, state.question_scope,state.retrieved_docs,
                                                 state.translation_language)
    elif state.question_action == "explain_more":
        response = state.agent_manager.explain_more(state.user_input, state.question_scope, state.retrieved_docs)
    else:
        user= User.objects.get(id=state.user_id)
        response = state.agent_manager.get_response_based_on_documents(state.user_input,user, state.retrieved_docs,
                                                                       state.retrieval_mode, state.section_id)
    state.llm_response = response
    return state


def web_search_node(state):
    search = TavilySearchResults(api_key=TAVILY_API_KEY)

    query = state.user_input
    results = search.invoke(query)
    print(results)

    formatted_results = [
        {"content": r.get("content", ""), "source": r.get("url", "")}
        for r in results
    ]
    state.retrieved_docs = formatted_results

    print(f"[web_search_node] Retrieved {len(results)} web results.")
    return state



graph = StateGraph(StudyPalState)

# Add nodes
graph.add_node("input", input_node)
graph.add_node("determine_scope", determine_scope_node)
graph.add_node("decide_retrieval", decide_retrieval_node)
graph.add_node("web_search", web_search_node)
graph.add_node("llm_answer", llm_answer_node)

## Start flow
graph.add_edge("input", "determine_scope")

# Determine if question is relevant
graph.add_conditional_edges(
    "determine_scope",
    lambda s: "irrelevant" if (s.relevant is False) else "relevant",
    {
        "irrelevant": "llm_answer",
        "relevant": "decide_retrieval",
    },
)

# Decide what to do next (retrieve, web, or direct answer)
graph.add_conditional_edges(
    "decide_retrieval",
    lambda s: s.retrieval_mode,
    {
        "retrieval": "llm_answer",
        "web": "web_search",
        "llm": "llm_answer",
    },
)

# Web search → LLM
graph.add_edge("web_search", "llm_answer")

# Entry & finish points
graph.set_entry_point("input")
graph.set_finish_point("llm_answer")

study_pal_graph = graph.compile()


