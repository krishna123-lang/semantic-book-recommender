"""
Recommendation Engine Module for Semantic Book Recommender
Loads FAISS index and provides semantic search with multilingual 
+ explainable recommendation support
"""

import pandas as pd
import numpy as np
import faiss
import sys
import re
from collections import Counter
from sentence_transformers import SentenceTransformer

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Language name mapping
LANGUAGE_NAMES = {
    'en': 'English', 'hi': 'Hindi', 'fr': 'French', 'de': 'German',
    'es': 'Spanish', 'pt': 'Portuguese', 'it': 'Italian', 'nl': 'Dutch',
    'ru': 'Russian', 'zh-cn': 'Chinese', 'zh-tw': 'Chinese', 'ja': 'Japanese',
    'ko': 'Korean', 'ar': 'Arabic', 'tr': 'Turkish', 'pl': 'Polish',
    'sv': 'Swedish', 'da': 'Danish', 'no': 'Norwegian', 'fi': 'Finnish',
    'ta': 'Tamil', 'te': 'Telugu', 'ml': 'Malayalam', 'kn': 'Kannada',
    'bn': 'Bengali', 'mr': 'Marathi', 'gu': 'Gujarati', 'pa': 'Punjabi',
    'ur': 'Urdu', 'th': 'Thai', 'vi': 'Vietnamese', 'id': 'Indonesian',
}

# Common stop words to exclude from keyword analysis
STOP_WORDS = {
    'a', 'an', 'the', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
    'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
    'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
    'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
    'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
    'between', 'out', 'off', 'over', 'under', 'again', 'further', 'then',
    'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'both',
    'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor',
    'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just',
    'about', 'and', 'but', 'or', 'if', 'while', 'that', 'this', 'it',
    'i', 'me', 'my', 'we', 'our', 'you', 'your', 'he', 'him', 'his',
    'she', 'her', 'they', 'them', 'their', 'what', 'which', 'who', 'whom',
    'book', 'story', 'novel', 'like', 'want', 'looking', 'find', 'recommend',
    'suggest', 'give', 'show', 'tell', 'read', 'good', 'best', 'great',
}


def detect_language(text):
    """
    Detect the language of the given text
    
    Args:
        text: Input text string
    
    Returns:
        tuple: (language_code, language_name)
    """
    try:
        from langdetect import detect
        lang_code = detect(text)
        lang_name = LANGUAGE_NAMES.get(lang_code, lang_code.capitalize())
        return lang_code, lang_name
    except Exception:
        return 'en', 'English'


def extract_keywords(text, top_n=8):
    """Extract meaningful keywords from text"""
    words = re.findall(r'[a-zA-Z]{3,}', text.lower())
    meaningful = [w for w in words if w not in STOP_WORDS]
    word_counts = Counter(meaningful)
    return [word for word, _ in word_counts.most_common(top_n)]


