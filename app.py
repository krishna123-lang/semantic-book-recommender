"""
Gradio Web Interface for Semantic Book Recommender
Multi-tab application with Discover, Chatbot, Curiosity Path, and Dashboard pages
Premium dark theme with glassmorphism and micro-animations
"""

import gradio as gr
from recommender import BookRecommender
from interaction_tracker import InteractionTracker
from chatbot import build_chatbot_tab
from dashboard import build_dashboard_tab
from curiosity_engine import CuriosityEngine
from curiosity_tab import build_curiosity_tab
import os
import random
from urllib.parse import quote

# Initialize systems
print("Starting Gradio Application...")
print("=" * 60)

try:
    recommender = BookRecommender()
    tracker = InteractionTracker()
    print("✓ Recommender system loaded successfully!")
    print("✓ Interaction tracker ready!")
except Exception as e:
    print(f"✗ Error loading recommender: {e}")
    print("\nPlease ensure you have run:")
    print("  1. python preprocess.py")
    print("  2. python embed.py")
    raise

# Mood mapping
mood_map = {
    "Happy": "uplifting joyful comedy",
    "Emotional": "emotional drama relationships",
    "Dark": "thriller horror mystery",
    "Adventurous": "adventure fantasy exploration",
    "Romantic": "love emotional romance"
}

# ──────────────────────────────────────────────────────────────
#  Premium Dark Theme CSS
# ──────────────────────────────────────────────────────────────

CUSTOM_CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Global dark theme */
.gradio-container {
    font-family: 'Inter', 'Segoe UI', sans-serif !important;
    background: linear-gradient(135deg, #0f0c29 0%, #1a1a2e 40%, #16213e 100%) !important;
    min-height: 100vh;
}

/* Tab styling */
.tab-nav button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1.05em !important;
    padding: 14px 28px !important;
    border-radius: 12px 12px 0 0 !important;
    transition: all 0.3s ease !important;
    color: #94a3b8 !important;
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-bottom: none !important;
}

.tab-nav button.selected {
    background: rgba(99,102,241,0.15) !important;
    color: #e2e8f0 !important;
    border-color: rgba(99,102,241,0.3) !important;
    box-shadow: 0 -2px 12px rgba(99,102,241,0.2) !important;
}

.tab-nav button:hover:not(.selected) {
    background: rgba(255,255,255,0.06) !important;
    color: #cbd5e1 !important;
}

/* Input fields */
textarea, input[type="text"] {
    background: rgba(255,255,255,0.05) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    font-family: 'Inter', sans-serif !important;
    transition: border-color 0.3s ease, box-shadow 0.3s ease !important;
}

textarea:focus, input[type="text"]:focus {
    border-color: rgba(99,102,241,0.5) !important;
    box-shadow: 0 0 20px rgba(99,102,241,0.15) !important;
}

/* Buttons */
button.primary {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%) !important;
    border: none !important;
    color: white !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 4px 15px rgba(99,102,241,0.3) !important;
}

button.primary:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.4) !important;
}

button.secondary {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: #e2e8f0 !important;
    border-radius: 12px !important;
    transition: all 0.3s ease !important;
}

button.secondary:hover {
    background: rgba(255,255,255,0.1) !important;
    transform: translateY(-1px) !important;
}

/* Mood buttons */
.mood-btn button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    color: #e2e8f0 !important;
    border-radius: 14px !important;
    padding: 16px 24px !important;
    font-size: 1.05em !important;
    font-weight: 500 !important;
    transition: all 0.3s ease !important;
}

.mood-btn button:hover {
    background: rgba(99,102,241,0.12) !important;
    border-color: rgba(99,102,241,0.3) !important;
    transform: translateY(-3px) !important;
    box-shadow: 0 8px 25px rgba(99,102,241,0.2) !important;
}

/* Slider */
input[type="range"] {
    accent-color: #6366f1 !important;
}

/* Chatbot */
.chatbot {
    background: rgba(255,255,255,0.02) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
}

/* Labels and text */
label, .label-wrap span {
    color: #94a3b8 !important;
    font-weight: 500 !important;
}

