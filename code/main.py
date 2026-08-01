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
from services.fatigue_service import FatigueService
from engines.decision_engine import DecisionEngine
from models.domain import Message
from models.state import RoutingContext

def run_vertical_slice(dataset_path: str, input_csv: str, output_csv: str):
    print(f"Loading datasets from {dataset_path}...")
    loader = DataLoader(dataset_path)
    normalizer = MessageNormalizer()
    
    # Initialize Services
    risk_svc = RiskService()
    trust_svc = TrustService()
    urgency_svc = UrgencyService()
    pref_svc = PreferenceService()
    fatigue_svc = FatigueService()
    
    from services.llm_validator_service import LLMValidatorService
    llm_validator = LLMValidatorService()
    
    from services.retrieval_service import RetrievalService
    print("Building BM25 Index for historical messages...")
    retrieval_svc = RetrievalService(loader.load_message_history())
    
    # Initialize Engines
    decision_engine = DecisionEngine()
    
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
        
        fatigue_assessment = fatigue_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, fatigue_assessment=fatigue_assessment)
        
        trust_result = trust_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, trust_result=trust_result)
        
        urgency_assessment = urgency_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, urgency_assessment=urgency_assessment)
        
        risk_assessment = risk_svc.evaluate(ctx)
        ctx = dataclasses.replace(ctx, risk_assessment=risk_assessment)
        
        retrieved_evidence = retrieval_svc.retrieve(ctx)
        ctx = dataclasses.replace(ctx, retrieved_evidence=retrieved_evidence)
        
        # 4. Decision Engine (Deterministic Fusion)
        decision = decision_engine.evaluate(ctx)
        ctx = dataclasses.replace(ctx, final_decision=decision)
        
        # 5. LLM Validator
        validation_result = llm_validator.evaluate(ctx)
        ctx = dataclasses.replace(ctx, validation_result=validation_result)
        
        final_action = validation_result.new_action if validation_result.status == "OVERRIDDEN" and validation_result.new_action else decision.action
        final_reason = f"{decision.reason} | {validation_result.reason}"
        
        # 6. Output strictly conforms to requirements
        # Extract comma-separated evidence IDs (handling "none")
        evidence_str = ",".join(decision.evidence) if decision.evidence and decision.evidence != ["none"] else "none"
        
        results.append({
            "message_id": msg.message_id,
            "action": final_action,
            "message_type": decision.category,
            "reason": final_reason,
            "confidence": decision.confidence,
            "evidence_message_ids": evidence_str
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
