"""Test that photo matches the person in the answer"""
from vector_db import vector_search_profiles, generate_ai_answer

print("Testing Photo Matching Logic\n")
print("=" * 80)

# Test 1: CEO of Amzur (should show Ganna's photo, not Bala's)
print("\n[TEST 1] CEO of Amzur")
print("-" * 80)
query1 = "who is ceo of amzur"
profiles = vector_search_profiles(query1, limit=5)
print(f"\nProfiles found: {[p['name'] for p in profiles]}")

answer1 = generate_ai_answer(query1, profiles)
print(f"\nQuestion: {query1}")
print(f"\nAnswer preview: {answer1[:200]}...")

# Extract photo URL
if "📸PHOTO📸" in answer1:
    photo_url = answer1.split("📸PHOTO📸")[1].strip()
    print(f"\nPhoto URL: {photo_url}")
    
    # Check which person's name is in the answer
    if "ganna" in answer1.lower():
        expected = "Ganna"
        if "Ganna" in photo_url or "ganna" in photo_url.lower():
            print("✅ PASSED: Photo matches Ganna (mentioned in answer)")
        else:
            print(f"❌ FAILED: Answer mentions Ganna but photo is: {photo_url}")
    elif "bala" in answer1.lower() and "nemani" in answer1.lower():
        expected = "Bala Nemani"
        if "Bala" in photo_url or "bala" in photo_url.lower():
            print("✅ PASSED: Photo matches Bala (mentioned in answer)")
        else:
            print(f"❌ FAILED: Answer mentions Bala but photo is: {photo_url}")
else:
    print("⚠️ No photo in answer")

# Test 2: President (should show Bala's photo)
print("\n\n[TEST 2] Who is the President")
print("-" * 80)
query2 = "who is the president"
profiles2 = vector_search_profiles(query2, limit=5)
print(f"\nProfiles found: {[p['name'] for p in profiles2]}")

answer2 = generate_ai_answer(query2, profiles2)
print(f"\nQuestion: {query2}")
print(f"\nAnswer preview: {answer2[:200]}...")

if "📸PHOTO📸" in answer2:
    photo_url2 = answer2.split("📸PHOTO📸")[1].strip()
    print(f"\nPhoto URL: {photo_url2}")
    
    if "bala" in answer2.lower():
        if "Bala" in photo_url2 or "bala" in photo_url2.lower():
            print("✅ PASSED: Photo matches the person mentioned in answer")
        else:
            print(f"❌ FAILED: Answer mentions Bala but photo is: {photo_url2}")
    elif "ganna" in answer2.lower():
        if "Ganna" in photo_url2 or "ganna" in photo_url2.lower():
            print("✅ PASSED: Photo matches the person mentioned in answer")
        else:
            print(f"❌ FAILED: Answer mentions Ganna but photo is: {photo_url2}")

print("\n" + "=" * 80)
print("Testing complete!")
