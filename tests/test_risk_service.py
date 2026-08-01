import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message, Business
from models.results import NormalizedMessage
from models.state import RoutingContext
from services.risk_service import RiskService

def test_risk_service_otp():
    svc = RiskService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Enter OTP 1234", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="Enter OTP 1234", normalized_text="enter otp 1234", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    ctx = RoutingContext(message=msg, normalized_message=norm)
    
    res = svc.evaluate(ctx)
    assert "suspicious_keyword_otp" in res.flags
    assert res.score >= 40.0
    assert res.level in ["MEDIUM", "HIGH"]

def test_risk_service_domain_mismatch():
    svc = RiskService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="business", group_id=None, business_id="b1", sender_user_id=None, created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="Hello", normalized_text="hello", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    
    bus = Business(business_id="b1", display_name="Bank", brand_name="Bank", category="finance", verified=0, official_domain="bank.com", domain_used_by_sender="scam-bank.com", account_age_days=10, messages_sent_30d=100, user_reports_30d=15, domain_used_by_sender_age_days=2)
    
    ctx = RoutingContext(message=msg, normalized_message=norm, business=bus)
    
    res = svc.evaluate(ctx)
    assert "domain_mismatch" in res.flags
    assert "high_user_reports" in res.flags
    assert res.score >= 100.0
    assert res.level == "HIGH"
    assert res.recommendation == "mute"

if __name__ == "__main__":
    test_risk_service_otp()
    test_risk_service_domain_mismatch()
    print("Risk service tests passed!")
