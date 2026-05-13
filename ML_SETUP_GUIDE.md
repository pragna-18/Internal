# 🤖 ML Model Setup & Configuration Guide

**SentinelMesh ML Infrastructure** - Complete Setup for Risk Scoring & MITRE Technique Classification

---

## ✅ ML Installation Status

### Installed Packages
- ✅ **scikit-learn** 1.5.1 - Machine Learning framework (RandomForest models)
- ✅ **joblib** 1.3.2 - Model serialization and persistence
- ✅ **numpy** 1.26.4 - Numerical computing library
- ✅ **pandas** 2.2.2 - Data manipulation and analysis
- ✅ **scipy** 1.13.1 - Scientific computing (required by sklearn)

### Pre-trained Models (Ready to Use)

#### 1. **Risk Scoring Model** (`backend/ml/risk_model.joblib`)
- **Type**: RandomForestRegressor (100 trees)
- **Size**: 12.5 MB
- **Purpose**: Predicts attack risk scores (0-100)
- **Input Features** (8):
  - `access_count` - Number of probes by attacker
  - `avg_interval` - Average seconds between probes
  - `interval_variance` - Variance in probe intervals
  - `keyword_hit_count` - Dangerous keywords found
  - `is_tor` - Binary: attack from TOR network
  - `is_datacenter` - Binary: attack from datacenter
  - `hour_of_day` - Time of attack (0-23)
  - `unique_honeypots_hit` - Number of honeypots targeted

**Feature Importance Rankings**:
```
1. avg_interval:       93.38% ⭐⭐⭐ (Most important)
2. interval_variance:   2.89%
3. hour_of_day:         1.42%
4. access_count:        0.86%
5. keyword_hit_count:   0.59%
6. unique_honeypots_hit: 0.33%
7. is_datacenter:       0.32%
8. is_tor:              0.23%
```

**Output**: Risk score 0-100
- 0-30: LOW risk
- 31-69: MEDIUM risk  
- 70-100: HIGH risk

---

#### 2. **MITRE Technique Classifier** (`backend/ml/mitre_model.joblib`)
- **Type**: RandomForestClassifier (100 trees, 9 classes)
- **Size**: 1.8 MB
- **Purpose**: Predicts which MITRE ATT&CK techniques are being used
- **Input Features** (8):
  - `resource_type` - Cloud resource targeted (S3, EC2, API, RDS, other)
  - `keywords_present` - Bitmask of threat keywords found
  - `access_pattern` - Attack pattern (scanner, human, systematic)
  - `repetition_count` - How many times same resource hit
  - `behavior_duration` - Seconds of activity
  - `is_tor` - Binary: TOR origin
  - `is_datacenter` - Binary: datacenter origin
  - `intent_score` - Attack intent (0-100)

**Feature Importance Rankings**:
```
1. keywords_present:  27.48% ⭐⭐⭐ (Most important)
2. behavior_duration: 17.48% ⭐⭐
3. intent_score:      17.19% ⭐⭐
4. resource_type:     15.02% ⭐⭐
5. access_pattern:     7.88%
6. repetition_count:   6.70%
7. is_datacenter:      4.48%
8. is_tor:             3.77%
```

**Output**: List of predicted MITRE techniques (9 possible classes):
- T1580: Cloud Infrastructure Discovery
- T1619: Cloud Storage Object Discovery
- T1087: Account Discovery
- T1552: Unsecured Credentials
- T1528: Steal Application Access Token
- T1530: Data from Cloud Storage Object
- T1550: Use Alternate Authentication Material
- T1078: Valid Accounts
- T1098: Account Manipulation

---

### Intelligence Data Files

**`backend/data/tor_exit_nodes.txt`** (508 KB)
- TOR exit node IP addresses for detection
- Used by IPEnricher to flag suspicious origins
- Updated periodically for accuracy

---

## 🚀 Using the ML Models

### 1. Load Models in Code

