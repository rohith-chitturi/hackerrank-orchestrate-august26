import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import TrustResult

class TrustService:
    def evaluate(self, ctx: RoutingContext) -> TrustResult:
        score = 50.0
        reasons = []
        signals = []
        
        # 1. Business Trust Heuristics
        if ctx.business:
            signals.append("is_business")
            if str(ctx.business.verified) == "1":
                score += 30.0
                reasons.append("Verified business account")
                signals.append("business_verified")
            else:
                score -= 10.0
                reasons.append("Unverified business account")
                signals.append("business_unverified")
                
            age = int(ctx.business.account_age_days) if ctx.business.account_age_days else 0
            if age > 365:
                score += 15.0
                reasons.append("Established business (>1 year)")
            elif age < 30:
                score -= 20.0
                reasons.append("New business account (<30 days)")
                signals.append("business_new")
                
            reports = int(ctx.business.user_reports_30d) if ctx.business.user_reports_30d else 0
            if reports == 0:
                score += 5.0
            elif reports > 10:
                score -= 30.0
                reasons.append(f"High report count ({reports} in 30d)")
                signals.append("business_reported")
                
        # 2. Personal/Group Trust Heuristics
        if ctx.message.conversation_type == "personal" and not ctx.business:
            signals.append("personal_chat")
            score += 20.0
            reasons.append("Direct personal message")
        elif ctx.message.conversation_type == "group":
            signals.append("group_chat")
            if ctx.group and int(ctx.group.member_count) < 10:
                score += 10.0
                reasons.append("Small group chat")
            elif ctx.group and int(ctx.group.member_count) > 100:
                score -= 10.0
                reasons.append("Large group chat")
                
        final_score = max(0.0, min(100.0, score))
        
        return TrustResult(
            score=final_score,
            reasons=reasons,
            signals=signals
        )
