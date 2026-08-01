import os
import pandas as pd

def test_output_schema():
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dataset"))
    output_path = os.path.join(dataset_path, "output.csv")
    
    if not os.path.exists(output_path):
        print("Skipping schema test: output.csv not found")
        return
        
    df = pd.read_csv(output_path)
    
    # 1. Column Check
    expected_cols = ["message_id", "action", "message_type", "reason", "confidence", "evidence_message_ids"]
    assert list(df.columns) == expected_cols, f"Columns mismatch. Expected {expected_cols}, got {list(df.columns)}"
    
    # 2. Action Values Check
    valid_actions = {"notify", "digest", "mute"}
    actions_found = set(df["action"].dropna().unique())
    invalid_actions = actions_found - valid_actions
    assert not invalid_actions, f"Invalid actions found: {invalid_actions}"
    
    # 3. Confidence Check
    if not df["confidence"].isna().all():
        assert df["confidence"].dropna().between(0, 1).all(), "Confidence not between 0 and 1"
        
    print("Schema test passed!")

if __name__ == "__main__":
    test_output_schema()
