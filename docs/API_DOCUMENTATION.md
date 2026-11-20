\# API Documentation — AI Enterprise Assistant



\*\*API Name:\*\* AI Enterprise Assistant  

\*\*Version:\*\* 1.0.0  

\*\*Framework:\*\* FastAPI



\## 1. Overview



The AI Enterprise Assistant API provides endpoints for:



\- User authentication using JWT bearer tokens

\- Role-based access control (RBAC)

\- User management

\- Document upload, indexing, listing, and deletion

\- Retrieval-Augmented Generation (RAG) question answering

\- AI agent execution and tool calling

\- Conversation and message persistence

\- Health monitoring



\## 2. Base Configuration



For local development, the backend API is assumed to run at:



`http://127.0.0.1:8000`



Interactive API documentation is available through FastAPI's default documentation routes:



\- Swagger UI: `/docs`

\- ReDoc: `/redoc`

\- OpenAPI schema: `/openapi.json`



\## 3. Authentication



Protected endpoints use the application's authentication dependencies.



\### Login



`POST /auth/login`



Authenticates a user and returns an access token.



\*\*Request body:\*\*



```json

{

&#x20; "username": "admin",

&#x20; "password": "your-password"

}

```



\*\*Successful response:\*\*



```json

{

&#x20; "access\_token": "JWT\_ACCESS\_TOKEN",

&#x20; "token\_type": "bearer"

}

```



\*\*Error response:\*\*



\- `401 Unauthorized` — Invalid username or password.



\### Authorization header



For authenticated endpoints, include:



```http

Authorization: Bearer YOUR\_ACCESS\_TOKEN

```



The actual token validation and expiration configuration are defined in the application's security and dependency modules.



\## 4. API Endpoints



\### 4.1 General



| Method | Endpoint | Description | Authentication |

|---|---|---|---|

| GET | `/` | API welcome message | No |

| GET | `/health` | Health status | No |



\### 4.2 Authentication



| Method | Endpoint | Description | Authentication |

|---|---|---|---|

| POST | `/auth/login` | Authenticate and generate an access token | No |



\### 4.3 Protected Profile



| Method | Endpoint | Description | Authentication |

|---|---|---|---|

| GET | `/protected/profile` | Retrieve authenticated user's ID and role | Yes |



\*\*Example response:\*\*



```json

{

&#x20; "message": "You are authenticated",

&#x20; "user\_id": 1,

&#x20; "role": "ADMIN"

}

```



\### 4.4 Role-Based Access Control



| Method | Endpoint | Required Role |

|---|---|---|

| GET | `/rbac/admin` | ADMIN |

| GET | `/rbac/manager` | MANAGER |

| GET | `/rbac/employee` | EMPLOYEE |



These endpoints demonstrate role-specific authorization.



\### 4.5 User Management



All user-management endpoints require the ADMIN role.



| Method | Endpoint | Description |

|---|---|---|

| POST | `/users/` | Create a user |

| GET | `/users/` | Retrieve all users |



\*\*Create user — POST `/users/`\*\*



The parameters are declared as individual function arguments in FastAPI, so they are query parameters.



Example:



`POST /users/?username=john\&email=john@example.com\&password=your-password\&role=EMPLOYEE`



Supported roles:



\- `ADMIN`

\- `MANAGER`

\- `EMPLOYEE`



\*\*Successful response:\*\*



```json

{

&#x20; "message": "User created successfully",

&#x20; "user\_id": 2,

&#x20; "username": "john",

&#x20; "role": "EMPLOYEE"

}

```



\*\*Possible errors:\*\*



\- `400 Bad Request` — Invalid role.

\- `400 Bad Request` — Username already exists.



\*\*List users — GET `/users/`\*\*



Returns user IDs, usernames, email addresses, and roles.



\### 4.6 Document Management



All document-management endpoints require the ADMIN role.



| Method | Endpoint | Description |

|---|---|---|

