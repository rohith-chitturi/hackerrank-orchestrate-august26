import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message, Business, Group
from models.state import RoutingContext
from services.trust_service import TrustService

def test_trust_verified_business():
    svc = TrustService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="business", group_id=None, business_id="b1", sender_user_id=None, created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    
    bus = Business(business_id="b1", display_name="Bank", brand_name="Bank", category="finance", verified=1, official_domain="bank.com", domain_used_by_sender="bank.com", account_age_days=400, messages_sent_30d=100, user_reports_30d=0, domain_used_by_sender_age_days=400)
    
    ctx = RoutingContext(message=msg, business=bus)
    
    res = svc.evaluate(ctx)
    assert res.score >= 90.0  # 50 + 30 (verified) + 15 (age) + 5 (no reports) = 100 -> capped at 100
    assert "business_verified" in res.signals

def test_trust_large_group():
    svc = TrustService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="group", group_id="g1", business_id=None, sender_user_id="u2", created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    
    group = Group(group_id="g1", group_name="Spam Group", group_type="public", member_count=500, admin_count=1, created_at="2026", messages_30d=5000)
    
    ctx = RoutingContext(message=msg, group=group)
    
    res = svc.evaluate(ctx)
    assert res.score <= 40.0  # 50 - 10 (large group) = 40
    assert "group_chat" in res.signals

if __name__ == "__main__":
    test_trust_verified_business()
    test_trust_large_group()
    print("Trust service tests passed!")
