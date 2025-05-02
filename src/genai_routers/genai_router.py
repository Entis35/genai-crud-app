import os
import json
from dotenv import load_dotenv
from typing import TypedDict

import openai
from langgraph.graph import StateGraph, START, END

from ..models import SessionLocal
from ..models.schemas import ItemSchema

from ..utils.crud_function import insert_item, get_all_items, get_one_item, update_item


# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI()

# Dependency to get the database session
def get_db():
    db = SessionLocal() # create a new session from session local
    try:
        yield db # yield session to the callers
    finally:
        db.close() # closed when it's done

# Define Graph State to store all the data in Dictionary format
class CrudState(TypedDict):
    user_input: str
    action: str
    item_id: int = None
    item: ItemSchema = None
    result: dict = None

# 2. Decision Node: Uses GPT-4 to determine CRUD action
def decide_crud_action(state: CrudState):
    """Determines CRUD action from user query using GPT-4 function calling."""

    print(f"\nUser input state: {state['user_input']}")
    if not state["user_input"]:  # Ensure key exists
        raise ValueError("Missing 'user_input' in state.")
        
    function_schema = {
        "name": "crud_action",
        "description": "Determines the CRUD operation",
        "parameters": {
            "type": "object",
            "properties": {
                "action": {"type": "string", "enum": ["insert", "get_one", "get_all", "update"]},
                "item_id": {"type": "integer", "nullable": True},
                "item": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string", "nullable": True}
                    },
                    "nullable": True
                }
            },
            "required": ["action"]
        }
    }

    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": state["user_input"]}],
        tools=[{"type": "function", "function": function_schema}],
        tool_choice="required"
    )

    if response.choices[0].message.tool_calls:
        arguments = json.loads(response.choices[0].message.tool_calls[0].function.arguments)
        # return GraphState(**arguments)
        state.update(arguments)  # Update state directly
        print(f"\nUpdated state after GenAI call: {state}")
        return state
    
    return None


# 3. Conditional edge function to route to the appropriate node
def route_decision(state: CrudState):
    # Return the node name you want to visit next
    if state["action"] == "insert":
        return "insert"
    elif state["action"] == "get_one":
        return "get_one"
    elif state["action"] == "get_all":
        return "get_all"
    elif state["action"] == "update":
        return "update"
        
# 4. Build LangGraph Workflow
def genai_router():
    graph = StateGraph(CrudState)

    # Decision node
    graph.add_node("decide_crud", decide_crud_action)

    # CRUD nodes
    # calling next(get_db()) will start the generator function get_db(), 
    # which will yield the database session (db). 
    # The next() function then retrieves that session object and hands it to the caller.
    graph.add_node("insert", lambda state: insert_item(state, next(get_db())))
    graph.add_node("get_one", lambda state: get_one_item(state, next(get_db())))
    graph.add_node("get_all", lambda state: get_all_items(state, next(get_db())))
    graph.add_node("update", lambda state: update_item(state, next(get_db())))

    # Routing based on decision
    graph.add_edge(START, "decide_crud")
    graph.add_conditional_edges(
    "decide_crud",
    route_decision,
        {  # Name returned by route_decision : Name of next node to visit
            "insert": "insert",
            "get_one": "get_one",
            "get_all": "get_all",
            "update": "update",
        },
    )
    
    # All nodes lead to END
    graph.add_edge("insert", END)
    graph.add_edge("get_one", END)
    graph.add_edge("get_all", END)
    graph.add_edge("update", END)

    return graph.compile()