| POST | `/documents/upload` | Upload and index a document |

| GET | `/documents/` | List uploaded documents |

| DELETE | `/documents/{filename}` | Delete a document and its indexed chunks |



\*\*Supported upload formats:\*\*



\- PDF (`.pdf`)

\- Text (`.txt`)



\*\*Maximum file size:\*\* 10 MB.



\*\*Upload — POST `/documents/upload`\*\*



Content type:



`multipart/form-data`



Form field:



`file` — Document to upload.



\*\*Successful response:\*\*



```json

{

&#x20; "message": "Document uploaded and indexed successfully",

&#x20; "filename": "company-policy.pdf",

&#x20; "chunks": 15

}

```



\*\*Possible errors:\*\*



\- `400 Bad Request` — Invalid filename or unsupported extension.

\- `409 Conflict` — Document already exists or is already indexed.

\- `413 Payload Too Large` — File exceeds 10 MB.

\- `500 Internal Server Error` — Document ingestion failed.



\*\*List documents — GET `/documents/`\*\*



Returns a sorted list of supported uploaded files and their count.



\*\*Delete document — DELETE `/documents/{filename}`\*\*



Deletes the document from storage and removes its indexed chunks.



Possible error:



\- `404 Not Found` — Document does not exist.



\### 4.7 Retrieval-Augmented Generation (RAG)



| Method | Endpoint | Description | Authentication |

|---|---|---|---|

| POST | `/rag/ask` | Ask a question against the knowledge base | Yes |



\*\*Request body:\*\*



```json

{

&#x20; "question": "What is the company leave policy?",

&#x20; "top\_k": 3,

&#x20; "source": "company-policy.pdf"

}

```



\*\*Request parameters:\*\*



| Field | Type | Default | Constraints |

|---|---|---|---|

| question | String | Required | 1–4000 characters |

| top\_k | Integer | 3 | 1–10 |

| source | String or null | null | Maximum 255 characters |



The `source` field can be used to restrict retrieval to a particular source document.



The endpoint calls the RAG pipeline's `ask\_question()` function.



The exact response structure is determined by that function.



\### 4.8 AI Agent



| Method | Endpoint | Description | Authentication |

|---|---|---|---|

| POST | `/agent/ask` | Execute an AI agent request within a conversation | Yes |



\*\*Request body:\*\*



```json

{

&#x20; "question": "Calculate the total of 250 and 350",

&#x20; "conversation\_id": 1

}

```



\*\*Request fields:\*\*



| Field | Type | Required |

|---|---|---|

| question | String | Yes |

| conversation\_id | Integer | Yes |



\*\*Successful response structure:\*\*



```json

{

&#x20; "conversation\_id": 1,

&#x20; "question": "Calculate the total of 250 and 350",

&#x20; "answer": "600",

&#x20; "intent": "calculation",

&#x20; "tool": "calculator",

&#x20; "tool\_result": {}

}

```



The values shown are illustrative. Actual intent, tool, answer, and tool result depend on agent execution.



The endpoint:



1\. Retrieves the conversation history.

2\. Verifies that the conversation belongs to the authenticated user.

3\. Saves the user's message.

4\. Executes the AI agent.

5\. Extracts any RAG sources from the tool result.

6\. Saves the assistant response and sources.

7\. Updates the conversation timestamp.

8\. Commits the database transaction.



\*\*Possible error:\*\*



\- `404 Not Found` — Conversation not found.



\### 4.9 Conversation Management



All conversation endpoints require authentication.



| Method | Endpoint | Description |

|---|---|---|

| POST | `/conversations/` | Create a conversation |

| GET | `/conversations/` | List the authenticated user's conversations |

| GET | `/conversations/{conversation\_id}` | Retrieve a conversation and its messages |

| POST | `/conversations/{conversation\_id}/messages` | Add a user message |

| DELETE | `/conversations/{conversation\_id}` | Delete a conversation |



