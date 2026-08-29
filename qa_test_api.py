import requests
import json

# Person 2's live local IP
BASE_URL = "http://172.31.98.4:8000/api/v1/scan/vpa"

test_cases = [
    {"name": "Trusted Merchant", "vpa": "demo_trusted_merchant@bank", "expected": "green"},
    {"name": "Unknown Entity", "vpa": "demo_caution_unknown@okaxis", "expected": "yellow"},
    {"name": "Flagged Scammer", "vpa": "demo_flagged_scammer@paytm", "expected": "red"}
]

print("🚀 Running QA Checklist against Person 2's API...\n")

for test in test_cases:
    try:
        response = requests.post(BASE_URL, json={"vpa": test["vpa"]})
        data = response.json()
        
        actual_verdict = data.get("verdict", "").lower()
        score = data.get("safety_score", "N/A")
        
        if actual_verdict == test["expected"]:
            print(f"✅ PASS: {test['name']} -> Verdict: {actual_verdict.upper()} (Score: {score})")
        else:
            print(f"❌ FAIL: {test['name']} -> Expected {test['expected']}, got {actual_verdict.upper()}")
            
    except Exception as e:
        print(f"⚠️ ERROR connecting to API for {test['name']}: {e}")

print("\nQA Test Complete.")