"""Test photo display logic for specific vs general queries"""
from vector_db import vector_search_profiles, generate_ai_answer

print("Testing Photo Display Logic: Specific vs General Queries\n")
print("=" * 80)

# Test 1: Specific person query (SHOULD show photo)
print("\n[TEST 1] SPECIFIC: 'who is ceo of amzur'")
print("-" * 80)
profiles1 = vector_search_profiles("who is ceo of amzur", limit=5)
answer1 = generate_ai_answer("who is ceo of amzur", profiles1)
has_photo1 = "📸PHOTO📸" in answer1
print(f"Profiles found: {len(profiles1)}")
print(f"Answer preview: {answer1[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo1 else '❌ NO'}")
print(f"Expected: ✅ YES (specific person)")
print(f"Result: {'✅ PASS' if has_photo1 else '❌ FAIL'}")

# Test 2: General/plural query (should NOT show photo)
print("\n\n[TEST 2] GENERAL: 'show me all executives'")
print("-" * 80)
profiles2 = vector_search_profiles("show me all executives", limit=5)
answer2 = generate_ai_answer("show me all executives", profiles2)
has_photo2 = "📸PHOTO📸" in answer2
print(f"Profiles found: {len(profiles2)}")
print(f"Answer preview: {answer2[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo2 else '❌ NO'}")
print(f"Expected: ❌ NO (general/plural)")
print(f"Result: {'✅ PASS' if not has_photo2 else '❌ FAIL'}")

# Test 3: List query (should NOT show photo)
print("\n\n[TEST 3] GENERAL: 'list all directors'")
print("-" * 80)
profiles3 = vector_search_profiles("list all directors", limit=5)
answer3 = generate_ai_answer("list all directors", profiles3)
has_photo3 = "📸PHOTO📸" in answer3
print(f"Profiles found: {len(profiles3)}")
print(f"Answer preview: {answer3[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo3 else '❌ NO'}")
print(f"Expected: ❌ NO (list query)")
print(f"Result: {'✅ PASS' if not has_photo3 else '❌ FAIL'}")

# Test 4: Specific role (SHOULD show photo)
print("\n\n[TEST 4] SPECIFIC: 'who is the president'")
print("-" * 80)
profiles4 = vector_search_profiles("who is the president", limit=5)
answer4 = generate_ai_answer("who is the president", profiles4)
has_photo4 = "📸PHOTO📸" in answer4
print(f"Profiles found: {len(profiles4)}")
print(f"Answer preview: {answer4[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo4 else '❌ NO'}")
print(f"Expected: ✅ YES (specific role)")
print(f"Result: {'✅ PASS' if has_photo4 else '❌ FAIL'}")

# Test 5: Multiple people query (should NOT show photo)
print("\n\n[TEST 5] GENERAL: 'who are the technology leaders'")
print("-" * 80)
profiles5 = vector_search_profiles("who are the technology leaders", limit=5)
answer5 = generate_ai_answer("who are the technology leaders", profiles5)
has_photo5 = "📸PHOTO📸" in answer5
print(f"Profiles found: {len(profiles5)}")
print(f"Answer preview: {answer5[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo5 else '❌ NO'}")
print(f"Expected: ❌ NO (plural 'who are')")
print(f"Result: {'✅ PASS' if not has_photo5 else '❌ FAIL'}")

# Test 6: Specific person by name (SHOULD show photo)
print("\n\n[TEST 6] SPECIFIC: 'tell me about Ganna Vadlamaani'")
print("-" * 80)
profiles6 = vector_search_profiles("Ganna Vadlamaani", limit=3)
answer6 = generate_ai_answer("tell me about Ganna Vadlamaani", profiles6)
has_photo6 = "📸PHOTO📸" in answer6
print(f"Profiles found: {len(profiles6)}")
print(f"Answer preview: {answer6[:150]}...")
print(f"Has photo: {'✅ YES' if has_photo6 else '❌ NO'}")
print(f"Expected: ✅ YES (specific person by name)")
print(f"Result: {'✅ PASS' if has_photo6 else '❌ FAIL'}")

print("\n" + "=" * 80)
print("Summary:")
print(f"  Specific queries (should have photos): {sum([has_photo1, has_photo4, has_photo6])}/3")
print(f"  General queries (should NOT have photos): {sum([not has_photo2, not has_photo3, not has_photo5])}/3")
print("\nTesting complete!")
