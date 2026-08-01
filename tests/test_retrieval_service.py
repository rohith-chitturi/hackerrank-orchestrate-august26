import os
import sys
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "code")))

from models.domain import Message
from models.results import NormalizedMessage
from models.state import RoutingContext
from services.retrieval_service import RetrievalService

def test_retrieval_user_scoped():
    history_data = {
        "user_id": ["u1", "u1", "u2"],
        "message_id": ["hist1", "hist2", "hist3"],
        "message_text": ["pizza is great", "call me tomorrow", "pizza is terrible"]
    }
    history_df = pd.DataFrame(history_data)
    
    svc = RetrievalService(history_df)
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u3", created_at="2026", message_text="do you like pizza?", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="do you like pizza?", normalized_text="do you like pizza", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    ctx = RoutingContext(message=msg, normalized_message=norm)
    
    results = svc.retrieve(ctx, top_k=2)
    
    assert len(results) == 1
    assert results[0].message_id == "hist1"
    
def test_retrieval_no_match():
    history_data = {
        "user_id": ["u1"],
        "message_id": ["hist1"],
        "message_text": ["apples and oranges"]
    }
    history_df = pd.DataFrame(history_data)
    
    svc = RetrievalService(history_df)
    
    msg = Message(message_id="m1", user_id="u1", conversation_type="personal", group_id=None, business_id=None, sender_user_id="u3", created_at="2026", message_text="pizza", media_type="", media_id="", forwarded_count=0)
    norm = NormalizedMessage(raw_text="pizza", normalized_text="pizza", language="en", mentions=[], urls=[], phone_numbers=[], currency=[], dates=[], times=[], entities=[])
    ctx = RoutingContext(message=msg, normalized_message=norm)
    
    results = svc.retrieve(ctx, top_k=2)
    
    assert len(results) == 0

if __name__ == "__main__":
    test_retrieval_user_scoped()
    test_retrieval_no_match()
    print("Retrieval service tests passed!")
