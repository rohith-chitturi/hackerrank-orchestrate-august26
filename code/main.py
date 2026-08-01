import os
import sys
import argparse
import pandas as pd
import numpy as np
import dataclasses

sys.path.append(os.path.dirname(__file__))

from core.dataloader import DataLoader
from core.normalizer import MessageNormalizer
from services.risk_service import RiskService
from services.trust_service import TrustService
from services.urgency_service import UrgencyService
from services.preference_service import PreferenceService
from models.domain import Message
from models.state import RoutingContext
from models.results import Decision

def run_vertical_slice(dataset_path: str, input_csv: str, output_csv: str):
    print(f"Loading datasets from {dataset_path}...")
    loader = DataLoader(dataset_path)
    normalizer = MessageNormalizer()
    risk_svc = RiskService()
    trust_svc = TrustService()
    urgency_svc = UrgencyService()
    pref_svc = PreferenceService()
    
    print(f"Reading incoming messages stream from {input_csv}...")
    messages_csv = os.path.join(dataset_path, input_csv)
    messages_df = pd.read_csv(messages_csv).replace({np.nan: None})
    
    results = []
    
    for idx, row in messages_df.iterrows():
        # 1. Parse row into Message model
        msg_dict = row.to_dict()
        valid_keys = Message.__dataclass_fields__.keys()
        msg_filtered = {k: v for k, v in msg_dict.items() if k in valid_keys}
        msg = Message(**msg_filtered)
        
        # 2. Hydrate Context & Normalize (Base state)
        ctx = RoutingContext(
            message=msg,
            normalized_message=normalizer.normalize(msg),
            user=loader.get_user(msg.user_id),
            group=loader.get_group(msg.group_id) if msg.group_id else None,
            business=loader.get_business(msg.business_id) if msg.business_id else None,
            group_member=loader.get_user_group_relationship(msg.user_id, msg.group_id) if msg.group_id else None,
            user_business_history=loader.get_user_business_relationship(msg.user_id, msg.business_id) if msg.business_id else None
        )
        
        # 3. Compute Features (Immutable state update)
        preference_profile = pref_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, preference_profile=preference_profile)
        
        trust_result = trust_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, trust_result=trust_result)
        
        urgency_assessment = urgency_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, urgency_assessment=urgency_assessment)
        
        risk_assessment = risk_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, risk_assessment=risk_assessment)
        
        # 4. Decision Engine (Deterministic Fusion)
        action = "digest" if msg.group_id else "notify"
        reason = f"Stub decision: Fallback default rule applied for {msg.conversation_type}."
        
        # Preference overrides
        if msg.group_id and msg.group_id in ctx.preference_profile.muted_groups:
            action = "mute"
            reason = "PreferenceService Override: User explicitly muted this group."
            
        if msg.business_id and msg.conversation_type == "business":
            if not ctx.preference_profile.likes_promotions:
                action = "digest"
                reason = "PreferenceService Override: User opted out of promotions."
        
        # Trust override for highly trusted businesses
        if ctx.trust_result.score >= 80.0 and msg.business_id:
            action = "notify"
            reason = f"TrustService Override: {ctx.trust_result.reasons}"
            
        # Urgency override forces notifications for time-sensitive messages
        if ctx.urgency_assessment.score >= 50.0:
            action = "notify"
            reason = f"UrgencyService Override: detected {ctx.urgency_assessment.keywords}"
            
        # Risk override (highest priority deterministic rule)
        if ctx.risk_assessment.level == "HIGH":
            action = "mute"
            reason = f"RiskService Override: {ctx.risk_assessment.flags}"
            
        confidence = 0.5
        evidence = "none"
        
        # Output strictly conforms to requirements
        results.append({
            "message_id": msg.message_id,
            "action": action,
            "message_type": "unknown",
            "reason": reason,
            "confidence": confidence,
            "evidence_message_ids": evidence
        })
        
    output_path = os.path.join(dataset_path, output_csv)
    print(f"Writing {len(results)} predictions to {output_path}...")
    output_df = pd.DataFrame(results)
    output_df.to_csv(output_path, index=False)
    print("Pipeline complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run message notification router pipeline")
    parser.add_argument("--eval", action="store_true", help="Run on sample_messages.csv for evaluation")
    args = parser.parse_args()
    
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
    
    if args.eval:
        run_vertical_slice(dataset_path, "sample_messages.csv", "sample_output.csv")
    else:
        run_vertical_slice(dataset_path, "messages.csv", "output.csv")
