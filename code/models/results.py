from dataclasses import dataclass
from typing import List, Optional, Dict

@dataclass(frozen=True)
class NormalizedMessage:
    raw_text: str
    normalized_text: str
    language: str
    mentions: List[str]
    urls: List[str]
    phone_numbers: List[str]
    currency: List[str]
    dates: List[str]
    times: List[str]
    entities: List[str]

@dataclass(frozen=True)
class RetrievedEvidence:
    message_id: str
    similarity: float
    retrieval_source: str  # e.g., "BM25", "Embedding", "Hybrid"

@dataclass(frozen=True)
class TrustResult:
    score: float
    reasons: List[str]
    signals: List[str]

@dataclass(frozen=True)
class RiskAssessment:
    level: str  # "LOW", "MEDIUM", "HIGH"
    score: float
    flags: List[str]
    recommendation: str

@dataclass(frozen=True)
class UrgencyAssessment:
    score: float
    deadline: Optional[str]
    keywords: List[str]
    time_sensitive: bool

@dataclass(frozen=True)
class PreferenceProfile:
    likes_promotions: bool
    reads_family: bool
    muted_groups: List[str]
    notification_tolerance: str
    business_affinity: Dict[str, float]

@dataclass(frozen=True)
class FatigueAssessment:
    is_fatigued: bool
    dnd_active: bool
    reason: str

@dataclass(frozen=True)
class ValidationResult:
    status: str  # "APPROVED" or "OVERRIDDEN"
    reason: str
    new_action: Optional[str] = None

@dataclass(frozen=True)
class Decision:
    intent: str
    category: str
    priority: str
    action: str
    confidence: float
    confidence_band: str
    reason: str
    evidence: List[str]
