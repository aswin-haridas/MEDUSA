import asyncio
import chromadb
import ollama
import uvicorn
from fastapi import FastAPI, Response
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

def generate_response(collection, prompt_template: str, text: str):
    # Generate a new response
    prompt = prompt_template.format(text=text)
    response = ollama.generate(
        model='gemma3:1b',
        prompt=prompt
    )
    generated_text = response['response']
    return TextResponse(result=generated_text)


@app.post("/summarize", response_model=TextResponse)
def summarize(request: TextRequest):
    return generate_response(
        documents,
        "Please summarize the following text: \n\n{text}. try to  return a 1-liner",
        request.text
    )

@app.post("/expand", response_model=TextResponse)
def expand(request: TextRequest):
    return generate_response(
        documents,
        "Please expand the following text with examples: \n\n{text}",
        request.text
    )


@app.post("/shorten", response_model=TextResponse)
def shorten(request: TextRequest):
    return generate_response(
        documents,
        "Please shorten the following text: \n\n{text}. It should compress to a tweet-length.",
        request.text
    )

@app.post("/thoughts", response_model=TextResponse)
def thoughts(request: TextRequest):
    return generate_response(
        documents,
        "Generate exactly 4 relevant search queries based on the following text:\n\n{text}\n\nEach query should be a clear, concise sentence, separated by a comma dont give any other text.",
        request.text
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
