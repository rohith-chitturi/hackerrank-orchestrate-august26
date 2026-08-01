import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import UrgencyAssessment

class UrgencyService:
    def evaluate(self, ctx: RoutingContext) -> UrgencyAssessment:
        score = 0.0
        keywords = []
        time_sensitive = False
        deadline = None
        
        text = ctx.normalized_message.normalized_text if ctx.normalized_message else ""
        
        # 1. High Urgency Keywords
        high_urgency = ["urgent", "emergency", "immediately", "asap", "call me now"]
        for kw in high_urgency:
            if kw in text:
                score += 50.0
                keywords.append(kw)
                time_sensitive = True
                
        # 2. Time Deadlines
        time_deadlines = ["today", "tomorrow", "tonight", "within 24 hours"]
        for kw in time_deadlines:
            if kw in text:
                score += 30.0
                keywords.append(kw)
                time_sensitive = True
                if not deadline:
                    deadline = kw
                
        # 3. Action keywords
        action_kws = ["please reply", "need an answer", "let me know soon"]
        for kw in action_kws:
            if kw in text:
                score += 20.0
                keywords.append(kw)
                
        return UrgencyAssessment(
            score=min(score, 100.0),
            deadline=deadline,
            keywords=keywords,
            time_sensitive=time_sensitive
        )