class BookRecommender:
    """
    Semantic book recommendation engine using FAISS vector search
    with multilingual support and explainable recommendations
    """
    
    def __init__(self, 
                 index_path='embeddings/faiss.index',
                 metadata_path='embeddings/books_metadata.csv',
                 model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
        """
        Initialize the recommender system
        
        Args:
            index_path: Path to FAISS index file
            metadata_path: Path to books metadata CSV
            model_name: Sentence transformer model name (multilingual)
        """
        print("Initializing Book Recommender System...")
        
        # Load FAISS index
        self.index = faiss.read_index(index_path)
        print(f"✓ Loaded FAISS index with {self.index.ntotal} books")
        
        # Load book metadata
        self.books_df = pd.read_csv(metadata_path)
        print(f"✓ Loaded metadata for {len(self.books_df)} books")
        
        # Load embedding model (multilingual)
        self.model = SentenceTransformer(model_name)
        print(f"✓ Loaded multilingual embedding model: {model_name}")
        
        print("✓ Recommender system ready!\n")
    
    def recommend_books(self, query, k=5):
        """
        Find books semantically similar to the query with explanations
        
        Args:
            query: User's text query (any language)
            k: Number of recommendations to return
        
        Returns:
            list: List of dicts with book info + explanation
        """
        # Detect query language
        lang_code, lang_name = detect_language(query)
        
        # Generate embedding for the query
        query_embedding = self.model.encode([query]).astype('float32')
        
        # Search FAISS index for k nearest neighbors
        distances, indices = self.index.search(query_embedding, k)
        
        # Extract keywords from query for explanation
        query_keywords = extract_keywords(query)
        
        # Prepare recommendations with explanations
        recommendations = []
        for i, (idx, distance) in enumerate(zip(indices[0], distances[0])):
            book = self.books_df.iloc[idx]
            
            # Convert L2 distance to similarity score (0-1 range)
            similarity_score = float(np.exp(-distance / 10))
            
            # Generate explanation
            explanation = self._generate_explanation(
                query, query_keywords, book, similarity_score
            )
            
            recommendations.append({
                'rank': i + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': book['description'],
                'similarity_score': similarity_score,
                'distance': float(distance),
                'language': lang_code,
                'language_name': lang_name,
                'explanation': explanation
            })
        
        return recommendations
    
    def _generate_explanation(self, query, query_keywords, book, similarity_score):
        """
        Generate a human-readable explanation for why a book was recommended
        
        Args:
            query: Original search query
            query_keywords: Extracted keywords from query
            book: Book data row
            similarity_score: Computed similarity score
            
        Returns:
            dict: Structured explanation data
        """
        description = str(book['description']).lower()
        category = str(book['categories']).lower()
        
        # 1. Keyword Overlap
        book_keywords = extract_keywords(description, top_n=12)
        common_keywords = [kw for kw in query_keywords if kw in book_keywords or kw in description]
        all_query_keywords = query_keywords[:6]
        
        # 2. Category Relevance
        category_match = any(kw in category for kw in query_keywords)
        category_explanation = (
            f"The book's category '{book['categories']}' aligns with your search"
            if category_match
            else f"While categorized as '{book['categories']}', the themes match your query"
        )
        
        # 3. Similarity Interpretation
        if similarity_score > 0.75:
            match_level = 'Excellent'
            match_color = '#27ae60'
            match_desc = 'Very strong semantic alignment with your query'
        elif similarity_score > 0.55:
            match_level = 'Good'
            match_color = '#f39c12'
            match_desc = 'Solid thematic connection to your search'
        else:
            match_level = 'Fair'
            match_color = '#e74c3c'
            match_desc = 'Some thematic overlap detected'
        
        # 4. Theme Analysis
        themes = []
        theme_keywords = {
            'mystery': ['mystery', 'detective', 'crime', 'murder', 'investigation', 'clue', 'suspect'],
            'romance': ['love', 'romance', 'heart', 'passion', 'relationship', 'romantic'],
            'adventure': ['adventure', 'journey', 'explore', 'quest', 'expedition', 'discover'],
            'fantasy': ['magic', 'dragon', 'wizard', 'fantasy', 'mythical', 'enchant', 'realm'],
            'sci-fi': ['space', 'future', 'technology', 'alien', 'dystopia', 'robot', 'science'],
            'horror': ['horror', 'fear', 'ghost', 'haunted', 'terror', 'dark', 'nightmare'],
            'historical': ['history', 'historical', 'war', 'ancient', 'century', 'kingdom', 'empire'],
            'drama': ['emotional', 'family', 'life', 'struggle', 'human', 'society', 'moral'],
        }
        
        combined_text = f"{query.lower()} {description}"
        for theme, keywords in theme_keywords.items():
            matches = [kw for kw in keywords if kw in combined_text]
            if len(matches) >= 2:
                themes.append(theme.capitalize())
        
        if not themes:
            themes = ['General Fiction']
        
        return {
            'common_keywords': common_keywords[:5],
            'query_keywords': all_query_keywords,
            'book_keywords': book_keywords[:6],
            'category_match': category_match,
            'category_explanation': category_explanation,
            'match_level': match_level,
            'match_color': match_color,
            'match_desc': match_desc,
            'themes': themes[:3],
            'similarity_pct': f"{similarity_score * 100:.1f}%"
        }
    
    def search_by_title(self, title_query):
        """
        Search for books by title (exact or partial match)
        
        Args:
            title_query: Title or partial title to search for
            
        Returns:
            list: Matching book records
        """
        mask = self.books_df['title'].str.lower().str.contains(
            title_query.lower(), na=False
        )
        results = []
        for _, book in self.books_df[mask].iterrows():
            results.append({
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': book['description']
            })
        return results[:5]
    
    def get_book_info(self, title):
        """
        Get detailed info about a specific book
        
        Args:
            title: Book title (case-insensitive match)
            
        Returns:
            dict or None: Book information
        """
        mask = self.books_df['title'].str.lower() == title.lower()
        matches = self.books_df[mask]
        if len(matches) > 0:
            book = matches.iloc[0]
            return {
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': book['description']
            }
        return None
    
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
            if 'explanation' in rec:
                exp = rec['explanation']
                output.append(f"\nWhy this book?")
                output.append(f"  Match Level: {exp['match_level']} ({exp['similarity_pct']})")
                output.append(f"  Common Keywords: {', '.join(exp['common_keywords'])}")
                output.append(f"  Themes: {', '.join(exp['themes'])}")
        
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
    
    # Example queries (including multilingual)
    test_queries = [
        "a thrilling mystery with a detective solving crimes",
        "epic fantasy adventure with magic and dragons",
        "romantic story set in historical times",
    ]
    
    for query in test_queries:
        print(f"\n\nQuery: '{query}'")
        print("-" * 60)
        recommendations = recommender.recommend_books(query, k=3)
        print(recommender.format_recommendations(recommendations))
    
    print("\n" + "=" * 60)
    print("✓ Recommender test complete!")
    print("=" * 60)
