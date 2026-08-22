import json
import os
import time  # <-- Imported time module
from agent import get_agent_chat_session

EVAL_FILE = os.path.join("evaluation", "visible-cases.json")

def run_evaluation():
    print("Starting Automated Evaluation Suite... (This will take a few minutes due to API rate limits)\n")
    
    with open(EVAL_FILE, "r", encoding="utf-8") as f:
        eval_data = json.load(f)
        
    cases = eval_data.get("cases", [])
    total_cases = len(cases)
    passed_cases = 0
    
    for index, case in enumerate(cases, 1):
        case_id = case["id"]
        category = case["category"]
        print(f"[{index}/{total_cases}] Testing Case: {case_id} ({category})")
        
        chat_session = get_agent_chat_session()
        final_response = ""
        
        for message in case["messages"]:
            try:
                response = chat_session.send_message(message["content"])
                final_response = response.text
                
                # Small pause between messages in a multi-turn conversation
                time.sleep(3) 
                
            except Exception as e:
                # If we still hit a rate limit, pause for 15 seconds and retry once
                if "429" in str(e):
                    print("  [API Rate Limit Hit] Pausing for 15 seconds to recover...")
                    time.sleep(15)
                    try:
                        retry_response = chat_session.send_message(message["content"])
                        final_response = retry_response.text
                    except Exception as retry_e:
                        final_response = f"ERROR on Retry: {retry_e}"
                else:
                    final_response = f"ERROR: {e}"
                
        # --- Run Assertions ---
        passed = True
        expectations = case.get("expect", {})
        final_response_lower = final_response.lower()
        
        for required_text in expectations.get("must_include", []):
            if required_text.lower() not in final_response_lower:
                print(f"  ❌ FAILED: Missing required exact text: '{required_text}'")
                passed = False
                
        for forbidden_text in expectations.get("must_not_include", []):
            if forbidden_text.lower() in final_response_lower:
                print(f"  ❌ FAILED: Found forbidden text: '{forbidden_text}'")
                passed = False
                
        for source in expectations.get("required_sources", []):
            if source.lower() not in final_response_lower:
                print(f"  ❌ FAILED: Missing required source citation: '{source}'")
                passed = False
                
        if passed:
            print("  ✅ PASSED")
            passed_cases += 1
        else:
            print(f"  Agent Output was:\n  --- \n  {final_response}\n  ---")
            
        print("-" * 50)
        
        # Mandatory 12-second cooldown before the next test case to prevent Error 429
        if index < total_cases:
            time.sleep(12) 
        
    print(f"\nEvaluation Complete! Score: {passed_cases}/{total_cases}")
    
if __name__ == "__main__":
    run_evaluation()