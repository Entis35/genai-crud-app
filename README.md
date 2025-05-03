# Genai CRUD Application

### Create .env file following the .env_template and set-up the API KEYs for LangSmith and OpenAI
- LANGSMITH_TRACING="true"
- LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
- LANGSMITH_API_KEY=""
- LANGSMITH_PROJECT="es-lang-crud"
- OPENAI_API_KEY = ""
- DATABASE_URL=sqlite:///./test.db

### Running the app
To run --> uvicorn app:app --reload   
For testing --> localhost:8000/docs

### A few input examples to run the app
- "insert product 1 with description grocery products"
- "insert product 2 with description diary products"
- "get all products"
- "get product 1"
- "update product 1 with updated product 1 and description updated grocery products"