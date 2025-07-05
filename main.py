import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import ollama
import chromadb
import uuid

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
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)   

def generateResponse(collection, prompt_template: str, text: str):
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
    return generateResponse(
        documents,
        "Please summarize the following text: \n\n{text}. try to  return a 1-liner",
        request.text
    )

@app.post("/expand", response_model=TextResponse)
def expand(request: TextRequest):
    
    return generateResponse(
        documents,
        "Please expand the following text with examples: \n\n{text}",
        request.text
    )


@app.post("/shorten", response_model=TextResponse)
def shorten(request: TextRequest):
    return generateResponse(
        documents,
        "Please shorten the following text: \n\n{text}. It should compress to a tweet-length.",
        request.text
    )


if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
