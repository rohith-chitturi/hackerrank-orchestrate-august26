import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import FatigueAssessment

class FatigueService:
    def evaluate(self, ctx: RoutingContext) -> FatigueAssessment:
        is_fatigued = False
        dnd_active = False
        reason = ""
        
        if ctx.user:
            if ctx.user.do_not_disturb_window == "always":
                dnd_active = True
                reason = "DND is active"
                
            if ctx.user.notifications_dismissed_30d and int(ctx.user.notifications_dismissed_30d) > 30:
                is_fatigued = True
                reason = "User is fatigued from excessive notifications"
                
        return FatigueAssessment(
            is_fatigued=is_fatigued,
            dnd_active=dnd_active,
            reason=reason
        )
