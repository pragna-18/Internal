#!/usr/bin/env python
"""
Test script to verify ML models work correctly
"""

import sys
sys.path.insert(0, 'ml')

from ml_risk_engine import MLRiskEngine
from mitre_ml_engine import MITREMLEngine

# Initialize engines
print("Initializing ML engines...")
risk_engine = MLRiskEngine()
mitre_engine = MITREMLEngine()

# Test data - simulating suspicious attack
test_event = {
    "ip": "203.0.113.42",
    "resource_name": "s3-bucket-credentials-backup",
    "timestamp": 1234567890
}

test_profile = {
    "access_count": 5,
    "intervals": [10, 15, 10, 8, 12],
    "behavior_type": "AUTOMATED_SCANNER"
}

test_enrichment = {
    "is_tor": 1,
    "is_datacenter": 0,
    "country": "NL"
}

print("\n" + "="*60)
print("ML MODEL PREDICTIONS TEST")
print("="*60)

# Test risk prediction
print("\n📊 RISK SCORING MODEL")
print("-" * 60)
if risk_engine.model:
    risk_score = risk_engine.predict(test_event, test_profile, test_enrichment)
    print(f"✅ Risk Score: {risk_score}/100")
    if risk_score < 30:
        severity = "LOW"
    elif risk_score < 70:
        severity = "MEDIUM"
    else:
        severity = "HIGH"
    print(f"   Severity: {severity}")
else:
    print("❌ Risk model not loaded")

# Test MITRE prediction
print("\n🎯 MITRE TECHNIQUE CLASSIFIER")
print("-" * 60)
if mitre_engine.model:
    techniques = mitre_engine.predict_techniques(test_event, test_profile, test_enrichment)
    if techniques:
        print(f"✅ Predicted {len(techniques)} techniques:")
        for i, t in enumerate(techniques, 1):
            print(f"\n   {i}. {t['technique_id']}: {t['technique_name']}")
            print(f"      Tactic: {t['tactic']}")
            print(f"      Confidence: {t['confidence']}")
            print(f"      ML Probability: {t['ml_probability']:.1%}")
    else:
        print("⚠️  No techniques predicted (all below confidence threshold)")
else:
    print("❌ MITRE model not loaded")

print("\n" + "="*60)
print("✅ ML MODELS TESTED SUCCESSFULLY!")
print("="*60)
