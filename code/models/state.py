from dataclasses import dataclass, field
from typing import List, Dict, Optional
from models.domain import User, Group, Business, Message, GroupMember, UserBusinessHistory
from models.results import RetrievedEvidence, TrustResult, RiskAssessment, UrgencyAssessment, PreferenceProfile, Decision, NormalizedMessage

@dataclass(frozen=True)
class RoutingContext:
    # 1. Raw Inputs & Normalization
    message: Message
    normalized_message: Optional[NormalizedMessage] = None
    
    # 2. Hydrated Entities
    user: Optional[User] = None
    group: Optional[Group] = None
    business: Optional[Business] = None
    group_member: Optional[GroupMember] = None
    user_business_history: Optional[UserBusinessHistory] = None
    
    # 3. Service Outputs
    retrieved_evidence: List[RetrievedEvidence] = field(default_factory=list)
    trust_result: Optional[TrustResult] = None
    risk_assessment: Optional[RiskAssessment] = None
    urgency_assessment: Optional[UrgencyAssessment] = None
    preference_profile: Optional[PreferenceProfile] = None
    notification_load_today: Optional[int] = None
    
    # 4. Observability & Debugging
    observability_metrics: Dict[str, float] = field(default_factory=dict)
    decision_trace: List[str] = field(default_factory=list)
    
    # 5. Final Output
    final_decision: Optional[Decision] = None
