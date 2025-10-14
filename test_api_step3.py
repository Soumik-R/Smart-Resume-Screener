"""
Test script for Phase 5 Step 3 API endpoints
Tests matching and shortlist endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_match_endpoint():
    """Test POST /match/{jd_id}"""
    print("="*80)
    print("🧪 Testing POST /match/{jd_id}")
    print("="*80)
    
    # Get existing candidates and JDs from database
    # You should replace these with actual IDs from your database
    jd_id = "test-jd-id"  # Replace with actual JD ID
    candidate_ids = ["test-candidate-1", "test-candidate-2"]  # Replace with actual candidate IDs
    
    url = f"{BASE_URL}/match/{jd_id}"
    payload = {
        "candidate_ids": candidate_ids
    }
    
    print(f"\n📤 POST {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}")
    
    try:
        response = requests.post(url, json=payload)
        print(f"\n✓ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ SUCCESS!")
            print(f"📊 JD ID: {data['jd_id']}")
            print(f"📊 Total Candidates: {data['total_candidates']}")
            print(f"\n📋 Top 3 Matches:")
            for i, candidate in enumerate(data['matched_candidates'][:3], 1):
                print(f"\n  {i}. Candidate ID: {candidate['id']}")
                print(f"     Overall Score: {candidate['overall']:.2f}")
                print(f"     Feedback: {candidate['feedback'][:100]}...")
                print(f"     Strengths: {', '.join(candidate['strengths'][:3])}")
        else:
            print(f"\n❌ ERROR: {response.status_code}")
            print(response.text)
    
    except Exception as e:
        print(f"\n❌ Exception: {e}")


def test_shortlist_endpoint():
    """Test GET /shortlist/{jd_id}"""
    print("\n" + "="*80)
    print("🧪 Testing GET /shortlist/{jd_id}")
    print("="*80)
    
    # Replace with actual JD ID
    jd_id = "test-jd-id"
    
    # Test with various filters
    test_cases = [
        {
            "name": "Basic (threshold=7.0)",
            "params": {"threshold": 7.0, "limit": 5}
        },
        {
            "name": "High threshold (threshold=8.5)",
            "params": {"threshold": 8.5, "limit": 5}
        },
        {
            "name": "With experience filter (min_experience=2)",
            "params": {"threshold": 7.0, "min_experience": 2, "limit": 5}
        },
        {
            "name": "With skills filter (min_skills_score=8.0)",
            "params": {"threshold": 7.0, "min_skills_score": 8.0, "limit": 5}
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Test Case: {test_case['name']}")
        print(f"   Params: {test_case['params']}")
        
        url = f"{BASE_URL}/shortlist/{jd_id}"
        
        try:
            response = requests.get(url, params=test_case['params'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Found {data['total_count']} candidates")
                print(f"   📄 Page {data['page']}, showing {len(data['candidates'])} results")
                
                if data['candidates']:
                    print(f"\n   🏆 Top Candidate:")
                    top = data['candidates'][0]
                    print(f"      Name: {top['name']}")
                    print(f"      Overall Score: {top['overall_score']:.2f}")
                    print(f"      Skills: {top['skills_score']:.2f} | Experience: {top['experience_score']:.2f}")
            else:
                print(f"   ❌ ERROR: {response.text[:200]}")
        
        except Exception as e:
            print(f"   ❌ Exception: {e}")


def test_health_check():
    """Test GET /health"""
    print("\n" + "="*80)
    print("🧪 Testing GET /health")
    print("="*80)
    
    url = f"{BASE_URL}/health"
    
    try:
        response = requests.get(url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✅ API Status: {data['status']}")
            print(f"📊 Database: {data['database']['name']}")
            print(f"📦 Collections: {', '.join(data['database']['collections'])}")
        else:
            print(f"❌ ERROR: {response.text}")
    
    except Exception as e:
        print(f"❌ Exception: {e}")


def main():
    """Run all tests"""
    print("\n" + "🚀 " + "="*76 + " 🚀")
    print("   PHASE 5 STEP 3 - API ENDPOINT TESTING")
    print("🚀 " + "="*76 + " 🚀\n")
    
    # Test health check first
    test_health_check()
    
    print("\n\n⚠️  NOTE: The following tests require actual candidate and JD IDs from your database.")
    print("⚠️  Please update the IDs in this script before running match/shortlist tests.\n")
    
    # Uncomment these when you have real IDs
    # test_match_endpoint()
    # test_shortlist_endpoint()
    
    print("\n" + "="*80)
    print("✅ Basic connectivity tests complete!")
    print("="*80)


if __name__ == "__main__":
    main()
