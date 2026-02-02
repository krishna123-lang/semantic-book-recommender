"""
Gradio Web Interface for Semantic Book Recommender
Interactive UI for book recommendations with E-Commerce Features
"""

import gradio as gr
from recommender import BookRecommender
import os
import random
from urllib.parse import quote

# Initialize the recommender system
print("Starting Gradio Application...")
print("=" * 60)

try:
    recommender = BookRecommender()
    print("✓ Recommender system loaded successfully!")
except Exception as e:
    print(f"✗ Error loading recommender: {e}")
    print("\nPlease ensure you have run:")
    print("  1. python preprocess.py")
    print("  2. python embed.py")
    raise

# Mood mapping for mood-based discovery
mood_map = {
    "Happy": "uplifting joyful comedy",
    "Emotional": "emotional drama relationships",
    "Dark": "thriller horror mystery",
    "Adventurous": "adventure fantasy exploration",
    "Romantic": "love emotional romance"
}

def format_book_card(rec):
    """
    Format a single book as a professional card with cover image and e-commerce links
    
    Args:
        rec: Book recommendation dictionary
    
    Returns:
        str: HTML formatted book card
    """
    # Color code similarity score
    score = rec['similarity_score']
    if score > 0.7:
        score_color = '#27ae60'  # Green
    elif score > 0.5:
        score_color = '#f39c12'  # Orange
    else:
        score_color = '#e74c3c'  # Red
    
    # URL encode book title for links
    title_encoded = quote(rec['title'])
    
    # Cover image URL
    cover_url = f"https://covers.openlibrary.org/b/title/{title_encoded}-M.jpg"
    
    # E-commerce links
    amazon_url = f"https://www.amazon.in/s?k={title_encoded}"
    flipkart_url = f"https://www.flipkart.com/search?q={title_encoded}"
    imdb_url = f"https://www.imdb.com/find?q={title_encoded}"
    
    # Get year or display "Unknown"
    year = rec.get('year', 'Unknown')
    
    # Truncate description if too long
    description = rec['description']
    if len(description) > 200:
        description = description[:200] + "..."
    
    card_html = f"""
    <div style='display: flex; background-color: #ffffff; border: 1px solid #e0e0e0; 
                border-radius: 10px; padding: 20px; margin: 20px 0; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.2s;'>
        
        <!-- Cover Image -->
        <div style='flex-shrink: 0; margin-right: 20px;'>
            <img src="{cover_url}" 
                 alt="{rec['title']}" 
                 style='width: 120px; height: 180px; object-fit: cover; border-radius: 5px; 
                        box-shadow: 0 2px 4px rgba(0,0,0,0.2);'
                 onerror="this.src='https://via.placeholder.com/120x180?text=No+Cover'"/>
        </div>
        
        <!-- Book Details -->
        <div style='flex-grow: 1;'>
            <h3 style='color: #2c3e50; margin-top: 0; margin-bottom: 10px;'>
                {rec['rank']}. {rec['title']}
            </h3>
            
            <p style='margin: 5px 0; color: #555;'>
                <strong>Author:</strong> {rec['authors']}
            </p>
            
            <p style='margin: 5px 0;'>
                <strong>Category:</strong> 
                <span style='background-color: #3498db; color: white; padding: 3px 10px; 
                             border-radius: 12px; font-size: 0.85em;'>
                    {rec['categories']}
                </span>
            </p>
            
            <p style='margin: 5px 0;'>
                <strong>Year:</strong> {year}
            </p>
            
            <p style='margin: 5px 0;'>
                <strong>Similarity Score:</strong> 
                <span style='color: {score_color}; font-weight: bold; font-size: 1.1em;'>
                    {score:.3f}
                </span>
            </p>
            
            <p style='margin: 10px 0; color: #666; line-height: 1.5; font-size: 0.95em;'>
                {description}
            </p>
            
            <!-- Action Buttons -->
            <div style='margin-top: 15px; display: flex; gap: 10px; flex-wrap: wrap;'>
                <a href="{amazon_url}" target="_blank" 
                   style='background-color: #FF9900; color: white; padding: 8px 16px; 
                          border-radius: 5px; text-decoration: none; font-weight: bold;
                          display: inline-block; transition: background-color 0.3s;'>
                    🛒 Buy on Amazon
                </a>
                
                <a href="{flipkart_url}" target="_blank" 
                   style='background-color: #2874F0; color: white; padding: 8px 16px; 
                          border-radius: 5px; text-decoration: none; font-weight: bold;
                          display: inline-block; transition: background-color 0.3s;'>
                    🛒 Buy on Flipkart
                </a>
                
                <a href="{imdb_url}" target="_blank" 
                   style='background-color: #F5C518; color: black; padding: 8px 16px; 
                          border-radius: 5px; text-decoration: none; font-weight: bold;
                          display: inline-block; transition: background-color 0.3s;'>
                    🎬 Movie Adaptation
                </a>
            </div>
        </div>
    </div>
    """
    
    return card_html