/* Markdown text */
.prose, .markdown-text {
    color: #cbd5e1 !important;
}

h1, h2, h3 {
    color: #f1f5f9 !important;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
}
::-webkit-scrollbar-track {
    background: rgba(255,255,255,0.03);
}
::-webkit-scrollbar-thumb {
    background: rgba(99,102,241,0.3);
    border-radius: 4px;
}

/* Carousel animation */
@keyframes slide {
    0%, 20% { opacity: 1; transform: scale(1); }
    25%, 100% { opacity: 0; transform: scale(0.95); }
}

.carousel-container {
    position: relative;
    width: 100%;
    max-width: 680px;
    height: 320px;
    margin: 20px auto;
    overflow: hidden;
    border-radius: 20px;
    box-shadow: 0 12px 40px rgba(0,0,0,0.4);
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
    padding: 30px;
}

.carousel-slide:nth-child(1) { animation-delay: 0s; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.carousel-slide:nth-child(2) { animation-delay: 3s; background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
.carousel-slide:nth-child(3) { animation-delay: 6s; background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
.carousel-slide:nth-child(4) { animation-delay: 9s; background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); }
.carousel-slide:nth-child(5) { animation-delay: 12s; background: linear-gradient(135deg, #fa709a 0%, #fee140 100%); }

.carousel-slide img {
    max-width: 140px;
    max-height: 200px;
    border-radius: 12px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.3);
    margin-bottom: 16px;
}

.carousel-slide h3 {
    margin: 8px 0;
    font-size: 1.5em;
    color: white;
    text-shadow: 2px 2px 8px rgba(0,0,0,0.3);
    font-weight: 700;
}

/* Explainer card animation */
@keyframes fadeInUp {
    from { opacity: 0; transform: translateY(12px); }
    to { opacity: 1; transform: translateY(0); }
}

.explain-card {
    animation: fadeInUp 0.4s ease;
}
"""

# ──────────────────────────────────────────────────────────────
#  Book Card Formatting (with Explainable Recommendations)
# ──────────────────────────────────────────────────────────────

def format_book_card(rec):
    """Format a single book as a professional card with explanation"""
    score = rec['similarity_score']
    score_pct = score * 100
    if score_pct > 70:
        score_color = '#27ae60'
    elif score_pct > 40:
        score_color = '#f39c12'
    else:
        score_color = '#e74c3c'
    
    title_encoded = quote(rec['title'])
    cover_url = f"https://covers.openlibrary.org/b/title/{title_encoded}-M.jpg"
    amazon_url = f"https://www.amazon.in/s?k={title_encoded}"
    flipkart_url = f"https://www.flipkart.com/search?q={title_encoded}"
    imdb_url = f"https://www.imdb.com/find?q={title_encoded}"
    
    year = rec.get('year', 'Unknown')
    description = rec['description']
    if len(description) > 200:
        description = description[:200] + "..."
    
    # Language badge
    lang_name = rec.get('language_name', '')
    lang_badge = ""
    if lang_name and lang_name != 'English':
        lang_badge = f"""
        <span style='background: linear-gradient(135deg, #6366f1, #a78bfa); color: white; 
                      padding: 3px 10px; border-radius: 8px; font-size: 0.8em; margin-left: 8px;'>
            🌍 {lang_name}
        </span>
        """
    
    # Explanation section
    explanation_html = ""
    exp = rec.get('explanation', {})
    if exp:
        common_kw = ', '.join(exp.get('common_keywords', [])) or 'Semantic match'
        themes = ', '.join(exp.get('themes', []))
        match_color = exp.get('match_color', '#6366f1')
        match_level = exp.get('match_level', 'Good')
        match_desc = exp.get('match_desc', '')
        cat_exp = exp.get('category_explanation', '')
        similarity_pct = exp.get('similarity_pct', '')
        
        # Keyword pills
        kw_pills = ''
        for kw in exp.get('common_keywords', [])[:5]:
            kw_pills += f"""
            <span style='background: rgba(99,102,241,0.15); color: #a5b4fc; 
                          padding: 3px 10px; border-radius: 8px; font-size: 0.82em; 
                          margin: 2px 3px; display: inline-block;'>
                {kw}
            </span>
            """
        if not kw_pills:
            kw_pills = "<span style='color: #64748b; font-size: 0.85em;'>Deep semantic matching</span>"
        
        explanation_html = f"""
        <div class='explain-card' style='margin-top: 14px; padding: 16px; 
                    background: rgba(99,102,241,0.06); border: 1px solid rgba(99,102,241,0.12);
                    border-radius: 12px; border-left: 3px solid {match_color};'>
            <div style='font-weight: 700; color: #e2e8f0; margin-bottom: 10px; font-size: 0.95em;'>
                💡 Why This Book?
            </div>
            <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.88em;'>
                <div>
                    <span style='color: #94a3b8;'>Match Level:</span>
                    <span style='color: {match_color}; font-weight: 700;'> {match_level} ({similarity_pct})</span>
                </div>
                <div>
                    <span style='color: #94a3b8;'>Themes:</span>
                    <span style='color: #c4b5fd;'> {themes}</span>
                </div>
            </div>
            <div style='margin-top: 8px; font-size: 0.88em;'>
                <span style='color: #94a3b8;'>Matching Keywords:</span>
                <div style='margin-top: 4px;'>{kw_pills}</div>
            </div>
            <div style='margin-top: 8px; color: #64748b; font-size: 0.82em; font-style: italic;'>
                {cat_exp}
            </div>
        </div>
        """
    
    card_html = f"""
    <div style='display: flex; background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.07); 
                border-radius: 16px; padding: 22px; margin: 18px 0; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.2);
                transition: transform 0.3s ease, box-shadow 0.3s ease;'
         onmouseover="this.style.transform='translateY(-3px)'; this.style.boxShadow='0 12px 40px rgba(0,0,0,0.3)'"
         onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 20px rgba(0,0,0,0.2)'">
        
        <!-- Cover Image -->
        <div style='flex-shrink: 0; margin-right: 22px;'>
            <img src="{cover_url}" 
                 alt="{rec['title']}" 
                 style='width: 120px; height: 180px; object-fit: cover; border-radius: 10px; 
                        box-shadow: 0 4px 15px rgba(0,0,0,0.3);'
                 onerror="this.src='https://via.placeholder.com/120x180/1e1b4b/a5b4fc?text=No+Cover'"/>
        </div>
        
        <!-- Book Details -->
        <div style='flex-grow: 1;'>
            <h3 style='color: #f1f5f9; margin-top: 0; margin-bottom: 10px; font-size: 1.15em;'>
                {rec['rank']}. {rec['title']} {lang_badge}
            </h3>
            
            <p style='margin: 5px 0; color: #94a3b8;'>
                <strong style='color: #cbd5e1;'>Author:</strong> {rec['authors']}
            </p>
            
            <p style='margin: 5px 0;'>
                <strong style='color: #cbd5e1;'>Category:</strong> 
                <span style='background: linear-gradient(135deg, #6366f1, #8b5cf6); color: white; 
                              padding: 3px 12px; border-radius: 10px; font-size: 0.85em;'>
                    {rec['categories']}
                </span>
            </p>
            
            <p style='margin: 5px 0; color: #94a3b8;'>
                <strong style='color: #cbd5e1;'>Similarity:</strong> 
                <span style='color: {score_color}; font-weight: bold; font-size: 1.1em;'>
                    {score_pct:.1f}%
                </span>
            </p>
            
            <p style='margin: 10px 0; color: #64748b; line-height: 1.6; font-size: 0.92em;'>
                {description}
            </p>
            
            {explanation_html}
            
            <!-- Action Buttons -->
            <div style='margin-top: 16px; display: flex; gap: 10px; flex-wrap: wrap;'>
                <a href="{amazon_url}" target="_blank" 
                   style='background: linear-gradient(135deg, #FF9900, #FFB347); color: white; padding: 8px 18px; 
                          border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.9em;
                          display: inline-block; transition: all 0.3s ease; box-shadow: 0 3px 10px rgba(255,153,0,0.3);'>
                    🛒 Amazon
                </a>
                
                <a href="{flipkart_url}" target="_blank" 
                   style='background: linear-gradient(135deg, #2874F0, #5a9cf5); color: white; padding: 8px 18px; 
                          border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.9em;
                          display: inline-block; transition: all 0.3s ease; box-shadow: 0 3px 10px rgba(40,116,240,0.3);'>
                    🛒 Flipkart
                </a>
                
                <a href="{imdb_url}" target="_blank" 
                   style='background: linear-gradient(135deg, #F5C518, #ffd54f); color: #1a1a2e; padding: 8px 18px; 
                          border-radius: 10px; text-decoration: none; font-weight: 600; font-size: 0.9em;
                          display: inline-block; transition: all 0.3s ease; box-shadow: 0 3px 10px rgba(245,197,24,0.3);'>
                    🎬 IMDb
                </a>
            </div>
        </div>
    </div>
    """
    
    return card_html


def get_recommendations(query, num_recommendations):
    """Get book recommendations with explanations"""
    if not query or query.strip() == "":
        return "<p style='color: #f87171; font-size: 1.1em;'>⚠️ Please enter a description of the book you're looking for.</p>"
    
    try:
        recommendations = recommender.recommend_books(query, k=int(num_recommendations))
        
        # Detect language for display
        lang_name = recommendations[0].get('language_name', 'English') if recommendations else 'English'
        lang_code = recommendations[0].get('language', 'en') if recommendations else 'en'
        
        lang_badge_html = ""
        if lang_name != 'English':
            lang_badge_html = f"""
            <div style='background: linear-gradient(135deg, #6366f1, #a78bfa); color: white;
                        display: inline-block; padding: 6px 16px; border-radius: 10px; 
                        font-size: 0.9em; margin-bottom: 15px;'>
                🌍 Query detected in <strong>{lang_name}</strong>
            </div>
            """
        
        html_output = f"""
        <div style='font-family: "Inter", "Segoe UI", sans-serif;'>
            <h2 style='color: #f1f5f9; border-bottom: 3px solid #6366f1; padding-bottom: 12px;
                       margin-bottom: 20px; font-size: 1.4em;'>
                📚 Top {len(recommendations)} Recommendations for You
            </h2>
            {lang_badge_html}
        """
        
        for rec in recommendations:
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        
        # Log interaction
        tracker.log_search(query, lang_code, len(recommendations), recommendations)
        for rec in recommendations:
            tracker.log_book_view(rec['title'], source='search')
        
        return html_output
        
    except Exception as e:
        return f"<p style='color: #f87171;'>Error: {str(e)}</p>"


def get_surprise_books():
    """Get random books (Surprise Me feature)"""
    try:
        random_indices = random.sample(range(len(recommender.books_df)), min(5, len(recommender.books_df)))
        
        html_output = """
        <div style='font-family: "Inter", "Segoe UI", sans-serif;'>
            <h2 style='color: #f1f5f9; border-bottom: 3px solid #f43f5e; padding-bottom: 12px;
                       margin-bottom: 20px; font-size: 1.4em;'>
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
                'similarity_score': 1.0,
                'year': 'Unknown',
                'explanation': {}
            }
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        
        tracker.log_surprise_click()
        
        return html_output
        
    except Exception as e:
        return f"<p style='color: #f87171;'>Error: {str(e)}</p>"


def mood_based_search(mood):
    """Search books based on mood selection"""
    query = mood_map.get(mood, "interesting books")
    
    try:
        recommendations = recommender.recommend_books(query, k=5)
        
        mood_colors = {
            'Happy': '#fbbf24', 'Emotional': '#a78bfa',
            'Dark': '#6b7280', 'Adventurous': '#f97316', 'Romantic': '#f472b6'
        }
        accent = mood_colors.get(mood, '#6366f1')
        
        html_output = f"""
        <div style='font-family: "Inter", "Segoe UI", sans-serif;'>
            <h2 style='color: #f1f5f9; border-bottom: 3px solid {accent}; padding-bottom: 12px;
                       margin-bottom: 20px; font-size: 1.4em;'>
                ✨ Books for Your {mood} Mood
            </h2>
        """
        
        for rec in recommendations:
            html_output += format_book_card(rec)
        
        html_output += "</div>"
        
        tracker.log_mood_selection(mood)
        tracker.log_search(f"mood:{mood}", 'en', len(recommendations), recommendations)
        
        return html_output
        
    except Exception as e:
        return f"<p style='color: #f87171;'>Error: {str(e)}</p>"


# ──────────────────────────────────────────────────────────────
#  Carousel HTML
# ──────────────────────────────────────────────────────────────

carousel_html = """
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


# ──────────────────────────────────────────────────────────────
#  Build Gradio App (4-Tab Layout)
# ──────────────────────────────────────────────────────────────

with gr.Blocks(
    title="Semantic Book Recommender",
) as demo:
    
    # Header
    gr.HTML("""
    <div style='text-align: center; padding: 30px 20px 10px 20px;'>
        <h1 style='font-size: 2.8em; margin: 0; 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
                    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                    font-weight: 800; letter-spacing: -1px;'>
            📚 Semantic Book Recommender
        </h1>
        <p style='color: #64748b; font-size: 1.15em; margin-top: 8px; font-weight: 400;'>
            AI-powered multilingual book discovery • Explainable recommendations • Conversational AI
        </p>
    </div>
    """)
    
    with gr.Tabs():
        
        # ════════════════════════════════════════════════════
        #  TAB 1: DISCOVER (Home)
        # ════════════════════════════════════════════════════
        with gr.Tab("📚 Discover", id="discover"):
            
            # Carousel
            gr.HTML(carousel_html)
            
            gr.HTML("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 25px 0;'>")
            
            # Mood Section
            gr.HTML("""
            <div style='text-align: center; margin-bottom: 16px;'>
                <h2 style='color: #f1f5f9; font-size: 1.5em; font-weight: 700;'>
                    🎭 How is your mood today?
                </h2>
                <p style='color: #64748b; font-size: 1em;'>
                    Choose your mood and discover books that match your feelings!
                </p>
            </div>
            """)
            
            with gr.Row(elem_classes="mood-btn"):
                mood_happy = gr.Button("😊 Happy", size="lg")
                mood_emotional = gr.Button("😢 Emotional", size="lg")
                mood_dark = gr.Button("😈 Dark", size="lg")
                mood_adventurous = gr.Button("🚀 Adventurous", size="lg")
                mood_romantic = gr.Button("💕 Romantic", size="lg")
            
            gr.HTML("<hr style='border: none; border-top: 1px solid rgba(255,255,255,0.06); margin: 25px 0;'>")
            
            # Search Section
            gr.HTML("""
            <div style='margin-bottom: 16px;'>
                <h2 style='color: #f1f5f9; font-size: 1.5em; font-weight: 700;'>
                    🔍 Search for Books
                </h2>
                <p style='color: #64748b; font-size: 1em;'>
                    Describe what you're looking for in any language — our AI understands 50+ languages!
                </p>
            </div>
            """)
            
            with gr.Row():
                with gr.Column(scale=2):
                    query_input = gr.Textbox(
                        label="What kind of book are you looking for?",
                        placeholder="e.g., 'a thrilling mystery', 'un roman d'aventure', 'रहस्य उपन्यास'...",
                        lines=3
                    )
                    
                    num_recommendations = gr.Slider(
                        minimum=1, maximum=10, value=5, step=1,
                        label="Number of recommendations"
                    )
                    
                    with gr.Row():
                        search_button = gr.Button("🔍 Find Books", variant="primary", size="lg")
                        surprise_button = gr.Button("🎲 Surprise Me", variant="secondary", size="lg")
                
                with gr.Column(scale=1):
                    gr.HTML("""
                    <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.06);
                                border-radius: 16px; padding: 22px;'>
                        <h3 style='color: #e2e8f0; margin-top: 0; font-size: 1.1em;'>💡 Example Queries</h3>
                        <div style='color: #94a3b8; line-height: 2; font-size: 0.92em;'>
                            <div>🇬🇧 <em>"mystery novel with a detective"</em></div>
                            <div>🇬🇧 <em>"epic fantasy with dragons"</em></div>
                            <div>🇫🇷 <em>"roman policier avec du suspense"</em></div>
                            <div>🇮🇳 <em>"रहस्य उपन्यास"</em></div>
                            <div>🇪🇸 <em>"novela de ciencia ficción"</em></div>
                            <div>🇬🇧 <em>"romantic historical fiction"</em></div>
                            <div>🇬🇧 <em>"horror story with ghosts"</em></div>
                            <div>🇬🇧 <em>"coming of age friendship"</em></div>
                        </div>
                    </div>
                    """)
            
            output = gr.HTML(label="Recommendations")
            
            # Interactions
            search_button.click(fn=get_recommendations, inputs=[query_input, num_recommendations], outputs=output)
            query_input.submit(fn=get_recommendations, inputs=[query_input, num_recommendations], outputs=output)
            surprise_button.click(fn=get_surprise_books, inputs=[], outputs=output)
            
            mood_happy.click(fn=lambda: mood_based_search("Happy"), inputs=[], outputs=output)
            mood_emotional.click(fn=lambda: mood_based_search("Emotional"), inputs=[], outputs=output)
            mood_dark.click(fn=lambda: mood_based_search("Dark"), inputs=[], outputs=output)
            mood_adventurous.click(fn=lambda: mood_based_search("Adventurous"), inputs=[], outputs=output)
            mood_romantic.click(fn=lambda: mood_based_search("Romantic"), inputs=[], outputs=output)
            
            # Technical Details
            gr.HTML("""
            <div style='margin-top: 30px; padding: 24px; background: rgba(255,255,255,0.02);
                        border: 1px solid rgba(255,255,255,0.05); border-radius: 16px;'>
                <h3 style='color: #e2e8f0; margin-top: 0;'>🔬 Technical Details</h3>
                <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 8px; color: #94a3b8; font-size: 0.9em;'>
                    <div>🧠 <strong>Embedding Model:</strong> Multilingual MiniLM-L12-v2</div>
                    <div>🔎 <strong>Vector Search:</strong> FAISS (L2 Distance)</div>
                    <div>📊 <strong>Dataset:</strong> 130+ curated books</div>
                    <div>🌍 <strong>Languages:</strong> 50+ supported</div>
                </div>
                <div style='margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px;'>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>🎨 Professional Book Cards</span>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>💡 Explainable AI</span>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>🌍 Multilingual</span>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>🤖 AI Chatbot</span>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>📊 Analytics Dashboard</span>
                    <span style='background: rgba(99,102,241,0.12); color: #a5b4fc; padding: 4px 12px; 
                                  border-radius: 8px; font-size: 0.82em;'>🛒 E-Commerce</span>
                </div>
            </div>
            """)
        
        # ════════════════════════════════════════════════════
        #  TAB 2: CHATBOT
        # ════════════════════════════════════════════════════
        build_chatbot_tab(recommender, tracker)
        
        # ════════════════════════════════════════════════════
        #  TAB 3: CURIOSITY PATH
        # ════════════════════════════════════════════════════
        print("Initializing AI Curiosity Engine...")
        curiosity_engine = CuriosityEngine(recommender, tracker)
        print("✓ Curiosity Engine ready!")
        build_curiosity_tab(curiosity_engine)
        
        # ════════════════════════════════════════════════════
        #  TAB 4: DASHBOARD
        # ════════════════════════════════════════════════════
        build_dashboard_tab(tracker, curiosity_engine)


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("LAUNCHING SEMANTIC BOOK RECOMMENDER")
    print("=" * 60)
    print("\nFeatures: Multilingual Search | Explainable AI | Chatbot | Curiosity Engine | Dashboard")
    print("The application will open in your default browser.")
    print("If it doesn't open automatically, copy the URL from below.\n")
    
    demo.launch(
        share=False,
        show_error=True,
        css=CUSTOM_CSS,
        theme=gr.themes.Base(
            primary_hue="indigo",
            secondary_hue="purple",
            neutral_hue="slate",
            font=["Inter", "Segoe UI", "sans-serif"]
        )
    )
