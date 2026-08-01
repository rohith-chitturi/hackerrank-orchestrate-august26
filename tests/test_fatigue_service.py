import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message, User
from models.state import RoutingContext
from services.fatigue_service import FatigueService

def test_fatigue_dnd():
    svc = FatigueService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    user = User(user_id="u1", do_not_disturb_window="always", messages_opened_30d=10, messages_replied_30d=10, notifications_dismissed_30d=0, messages_reported_30d=0)
    
    ctx = RoutingContext(message=msg, user=user)
    
    res = svc.evaluate(ctx)
    assert res.dnd_active is True
    assert res.is_fatigued is False

def test_fatigue_notification_load():
    svc = FatigueService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u2", created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    user = User(user_id="u1", do_not_disturb_window="none", messages_opened_30d=10, messages_replied_30d=10, notifications_dismissed_30d=45, messages_reported_30d=0)
    
    ctx = RoutingContext(message=msg, user=user)
    
    res = svc.evaluate(ctx)
    assert res.dnd_active is False
    assert res.is_fatigued is True

if __name__ == "__main__":
    test_fatigue_dnd()
    test_fatigue_notification_load()
    print("Fatigue service tests passed!")
