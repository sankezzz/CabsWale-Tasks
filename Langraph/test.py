

from typing import Annotated, Sequence, TypedDict
from langgraph.graph import StateGraph
from langgraph.graph.message import add_messages
from langchain_google_genai import ChatGoogleGenerativeAI

class AgentState(TypedDict):
    messages: Annotated[Sequence, add_messages]

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash"
)

def chatbot(state: AgentState):
    # Pass all messages
    response = llm.invoke(state["messages"])
    # Append model reply to state
    return {"messages": state["messages"] + [response]}

graph = StateGraph(AgentState)
graph.add_node("chat", chatbot)
graph.set_entry_point("chat")
graph.set_finish_point("chat")
compiled_graph = graph.compile()

from langchain_core.messages import HumanMessage

output = compiled_graph.invoke({"messages": [HumanMessage(content="Hello!") ]})
print(output)
