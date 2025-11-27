# Changelog

## [Release: EnergyX v1.8.1]
**November 27, 2025**

We've refined the Android runtime setup and updated our documentation to ensure a smoother mobile development workflow.

*   **Tooling & Configuration:** Refined Android runtime setup: centralized API host constants, adjusted cleartext traffic policy, validated Gradle/Capacitor sync, and verified `adb reverse` routing so the mobile build can reach local services reliably.
*   **Documentation:** Captured the new Android workflow and supporting commands in `DOCUMENTATION.md`, covering backend startup, mock IoT server, build/sync steps, port forwarding, and Android Studio launch.
*   **Refactor:** Android runtime documentation tracked in issue [#48](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/48).

Tags:
[Release] [Mobile] [Documentation]

## [Release: EnergyX v1.8.0]
**November 23, 2025**

Introducing comprehensive device simulation capabilities. Users can now schedule devices, visualize costs, and compare tariffs with our new simulation engine.

*   **Backend:** Added `/api/simulate` endpoint and simulation backend improvements: accept scenario input (schedules), load baseline device/household hourly usage, apply on/off schedules, compute hourly usage, and calculate cost for one or more tariffs; improved validation and consistent JSON error responses for invalid payloads ([#47](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/47)).
*   **Forecasting:** Introduced device-aware forecasting totals so simulations align with the LSTM adjustments for thermostat, AC, lighting, and saver modes.
*   **Frontend Experience:** Created a new "Device Simulation" consumer page with configurable device rows, cost deltas, and side-by-side forecast charts. Connected navigation and app router updates so the new page is available from the sidebar on logged-in consumer accounts.
*   **Enhancements:** Frontend simulation and tariff calculator enhancements (device scheduling UI, time-interval selection, range selection, and simulated-vs-baseline cost charts) implemented and tracked in issue [#41](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/41).
*   **RAG & Logging:** Extended `simple_log_handler` to persist numbered entries up to `4)` ensuring the device simulation summary is stored alongside existing monitoring lines. Updated simulation flow to emit a structured `4)Device simulation ...` log entry, enabling retrieval workflows to ingest the latest scenario insights.

Tags:
[Release] [Simulation] [Frontend] [Backend]

## [Release: EnergyX v1.7]
**November 2025**

A major security and authentication overhaul. We've implemented a robust JWT-based authentication system, role-based access (Provider/Consumer), and secured all API endpoints.

*   **Backend:**
    *   PostgreSQL `users` table with user data (id, username, email, password, role, smart_meter_id).
    *   Implemented JWT token-based authentication:
        *   `/auth/register` endpoint with field validation.
        *   `/auth/login` endpoint with token generation (24-hour expiration).
        *   `/auth/logout` endpoint.
        *   `/auth/verify` endpoint for token validation.
    *   Protected all API endpoints with `@token_required` decorator.
    *   Added password hashing and email format validation.
    *   Smart meter ID validation for both user roles.
*   **Frontend:**
    *   Redesigned authentication UI with role selection (Provider/Consumer).
    *   Added user registration flow with form validation.
    *   Implemented JWT token storage in localStorage.
    *   Created `fetchWithAuth` utility for authenticated API calls.
    *   Updated all components (HomePage, Chatbot, etc.) to use token authentication.
    *   Automatic logout on token expiration.
*   **Security:**
    *   JWT tokens with expiration.
    *   Secure password hashing (not storing plain text).
    *   Token verification on all protected routes.
    *   Automatic session cleanup on authentication failure.
*   **Database:**
    *   Set up Docker-based PostgreSQL database.
    *   Created database initialization scripts.
    *   Implemented connection pooling with SQLAlchemy.
*   **Technical Details:**
    *   **New dependencies:** PyJWT, python-dotenv, psycopg2-binary.
    *   **Database:** PostgreSQL 15 (Docker).
    *   **Authentication method:** JWT with Bearer token.
    *   **Token expiration:** 24 hours.

Tags:
[Release] [Security] [Authentication] [Database]

## [Release: EnergyX v1.6.0]
**November 1, 2025**

Gamifying energy savings with a new Smart House points system and leaderboard.

*   **Smart House Points:** Introduced smart house points system and implemented initial logic for point allocation. Added points calculation logic for user activities and defined rules for energy-saving actions.
*   **Leaderboard:** Linked point system to leaderboard metrics and developed in-memory leaderboard storage.
*   **UI & Integration:** Refined UI for clarity and responsiveness. Improved integration with backend pricing logic and connected user actions to reward system.
*   **Testing:** Conducted endpoint testing and minor modifications. Adjusted response formats for frontend compatibility.

Tags:
[Release] [Gamification] [Smart House]

## [Release: EnergyX v1.5.0]
**October 30, 2025**

Improving security and deployment flexibility with dynamic configuration management.

*   **Configuration:** Implemented dynamic loading mechanism for OpenAI key configuration.
*   **Security:** Enhanced flexibility for environment-based key management and reduced risk of hardcoded secrets in deployment.
*   **Integration:** Resolved minor conflicts during integration.

Tags:
[Release] [Security] [DevOps]

## [Release: EnergyX v1.4.0]
**October 23, 2025**

Launching the IoT infrastructure and Smart House simulation environment, alongside major performance optimizations for the provider dashboard.

*   **IoT Infrastructure:** Integrated comprehensive IoT server infrastructure ([#21](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/21)).
    *   Established bidirectional communication between IoT devices and backend.
    *   Implemented real-time device state synchronization.
    *   Added support for multiple device types (thermostats, lighting, AC units).
    *   Created WebSocket endpoints for live updates.
*   **Smart House Simulation:** Developed interactive Smart House simulation environment.
    *   Added real-time device control interface.
    *   Implemented energy consumption visualization.
    *   Created scenario-based demonstrations for energy saving features.
    *   Added interactive tutorials for user engagement.
*   **Performance:** Major optimization of providers dashboard map rendering.
    *   Reduced loading time from 60 seconds to under 1 second.
    *   Implemented efficient location-based data aggregation system.
    *   Created pre-computation pipeline for regional statistics.
    *   Added intelligent caching layer using JSON for fast retrieval.
    *   Optimized data structures for quick spatial queries.
    *   Implemented incremental updates for real-time data.

Tags:
[Release] [IoT] [Performance] [Simulation]

## [Release: EnergyX v1.3.0]
**October 19, 2025**

Enhancing AI accuracy and reliability with a complete overhaul of the provider LLM architecture and critical fixes to the prediction system.

*   **AI Improvements:** Complete overhaul of provider LLM system architecture.
    *   Redesigned context injection system for improved accuracy.
    *   Implemented robust response validation pipeline.
    *   Enhanced data consistency checks for AI outputs.
    *   Added comprehensive error handling for edge cases.
    *   Improved response formatting and structure.
    *   Implemented automatic data validation against current metrics.
*   **Fixed:** Critical resolution of smart meter prediction system ([#5](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/5)).
    *   Completely rebuilt prediction model architecture.
    *   Implemented new training pipeline with validated database records.
    *   Switched from problematic ID-based lookup to direct series analysis.
    *   Added comprehensive error handling for edge cases.
    *   Implemented automatic data validation and cleaning.
    *   Created new monitoring system for prediction accuracy.
*   **Architecture:** Modernized data processing architecture.
    *   Replaced static computations with dynamic database queries.
    *   Implemented real-time aggregation for current usage metrics.
    *   Added caching layer for frequently accessed data.
    *   Created new API endpoints for real-time data access.
    *   Improved error handling and data validation.
    *   Added comprehensive logging for debugging.

Tags:
[Release] [AI] [Fixes] [Architecture]

## [Release: EnergyX v1.2.0]
**October 14, 2025**

Establishing a robust data foundation with a complete PostgreSQL infrastructure implementation and significant performance tuning.

*   **Database:** Complete PostgreSQL infrastructure implementation ([#1](https://github.com/ValeriaPostica/EnergyX_Team_4/pull/1)).
    *   Designed and implemented robust database schema (contour table, time-series optimization, foreign keys, serial IDs).
    *   Developed comprehensive data management system (migration pipelines, interpolation algorithms, validation).
    *   Set up production-ready deployment (Docker, docker-compose, security configs).
    *   Created developer toolkit (series.py, test.py, documentation).
    *   Integrated modern data access layer (SQLAlchemy, connection pooling, parameterized queries).
    *   Enhanced data processing capabilities (hourly aggregation, interpolation schemas).
*   **Performance:** Significant optimization of recommendation system.
    *   Reduced page load time from 8-10 seconds to 0.5-1 seconds.
    *   Implemented smart caching for top consumer data.
    *   Created efficient data preloading system.
    *   Optimized database queries for faster retrieval.
    *   Added asynchronous data loading where applicable.
*   **DevOps:** Enhanced deployment and development workflow.
    *   Created unified `run.py` for seamless startup.
    *   Implemented comprehensive error handling.
    *   Added detailed logging for troubleshooting.
    *   Resolved Windows-specific compatibility issues.
    *   Created cross-platform testing procedures.

Tags:
[Release] [Database] [Performance] [DevOps]

## [Release: EnergyX v1.1.0]
**October 6, 2025**

Advanced AI integration using Langchain and a comprehensive real-time monitoring system.

*   **AI & Machine Learning:** Advanced Langchain integration for AI enhancement ([#10](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/10)).
    *   Implemented sophisticated model tracking system.
    *   Reduced average response time by 3-4 seconds.
    *   Enhanced prompt engineering with dynamic templates.
    *   Added comprehensive performance monitoring.
    *   Implemented A/B testing for prompt optimization.
*   **Real-time Monitoring:** Comprehensive real-time monitoring system.
    *   Implemented sophisticated simple_log handler.
    *   Real-time smart meter data processing.
    *   Advanced consumption forecasting algorithms.
    *   Dynamic tariff cost estimation.
    *   Comprehensive Smart House monitoring (temperature, usage patterns, motion, device state, efficiency).
*   **RAG Architecture:** Implemented advanced RAG architecture.
    *   Optimized document chunking (1000 tokens with 200 overlap).
    *   Enhanced vector store integration.
    *   Implemented sophisticated distance computation.
    *   Added context-aware response generation.
    *   Created comprehensive validation pipeline.
*   **Tariff Calculation:** Revolutionary tariff calculation system.
    *   Implemented dual Gaussian function algorithm.
    *   Optimized for different usage patterns.
    *   Enhanced accuracy in edge cases.
    *   Improved processing efficiency.
    *   Added validation for extreme values.
    *   Created visualization tools for analysis.

Tags:
[Release] [AI] [RAG] [Monitoring]