def get_recommendations(query, num_recommendations):
    """
    Get book recommendations based on user query
    
    Args:
        query: User's search query
        num_recommendations: Number of books to recommend
    
    Returns:
        str: Formatted HTML output with recommendations
    """
    if not query or query.strip() == "":
        return "<p style='color: red; font-size: 1.1em;'>⚠️ Please enter a description of the book you're looking for.</p>"
    
    try:
        # Get recommendations
        recommendations = recommender.recommend_books(query, k=int(num_recommendations))
        
        # Format as HTML with professional book cards
        html_output = f"""
        <div style='font-family: "Segoe UI", Arial, sans-serif;'>
            <h2 style='color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px;
                       margin-bottom: 20px;'>
                📚 Top {len(recommendations)} Recommendations for You
            </h2>
        """
        
        for rec in recommendations:
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        return html_output
        
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

def get_surprise_books():
    """
    Get random books from the dataset (Surprise Me feature)
    
    Returns:
        str: Formatted HTML output with random books
    """
    try:
        # Get random books from metadata
        random_indices = random.sample(range(len(recommender.books_df)), min(5, len(recommender.books_df)))
        
        html_output = """
        <div style='font-family: "Segoe UI", Arial, sans-serif;'>
            <h2 style='color: #2c3e50; border-bottom: 3px solid #e74c3c; padding-bottom: 10px;
                       margin-bottom: 20px;'>
                🎲 Surprise! Here are 5 Random Books
            </h2>
        """
        
        for i, idx in enumerate(random_indices):
            book = recommender.books_df.iloc[idx]
            rec = {
                'rank': i + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': book['description'],
                'similarity_score': 1.0,  # Not applicable for random
                'year': 'Unknown'
            }
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        return html_output
        
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

def mood_based_search(mood):
    """
    Search books based on mood selection
    
    Args:
        mood: Selected mood (Happy, Emotional, Dark, Adventurous, Romantic)
    
    Returns:
        str: Formatted HTML output with mood-based recommendations
    """
    query = mood_map.get(mood, "interesting books")
    
    try:
        recommendations = recommender.recommend_books(query, k=5)
        
        html_output = f"""
        <div style='font-family: "Segoe UI", Arial, sans-serif;'>
            <h2 style='color: #2c3e50; border-bottom: 3px solid #9b59b6; padding-bottom: 10px;
                       margin-bottom: 20px;'>
                ✨ Books for Your {mood} Mood
            </h2>
        """
        
        for rec in recommendations:
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        return html_output
        
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

# Create auto-sliding carousel HTML/CSS
carousel_html = """
<style>
@keyframes slide {
    0%, 20% { opacity: 1; }
    25%, 100% { opacity: 0; }
}

.carousel-container {
    position: relative;
    width: 100%;
    max-width: 600px;
    height: 300px;
    margin: 20px auto;
    overflow: hidden;
    border-radius: 15px;
    box-shadow: 0 8px 16px rgba(0,0,0,0.2);
}

.carousel-slide {
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    animation: slide 15s infinite;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 20px;
}

.carousel-slide:nth-child(1) { animation-delay: 0s; }
.carousel-slide:nth-child(2) { animation-delay: 3s; }
.carousel-slide:nth-child(3) { animation-delay: 6s; }
.carousel-slide:nth-child(4) { animation-delay: 9s; }
.carousel-slide:nth-child(5) { animation-delay: 12s; }

.carousel-slide img {
    max-width: 150px;
    max-height: 200px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    margin-bottom: 15px;
}

.carousel-slide h3 {
    margin: 10px 0;
    font-size: 1.5em;
    text-align: center;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}
</style>

<div class="carousel-container">
    <div class="carousel-slide">
        <img src="https://covers.openlibrary.org/b/title/To%20Kill%20a%20Mockingbird-M.jpg" alt="Book 1">
        <h3>To Kill a Mockingbird</h3>
    </div>
    <div class="carousel-slide">
        <img src="https://covers.openlibrary.org/b/title/1984-M.jpg" alt="Book 2">
        <h3>1984</h3>
    </div>
    <div class="carousel-slide">
        <img src="https://covers.openlibrary.org/b/title/Pride%20and%20Prejudice-M.jpg" alt="Book 3">
        <h3>Pride and Prejudice</h3>
    </div>
    <div class="carousel-slide">
        <img src="https://covers.openlibrary.org/b/title/The%20Great%20Gatsby-M.jpg" alt="Book 4">
        <h3>The Great Gatsby</h3>
    </div>
    <div class="carousel-slide">
        <img src="https://covers.openlibrary.org/b/title/Harry%20Potter-M.jpg" alt="Book 5">
        <h3>Harry Potter</h3>
    </div>
</div>
"""

