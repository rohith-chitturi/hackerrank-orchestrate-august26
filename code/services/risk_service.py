import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import RiskAssessment

class RiskService:
    def evaluate(self, ctx: RoutingContext) -> RiskAssessment:
        flags = []
        score = 0.0
        level = "LOW"
        recommendation = "safe"
        
        # 1. Forwarding heuristic
        if ctx.message.forwarded_count and int(ctx.message.forwarded_count) > 3:
            flags.append("highly_forwarded")
            score += 30.0
            
        # 2. Domain Mismatch & Business Trust
        if ctx.business:
            if str(ctx.business.verified) == "0" and ctx.business.official_domain != ctx.business.domain_used_by_sender:
                flags.append("domain_mismatch")
                score += 80.0
            if ctx.business.user_reports_30d and int(ctx.business.user_reports_30d) > 10:
                flags.append("high_user_reports")
                score += 40.0
                
        # 3. Scam Keywords
        text = ctx.normalized_message.normalized_text if ctx.normalized_message else ""
        scam_keywords = ["otp", "password", "urgent payment", "click here to claim", "lottery", "release package"]
        for kw in scam_keywords:
            if kw in text:
                flags.append(f"suspicious_keyword_{kw.replace(' ', '_')}")
                score += 40.0
                
        # 4. Determine Level
        if score >= 70.0:
            level = "HIGH"
            recommendation = "mute"
        elif score >= 40.0:
            level = "MEDIUM"
            recommendation = "digest"
            
        return RiskAssessment(
            level=level,
            score=min(score, 100.0),
            flags=flags,
            recommendation=recommendation
        )
