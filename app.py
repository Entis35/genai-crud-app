import os
from fastapi import FastAPI
from langsmith import traceable
from dotenv import load_dotenv
from pydantic import BaseModel

from src.genai_routers.genai_router import CrudState, genai_router


app = FastAPI()

# Load environment variables from .env
load_dotenv()

# GenAI Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# LangSmith Key for debugging the processes
LANGSMITH_TRACING = os.getenv("LANGSMITH_TRACING", "true")  # Default to "true" if not set
LANGSMITH_API_KEY = os.getenv("LANGSMITH_API_KEY")

# User input
class CrudInput(BaseModel):
    user_query: str

# Initiate the process
initial_state = CrudState()    # store user input and other data
router = genai_router()   # act as the Router function
 
@app.post("/crud/")
@traceable
async def handle_crud(input: CrudInput):
    """CRUD operations using GenAI"""
    initial_state = {"user_input": input.user_query}
    final_state = router.invoke(initial_state) # route into insert, get, update functions
    print(f"\nFinal state returned: {final_state}")
    return final_state["result"] # get the results in dict format

# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
    
# to run : uvicorn app:app --reload   
# For testing
# localhost:8000/docs