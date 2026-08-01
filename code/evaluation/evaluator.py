import pandas as pd
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
import warnings
warnings.filterwarnings("ignore")

def evaluate_predictions(predictions_path: str, ground_truth_path: str):
    print("Running Evaluation Loop...")
    
    # Load ground truth and predictions
    gt_df = pd.read_csv(ground_truth_path)
    pred_df = pd.read_csv(predictions_path)
    
    # Ensure they have the same message_ids
    merged = pd.merge(gt_df, pred_df, on="message_id", suffixes=('_true', '_pred'))
    
    if len(merged) == 0:
        print("Error: No overlapping message_ids found between predictions and ground truth.")
        return
        
    print(f"Evaluated on {len(merged)} sample messages.")
    
    # Action metrics
    y_true_action = merged['action_true'].fillna('unknown')
    y_pred_action = merged['action_pred'].fillna('unknown')
    
    acc_action = accuracy_score(y_true_action, y_pred_action)
    p_act, r_act, f_act, _ = precision_recall_fscore_support(y_true_action, y_pred_action, average='weighted', zero_division=0)
    
    # Message type metrics
    y_true_type = merged['message_type_true'].fillna('unknown')
    y_pred_type = merged['message_type_pred'].fillna('unknown')
    
    acc_type = accuracy_score(y_true_type, y_pred_type)
    
    print("\n--- RESULTS ---")
    print(f"Action Accuracy:      {acc_action:.2%}")
    print(f"Action F1 (Weighted): {f_act:.2%}")
    print(f"Msg Type Accuracy:    {acc_type:.2%}")
    
    print("\n--- ACTION CONFUSION MATRIX ---")
    print(pd.crosstab(y_true_action, y_pred_action, rownames=['Actual'], colnames=['Predicted']))
    print("-------------------------------\n")

if __name__ == "__main__":
    import os
    
    dataset_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "dataset"))
    
    ground_truth_path = os.path.join(dataset_path, "sample_messages.csv")
    predictions_path = os.path.join(dataset_path, "sample_output.csv")
    
    if os.path.exists(predictions_path):
        evaluate_predictions(predictions_path, ground_truth_path)
    else:
        print(f"Please run pipeline on sample_messages.csv to generate {predictions_path} first.")
