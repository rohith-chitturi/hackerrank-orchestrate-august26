import os
import sys
import json
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import ValidationResult

class LLMValidatorService:
    def evaluate(self, ctx: RoutingContext) -> ValidationResult:
        # In a real environment, we'd invoke the LLM here via API.
        # We simulate the LLM verifying the structured context.
        
        # 1. Structure the deterministic context
        payload = {
            "candidate_action": ctx.final_decision.action if ctx.final_decision else "unknown",
            "trust": ctx.trust_result.score if ctx.trust_result else 50.0,
            "risk_level": ctx.risk_assessment.level if ctx.risk_assessment else "LOW",
            "urgency": ctx.urgency_assessment.score if ctx.urgency_assessment else 0.0,
            "likes_promotions": ctx.preference_profile.likes_promotions if ctx.preference_profile else True,
            "dnd_active": ctx.fatigue_assessment.dnd_active if ctx.fatigue_assessment else False,
            "evidence": [ev.message_id for ev in ctx.retrieved_evidence] if ctx.retrieved_evidence else []
        }
        
        prompt = f"""
        Here is my deterministic reasoning. Do you agree?
        Payload: {json.dumps(payload, indent=2)}
        Message: "{ctx.message.message_text}"
        """
        
        # 2. Simulate LLM Rules for this Hackathon MVP
        status = "APPROVED"
        new_action = None
        reason = "LLM agrees with deterministic candidate."
        
        # Stub logic: Simulate the LLM catching contextual nuance missed by heuristics
        text = ctx.message.message_text.lower() if ctx.message.message_text else ""
        if payload["candidate_action"] == "digest" and "review this contract" in text:
            status = "OVERRIDDEN"
            new_action = "notify"
            reason = "LLM Override: Detected hidden urgency in contextual text."
            
        elif payload["candidate_action"] == "notify" and payload["risk_level"] != "HIGH" and "free iphone" in text:
            status = "OVERRIDDEN"
            new_action = "mute"
            reason = "LLM Override: Semantic scam detected."

        return ValidationResult(
            status=status,
            reason=reason,
            new_action=new_action
        )
