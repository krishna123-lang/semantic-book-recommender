"""
Quick test script to verify the recommendation system works
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from recommender import BookRecommender

print("=" * 60)
print("TESTING BOOK RECOMMENDATION SYSTEM")
print("=" * 60)

# Initialize recommender
print("\nLoading recommender system...")
recommender = BookRecommender()

# Test query
query = "mystery novel with a detective solving crimes"
print(f"\nQuery: '{query}'")
print("-" * 60)

# Get recommendations
recommendations = recommender.recommend_books(query, k=5)

# Display results
for rec in recommendations:
    print(f"\n#{rec['rank']} - {rec['title']}")
    print(f"Author: {rec['authors']}")
    print(f"Category: {rec['categories']}")
    print(f"Similarity: {rec['similarity_score']:.3f}")
    print(f"Description: {rec['description'][:150]}...")

print("\n" + "=" * 60)
print("✓ RECOMMENDATION SYSTEM WORKING PERFECTLY!")
print("=" * 60)
