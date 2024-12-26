# RAG-system-that-provides-an-answer-about-a-PDF
1. **AI Framework Module**  
   - **Technologies Used**:  
     - LangChain  
   - **Purpose**:  
     - Handles document loading, splitting, embedding generation, and database interactions.  
   - **Key Components**:  
     - **Document Loader**: Leverages the `PyPDFDirectoryLoader` from LangChain to load and parse PDF files.  
     - **Text Splitter**: Uses the `RecursiveCharacterTextSplitter` to divide documents into smaller chunks for embedding.  
     - **Vector Store**: Implements Chroma as the vector database to store and retrieve document embeddings.

2. **GenAI Module**  
   - **Technologies Used**:  
     - OLLama: Provides the LLM (Mistral) to generate responses based on retrieved document chunks.  
   - **Purpose**:  
     - Generates embeddings for document chunks and produces natural language responses based on the retrieved context.  
   - **Key Components**:  
     - **OllamaEmbeddings**: Used to generate embeddings when querying documents.  
     - **LLM Integration**: The Mistral model from Ollama processes the retrieved context and generates responses.

3. **Backend Module**  
   - **Technology Used**:  
     - FastAPI
