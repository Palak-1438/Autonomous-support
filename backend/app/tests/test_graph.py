import pytest
from app.orchestration.graph import app_graph
from app.config import get_settings

def test_graph_happy_path():
    settings = get_settings()
    assert settings.llm_mode == "mock"

    initial_state = {
        "content": "I need help with my order",
        "classification": None,
        "specialist": None,
        "supervisor": None,
        "response_content": None,
        "escalated": False
    }

    result = app_graph.invoke(initial_state)

    assert result["classification"] is not None
    assert result["classification"].domain == "ecommerce"

    assert result["specialist"] is not None
    assert result["specialist"].specialist_id == "general"

    assert result["supervisor"] is not None
    assert result["supervisor"].outcome == "APPROVE"

    assert result["escalated"] is False
    assert "mock response" in result["response_content"].lower()

def test_graph_escalation_on_unknown():
    initial_state = {
        "content": "I have an unknown issue",
        "classification": None,
        "specialist": None,
        "supervisor": None,
        "response_content": None,
        "escalated": False
    }

    result = app_graph.invoke(initial_state)

    assert result["classification"] is not None
    assert result["classification"].domain == "unknown"

    # We escalated directly after route due to selected_specialist == human_handoff
    assert result["specialist"] is None
    assert result["supervisor"] is None

    assert result["escalated"] is True
    assert "escalated" in result["response_content"].lower()

def test_graph_supervisor_rejection():
    initial_state = {
        "content": "Please reject this bad answer",
        "classification": None,
        "specialist": None,
        "supervisor": None,
        "response_content": None,
        "escalated": False
    }

    result = app_graph.invoke(initial_state)

    assert result["classification"] is not None
    assert result["classification"].domain == "ecommerce"

    assert result["specialist"] is not None
    assert result["specialist"].specialist_id == "general"

    assert result["supervisor"] is not None
    assert result["supervisor"].outcome == "ESCALATE"

    assert result["escalated"] is True
    assert "escalated" in result["response_content"].lower()
