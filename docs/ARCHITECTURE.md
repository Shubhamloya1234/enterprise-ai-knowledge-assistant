\# System Architecture — Enterprise AI Knowledge Assistant



\## 1. Overview



The Enterprise AI Knowledge Assistant is a full-stack application combining a React frontend, FastAPI backend, persistent application data, Retrieval-Augmented Generation (RAG), and agent-based tool execution.



The backend is organized into modular components to separate API handling, business logic, authentication, data access, document retrieval, and AI execution.



\## 2. Technology Stack



| Component | Technology |

|---|---|

| Frontend | React |

| Frontend build tool | Vite |

| Backend framework | FastAPI |

| Programming language | Python |

| ORM | SQLAlchemy |

| Database migrations | Alembic |

| Vector database | ChromaDB |

| Embedding model | Sentence Transformers |

| Embedding model name | all-MiniLM-L6-v2 |

| LLM runtime | Ollama |

| Language model | Qwen 2.5 (1.5B) |

| Testing | Pytest |



\## 3. High-Level Architecture



```mermaid

flowchart TB

&#x20;   USER\[User]

&#x20;   FRONTEND\[React Frontend]

&#x20;   API\[FastAPI Application]



&#x20;   CORE\[Core and Security]

&#x20;   ROUTES\[API Routes]

&#x20;   SERVICES\[Services]

&#x20;   DB\[(Application Database)]



&#x20;   RAG\[RAG Engine]

&#x20;   VECTOR\[(ChromaDB)]

&#x20;   EMB\[Embedding Model]

&#x20;   LLM\[Ollama LLM]



&#x20;   AGENTS\[Agent Execution]

&#x20;   TOOLS\[Tool Registry and Tools]



&#x20;   USER --> FRONTEND

&#x20;   FRONTEND --> API



&#x20;   API --> ROUTES

&#x20;   API --> CORE



&#x20;   ROUTES --> SERVICES

&#x20;   ROUTES --> DB



&#x20;   ROUTES --> RAG

&#x20;   RAG --> EMB

&#x20;   EMB --> VECTOR

&#x20;   RAG --> LLM



&#x20;   ROUTES --> AGENTS

&#x20;   AGENTS --> TOOLS

&#x20;   AGENTS --> LLM

```



\## 4. Backend Architecture



The backend source code is organized under `backend/app`.



\### 4.1 Application Entry Point



\*\*Location:\*\* `backend/app/main.py`



Responsibilities:

\- Initialize the FastAPI application.

\- Register application routes.

\- Provide the backend application entry point.



\### 4.2 API Layer



\*\*Location:\*\* `backend/app/api/`



| Module | Responsibility indicated by module name |

|---|---|

| `auth.py` | Authentication endpoints |

| `users.py` | User-related endpoints |

| `documents.py` | Document management endpoints |

| `rag.py` | RAG-related endpoints |

| `conversations.py` | Conversation management |

| `agent.py` | Agent execution endpoints |

| `protected.py` | Protected API endpoints |

| `rbac.py` | Role-based access control endpoints |



This layer exposes application functionality through HTTP endpoints.



\### 4.3 Core Layer



\*\*Location:\*\* `backend/app/core/`



| Module | Responsibility |

|---|---|

| `config.py` | Application configuration |

| `dependencies.py` | Shared FastAPI dependencies |

| `security.py` | Security and authentication utilities |



This layer contains shared application infrastructure.



\### 4.4 Database Layer



\*\*Location:\*\* `backend/app/db/`



\- `database.py`: Database connection and session infrastructure.



\*\*Models:\*\* `backend/app/models/`



| Model | Domain |

|---|---|

| `user.py` | Users |

| `conversation.py` | Conversations |

| `message.py` | Messages |

| `employee.py` | Employees |

| `department.py` | Departments |

| `task.py` | Tasks |



These modules define the application's data model. Exact relationships and database constraints should be verified against the model definitions.



\### 4.5 RAG Layer



\*\*Location:\*\* `backend/app/rag/`



| Module | Responsibility indicated by module name |

|---|---|

| `loader.py` | Document loading |

| `chunker.py` | Text chunking |

| `embeddings.py` | Embedding generation |

| `ingestion.py` | Document ingestion |

| `vector\_store.py` | Vector storage |

| `knowledge\_base.py` | Knowledge base operations |

| `retriever.py` | Relevant content retrieval |

| `llm.py` | Language model integration |

| `rag\_pipeline.py` | RAG workflow orchestration |



\#### RAG processing flow



