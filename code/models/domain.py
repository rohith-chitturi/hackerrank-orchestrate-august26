from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class User:
    user_id: str
    do_not_disturb_window: str
    messages_opened_30d: int
    messages_replied_30d: int
    notifications_dismissed_30d: int
    messages_reported_30d: int

@dataclass(frozen=True)
class Group:
    group_id: str
    group_name: str
    group_type: str
    member_count: int
    admin_count: int
    created_at: str
    messages_30d: int

@dataclass(frozen=True)
class GroupMember:
    group_id: str
    user_id: str
    role: str
    joined_at: str
    messages_sent_30d: int
    messages_read_30d: int
    replies_sent_30d: int
    notifications_dismissed_30d: int
    group_muted_by_user: int

@dataclass(frozen=True)
class Business:
    business_id: str
    display_name: str
    brand_name: str
    category: str
    verified: int
    official_domain: str
    domain_used_by_sender: str
    account_age_days: int
    messages_sent_30d: int
    user_reports_30d: int
    domain_used_by_sender_age_days: int

@dataclass(frozen=True)
class UserBusinessHistory:
    user_id: str
    business_id: str
    why_user_knows_account: str
    last_activity_at: str
    allows_promotions: int
    promotions_opted_out_at: str
    activity_count_180d: int
    messages_opened_30d: int
    messages_dismissed_30d: int
    messages_replied_30d: int
    last_reply_at: str

@dataclass(frozen=True)
class Message:
    message_id: str
    user_id: str
    conversation_type: str
    group_id: str
    business_id: str
    sender_user_id: str
    created_at: str
    message_text: str
    media_type: str
    media_id: str
    forwarded_count: int

@dataclass(frozen=True)
class HistoricalMessage:
    message_id: str
    user_id: str
    conversation_type: str
    group_id: str
    business_id: str
    sender_user_id: str
    created_at: str
    message_text: str
    media_type: str
    media_id: str
    forwarded_count: int

@dataclass(frozen=True)
class MessageEvent:
    user_id: str
    message_id: str
    message_opened: int
    message_replied: int
    reaction_time_minutes: float
    notification_dismissed: int
    muted_after_message: int
    message_reported: int

@dataclass(frozen=True)
class DailyFatigue:
    user_id: str
    date: str
    notifications_sent: int
    notifications_dismissed: int
