"""Test that AI doesn't hallucinate about external companies"""
from vector_db import vector_search_profiles, generate_ai_answer

print("Testing AI Hallucination Prevention\n")
print("=" * 80)

# Get some profiles from database
profiles = vector_search_profiles("CEO", limit=3)
print(f"\nProfiles in context: {[p['name'] for p in profiles]}\n")

# Test 1: Question about Microsoft CEO (should refuse)
print("\n🧪 TEST 1: Question about Microsoft CEO")
print("-" * 80)
query1 = "Who is the CEO of Microsoft?"
answer1 = generate_ai_answer(query1, profiles)
print(f"Question: {query1}")
print(f"Answer: {answer1}\n")

if "microsoft" in answer1.lower() and any(name in answer1 for name in ['satya', 'nadella', 'gates']):
    print("❌ FAILED: AI hallucinated about Microsoft!")
elif "can only answer" in answer1.lower() or "don't have information" in answer1.lower():
    print("✅ PASSED: AI correctly refused to answer about external company")
else:
    print("⚠️ UNCLEAR: Check the answer manually")

# Test 2: Question about Google (should refuse)
print("\n🧪 TEST 2: Question about Google CEO")
print("-" * 80)
query2 = "Who is the CEO of Google?"
answer2 = generate_ai_answer(query2, profiles)
print(f"Question: {query2}")
print(f"Answer: {answer2}\n")

if "google" in answer2.lower() and "pichai" in answer2.lower():
    print("❌ FAILED: AI hallucinated about Google!")
elif "can only answer" in answer2.lower() or "don't have information" in answer2.lower():
    print("✅ PASSED: AI correctly refused to answer about external company")
else:
    print("⚠️ UNCLEAR: Check the answer manually")

# Test 3: Question about our actual CEO (should answer correctly)
print("\n🧪 TEST 3: Question about actual CEO in database")
print("-" * 80)
query3 = "Who is the CEO?"
answer3 = generate_ai_answer(query3, profiles)
print(f"Question: {query3}")
print(f"Answer: {answer3}\n")

if any(profile['name'] in answer3 for profile in profiles):
    print("✅ PASSED: AI answered about actual team members")
else:
    print("❌ FAILED: AI didn't answer about team members")

# Test 4: Question about Amzur team member (should answer)
print("\n🧪 TEST 4: Question about Amzur team member")
print("-" * 80)
query4 = "Tell me about Ganna Vadlamaani"
profiles4 = vector_search_profiles("Ganna", limit=1)
answer4 = generate_ai_answer(query4, profiles4)
print(f"Question: {query4}")
print(f"Answer: {answer4}\n")

if "ganna" in answer4.lower() and "amzur" in answer4.lower():
    print("✅ PASSED: AI answered about actual team member")
else:
    print("❌ FAILED: AI didn't properly answer about team member")

print("\n" + "=" * 80)
print("Testing complete! Check results above.")
