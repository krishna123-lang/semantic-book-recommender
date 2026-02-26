"""
Professional Analytics Dashboard Module for Semantic Book Recommender
Interactive charts and visualizations of user interactions
"""

import gradio as gr
import json
from datetime import datetime


def _generate_chart_html(tracker, curiosity_engine=None):
    """
    Generate all dashboard charts as HTML with inline CSS/JS
    
    Args:
        tracker: InteractionTracker instance
        curiosity_engine: CuriosityEngine instance (optional)
        
    Returns:
        str: Complete dashboard HTML
    """
    stats = tracker.get_summary_stats()
    mood_dist = tracker.get_mood_distribution()
    lang_stats = tracker.get_language_stats()
    popular_books = tracker.get_popular_books(limit=8)
    search_trends = tracker.get_search_trends()
    recent = tracker.get_recent_activity(limit=15)
    
    # ── Summary Cards ──
    cards_html = f"""
    <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 30px;'>
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    border-radius: 16px; padding: 24px; color: white;
                    box-shadow: 0 8px 32px rgba(102,126,234,0.3);'>
            <div style='font-size: 2.4em; font-weight: 800;'>{stats['total_searches']}</div>
            <div style='font-size: 0.95em; opacity: 0.9; margin-top: 4px;'>🔍 Total Searches</div>
        </div>
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    border-radius: 16px; padding: 24px; color: white;
                    box-shadow: 0 8px 32px rgba(245,87,108,0.3);'>
            <div style='font-size: 2.4em; font-weight: 800;'>{stats['total_chats']}</div>
            <div style='font-size: 0.95em; opacity: 0.9; margin-top: 4px;'>🤖 Chat Messages</div>
        </div>
        <div style='background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); 
                    border-radius: 16px; padding: 24px; color: white;
                    box-shadow: 0 8px 32px rgba(79,172,254,0.3);'>
            <div style='font-size: 2.4em; font-weight: 800;'>{stats['unique_languages']}</div>
            <div style='font-size: 0.95em; opacity: 0.9; margin-top: 4px;'>🌍 Languages Used</div>
        </div>
        <div style='background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%); 
                    border-radius: 16px; padding: 24px; color: white;
                    box-shadow: 0 8px 32px rgba(67,233,123,0.3);'>
            <div style='font-size: 2.4em; font-weight: 800;'>{stats['total_interactions']}</div>
            <div style='font-size: 0.95em; opacity: 0.9; margin-top: 4px;'>⚡ Total Interactions</div>
        </div>
    </div>
    """
    
    # ── Mood Distribution Chart (CSS bars) ──
    mood_colors = {
        'Happy': '#fbbf24', 'Emotional': '#a78bfa', 
        'Dark': '#6b7280', 'Adventurous': '#f97316', 'Romantic': '#f472b6'
    }
    mood_emojis = {
        'Happy': '😊', 'Emotional': '😢', 
        'Dark': '😈', 'Adventurous': '🚀', 'Romantic': '💕'
    }
    
    max_mood = max(mood_dist.values()) if mood_dist else 1
    mood_bars = ""
    for mood, count in sorted(mood_dist.items(), key=lambda x: x[1], reverse=True):
        pct = (count / max_mood) * 100
        color = mood_colors.get(mood, '#6366f1')
        emoji = mood_emojis.get(mood, '🎭')
        mood_bars += f"""
        <div style='margin-bottom: 14px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                <span style='color: #e2e8f0; font-weight: 600;'>{emoji} {mood}</span>
                <span style='color: #94a3b8; font-weight: 500;'>{count}</span>
            </div>
            <div style='background: rgba(255,255,255,0.08); border-radius: 8px; height: 28px; overflow: hidden;'>
                <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 8px;
                            transition: width 0.8s ease; box-shadow: 0 0 12px {color}40;'></div>
            </div>
        </div>
        """
    
    if not mood_bars:
        mood_bars = "<p style='color: #64748b; text-align: center; padding: 30px;'>No mood selections yet. Try the mood buttons on the Discover page! 🎭</p>"
    
    # ── Language Distribution ──
    lang_names = {
        'en': '🇬🇧 English', 'hi': '🇮🇳 Hindi', 'fr': '🇫🇷 French', 
        'de': '🇩🇪 German', 'es': '🇪🇸 Spanish', 'pt': '🇧🇷 Portuguese',
        'it': '🇮🇹 Italian', 'ja': '🇯🇵 Japanese', 'ko': '🇰🇷 Korean',
        'zh-cn': '🇨🇳 Chinese', 'ru': '🇷🇺 Russian', 'ar': '🇸🇦 Arabic',
        'ta': '🇮🇳 Tamil', 'te': '🇮🇳 Telugu', 'tr': '🇹🇷 Turkish',
    }
    
    max_lang = max(lang_stats.values()) if lang_stats else 1
    lang_bars = ""
    lang_colors = ['#6366f1', '#8b5cf6', '#a78bfa', '#c4b5fd', '#ddd6fe',
                   '#06b6d4', '#14b8a6', '#10b981', '#22c55e', '#84cc16']
    
    for i, (lang, count) in enumerate(sorted(lang_stats.items(), key=lambda x: x[1], reverse=True)):
        pct = (count / max_lang) * 100
        color = lang_colors[i % len(lang_colors)]
        display_name = lang_names.get(lang, f'🌐 {lang.upper()}')
        lang_bars += f"""
        <div style='margin-bottom: 14px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                <span style='color: #e2e8f0; font-weight: 600;'>{display_name}</span>
                <span style='color: #94a3b8; font-weight: 500;'>{count}</span>
            </div>
            <div style='background: rgba(255,255,255,0.08); border-radius: 8px; height: 28px; overflow: hidden;'>
                <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 8px;
                            transition: width 0.8s ease;'></div>
            </div>
        </div>
        """
    
    if not lang_bars:
        lang_bars = "<p style='color: #64748b; text-align: center; padding: 30px;'>No language data yet. Start searching to see language stats! 🌍</p>"
    
    # ── Popular Books ──
    max_book = max(popular_books.values()) if popular_books else 1
    book_bars = ""
    book_colors = ['#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4', '#10b981',
                   '#f97316', '#ec4899', '#6366f1']
    
    for i, (title, count) in enumerate(popular_books.items()):
        pct = (count / max_book) * 100
        color = book_colors[i % len(book_colors)]
        short_title = title[:35] + ('...' if len(title) > 35 else '')
        book_bars += f"""
        <div style='margin-bottom: 14px;'>
            <div style='display: flex; justify-content: space-between; margin-bottom: 6px;'>
                <span style='color: #e2e8f0; font-weight: 600; font-size: 0.9em;'>📖 {short_title}</span>
                <span style='color: #94a3b8; font-weight: 500;'>{count}</span>
            </div>
            <div style='background: rgba(255,255,255,0.08); border-radius: 8px; height: 24px; overflow: hidden;'>
                <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 8px;
                            transition: width 0.8s ease;'></div>
            </div>
        </div>
        """
    
    if not book_bars:
        book_bars = "<p style='color: #64748b; text-align: center; padding: 30px;'>No book data yet. Search for books to see this chart! 📚</p>"
    
    # ── Search Trends (Sparkline style) ──
    trend_items = ""
    if search_trends:
        max_trend = max(search_trends.values()) if search_trends else 1
        for date, count in search_trends.items():
            pct = (count / max_trend) * 100
            trend_items += f"""
            <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 10px;'>
                <span style='color: #94a3b8; font-size: 0.85em; min-width: 90px;'>{date}</span>
                <div style='flex-grow: 1; background: rgba(255,255,255,0.08); border-radius: 6px; height: 22px; overflow: hidden;'>
                    <div style='background: linear-gradient(90deg, #6366f1, #a78bfa); width: {pct}%; height: 100%; 
                                border-radius: 6px; transition: width 0.8s ease;'></div>
                </div>
                <span style='color: #e2e8f0; font-weight: 600; min-width: 30px; text-align: right;'>{count}</span>
            </div>
            """
    else:
        trend_items = "<p style='color: #64748b; text-align: center; padding: 30px;'>No search history yet. Start exploring books! 📈</p>"
    
    # ── Recent Activity Feed ──
    activity_rows = ""
    for act in recent:
        ts = act['timestamp'][:16].replace('T', ' ')
        activity_rows += f"""
        <tr style='border-bottom: 1px solid rgba(255,255,255,0.06);'>
            <td style='padding: 12px 16px; color: #e2e8f0;'>{act['type']}</td>
            <td style='padding: 12px 16px; color: #94a3b8;'>{act['detail']}</td>
            <td style='padding: 12px 16px; color: #64748b; font-size: 0.85em;'>{act['language']}</td>
            <td style='padding: 12px 16px; color: #64748b; font-size: 0.85em;'>{ts}</td>
        </tr>
        """
    
    if not activity_rows:
        activity_rows = """
        <tr><td colspan='4' style='padding: 30px; color: #64748b; text-align: center;'>
            No activity recorded yet. Start using the app to see data here! 🚀
        </td></tr>
        """
    
    # ── Curiosity Impact Score (if engine available) ──
    curiosity_html = ""
    if curiosity_engine:
        try:
            impact = curiosity_engine.compute_curiosity_impact_score()
            
            def gauge(label, value, color, icon):
                return f"""
                <div style='text-align: center; padding: 20px;
                            background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                            border-radius: 16px;'>
                    <div style='font-size: 1.3em; margin-bottom: 6px;'>{icon}</div>
                    <div style='position: relative; width: 100px; height: 100px; margin: 0 auto 10px auto;'>
                        <svg viewBox="0 0 120 120" style='transform: rotate(-90deg);'>
                            <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
                            <circle cx="60" cy="60" r="52" fill="none" stroke="{color}" stroke-width="10"
                                    stroke-dasharray="{value * 3.27} {327 - value * 3.27}"
                                    stroke-linecap="round"/>
                        </svg>
                        <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                                    font-size: 1.4em; font-weight: 800; color: {color};'>{value}</div>
                    </div>
                    <div style='color: #e2e8f0; font-weight: 600; font-size: 0.88em;'>{label}</div>
                </div>
                """
            
            curiosity_html = f"""
            <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 16px; padding: 24px; margin-bottom: 24px;'>
                <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                    🧠 Curiosity Impact Score
                </h3>
                <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px;'>
                    {gauge('Exploration Level', impact['exploration_level'], '#6366f1', '🔭')}
                    {gauge('Intellectual Diversity', impact['intellectual_diversity'], '#22c55e', '🌈')}
                    {gauge('Growth Index', impact['growth_index'], '#f59e0b', '📈')}
                </div>
            </div>
            """
        except Exception:
            curiosity_html = ""
    
    # ── Assemble Full Dashboard ──
    html = f"""
    <div style='font-family: "Inter", "Segoe UI", sans-serif; max-width: 1200px; margin: 0 auto;'>
        
        {cards_html}
        
        {curiosity_html}
        
        <!-- Charts Grid -->
        <div style='display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 24px;'>
            
            <!-- Mood Distribution -->
            <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 16px; padding: 24px;'>
                <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                    🎭 Mood Distribution
                </h3>
                {mood_bars}
            </div>
            
            <!-- Language Distribution -->
            <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                        border-radius: 16px; padding: 24px;'>
                <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                    🌍 Language Distribution
                </h3>
                {lang_bars}
            </div>
        </div>
        
        <!-- Popular Books -->
        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px; padding: 24px; margin-bottom: 24px;'>
            <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                📚 Most Popular Books
            </h3>
            {book_bars}
        </div>
        
        <!-- Search Trends -->
        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px; padding: 24px; margin-bottom: 24px;'>
            <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                📈 Search Activity Over Time
            </h3>
            {trend_items}
        </div>
        
        <!-- Recent Activity -->
        <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px; padding: 24px; margin-bottom: 24px;'>
            <h3 style='color: #f1f5f9; margin: 0 0 20px 0; font-size: 1.15em;'>
                🕐 Recent Activity
            </h3>
            <div style='overflow-x: auto;'>
                <table style='width: 100%; border-collapse: collapse;'>
                    <thead>
                        <tr style='border-bottom: 2px solid rgba(255,255,255,0.1);'>
                            <th style='padding: 12px 16px; text-align: left; color: #94a3b8; font-weight: 600;'>Type</th>
                            <th style='padding: 12px 16px; text-align: left; color: #94a3b8; font-weight: 600;'>Detail</th>
                            <th style='padding: 12px 16px; text-align: left; color: #94a3b8; font-weight: 600;'>Lang</th>
                            <th style='padding: 12px 16px; text-align: left; color: #94a3b8; font-weight: 600;'>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {activity_rows}
                    </tbody>
                </table>
            </div>
        </div>
        
    </div>
    """
    
    return html


def build_dashboard_tab(tracker, curiosity_engine=None):
    """
    Build the Dashboard tab for the Gradio app
    
    Args:
        tracker: InteractionTracker instance
        curiosity_engine: CuriosityEngine instance (optional)
    
    Returns:
        gr.Tab: The dashboard tab component
    """
    with gr.Tab("📊 Dashboard", id="dashboard") as tab:
        gr.HTML("""
        <div style='text-align: center; padding: 25px 20px 15px 20px;'>
            <h1 style='font-size: 2.2em; margin: 0; 
                        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-weight: 800; letter-spacing: -0.5px;'>
                📊 Analytics Dashboard
            </h1>
            <p style='color: #94a3b8; font-size: 1.1em; margin-top: 8px;'>
                Real-time insights into user interactions • Search trends • Curiosity analytics
            </p>
        </div>
        """)
        
        refresh_btn = gr.Button("🔄 Refresh Dashboard", variant="primary", size="lg")
        
        dashboard_output = gr.HTML(
            value=_generate_chart_html(tracker, curiosity_engine),
            label=""
        )
        
        refresh_btn.click(
            fn=lambda: _generate_chart_html(tracker, curiosity_engine),
            inputs=[],
            outputs=dashboard_output
        )
    

    return tab