```python
from backend.ml.ml_risk_engine import MLRiskEngine
from backend.ml.mitre_ml_engine import MITREMLEngine

# Initialize
risk_engine = MLRiskEngine()
mitre_engine = MITREMLEngine()

# Use
risk_score = risk_engine.predict(event, profile, enrichment)
techniques = mitre_engine.predict_techniques(event, profile, enrichment)
```

### 2. Risk Score Prediction

```python
event = {
    "ip": "192.168.1.1",
    "resource_name": "s3-bucket-credentials",
}

profile = {
    "access_count": 5,
    "intervals": [10, 15, 10, 8, 12],
}

enrichment = {
    "is_tor": 1,
    "is_datacenter": 0,
}

score = risk_engine.predict(event, profile, enrichment)
# Returns: 54 (MEDIUM RISK)
```

### 3. MITRE Technique Prediction

```python
techniques = mitre_engine.predict_techniques(event, profile, enrichment)

# Example output:
# [
#   {
#     "technique_id": "T1619",
#     "technique_name": "Cloud Storage Object Discovery",
#     "tactic": "Discovery (TA0007)",
#     "confidence": "HIGH",
#     "ml_probability": 0.75,
#     "source": "ML_CLASSIFIER"
#   }
# ]
```

---

## 🔄 Regenerating Models

### When to Regenerate

- After significant code changes to feature extraction
- To train on new synthetic data
- To improve model performance after feedback
- When updating scikit-learn versions (for compatibility)

### Training Scripts

#### Risk Model Training
```bash
cd backend/ml
python generate_training_data.py
```

**Output**:
- Generates 2,000 synthetic attack samples
- Trains RandomForestRegressor on risk patterns
- Saves to `risk_model.joblib`
- Displays feature importance

#### MITRE Model Training
```bash
cd backend/ml
python mitre_training_data.py
```

**Output**:
- Generates 1,500 synthetic MITRE samples
- Trains RandomForestClassifier (9 classes)
- Saves to `mitre_model.joblib`
- Displays feature importance

---

## 🧪 Testing ML Models

### Test Script
```bash
cd backend
python test_ml_models.py
```

Tests both models with sample attack data and verifies:
- ✅ Models load without errors
- ✅ Risk prediction works
- ✅ MITRE classification works
- ✅ Feature extraction functions properly

### Integration with Backend

The backend Flask app automatically loads and uses ML models:

```python
# from backend/main.py
from ml_risk_engine import MLRiskEngine
from mitre_ml_engine import MITREMLEngine

risk_engine = MLRiskEngine()
mitre_mapper = MITREMLEngine()

# Models are used in event processing pipeline
@app.post("/webhook")
def handle_event():
    risk_score = risk_engine.predict(event, profile, enrichment)
    techniques = mitre_mapper.predict_techniques(event, profile, enrichment)
    # ... rest of processing
```

---

## 📊 Model Architecture Details

### Random Forest Regressor (Risk Scoring)

**Configuration**:
```python
RandomForestRegressor(
    n_estimators=100,      # 100 decision trees
    max_depth=15,          # Tree depth
    random_state=42,       # Reproducibility
    n_jobs=-1              # Use all CPU cores
)
```

**Training Data**:
- 2,000 synthetic samples
- Stratified by risk level (low/medium/high)
- Features: 8-dimensional vectors
- Labels: 0-100 continuous scores

**Prediction**:
- Averages predictions from 100 trees
- Clamps output to 0-100 range
- Includes fallback heuristic if model fails

---

### Random Forest Classifier (MITRE Techniques)

**Configuration**:
```python
RandomForestClassifier(
    n_estimators=100,      # 100 decision trees
    max_depth=15,          # Tree depth
    random_state=42,       # Reproducibility
    n_jobs=-1              # Use all CPU cores
)
```

**Training Data**:
- 1,500 synthetic samples (≈166 per technique)
- 9-class classification problem
- Features: 8-dimensional vectors
- Labels: 0-8 (technique indices)

