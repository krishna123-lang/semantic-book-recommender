"""
Recommendation Engine Module for Semantic Book Recommender
Loads FAISS index and provides semantic search functionality
"""

import pandas as pd
import numpy as np
import faiss
import sys
from sentence_transformers import SentenceTransformer

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


class BookRecommender:
    """
    Semantic book recommendation engine using FAISS vector search
    """
    
    def __init__(self, 
                 index_path='embeddings/faiss.index',
                 metadata_path='embeddings/books_metadata.csv',
                 model_name='sentence-transformers/all-MiniLM-L6-v2'):
        """
        Initialize the recommender system
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to books metadata CSV
            model_name: Sentence transformer model name
        """
        print("Initializing Book Recommender System...")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        print(f"✓ Loaded FAISS index with {self.index.ntotal} books")
        
        # Load book metadata
        self.books_df = pd.read_csv(metadata_path)
        print(f"✓ Loaded metadata for {len(self.books_df)} books")
        
        # Load embedding model
        self.model = SentenceTransformer(model_name)
        print(f"✓ Loaded embedding model: {model_name}")
        
        print("✓ Recommender system ready!\n")
    
    def recommend_books(self, query, k=5):
        """
        Find books semantically similar to the query
        
        Args:
            query: User's text query describing desired book
            k: Number of recommendations to return
        
        Returns:
            list: List of dictionaries containing book recommendations
        """
        # Generate embedding for the query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search FAISS index for k nearest neighbors
        distances, indices = self.index.search(query_embedding, k)
        
        # Prepare recommendations
        recommendations = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            book = self.books_df.iloc[idx]
            
            # Convert L2 distance to similarity score (0-1 range, higher is better)
            # Using exponential decay: similarity = exp(-distance)
            similarity_score = np.exp(-distance / 10)  # Scale factor for readability
            
            recommendations.append({
                'rank': i + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': book['description'],
                'similarity_score': float(similarity_score),
                'distance': float(distance)
            })
        
        return recommendations
    
    def format_recommendations(self, recommendations):
        """
        Format recommendations for display
        
        Args:
            recommendations: List of recommendation dictionaries
        
        Returns:
            str: Formatted string for display
        """
        output = []
        for rec in recommendations:
            output.append(f"\n{'='*60}")
            output.append(f"#{rec['rank']} - {rec['title']}")
            output.append(f"{'='*60}")
            output.append(f"Author(s): {rec['authors']}")
            output.append(f"Category: {rec['categories']}")
            output.append(f"Similarity: {rec['similarity_score']:.3f}")
            output.append(f"\nDescription:")
            output.append(f"{rec['description'][:300]}...")
        
        return '\n'.join(output)

def load_recommender():
    """
    Convenience function to load the recommender system
    
    Returns:
        BookRecommender: Initialized recommender instance
    """
    return BookRecommender()

if __name__ == "__main__":
    # Test the recommender
    print("=" * 60)
    print("TESTING BOOK RECOMMENDER")
    print("=" * 60)
    
    recommender = load_recommender()
    
    # Example queries
    test_queries = [
        "a thrilling mystery with a detective solving crimes",
        "epic fantasy adventure with magic and dragons",
        "romantic story set in historical times"
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: '{query}'")
        print("-" * 60)
        recommendations = recommender.recommend_books(query, k=3)
        print(recommender.format_recommendations(recommendations))
    
    print("\n" + "=" * 60)
    print("✓ Recommender test complete!")
    print("=" * 60)
