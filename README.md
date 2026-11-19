\# Enterprise AI Knowledge Assistant



An AI-powered enterprise knowledge assistant that enables users to upload documents, ask questions in natural language, retrieve relevant information using Retrieval-Augmented Generation (RAG), and interact with an AI agent capable of executing tools.



\## Overview



The Enterprise AI Knowledge Assistant combines document retrieval, large language models, and a web application to make organizational knowledge easier to access.



Users can upload documents, ask questions about their content, receive context-aware answers with source references, and maintain persistent conversations.



\## Key Features



\- \*\*Document upload:\*\* Upload documents to build a searchable knowledge base.

\- \*\*Retrieval-Augmented Generation (RAG):\*\* Retrieve relevant document chunks and use them as context for answers.

\- \*\*Semantic search:\*\* Generate embeddings using Sentence Transformers and store vectors in ChromaDB.

\- \*\*Source references:\*\* Display source filenames and relevant document chunks.

\- \*\*AI-powered question answering:\*\* Use Ollama with Qwen 2.5 (1.5B) as the local language model.

\- \*\*Conversation persistence:\*\* Maintain conversations and their history.

\- \*\*Multi-agent execution:\*\* Support agent-based tool execution.

\- \*\*Calculator tool:\*\* Allow the agent to execute calculator operations.

\- \*\*Authentication and authorization:\*\* Support protected APIs and role-based access control.

\- \*\*REST API:\*\* Expose backend functionality through FastAPI.



\## Technology Stack



| Layer | Technologies |

|---|---|

| Frontend | React, Vite |

| Backend | Python, FastAPI |

| Database / ORM | SQLAlchemy |

| Database migrations | Alembic |

| Vector database | ChromaDB |

| Embeddings | Sentence Transformers |

| Embedding model | all-MiniLM-L6-v2 |

| LLM runtime | Ollama |

| Language model | Qwen 2.5 (1.5B) |

| API documentation | FastAPI / Swagger UI |

| Testing | Pytest |



\## Architecture



```mermaid

flowchart TB

&#x20;   U\[User] --> F\[React Frontend]

&#x20;   F --> API\[FastAPI Backend]



&#x20;   API --> AUTH\[Authentication and RBAC]

&#x20;   API --> DOC\[Document Upload]

&#x20;   API --> CHAT\[Chat and Conversation APIs]



&#x20;   DOC --> EMB\[Sentence Transformer Embeddings]

&#x20;   EMB --> VDB\[(ChromaDB)]



&#x20;   CHAT --> RET\[Document Retrieval]

&#x20;   RET --> VDB

&#x20;   RET --> LLM\[Ollama - Qwen 2.5]

&#x20;   LLM --> ANS\[Context-aware Answer]

&#x20;   ANS --> SRC\[Source References]

&#x20;   SRC --> F



&#x20;   CHAT --> AG\[Multi-Agent Tool Execution]

&#x20;   AG --> CALC\[Calculator Tool]

&#x20;   AG --> LLM



&#x20;   API --> DB\[(Application Database)]

```



\## RAG Pipeline



The document question-answering workflow follows these stages:



1\. \*\*Document ingestion:\*\* A user uploads a document.

2\. \*\*Text extraction:\*\* The backend extracts document content.

3\. \*\*Chunking:\*\* Content is divided into smaller chunks.

4\. \*\*Embedding generation:\*\* Sentence Transformers converts chunks into vector representations.

5\. \*\*Vector storage:\*\* Chunks and embeddings are stored in ChromaDB.

6\. \*\*User query:\*\* A user asks a question through the React interface.

7\. \*\*Semantic retrieval:\*\* Relevant chunks are retrieved from the vector database.

8\. \*\*Context construction:\*\* Retrieved information is provided to the language model.

9\. \*\*Answer generation:\*\* Ollama generates a response using the retrieved context.

10\. \*\*Source attribution:\*\* The application returns source information alongside the answer.



\## Local Development Setup



\### Prerequisites



\- Python 3.13

\- Node.js and npm

\- Ollama

\- Git



\### 1. Clone the repository



```powershell

git clone https://github.com/Shubhamloya1234/enterprise-ai-knowledge-assistant.git

cd enterprise-ai-knowledge-assistant

```



\### 2. Set up the backend



```powershell

py -3.13 -m venv .venv313

.\\.venv313\\Scripts\\Activate.ps1

```



Set the backend module path:



```powershell

$env:PYTHONPATH = "$PWD\\backend"

```



Install the backend dependencies using the requirements file in the repository. Confirm its exact path before running the installation command.



Start the backend:



```powershell

uvicorn app.main:app --reload

```



\### 3. Set up the frontend



Open another PowerShell terminal:



```powershell

cd frontend

npm install

npm run dev

```



\### 4. Configure Ollama



Install Ollama and make sure the configured model is available locally.



The project uses:



```powershell

ollama pull qwen2.5:1.5b

```



Ensure the backend's Ollama configuration matches the model and local Ollama service.



\### 5. Access the application



| Component | Local URL |

|---|---|

| React frontend | http://localhost:5173 |

| FastAPI backend | http://127.0.0.1:8000 |

| Swagger API documentation | http://127.0.0.1:8000/docs |



\*\*Configuration note:\*\* Set up the required environment variables using the project's example configuration or existing application settings. Never commit real API keys, passwords, database credentials, or secret keys.



\## Testing



The backend test suite was executed during development.



\*\*Latest reported result:\*\*



\- 120 tests passed

\- 0 tests failed

\- 4 non-blocking warnings



Run the test suite with:



```powershell

pytest -v

```



\## Security Considerations



\- Keep secrets and environment files out of version control.

\- Use authentication for protected endpoints.

\- Apply role-based authorization to restricted operations.

\- Validate uploaded documents and user inputs.

\- Configure production secrets through environment variables.

\- Restrict access to the vector database and application database.

\- Use HTTPS and appropriate deployment security controls in production.



\## Production Deployment



The project has been tested locally. Before production deployment, the following should be configured and verified:



\- Production database and migrations.

\- Persistent vector database storage.

\- Secure environment and secret management.

\- Production frontend build and hosting.

\- Backend hosting and process management.

\- Authentication, authorization, and rate limiting.

\- Logging, monitoring, and error tracking.

\- Document storage backups and recovery.

\- HTTPS and CORS configuration.



\## Future Improvements



\- Support additional document formats and ingestion pipelines.

\- Add more enterprise integrations.

\- Introduce advanced agent orchestration.

\- Improve retrieval quality with hybrid search and reranking.

\- Add evaluation metrics for RAG answer quality.

\- Introduce scalable multi-tenant knowledge bases.

\- Add production deployment and monitoring automation.



\## Project Repository



\[GitHub – Enterprise AI Knowledge Assistant](https://github.com/Shubhamloya1234/enterprise-ai-knowledge-assistant)



\---



\*\*Built with:\*\* Python · FastAPI · React · ChromaDB · Sentence Transformers · Ollama



