import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import Decision

class DecisionEngine:
    def _classify_message_type(self, ctx: RoutingContext) -> str:
        text = ctx.normalized_message.normalized_text if ctx.normalized_message else ""
        
        # 1. Scam / Spam
        if ctx.risk_assessment and ctx.risk_assessment.level == "HIGH":
            return "scam" if "phishing" in str(ctx.risk_assessment.flags) or "domain" in str(ctx.risk_assessment.flags) else "spam"
            
        # 2. Payment
        if any(kw in text for kw in ["payment", "bill", "invoice", "transfer", "otp"]):
            return "payment"
            
        # 3. Promotion
        if any(kw in text for kw in ["offer", "discount", "promo", "off today", "sale", "free"]):
            return "promotion"
            
        # 4. Urgent / Event
        if ctx.urgency_assessment and ctx.urgency_assessment.time_sensitive:
            return "urgent"
        if any(kw in text for kw in ["birthday", "party", "wedding", "meeting", "event"]):
            return "event"
            
        # 5. Forward
        if ctx.message.forwarded_count and int(ctx.message.forwarded_count) > 0:
            return "forward"
            
        # 6. Business Update
        if ctx.message.business_id:
            return "business_update"
            
        # 7. Greeting / Personal
        if any(kw in text for kw in ["hello", "hi", "good morning", "thanks", "welcome"]):
            return "greeting"
            
        return "personal"

    def evaluate(self, ctx: RoutingContext) -> Decision:
        action = "notify"
        reason = "Default notify"
        confidence = 0.5
        
        # 1. Base Heuristic
        if ctx.message.group_id:
            action = "digest"
            reason = "Group messages default to digest."
            confidence = 0.6
            
        # 2. Preference & Fatigue Overrides
        if ctx.preference_profile:
            if ctx.message.group_id and ctx.message.group_id in ctx.preference_profile.muted_groups:
                action = "mute"
                reason = "Preference: Group explicitly muted."
                confidence = 0.9
            if ctx.message.business_id and ctx.message.conversation_type == "business":
                if not ctx.preference_profile.likes_promotions:
                    action = "digest"
                    reason = "Preference: User opted out of promotions."
                    confidence = 0.8
                    
        if ctx.fatigue_assessment:
            if ctx.fatigue_assessment.dnd_active:
                action = "digest"
                reason = "Fatigue: DND is active."
                confidence = 0.8
            elif ctx.fatigue_assessment.is_fatigued and action == "notify":
                action = "digest"
                reason = "Fatigue: User is suffering notification fatigue."
                confidence = 0.7
                
        # 3. Trust Override (Can promote digest -> notify for highly trusted businesses)
        if ctx.trust_result and ctx.trust_result.score >= 80.0 and ctx.message.business_id:
            if action == "digest" and not (ctx.fatigue_assessment and ctx.fatigue_assessment.dnd_active):
                action = "notify"
                reason = f"Trust: Highly trusted business ({ctx.trust_result.reasons})."
                confidence = 0.75
                
        # 4. Urgency Override (Forces notify for emergencies)
        if ctx.urgency_assessment and ctx.urgency_assessment.score >= 50.0:
            action = "notify"
            reason = f"Urgency: Detected time-sensitive keywords ({ctx.urgency_assessment.keywords})."
            confidence = 0.9
            
        # 5. Risk Override (Highest priority, suppresses scams)
        if ctx.risk_assessment and ctx.risk_assessment.level == "HIGH":
            action = "mute"
            reason = f"Risk: High risk detected ({ctx.risk_assessment.flags})."
            confidence = 0.95
            
        # 6. Evidence Extraction
        evidence = [ev.message_id for ev in ctx.retrieved_evidence] if ctx.retrieved_evidence else ["none"]
        
        # 7. Message Type Classification
        message_type = self._classify_message_type(ctx)
        
        if confidence >= 0.9:
            confidence_band = "VERY_HIGH"
        elif confidence >= 0.75:
            confidence_band = "HIGH"
        elif confidence >= 0.6:
            confidence_band = "MEDIUM"
        else:
            confidence_band = "LOW"
            
        return Decision(
            intent="unknown",
            category=message_type,
            priority="unknown",
            action=action,
            confidence=confidence,
            confidence_band=confidence_band,
            reason=reason,
            evidence=evidence
        )