# Create Gradio interface
with gr.Blocks(title="Semantic Book Recommender") as demo:
    
    gr.Markdown(
        """
        # 📚 Semantic Book Recommendation System
        
        Discover your next favorite book using AI-powered semantic search! 
        """
    )
    
    # FEATURE 2: Auto-sliding carousel
    gr.HTML(carousel_html)
    
    gr.Markdown("---")
    
    # FEATURE 3: Mood-based discovery
    gr.Markdown(
        """
        ## 🎭 How is your mood today?
        
        <p style='text-align: center; font-size: 1.1em; color: #555;'>
        Choose your mood and discover books that match your feelings!
        </p>
        """
    )
    
    with gr.Row():
        mood_happy = gr.Button("😊 Happy", elem_classes="mood-button", size="lg")
        mood_emotional = gr.Button("😢 Emotional", elem_classes="mood-button", size="lg")
        mood_dark = gr.Button("😈 Dark", elem_classes="mood-button", size="lg")
        mood_adventurous = gr.Button("🚀 Adventurous", elem_classes="mood-button", size="lg")
        mood_romantic = gr.Button("💕 Romantic", elem_classes="mood-button", size="lg")
    
    gr.Markdown("---")
    
    # Original search interface
    gr.Markdown(
        """
        ## 🔍 Search for Books
        
        Describe the kind of book you're looking for, and our AI will find the best matches.
        """
    )
    
    with gr.Row():
        with gr.Column(scale=2):
            query_input = gr.Textbox(
                label="What kind of book are you looking for?",
                placeholder="e.g., 'a thrilling mystery with a detective', 'fantasy adventure with magic', 'romantic historical fiction'",
                lines=3
            )
            
            num_recommendations = gr.Slider(
                minimum=1,
                maximum=10,
                value=5,
                step=1,
                label="Number of recommendations"
            )
            
            with gr.Row():
                search_button = gr.Button("🔍 Find Books", variant="primary", size="lg")
                # FEATURE 4: Surprise Me button
                surprise_button = gr.Button("🎲 Surprise Me", variant="secondary", size="lg")
        
        with gr.Column(scale=1):
            gr.Markdown(
                """
                ### 💡 Example Queries:
                
                - *"mystery novel with a detective solving crimes"*
                - *"epic fantasy with dragons and magic"*
                - *"dystopian future with rebellion"*
                - *"romantic story in Victorian era"*
                - *"horror story with supernatural elements"*
                - *"coming of age story about friendship"*
                - *"space adventure with aliens"*
                - *"psychological thriller with plot twists"*
                """
            )
    
    output = gr.HTML(label="Recommendations")
    
    # Set up interactions
    search_button.click(
        fn=get_recommendations,
        inputs=[query_input, num_recommendations],
        outputs=output
    )
    
    query_input.submit(
        fn=get_recommendations,
        inputs=[query_input, num_recommendations],
        outputs=output
    )
    
    # Surprise Me button
    surprise_button.click(
        fn=get_surprise_books,
        inputs=[],
        outputs=output
    )
    
    # Mood buttons
    mood_happy.click(fn=lambda: mood_based_search("Happy"), inputs=[], outputs=output)
    mood_emotional.click(fn=lambda: mood_based_search("Emotional"), inputs=[], outputs=output)
    mood_dark.click(fn=lambda: mood_based_search("Dark"), inputs=[], outputs=output)
    mood_adventurous.click(fn=lambda: mood_based_search("Adventurous"), inputs=[], outputs=output)
    mood_romantic.click(fn=lambda: mood_based_search("Romantic"), inputs=[], outputs=output)
    
    gr.Markdown(
        """
        ---
        
        ### 🔬 Technical Details:
        
        - **Embedding Model:** sentence-transformers/all-MiniLM-L6-v2
        - **Vector Search:** FAISS (Facebook AI Similarity Search)
        - **Dataset:** 150+ curated books across multiple genres
        - **Similarity Metric:** L2 distance with exponential decay scoring
        
        ### ✨ Features:
        
        - 🎨 **Professional Book Cards** with cover images
        - 🛒 **E-Commerce Integration** (Amazon & Flipkart)
        - 🎬 **Movie Adaptations** (IMDb links)
        - 🎭 **Mood-Based Discovery**
        - 🎲 **Random Book Discovery**
        - 🎠 **Auto-Sliding Hero Carousel**
        """
    )

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LAUNCHING GRADIO WEB INTERFACE")
    print("=" * 60)
    print("\nThe application will open in your default browser.")
    print("If it doesn't open automatically, copy the URL from below.\n")
    
    # Launch the app
    demo.launch(
        share=False,
        show_error=True
    )
