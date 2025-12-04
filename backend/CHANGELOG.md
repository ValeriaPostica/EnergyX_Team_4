**Backend**
- PostgreSQL `users` table with user data (id, username, email, password, role, smart_meter_id)
- implemented JWT token-based authentication
  - `/auth/register` endpoint with field validation
  - `/auth/login` endpoint with token generation (24-hour expiration)
  - `/auth/logout` endpoint
  - `/auth/verify` endpoint for token validation
- protected all API endpoints with `@token_required` decorator
- added password hashing
- implemented email format validation
- smart meter ID validation for both user roles
- notifications module:
    - detects locations with high energy usage
    - generates AI suggestions for providers
- new API route: /notifications — returns usage alerts + AI recommendation
- AI integration
    - get_ai_suggestion() inside the notifications system
    - reused existing OpenAI client inside app.py
    - logic to call the AI model only when alerts are detected

**Frontend**
- redesigned authentication UI with role selection (Provider/Consumer)
- added user registration flow with form validation
- Implemented JWT token storage in localStorage
- created `fetchWithAuth` utility for authenticated API calls
- updated all components (HomePage, Chatbot, etc.) to use token authentication
- automatic logout on token expiration (don't have time to test it)

**Security**
- JWT tokens with expiration
- Secure password hashing (not storing plain text)
- token verification on all protected routes
- automatic session cleanup on authentication failure

**Database**
- Set up Docker-based PostgreSQL database
- Created database initialization scripts
- Implemented connection pooling with SQLAlchemy

### changed
- from open API endpoints to fully authenticated system
- updated all frontend components to handle authentication state

### technical details
- **New dependencies**: PyJWT, python-dotenv, psycopg2-binary
- **Database**: PostgreSQL 15 (Docker)
- **Authentication method**: JWT with Bearer token
- **Token expiration**: 24 hours

NOTE:
i did use ai quite a lot. mostly for explaining what am i doing, 
how to implement this stuff or that stuff. greatly helped me whenever i 
started a new part of the task, but was absolutely useless with error fixing.
