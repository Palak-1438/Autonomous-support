from abc import ABC, abstractmethod
from typing import Optional

from app.config import get_settings
from app.schemas.orchestration import (
    ClassificationResult,
    SpecialistResult,
    SupervisorDecision,
)

class LLMProvider(ABC):
    @abstractmethod
    def classify(self, content: str) -> ClassificationResult:
        pass

    @abstractmethod
    def process(self, content: str, classification: ClassificationResult) -> SpecialistResult:
        pass

    @abstractmethod
    def supervise(self, content: str, specialist: SpecialistResult) -> SupervisorDecision:
        pass

class MockProvider(LLMProvider):
    def classify(self, content: str) -> ClassificationResult:
        low_confidence_keywords = ["unknown", "unsupported", "fail", "error", "escalate"]
        reject_keywords = ["reject", "bad answer"]

        is_low_confidence = any(kw in content.lower() for kw in low_confidence_keywords)
        is_reject_test = any(kw in content.lower() for kw in reject_keywords)

        if is_low_confidence:
            return ClassificationResult(
                domain="unknown",
                intent="unknown",
                selected_specialist="human_handoff",
                routing_confidence=0.3,
                rationale="Low confidence mock response",
                urgency="medium",
                risk_level="high",
            )
        elif is_reject_test:
             return ClassificationResult(
                domain="ecommerce",
                intent="general_inquiry",
                selected_specialist="general",
                routing_confidence=0.9,
                rationale="High confidence mock response",
                urgency="low",
                risk_level="low",
            )
        else:
            return ClassificationResult(
                domain="ecommerce",
                intent="general_inquiry",
                selected_specialist="general",
                routing_confidence=0.9,
                rationale="High confidence mock response",
                urgency="low",
                risk_level="low",
            )

    def process(self, content: str, classification: ClassificationResult) -> SpecialistResult:
        reject_keywords = ["reject", "bad answer"]
        is_reject_test = any(kw in content.lower() for kw in reject_keywords)

        if classification.selected_specialist == "human_handoff":
            return SpecialistResult(
                specialist_id="human_handoff",
                proposed_answer="Escalating to human.",
                uncertainty=0.9,
                needs_escalation=True,
                escalation_reason="Mock forced escalation",
            )
        elif is_reject_test:
            # High uncertainty so supervisor will reject it
            return SpecialistResult(
                specialist_id="general",
                proposed_answer="This is a bad answer that should be rejected.",
                uncertainty=0.9,
            )
        else:
            return SpecialistResult(
                specialist_id="general",
                proposed_answer="This is a mock response.",
                uncertainty=0.1,
            )

    def supervise(self, content: str, specialist: SpecialistResult) -> SupervisorDecision:
        if specialist.needs_escalation or specialist.uncertainty > 0.5:
            return SupervisorDecision(
                outcome="ESCALATE",
                reason="Low confidence or unsupported request.",
                require_human=True,
            )
        else:
            return SupervisorDecision(
                outcome="APPROVE",
                reason="High confidence mock response.",
                approved_answer=specialist.proposed_answer,
            )

class OpenAIProvider(LLMProvider):
    def classify(self, content: str) -> ClassificationResult:
        raise NotImplementedError("OpenAI provider not fully implemented.")

    def process(self, content: str, classification: ClassificationResult) -> SpecialistResult:
        raise NotImplementedError("OpenAI provider not fully implemented.")

    def supervise(self, content: str, specialist: SpecialistResult) -> SupervisorDecision:
        raise NotImplementedError("OpenAI provider not fully implemented.")

def get_provider() -> LLMProvider:
    settings = get_settings()
    if settings.llm_mode == "mock":
        return MockProvider()
    return OpenAIProvider()
