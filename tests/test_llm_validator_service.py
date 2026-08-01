import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message
from models.results import Decision
from models.state import RoutingContext
from services.llm_validator_service import LLMValidatorService

def test_llm_validator_approve():
    svc = LLMValidatorService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    decision = Decision(intent="unknown", category="unknown", priority="unknown", action="notify", confidence=0.8, confidence_band="HIGH", reason="default", evidence=[])
    
    ctx = RoutingContext(message=msg, final_decision=decision)
    
    res = svc.evaluate(ctx)
    assert res.status == "APPROVED"
    assert res.new_action is None

def test_llm_validator_override():
    svc = LLMValidatorService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="You won a free iPhone!", media_type="", media_id="", forwarded_count=0)
    decision = Decision(intent="unknown", category="unknown", priority="unknown", action="notify", confidence=0.8, confidence_band="HIGH", reason="default", evidence=[])
    
    ctx = RoutingContext(message=msg, final_decision=decision)
    
    res = svc.evaluate(ctx)
    assert res.status == "OVERRIDDEN"
    assert res.new_action == "mute"

if __name__ == "__main__":
    test_llm_validator_approve()
    test_llm_validator_override()
    print("LLM Validator tests passed!")
