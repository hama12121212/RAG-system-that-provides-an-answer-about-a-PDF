import argparse
import os
import shutil
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from langchain.document_loaders.pdf import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from get_embedding_function import get_embedding_function
from langchain.vectorstores.chroma import Chroma
from io import BytesIO

CHROMA_PATH = "chroma"

app = FastAPI()


@app.post("/upload-pdf/")
async def upload_pdf(files: list[UploadFile] = File(...)):
    """
    Endpoint to upload PDF files and process them into chunks stored in Chroma DB.
    """
    pdf_paths = []
    for file in files:
        pdf_path = f"temp_{file.filename}"
        pdf_paths.append(pdf_path)
        with open(pdf_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

    try:
        # Process the uploaded PDFs
        documents = load_documents(pdf_paths)
        chunks = split_documents(documents)
        add_to_chroma(chunks)

        # Clean up temporary files
        for pdf_path in pdf_paths:
            os.remove(pdf_path)

        return JSONResponse(content={"message": "PDFs uploaded and processed successfully."}, status_code=200)
    
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)


@app.post("/reset-db/")
async def reset_db():
    """
    Endpoint to reset the Chroma DB.
    """
    try:
        clear_database()
        return JSONResponse(content={"message": "Database reset successfully."}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=500)


def load_documents(pdf_paths):
    documents = []
    for path in pdf_paths:
        document_loader = PyPDFLoader(path)
        documents.extend(document_loader.load())
    return documents


def split_documents(documents: list[Document]):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)


def add_to_chroma(chunks: list[Document]):
    # Load the existing database.
    db = Chroma(
        persist_directory=CHROMA_PATH, embedding_function=get_embedding_function()
    )

    # Calculate Page IDs.
    chunks_with_ids = calculate_chunk_ids(chunks)

    # Add or Update the documents.
    existing_items = db.get(include=[])  # IDs are always included by default
    existing_ids = set(existing_items["ids"])
    print(f"Number of existing documents in DB: {len(existing_ids)}")

    # Only add documents that don't exist in the DB.
    new_chunks = []
    for chunk in chunks_with_ids:
        if chunk.metadata["id"] not in existing_ids:
            new_chunks.append(chunk)

    if len(new_chunks):
        print(f"👉 Adding new documents: {len(new_chunks)}")
        new_chunk_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_chunk_ids)
        db.persist()
    else:
        print("✅ No new documents to add")


def calculate_chunk_ids(chunks):
    # Page Source : Page Number : Chunk Index
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page")
        current_page_id = f"{source}:{page}"

        # If the page ID is the same as the last one, increment the index.
        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        # Calculate the chunk ID.
        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id

        # Add it to the page meta-data.
        chunk.metadata["id"] = chunk_id

    return chunks


def clear_database():
    if os.path.exists(CHROMA_PATH):
        shutil.rmtree(CHROMA_PATH)


if __name__ == "__main__":
    
    pass
