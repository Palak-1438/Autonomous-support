# Autonomous Multi-Domain Customer Support Platform

Production-oriented, domain-agnostic customer support platform with shared agent orchestration using LangGraph, FastAPI, and configurable domain policies.

## Setup

1. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

2. Run the application:
   ```bash
   cd backend
   PYTHONPATH=. python -m uvicorn app.api:app --reload
   ```

## Testing

To run the test suite, simply use `pytest`:
```bash
cd backend
PYTHONPATH=. pytest
```

By default, the application runs in mock mode (`llm_mode=mock`), so you do not need an OpenAI API key for basic setup and testing of the LangGraph workflows.
