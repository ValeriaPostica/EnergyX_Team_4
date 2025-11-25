# Changelog

## [1.7.1] - 2025-11-25
### Tooling & Configuration
- Refined Android runtime setup: centralized API host constants, adjusted cleartext traffic policy, validated Gradle/Capacitor sync, and verified `adb reverse` routing so the mobile build can reach local services reliably.
### Documentation
- Captured the new Android workflow and supporting commands in `DOCUMENTATION.md`, covering backend startup, mock IoT server, build/sync steps, port forwarding, and Android Studio launch.

## [1.7.0] - 2025-11-1
### Added and updated
- Added `/pred/simulate` backend improvements: accept URL-encoded JSON schedules, validate tuples, and surface consistent JSON errors when payloads are invalid.
- Introduced device-aware forecasting totals so simulations align with the LSTM adjustments for thermostat, AC, lighting, and saver modes.

## [1.6.0] - 2025-11-1
### Added and updated
- Introduced smart house points system
- Implemented initial logic for point allocation
- Marked for further debugging and refinement

- Added points calculation logic for user activities
- Defined rules for energy-saving actions
- Linked point system to leaderboard metrics
- Developed in-memory leaderboard storage

- Refined UI for clarity and responsiveness
- Improved integration with backend pricing logic
- Connected user actions to reward system
- Conducted endpoint testing and minor modifications
- Adjusted response formats for frontend compatibility

## [1.5.0] - 2025-10-30
### Additions and changes
- Implemented dynamic loading mechanism for OpenAI key configuration
- Enhanced flexibility for environment-based key management
- Reduced risk of hardcoded secrets in deployment
- Resolved minor conflicts during integration

## [1.4.0] - 2025-10-23
### Added
- Integrated comprehensive IoT server infrastructure ([#21](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/21))
  - Established bidirectional communication between IoT devices and backend
  - Implemented real-time device state synchronization
  - Added support for multiple device types (thermostats, lighting, AC units)
  - Created WebSocket endpoints for live updates
- Developed interactive Smart House simulation environment
  - Added real-time device control interface
  - Implemented energy consumption visualization
  - Created scenario-based demonstrations for energy saving features
  - Added interactive tutorials for user engagement

### Performance
- Major optimization of providers dashboard map rendering
  - Reduced loading time from 60 seconds to under 1 second
  - Implemented efficient location-based data aggregation system
  - Created pre-computation pipeline for regional statistics
  - Added intelligent caching layer using JSON for fast retrieval
  - Optimized data structures for quick spatial queries
  - Implemented incremental updates for real-time data

## [1.3.0] - 2025-10-19
### AI Improvements
- Complete overhaul of provider LLM system architecture
  - Redesigned context injection system for improved accuracy
  - Implemented robust response validation pipeline
  - Enhanced data consistency checks for AI outputs
  - Added comprehensive error handling for edge cases
  - Improved response formatting and structure
  - Implemented automatic data validation against current metrics

### Fixed
- Critical resolution of smart meter prediction system ([#5](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/5))
  - Completely rebuilt prediction model architecture
  - Implemented new training pipeline with validated database records
  - Switched from problematic ID-based lookup to direct series analysis
  - Added comprehensive error handling for edge cases
  - Implemented automatic data validation and cleaning
  - Created new monitoring system for prediction accuracy

### Changed
- Modernized data processing architecture
  - Replaced static computations with dynamic database queries
  - Implemented real-time aggregation for current usage metrics
  - Added caching layer for frequently accessed data
  - Created new API endpoints for real-time data access
  - Improved error handling and data validation
  - Added comprehensive logging for debugging

## [1.2.0] - 2025-10-14
### Database
- Complete PostgreSQL infrastructure implementation ([#1](https://github.com/ValeriaPostica/EnergyX_Team_4/pull/1))
  - Designed and implemented robust database schema
    - Created `contour` table with advanced fuel coefficient tracking
    - Implemented `contour_data` table with time-series optimization
    - Added foreign key constraints and indexing for performance
    - Implemented serial IDs for reliable data tracking
  - Developed comprehensive data management system
    - Created efficient data migration pipelines
    - Implemented sophisticated data interpolation algorithms
    - Added data validation and cleaning procedures
  - Set up production-ready deployment
    - Configured Docker container with optimal settings
    - Implemented docker-compose for easy deployment
    - Set up port 5433 with security configurations
  - Created developer toolkit
    - Implemented series.py for time-series analysis
    - Added test.py for comprehensive testing
    - Created documentation and usage examples
  - Integrated modern data access layer
    - Implemented SQLAlchemy with connection pooling
    - Added parameterized queries for security
    - Created efficient query optimization patterns
  - Enhanced data processing capabilities
    - Added hourly consumption aggregation
    - Implemented data interpolation schemas
    - Created efficient data access patterns

### Performance
- Significant optimization of recommendation system
  - Reduced page load time from 8-10 seconds to 0.5-1 seconds
  - Implemented smart caching for top consumer data
  - Created efficient data preloading system
  - Optimized database queries for faster retrieval
  - Added asynchronous data loading where applicable

### DevOps
- Enhanced deployment and development workflow
  - Created unified `run.py` for seamless startup
  - Implemented comprehensive error handling
  - Added detailed logging for troubleshooting
  - Resolved Windows-specific compatibility issues
  - Created cross-platform testing procedures

## [1.1.0] - 2025-10-06
### AI and Machine Learning
- Advanced Langchain integration for AI enhancement ([#10](https://github.com/ValeriaPostica/EnergyX_Team_4/issues/10))
  - Implemented sophisticated model tracking system
  - Reduced average response time by 3-4 seconds
  - Enhanced prompt engineering with dynamic templates
  - Added comprehensive performance monitoring
  - Implemented A/B testing for prompt optimization

### Added
- Comprehensive real-time monitoring system
  - Implemented sophisticated simple_log handler
    - Real-time smart meter data processing
    - Advanced consumption forecasting algorithms
    - Dynamic tariff cost estimation
    - Comprehensive Smart House monitoring
      - Temperature tracking and analysis
      - Usage pattern detection
      - Motion-based optimization
      - Device state management
      - Energy efficiency monitoring

### Enhanced
- Implemented advanced RAG architecture
  - Optimized document chunking (1000 tokens with 200 overlap)
  - Enhanced vector store integration
  - Implemented sophisticated distance computation
  - Added context-aware response generation
  - Created comprehensive validation pipeline
- Revolutionary tariff calculation system
  - Implemented dual Gaussian function algorithm
    - Optimized for different usage patterns
    - Enhanced accuracy in edge cases
    - Improved processing efficiency
    - Added validation for extreme values
    - Created visualization tools for analysis