\*\*Create conversation — POST `/conversations/`\*\*



Uses the `ConversationCreate` request schema.



\*\*List conversations — GET `/conversations/`\*\*



Returns conversations belonging to the authenticated user, ordered by descending conversation ID.



\*\*Get conversation — GET `/conversations/{conversation\_id}`\*\*



Returns conversation information and its messages.



\*\*Add message — POST `/conversations/{conversation\_id}/messages`\*\*



Uses the `MessageCreate` request schema.



Clients can only submit messages with the role `user`.



Possible errors:



\- `400 Bad Request` — Clients can only submit user messages.

\- `404 Not Found` — Conversation not found.



\*\*Delete conversation — DELETE `/conversations/{conversation\_id}`\*\*



Deletes the specified conversation belonging to the authenticated user.



Successful response:



```json

{

&#x20; "message": "Conversation deleted successfully"

}

```



\## 5. Role and Permission Summary



The following permissions are explicitly enforced by the route dependencies:



| Feature | ADMIN | MANAGER | EMPLOYEE |

|---|---|---|---|

| Admin RBAC endpoint | Yes | No | No |

| Manager RBAC endpoint | No | Yes | No |

| Employee RBAC endpoint | No | No | Yes |

| Create users | Yes | No | No |

| List users | Yes | No | No |

| Upload documents | Yes | No | No |

| List documents | Yes | No | No |

| Delete documents | Yes | No | No |



Authenticated endpoints that use `get\_current\_user` or `get\_current\_user\_record` require a valid authenticated user. Their additional role restrictions are not specified in the route definitions.



\## 6. Error Handling



The following HTTP errors are explicitly raised by the route handlers:



| Status | Meaning |

|---|---|

| 400 | Invalid input or unsupported message role |

| 401 | Invalid login credentials |

| 404 | Conversation or document not found |

| 409 | Duplicate document |

| 413 | Document exceeds the maximum size |

| 500 | Document ingestion failure |



FastAPI also performs request validation and may return `422 Unprocessable Entity` for invalid request parameters or bodies.



\## 7. CORS Configuration



The backend currently allows these frontend origins:



\- `http://localhost:5173`

\- `http://127.0.0.1:5173`



The configured CORS middleware allows credentials, all HTTP methods, and all headers.



These origins are configured for local development and should be reviewed before production deployment.



\## 8. API Architecture



The API is organized into separate router modules:



| Module | Responsibility |

|---|---|

| `auth.py` | Authentication |

| `protected.py` | Authenticated profile |

| `rbac.py` | Role-based authorization |

| `users.py` | User administration |

| `documents.py` | Document lifecycle |

| `rag.py` | Knowledge-base question answering |

| `agent.py` | AI agent execution |

| `conversations.py` | Conversation and message persistence |



All routers are registered in `backend/app/main.py`.



\## 9. API Testing



The endpoints can be tested using:



\- Swagger UI (`/docs`)

\- Postman

\- Automated FastAPI tests



Recommended testing sequence:



1\. Authenticate using `/auth/login`.

2\. Copy the returned access token.

3\. Authorize Swagger UI using the bearer token.

4\. Test the protected profile endpoint.

5\. Test role-specific endpoints with users from each role.

6\. Test document upload and retrieval.

7\. Test RAG question answering.

8\. Create a conversation and test agent execution.

9\. Verify conversation history and deletion.



\## 10. Documentation Scope



This document describes the API routes and behavior visible in the route modules and application entry point.



The following details require inspection of their respective implementation files before being documented as exact contracts:



\- Detailed JWT claims, token expiry, and validation behavior.

\- Exact `LoginRequest` and `TokenResponse` schemas.

\- Exact conversation and message request/response schemas.

\- Exact RAG response structure.

\- Detailed agent intent and tool-result schemas.

\- Any additional authorization behavior inside shared dependencies.



For the latest API contract, use the running application's OpenAPI specification at `/openapi.json`.