**Prediction**:
- Returns probability for each technique
- Filters by 30% confidence threshold
- Sorts by probability (descending)
- Includes tactic mapping

---

## 🔧 Configuration & Customization

### Adjusting Confidence Threshold

**File**: `backend/ml/mitre_ml_engine.py`

```python
# Current: 30% threshold
threshold = 0.3  # Change this value

# Only techniques with probability > threshold are returned
```

**Guidance**:
- 0.2: More permissive (more false positives)
- 0.3: Balanced (default)
- 0.5: Conservative (fewer predictions)

---

### Hyperparameter Tuning

**File**: `backend/ml/generate_training_data.py` / `backend/ml/mitre_training_data.py`

```python
# Adjust for better performance
model = RandomForestRegressor(
    n_estimators=150,      # More trees = better but slower
    max_depth=20,          # Deeper trees = more complex patterns
    min_samples_split=5,   # Minimum samples for split
    min_samples_leaf=2,    # Minimum samples in leaf
    random_state=42
)
```

---

## 🚨 Fallback Behavior

### If Models Fail to Load

Both engines include automatic fallback mechanisms:

**Risk Engine Fallback**:
- Uses heuristic scoring if model unavailable
- Checks keyword hits, TOR origin, access patterns
- Returns reasonable risk estimate

**MITRE Engine Fallback**:
- Uses rule-based MITRE mapping
- Matches keywords/patterns to techniques
- No ML-driven probability scores

---

## 📈 Model Performance Metrics

### Risk Model
- Training samples: 2,000
- Features: 8
- Output range: 0-100
- Typical prediction time: <1ms per sample
- Memory footprint: 12.5 MB

### MITRE Model
- Training samples: 1,500
- Features: 8
- Output classes: 9
- Typical prediction time: <1ms per sample
- Memory footprint: 1.8 MB

---

## 🔄 Continuous Improvement

### Collecting Training Data

Monitor real attacks to improve models:

```python
# Log high-confidence predictions for validation
if risk_score > 80:
    log_for_review(event, risk_score, techniques)

# Periodically retrain with validated data
python backend/ml/generate_training_data.py
```

### Model Versioning

Keep track of model changes:

```bash
# Save model backup before training new one
cp backend/ml/risk_model.joblib backend/ml/risk_model.joblib.backup

# Train and test new version
python backend/ml/generate_training_data.py

# If better, keep new version; otherwise restore backup
```

---

## 📋 Troubleshooting

### Models Fail to Load
```
⚠️ Model not found at [path]
```
**Solution**: Run training scripts to generate models
```bash
python backend/ml/generate_training_data.py
python backend/ml/mitre_training_data.py
```

### Version Warnings
```
InconsistentVersionWarning: Trying to unpickle from version X.X
```
**Solution**: Models were trained with different scikit-learn version  
**Action**: Regenerate models with current version
```bash
python backend/ml/generate_training_data.py
```

### Predictions Always Return Same Value
**Cause**: Features not being extracted correctly  
**Solution**: Check feature extraction in engine classes

### Memory Issues
**Cause**: Large models with many trees  
**Solution**: Reduce `n_estimators` in training script

---

## 🎯 Summary Checklist

- ✅ scikit-learn 1.5.1 installed
- ✅ joblib 1.3.2 installed  
- ✅ numpy 1.26.4 installed
- ✅ pandas 2.2.2 installed
- ✅ scipy 1.13.1 installed
- ✅ Risk model trained and tested
- ✅ MITRE model trained and tested
- ✅ TOR exit node data available
- ✅ ML engines integrate with backend
- ✅ Fallback mechanisms in place
- ✅ Test script executes successfully

**Your ML infrastructure is fully operational! 🚀**

---

**Last Updated**: April 25, 2026  
**Model Generation Date**: April 25, 2026  
**scikit-learn Version**: 1.5.1  
**Status**: ✅ PRODUCTION READY
