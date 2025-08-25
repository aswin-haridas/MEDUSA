import asyncio
import chromadb
import ollama
import uvicorn
from fastapi import FastAPI, Response
from fastapi import WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

EMBEDDING_MODEL = 'nomic-embed-text'

# ChromaDB setup
client = chromadb.Client()
documents = client.get_or_create_collection(name="documents")

class TextRequest(BaseModel):
    text: str

class TextResponse(BaseModel):
    result: str

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173","https://stpg-ebon.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received via WebSocket: {data}")
            generate_response(data)
    except Exception as e:
        print(f"WebSocket connection closed: {e}")

def generate_response(collection, prompt_template: str, text: str):
    # Generate a new response
    prompt = prompt_template.format(text=text)
    response = ollama.generate(
        model='gemma3:1b',
        prompt=prompt
    )
    generated_text = response['response']
    return TextResponse(result=generated_text)  

@app.post("/thoughts", response_model=TextResponse)
def thoughts(request: TextRequest):
    return generate_response(
        documents,
        "Generate exactly 4 relevant search queries based on the following text:\n\n{text}\n\nEach query should be a clear, concise sentence, separated by a comma dont give any other text.",
        request.text
    )

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
