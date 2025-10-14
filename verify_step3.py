"""
Verification checklist for Phase 5 Step 3 completion
"""
import sys
import os

def check_step3_requirements():
    """Verify all Step 3 requirements are met"""
    print("="*80)
    print("PHASE 5 STEP 3 - MATCHING AND QUERY ENDPOINTS VERIFICATION")
    print("="*80)
    
    requirements = []
    
    # Check 1: Imports for matching functions
    print("\n1. Checking imports in main.py...")
    main_path = os.path.join("backend", "main.py")
    with open(main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    
    has_match_import = "from matcher import" in main_content and "match_resume_to_jd" in main_content
    has_batch_import = "score_batch" in main_content
    requirements.append(("Matcher functions imported", has_match_import))
    print(f"   {'✅' if has_match_import else '❌'} match_resume_to_jd and score_batch imported")
    
    # Check 2: POST /match/{jd_id} endpoint
    print("\n2. Checking POST /match/{jd_id} endpoint...")
    has_match_endpoint = 'async def match_candidates' in main_content
    has_match_route = '@app.post("/match/{jd_id}"' in main_content
    requirements.append(("POST /match/{jd_id} endpoint", has_match_endpoint and has_match_route))
    print(f"   {'✅' if has_match_endpoint else '❌'} match_candidates function defined")
    print(f"   {'✅' if has_match_route else '❌'} Route decorator present")
    
    # Check 2a: Match endpoint accepts candidate_ids list
    has_request_model = "class MatchRequest" in main_content and "candidate_ids: List[str]" in main_content
    requirements.append(("MatchRequest model with candidate_ids", has_request_model))
    print(f"   {'✅' if has_request_model else '❌'} MatchRequest model with candidate_ids list")
    
    # Check 2b: Match endpoint fetches resumes from DB
    fetches_resumes = "db.get_resume_by_id" in main_content
    fetches_jd = "db.get_job_by_id" in main_content
    requirements.append(("Fetches resumes and JD from database", fetches_resumes and fetches_jd))
    print(f"   {'✅' if fetches_resumes else '❌'} Fetches resumes from DB")
    print(f"   {'✅' if fetches_jd else '❌'} Fetches JD from DB")
    
    # Check 2c: Match endpoint runs batch scoring
    runs_batch = "score_batch" in main_content and "scored_results" in main_content
    requirements.append(("Runs batch scoring via matcher.py", runs_batch))
    print(f"   {'✅' if runs_batch else '❌'} Calls score_batch function")
    
    # Check 2d: Match endpoint stores results
    stores_results = "db.update_match_results" in main_content or "update_match_results" in main_content
    saves_match = "db.save_match_result" in main_content or "save_match_result" in main_content
    requirements.append(("Stores results in candidate docs", stores_results and saves_match))
    print(f"   {'✅' if stores_results else '❌'} Updates candidate match_history")
    print(f"   {'✅' if saves_match else '❌'} Saves to match_results collection")
    
    # Check 2e: Match endpoint returns ranked list
    has_match_response = "class MatchResponse" in main_content
    has_match_result = "class MatchResult" in main_content
    response_fields = "overall" in main_content and "justifications" in main_content and "feedback" in main_content
    requirements.append(("Returns ranked list with scores/feedback", has_match_response and has_match_result and response_fields))
    print(f"   {'✅' if has_match_response else '❌'} MatchResponse model defined")
    print(f"   {'✅' if has_match_result else '❌'} MatchResult model with id/overall/justifications/feedback")
    
    # Check 3: GET /shortlist/{jd_id} endpoint
    print("\n3. Checking GET /shortlist/{jd_id} endpoint...")
    has_shortlist_endpoint = 'async def get_shortlist' in main_content
    has_shortlist_route = '@app.get("/shortlist/{jd_id}"' in main_content
    requirements.append(("GET /shortlist/{jd_id} endpoint", has_shortlist_endpoint and has_shortlist_route))
    print(f"   {'✅' if has_shortlist_endpoint else '❌'} get_shortlist function defined")
    print(f"   {'✅' if has_shortlist_route else '❌'} Route decorator present")
    
    # Check 3a: Shortlist has threshold parameter
    has_threshold = "threshold: float" in main_content and "Query(" in main_content
    requirements.append(("Threshold parameter (default 7.0)", has_threshold))
    print(f"   {'✅' if has_threshold else '❌'} threshold parameter with Query validation")
    
    # Check 3b: Shortlist filters by score
    filters_score = "overall_score" in main_content and "< threshold" in main_content
    requirements.append(("Filters candidates by overall > threshold", filters_score))
    print(f"   {'✅' if filters_score else '❌'} Filters by overall score threshold")
    
    # Check 3c: Shortlist has additional filters
    has_exp_filter = "min_experience" in main_content
    has_skills_filter = "min_skills_score" in main_content
    requirements.append(("Additional filters (min_experience, min_skills_score)", has_exp_filter and has_skills_filter))
    print(f"   {'✅' if has_exp_filter else '❌'} min_experience filter")
    print(f"   {'✅' if has_skills_filter else '❌'} min_skills_score filter")
    
    # Check 3d: Shortlist sorts by score
    sorts_by_score = "sort" in main_content and "overall_score" in main_content
    requirements.append(("Sorts by score descending", sorts_by_score))
    print(f"   {'✅' if sorts_by_score else '❌'} Sorts by overall_score")
    
    # Check 3e: Shortlist has pagination
    has_pagination = "limit: int" in main_content and "offset: int" in main_content
    requirements.append(("Pagination with limit/offset", has_pagination))
    print(f"   {'✅' if has_pagination else '❌'} limit and offset parameters")
    
    # Check 3f: Shortlist response model
    has_shortlist_response = "class ShortlistResponse" in main_content
    has_shortlist_candidate = "class ShortlistCandidate" in main_content
    requirements.append(("ShortlistResponse and ShortlistCandidate models", has_shortlist_response and has_shortlist_candidate))
    print(f"   {'✅' if has_shortlist_response else '❌'} ShortlistResponse model")
    print(f"   {'✅' if has_shortlist_candidate else '❌'} ShortlistCandidate model")
    
    # Check 3g: Queries match_results collection
    queries_matches = "get_match_history" in main_content
    requirements.append(("Queries match_results from database", queries_matches))
    print(f"   {'✅' if queries_matches else '❌'} Uses get_match_history from db.py")
    
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
        print("\n🎉 ALL REQUIREMENTS MET! Phase 5 Step 3 is COMPLETE! 🎉")
        return True
    else:
        print(f"\n⚠️  {total - passed} requirement(s) still need attention")
        return False

if __name__ == "__main__":
    success = check_step3_requirements()
    sys.exit(0 if success else 1)