```mermaid

flowchart TD

&#x20;   A\[Document Upload]

&#x20;   B\[Document Loader]

&#x20;   C\[Text Chunking]

&#x20;   D\[Embedding Generation]

&#x20;   E\[(ChromaDB)]

&#x20;   F\[User Question]

&#x20;   G\[Retriever]

&#x20;   H\[Relevant Document Chunks]

&#x20;   I\[LLM]

&#x20;   J\[Generated Answer]



&#x20;   A --> B

&#x20;   B --> C

&#x20;   C --> D

&#x20;   D --> E



&#x20;   F --> G

&#x20;   E --> G

&#x20;   G --> H

&#x20;   H --> I

&#x20;   I --> J

```



The diagram represents the intended document-ingestion and retrieval responsibilities suggested by the RAG modules. Exact invocation order, filtering, and persistence behavior should be confirmed in the implementation.



\### 4.6 Agent Architecture



\*\*Location:\*\* `backend/app/agents/`



| Module | Responsibility indicated by module name |

|---|---|

| `agent.py` | Agent implementation |

| `executor.py` | Execution logic |

| `multi\_executor.py` | Multi-agent execution |

| `router.py` | Agent routing |

| `validator.py` | Validation |

| `response\_generator.py` | Response generation |



The agent layer separates AI execution and orchestration from the API layer.



\### 4.7 Tool Architecture



\*\*Location:\*\* `backend/app/tools/`



| Module | Responsibility |

|---|---|

| `calculator\_tool.py` | Calculator functionality |

| `employee\_tool.py` | Employee-related operations |

| `rag\_tool.py` | RAG functionality exposed as a tool |

| `registry.py` | Tool registry |

| `schemas.py` | Tool schemas |

| `schema\_registry.py` | Schema registry |



Tools provide modular capabilities that can be used by the agent execution system.



\### 4.8 Services and Schemas



\*\*Services:\*\* `backend/app/services/`



\- `memory\_service.py`: Memory-related service functionality.



\*\*Schemas:\*\* `backend/app/schemas/`



\- `auth.py`: Authentication-related schemas.

\- `memory.py`: Memory-related schemas.



These components separate service logic and data validation structures from HTTP route definitions.



\## 5. Frontend Architecture



The frontend is maintained separately under the `frontend/` directory.



It is built with React and Vite.



Its responsibilities include:

\- User interaction.

\- Authentication interface.

\- Document upload interface.

\- Chat and question-answering interface.

\- Displaying generated responses and source references.

\- Communicating with FastAPI endpoints.



Detailed component-level architecture should be documented separately after reviewing the frontend source structure.



\## 6. Main Application Workflows



\### Workflow A: Authentication



1\. User interacts with the frontend authentication interface.

2\. Authentication requests reach the backend API.

3\. Security utilities and dependencies support protected operations.

4\. User-related information is handled through the application data layer.



Exact token lifecycle and authorization checks should be verified in the security implementation.



\### Workflow B: Document Question Answering



1\. User uploads a document.

2\. Document processing components load and prepare its content.

3\. Content is divided into chunks.

4\. Embeddings are generated.

5\. Vector representations are stored in ChromaDB.

6\. A user submits a question.

7\. The retrieval component searches for relevant content.

8\. The language model generates a response.

9\. The application returns the answer and available source references.



\### Workflow C: Agent Tool Execution



1\. A request reaches the agent API.

2\. Agent routing and execution components handle the request.

3\. The agent execution system can interact with registered tools.

4\. Available tool modules include calculator, employee, and RAG tools.

5\. The response generation component contributes to producing the result.



Exact routing and execution rules should be verified in the agent implementation.



\## 7. Security Architecture



Security-related modules are located in:



\- `core/security.py`

\- `core/dependencies.py`

\- `api/auth.py`

\- `api/protected.py`

\- `api/rbac.py`



The application includes authentication and role-based access control functionality.



Production deployment should additionally verify:

\- Token expiration and validation.

\- Password hashing.

\- Role and permission enforcement.

\- Input validation.

\- File upload restrictions.

\- Secret management.

\- Database access controls.



\## 8. Testing



The backend uses Pytest.



Latest reported development test result:



\- 120 passed.

\- 0 failed.

\- 4 non-blocking warnings.



Frontend linting and build checks were also reported as passing during development.



\## 9. Architectural Design Principles



The backend structure reflects the following design goals:



1\. Separation of concerns.

2\. Modular API organization.

3\. Reusable security infrastructure.

4\. Separation of data models and API schemas.

5\. Independent RAG processing components.

6\. Modular agent and tool execution.

7\. Testable backend functionality.



\## 10. Future Architecture Improvements



Potential improvements include:



\- Multi-tenant knowledge base isolation.

\- Hybrid search and reranking.

\- Background document ingestion.

\- Asynchronous task processing.

\- Centralized observability.

\- Production deployment automation.

\- API rate limiting.

\- RAG evaluation and quality metrics.

\- More granular permissions.



\---



\*\*Repository:\*\* https://github.com/Shubhamloya1234/enterprise-ai-knowledge-assistant



