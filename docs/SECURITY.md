\# Security Documentation — AI Enterprise Assistant



\## 1. Overview



The AI Enterprise Assistant implements multiple security controls to protect authentication, user accounts, API endpoints, and uploaded knowledge-base documents.



The security implementation includes:



\- Bcrypt password hashing

\- JWT-based authentication

\- Token expiration and claim validation

\- Role-Based Access Control (RBAC)

\- Database-backed user verification

\- Document upload validation

\- Filename and path traversal protection

\- Duplicate document prevention

\- Upload size restrictions

\- Cleanup following document ingestion failures



\## 2. Password Security



The application uses Passlib's `CryptContext` with the bcrypt hashing scheme.



\### Password hashing



User passwords are hashed before being stored in the database.



```python

def hash\_password(password: str) -> str:

&#x20;   return pwd\_context.hash(password)

```



\### Password verification



During authentication, the submitted password is verified against the stored password hash.



```python

def verify\_password(

&#x20;   plain\_password: str,

&#x20;   hashed\_password: str

) -> bool:

&#x20;   return pwd\_context.verify(

&#x20;       plain\_password,

&#x20;       hashed\_password

&#x20;   )

```



Passwords are not stored as plaintext by these password-management functions.



\## 3. JWT Authentication



The application uses JSON Web Tokens (JWT) to authenticate API requests.



\### Token configuration



| Security setting | Implementation |

|---|---|

| Signing algorithm | HS256 |

| Default token lifetime | 30 minutes |

| Secret storage | Environment configuration |

| Minimum secret length | 32 bytes |

| Required claims | user\_id, role, iat, exp |



\### JWT payload



The token contains:



\- `user\_id`: Database ID of the authenticated user.

\- `role`: User's assigned role at token creation.

\- `iat`: Token issuance timestamp.

\- `exp`: Token expiration timestamp.



\### Token validation



The application validates:



1\. JWT signature.

2\. Token expiration.

3\. Required JWT claims.

4\. Positive integer `user\_id`.

5\. Non-empty string `role`.



Only the HS256 algorithm is supported.



\### Token configuration validation



Application startup validates that:



\- JWT\_SECRET is configured.

\- JWT\_SECRET contains at least 32 bytes.

\- JWT\_ALGORITHM is HS256.

\- JWT\_ACCESS\_TOKEN\_EXPIRE\_MINUTES is greater than zero.



\### Authentication header



Protected endpoints require:



```http

Authorization: Bearer YOUR\_ACCESS\_TOKEN

```



Invalid or expired tokens return HTTP `401 Unauthorized`.



\## 4. Database-Backed User Verification



After decoding a JWT, the application retrieves the corresponding user from the database.



This is implemented through `get\_current\_user\_record()`.



If the user account no longer exists, the application rejects the request with:



```json

{

&#x20; "detail": "User account no longer exists"

}

```



This ensures that a validly signed token alone is insufficient when the associated user account has been deleted.



\## 5. Role-Based Access Control (RBAC)



The application implements role authorization through the `require\_role()` dependency.



\### Supported roles



\- ADMIN

\- MANAGER

\- EMPLOYEE



\### Authorization process



1\. Validate the JWT.

2\. Retrieve the current user from the database.

3\. Read the user's current database role.

4\. Compare it with the role required by the endpoint.

5\. Grant or deny access.



If the user does not have the required role, the application returns:



```json

{

&#x20; "detail": "Insufficient permissions"

}

```



HTTP status: `403 Forbidden`.



\### Protected operations



| Operation | Required role |

|---|---|

| Create users | ADMIN |

| List users | ADMIN |

| Upload documents | ADMIN |

| List documents | ADMIN |

| Delete documents | ADMIN |

| Admin RBAC endpoint | ADMIN |

| Manager RBAC endpoint | MANAGER |

| Employee RBAC endpoint | EMPLOYEE |



Other authenticated endpoints use their respective authentication dependencies.



\## 6. Employee Account Association



The application defines a `require\_linked\_employee()` dependency.



It checks whether the authenticated user has:



\- A non-null `employee\_id`.

\- An associated employee record.



If either condition is not satisfied, access is denied with HTTP `403 Forbidden`.



This supports endpoints that require an account to be linked to an employee record.



\## 7. Document Upload Security



Document management is restricted to ADMIN users.



\### Supported file formats



| Extension | Supported |

|---|---|

| PDF | Yes |

| TXT | Yes |

| Other formats | No |



\### Maximum upload size



The application enforces a maximum document size of:



\*\*10 MB\*\*



Files are read in chunks of up to 1 MB, and the accumulated size is checked against the maximum.



\### Filename validation



The application validates filenames to prevent unsafe paths and path traversal attempts.



The validation includes:



\- Rejecting empty filenames.

\- Rejecting directory paths.

\- Restricting filenames to an allowed character pattern.

\- Limiting filename length.

\- Rejecting `.` and `..`.



\### Duplicate document prevention



The upload process checks:



1\. Whether a file with the same name already exists on disk.

2\. Whether a document with the same source filename already exists in ChromaDB.



Existing documents cannot be overwritten through the upload endpoint.



\### Ingestion failure cleanup



If document ingestion fails, the application attempts to:



\- Remove the newly created file.

\- Delete indexed chunks associated with the filename.

\- Return an HTTP `500 Internal Server Error`.



This helps prevent incomplete document uploads from remaining in storage.



\## 8. Document Deletion Security



Document deletion is restricted to ADMIN users.



Before deletion, the filename is validated using the same filename validation function.



The application removes the indexed document chunks and deletes the stored file when present.



If neither indexed chunks nor a stored file exists, the endpoint returns HTTP `404 Not Found`.



\## 9. Security Error Responses



| HTTP status | Security-related condition |

|---|---|

| 400 | Invalid filename or unsupported file extension |

| 401 | Invalid or expired token |

| 401 | User account no longer exists |

| 403 | Insufficient role permissions |

| 403 | Employee account is not linked |

| 409 | Duplicate document |

| 413 | Document exceeds 10 MB |



\## 10. Environment Configuration



The application loads configuration from the backend `.env` file.



Important security-related variables include:



```env

JWT\_SECRET=your-strong-secret-at-least-32-bytes

JWT\_ALGORITHM=HS256

JWT\_ACCESS\_TOKEN\_EXPIRE\_MINUTES=30

```



\*\*Important:\*\* The actual secret must never be committed to GitHub.



Use a strong, randomly generated secret for each deployment environment.



\## 11. Additional Production Security Considerations



The following are recommended areas for further security hardening. They are not confirmed as implemented by the reviewed files.



| Area | Recommended improvement |

|---|---|

| Login protection | Add rate limiting and brute-force protection |

| Document validation | Verify actual file content and signatures, not just extensions |

| File scanning | Consider malware scanning before ingestion |

| Transport security | Enforce HTTPS in production |

| Secret management | Use a dedicated secrets manager |

| Logging | Add security-event logging and monitoring |

| Token lifecycle | Consider refresh-token rotation and revocation |

| Upload storage | Consider isolated, access-controlled storage |

| Dependency security | Regularly scan and update dependencies |

| Database security | Use least-privilege database credentials |



\## 12. Security Scope



This document describes security controls verified in the following implementation files:



\- `backend/app/core/security.py`

\- `backend/app/core/dependencies.py`

\- `backend/app/core/config.py`

\- `backend/app/api/documents.py`



Recommendations are separated from implemented controls to avoid overstating the application's current security capabilities.

