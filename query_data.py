from fastapi import FastAPI, HTTPException
from langchain.vectorstores.chroma import Chroma
from langchain.prompts import ChatPromptTemplate
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
from get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

PROMPT_TEMPLATE = """
Answer the question based only on the following context:

{context}

---

Answer the question based on the above context: {question}
"""

app = FastAPI()


model_name = "gpt2" 
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Initialize the Hugging Face pipeline for text generation
hf_pipeline = pipeline("text-generation", model=model, tokenizer=tokenizer)

@app.post("/query-pdf/")
async def query_pdf(query_text: str):
    """
    Endpoint to query the Chroma DB with the provided query text.
    """
    try:
        response_text = query_rag(query_text)
        return {"response": response_text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")


def query_rag(query_text: str):
    # Prepare the DB.
    embedding_function = get_embedding_function()
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=embedding_function)

    # Search the DB.
    results = db.similarity_search_with_score(query_text, k=5)

    context_text = "\n\n---\n\n".join([doc.page_content for doc, _score in results])
    prompt_template = ChatPromptTemplate.from_template(PROMPT_TEMPLATE)
    prompt = prompt_template.format(context=context_text, question=query_text)

    # Generate response using Hugging Face model
    generated_output = hf_pipeline(prompt, max_length=200, num_return_sequences=1)
    response_text = generated_output[0]['generated_text']

    sources = [doc.metadata.get("id", None) for doc, _score in results]
    formatted_response = f"Response: {response_text}\nSources: {sources}"
    print(formatted_response)
    return response_text


if __name__ == "__main__":
    # Run the FastAPI server with: uvicorn <filename>:app --reload
    pass
