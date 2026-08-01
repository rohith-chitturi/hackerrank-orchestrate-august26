import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from models.state import RoutingContext
from models.results import PreferenceProfile

class PreferenceService:
    def evaluate(self, ctx: RoutingContext) -> PreferenceProfile:
        likes_promotions = True
        reads_family = True
        muted_groups = []
        notification_tolerance = "HIGH"
        business_affinity = {}
        
        # 1. Business Preferences
        if ctx.user_business_history:
            history = ctx.user_business_history
            likes_promotions = str(history.allows_promotions) == "1"
            
            affinity_score = 50.0
            if history.messages_replied_30d and int(history.messages_replied_30d) > 0:
                affinity_score += 30.0
            if history.messages_dismissed_30d and int(history.messages_dismissed_30d) > 5:
                affinity_score -= 20.0
                
            business_affinity[history.business_id] = min(100.0, max(0.0, affinity_score))
            
        # 2. Group Preferences
        if ctx.group_member:
            if str(ctx.group_member.group_muted_by_user) == "1":
                muted_groups.append(ctx.group_member.group_id)
                
        # 3. User Baseline
        if ctx.user:
            if ctx.user.notifications_dismissed_30d and int(ctx.user.notifications_dismissed_30d) > 50:
                notification_tolerance = "LOW"
            elif ctx.user.notifications_dismissed_30d and int(ctx.user.notifications_dismissed_30d) > 20:
                notification_tolerance = "MEDIUM"
                
        return PreferenceProfile(
            likes_promotions=likes_promotions,
            reads_family=reads_family,
            muted_groups=muted_groups,
            notification_tolerance=notification_tolerance,
            business_affinity=business_affinity
        )
