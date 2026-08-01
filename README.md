# Message Notification Router

## Hybrid AI Notification Routing System

### Features
- Personalized routing
- BM25 evidence retrieval
- Hybrid deterministic + LLM
- OCR
- ASR
- Explainability

### Architecture Diagram

```mermaid
graph TD
    IncomingMessage["Incoming Message"] --> MessageNormalizer["Message Normalizer"]
    MessageNormalizer --> RoutingContext["RoutingContext"]
    
    RoutingContext --> RiskService["Risk Service"]
    RoutingContext --> TrustService["Trust Service"]
    RoutingContext --> UrgencyService["Urgency Service"]
    RoutingContext --> PreferenceService["Preference Service"]
    RoutingContext --> FatigueService["Fatigue Service"]
    RoutingContext --> RetrievalService["Retrieval Service"]
    
    RiskService --> DecisionEngine["Decision Engine"]
    TrustService --> DecisionEngine
    UrgencyService --> DecisionEngine
    PreferenceService --> DecisionEngine
    FatigueService --> DecisionEngine
    RetrievalService --> DecisionEngine
    
    DecisionEngine --> CandidateDecision["Candidate Decision"]
    CandidateDecision --> LLMValidator["LLM Validator"]
    LLMValidator --> OutputCSV["output.csv"]
```

### Pipeline

```text
Incoming Message
↓
Normalizer
↓
RoutingContext
↓
Feature Services
↓
Decision Engine
↓
LLM Validator
↓
output.csv
```

### Tech Stack
- Python
- Pandas
- BM25
- Gemini
- OCR
- ASR

### Running

```bash
pip install -r requirements.txt
python code/main.py
```
