# Development Log

This file tracks the progress, issues, and decisions made during the execution of each phase.

## Day 1
### Phase 0: Environment Setup
- **Tasks Completed:** Initialized Python & Node environments. Generated core folder skeleton. Initialized Git and pushed to remote branch `main`. Configured `config.yaml`.
- **Issues/Decisions:** Full Hadoop HDFS setup on local Windows machine is avoided due to system overhead. As authorized by the SRS, simulated HDFS local path (`hdfs_scripts/local_hdfs_sim`) and mock script will be used to demonstrate HDFS commands functionality. Database is defaulted to SQLite for development, to be upgraded to PostgreSQL if production deployment requires it.
