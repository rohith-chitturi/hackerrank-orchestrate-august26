import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message
from models.results import NormalizedMessage
from models.state import RoutingContext
from services.urgency_service import UrgencyService

def test_urgency_emergency():
    svc = UrgencyService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Call me immediately, emergency!", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="Call me immediately, emergency!", normalized_text="call me immediately, emergency!", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    ctx = RoutingContext(message=msg, normalized_message=norm)
    
    res = svc.evaluate(ctx)
    assert res.time_sensitive is True
    assert res.score >= 100.0  # immediately (50) + emergency (50)
    assert "immediately" in res.keywords

def test_urgency_deadline():
    svc = UrgencyService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Let me know tomorrow", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="Let me know tomorrow", normalized_text="let me know tomorrow", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    ctx = RoutingContext(message=msg, normalized_message=norm)
    
    res = svc.evaluate(ctx)
    assert res.time_sensitive is True
    assert res.deadline == "tomorrow"
    assert res.score >= 30.0

if __name__ == "__main__":
    test_urgency_emergency()
    test_urgency_deadline()
    print("Urgency service tests passed!")
