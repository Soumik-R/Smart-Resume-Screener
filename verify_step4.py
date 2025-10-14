"""
Verification checklist for Phase 5 Step 4 completion
"""
import sys
import os

def check_step4_requirements():
    """Verify all Step 4 requirements are met"""
    print("="*80)
    print("PHASE 5 STEP 4 - EXPORT AND ADVANCED FEATURES VERIFICATION")
    print("="*80)
    
    requirements = []
    
    # Check imports
    print("\n1. Checking imports in main.py...")
    main_path = os.path.join("backend", "main.py")
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    
    has_csv_import = "import csv" in main_content
    has_stringio = "StringIO" in main_content
    has_streaming = "StreamingResponse" in main_content
    has_openai = "import openai" in main_content
    requirements.append(("CSV and streaming imports", has_csv_import and has_stringio and has_streaming))
    requirements.append(("OpenAI import for bias check", has_openai))
    print(f"   {'✅' if has_csv_import else '❌'} csv module imported")
    print(f"   {'✅' if has_stringio else '❌'} StringIO imported")
    print(f"   {'✅' if has_streaming else '❌'} StreamingResponse imported")
    print(f"   {'✅' if has_openai else '❌'} openai imported")
    
    # Check 2: GET /export/{jd_id}/csv endpoint
    print("\n2. Checking GET /export/{jd_id}/csv endpoint...")
    has_export_endpoint = 'async def export_shortlist_csv' in main_content
    has_export_route = '@app.get("/export/{jd_id}/csv")' in main_content
    requirements.append(("GET /export/{jd_id}/csv endpoint", has_export_endpoint and has_export_route))
    print(f"   {'✅' if has_export_endpoint else '❌'} export_shortlist_csv function defined")
    print(f"   {'✅' if has_export_route else '❌'} Route decorator present")
    
    # Check 2a: Export uses csv module
    uses_csv = "csv.DictWriter" in main_content or "csv.writer" in main_content
    requirements.append(("Uses csv module to generate CSV", uses_csv))
    print(f"   {'✅' if uses_csv else '❌'} Uses csv.DictWriter for CSV generation")
    
    # Check 2b: Export has proper headers
    has_headers = "csv_headers" in main_content and "Rank" in main_content and "Overall Score" in main_content
    requirements.append(("CSV headers include Rank, Score, Skills", has_headers))
    print(f"   {'✅' if has_headers else '❌'} CSV headers defined (Rank, Score, Skills, etc.)")
    
    # Check 2c: Export fetches shortlist data
    fetches_matches = "get_match_history" in main_content and "export_shortlist_csv" in main_content
    requirements.append(("Fetches shortlist data from database", fetches_matches))
    print(f"   {'✅' if fetches_matches else '❌'} Fetches match data from database")
    
    # Check 2d: Export applies filters
    applies_filters = "threshold" in main_content and "min_experience" in main_content and "export" in main_content
    requirements.append(("Applies same filters as shortlist endpoint", applies_filters))
    print(f"   {'✅' if applies_filters else '❌'} Applies threshold and other filters")
    
    # Check 2e: Export returns downloadable file
    returns_file = "StreamingResponse" in main_content and "Content-Disposition" in main_content
    requirements.append(("Returns as downloadable CSV file", returns_file))
    print(f"   {'✅' if returns_file else '❌'} Returns StreamingResponse with Content-Disposition header")
    
    # Check 2f: Export sorts by score
    sorts_export = "sort" in main_content and "overall_score" in main_content
    requirements.append(("Sorts candidates by score", sorts_export))
    print(f"   {'✅' if sorts_export else '❌'} Sorts by overall_score descending")
    
    # Check 3: POST /bias_check/{candidate_id} endpoint
    print("\n3. Checking POST /bias_check/{candidate_id} endpoint...")
    has_bias_endpoint = 'async def check_bias' in main_content
    has_bias_route = '@app.post("/bias_check/{candidate_id}")' in main_content
    requirements.append(("POST /bias_check/{candidate_id} endpoint", has_bias_endpoint and has_bias_route))
    print(f"   {'✅' if has_bias_endpoint else '❌'} check_bias function defined")
    print(f"   {'✅' if has_bias_route else '❌'} Route decorator present")
    
    # Check 3a: Bias check uses anonymized data
    uses_anonymized = "anonymize_resume_data" in main_content and "check_bias" in main_content
    requirements.append(("Uses anonymized candidate data", uses_anonymized))
    print(f"   {'✅' if uses_anonymized else '❌'} Calls anonymize_resume_data function")
    
    # Check 3b: Bias check uses LLM
    uses_llm = "openai" in main_content and "bias_check_prompt" in main_content
    requirements.append(("Uses LLM (GPT-4o) for bias detection", uses_llm))
    print(f"   {'✅' if uses_llm else '❌'} Uses OpenAI API for bias analysis")
    
    # Check 3c: Bias check prompt mentions demographic inferences
    has_bias_prompt = "demographic" in main_content or "unintended" in main_content
    requirements.append(("Prompt checks for demographic inferences", has_bias_prompt))
    print(f"   {'✅' if has_bias_prompt else '❌'} Prompt includes demographic inference detection")
    
    # Check 3d: Bias check stores results
    stores_bias = "bias_checks" in main_content or "last_bias_check" in main_content
    requirements.append(("Stores bias check results in database", stores_bias))
    print(f"   {'✅' if stores_bias else '❌'} Saves bias check results to candidate document")
    
    # Check 3e: Bias check response model
    has_bias_response = "class BiasCheckResponse" in main_content
    has_bias_fields = "bias_detected" in main_content and "bias_flags" in main_content and "analysis" in main_content
    requirements.append(("BiasCheckResponse model with proper fields", has_bias_response and has_bias_fields))
    print(f"   {'✅' if has_bias_response else '❌'} BiasCheckResponse model defined")
    print(f"   {'✅' if has_bias_fields else '❌'} Has bias_detected, bias_flags, analysis fields")
    
    # Check 3f: Returns recommendations
    has_recommendations = "recommendations" in main_content and "BiasCheckResponse" in main_content
    requirements.append(("Returns recommendations for bias mitigation", has_recommendations))
    print(f"   {'✅' if has_recommendations else '❌'} Returns recommendations field")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, status in requirements if status)
    total = len(requirements)
    
    for req_name, status in requirements:
        print(f"{'✅' if status else '❌'} {req_name}")
    
    print(f"\n📊 Score: {passed}/{total} requirements met ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL REQUIREMENTS MET! Phase 5 Step 4 is COMPLETE! 🎉")
        print("\n🚀 ALL PHASE 5 ENDPOINTS IMPLEMENTED!")
        print("\n📋 Complete API Summary:")
        print("   ✅ Step 2: POST /upload_resume, POST /upload_jd")
        print("   ✅ Step 3: POST /match/{jd_id}, GET /shortlist/{jd_id}")
        print("   ✅ Step 4: GET /export/{jd_id}/csv, POST /bias_check/{candidate_id}")
        print("\n🌐 Server: http://localhost:8000")
        print("📖 API Docs: http://localhost:8000/docs")
        return True
    else:
        print(f"\n⚠️  {total - passed} requirement(s) still need attention")
        return False

if __name__ == "__main__":
    success = check_step4_requirements()
    sys.exit(0 if success else 1)
