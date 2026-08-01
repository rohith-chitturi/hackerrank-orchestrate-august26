import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message, GroupMember, UserBusinessHistory
from models.state import RoutingContext
from services.preference_service import PreferenceService

def test_preference_muted_group():
    svc = PreferenceService()
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="group", group_id="g1", business_id=None, sender_user_id="u2", created_at="2026", message_text="Hello", media_type="", media_id="", forwarded_count=0)
    group_member = GroupMember(group_id="g1", user_id="u1", role="member", joined_at="2026", messages_sent_30d=0, messages_read_30d=0, replies_sent_30d=0, notifications_dismissed_30d=10, group_muted_by_user=1)
    
    ctx = RoutingContext(message=msg, group_member=group_member)
    
    res = svc.evaluate(ctx)
    assert "g1" in res.muted_groups

def test_preference_opted_out_promotions():
    svc = PreferenceService()
    
    msg = Message(message_id="m2", user_id="u1", conversation_type="business", group_id=None, business_id="b1", sender_user_id=None, created_at="2026", message_text="Promo", media_type="", media_id="", forwarded_count=0)
    history = UserBusinessHistory(user_id="u1", business_id="b1", why_user_knows_account="ad", last_activity_at="2026", allows_promotions=0, promotions_opted_out_at="2026", activity_count_180d=1, messages_opened_30d=0, messages_dismissed_30d=10, messages_replied_30d=0, last_reply_at="")
    
    ctx = RoutingContext(message=msg, user_business_history=history)
    
    res = svc.evaluate(ctx)
    assert res.likes_promotions is False
    assert res.business_affinity["b1"] < 50.0

if __name__ == "__main__":
    test_preference_muted_group()
    test_preference_opted_out_promotions()
    print("Preference service tests passed!")
