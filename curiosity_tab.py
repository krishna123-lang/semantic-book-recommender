"""
Curiosity Path Tab for Semantic Book Recommender
Premium UI for AI Curiosity Engine — shows user profile, expansion predictions,
and structured reading journeys with Curiosity Impact Score
"""

import gradio as gr
from urllib.parse import quote


def _build_curiosity_html(engine):
    """
    Generate the full Curiosity Path page HTML

    Args:
        engine: CuriosityEngine instance

    Returns:
        str: Complete HTML for the curiosity path page
    """
    profile = engine.analyze_user_profile()
    expansions = engine.predict_curiosity_expansion(profile)
    journey = engine.generate_reading_journey(profile, steps=3)
    impact = engine.compute_curiosity_impact_score(profile)

    # ── User Profile Card ──
    is_new = profile.get('is_new_user', True)
    total_books = profile.get('total_books_explored', 0)
    breadth_pct = int(profile.get('exploration_breadth', 0) * 100)
    dominant = profile.get('dominant_interest', '🆕 New Explorer')

    profile_html = f"""
    <div style='background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                border-radius: 20px; padding: 30px; margin-bottom: 24px;
                box-shadow: 0 8px 32px rgba(0,0,0,0.2);'>
        <div style='display: flex; align-items: center; gap: 24px; flex-wrap: wrap;'>
            <div style='flex-shrink: 0;'>
                <div style='width: 80px; height: 80px; border-radius: 50%;
                            background: linear-gradient(135deg, #6366f1, #a78bfa);
                            display: flex; align-items: center; justify-content: center;
                            font-size: 2em; box-shadow: 0 4px 20px rgba(99,102,241,0.4);'>
                    🧠
                </div>
            </div>
            <div style='flex-grow: 1;'>
                <h2 style='color: #f1f5f9; margin: 0 0 6px 0; font-size: 1.4em;'>
                    Your Intellectual Profile
                </h2>
                <div style='color: #94a3b8; font-size: 1em;'>
                    {'Start exploring to build your curiosity profile!' if is_new else
                     f'Based on {total_books} books explored across your reading history'}
                </div>
            </div>
            <div style='display: flex; gap: 20px; flex-wrap: wrap;'>
                <div style='text-align: center;'>
                    <div style='font-size: 2em; font-weight: 800; color: #a78bfa;'>{total_books}</div>
                    <div style='color: #64748b; font-size: 0.85em;'>Books Explored</div>
                </div>
                <div style='text-align: center;'>
                    <div style='font-size: 2em; font-weight: 800; color: #22c55e;'>{breadth_pct}%</div>
                    <div style='color: #64748b; font-size: 0.85em;'>Breadth</div>
                </div>
            </div>
        </div>
        <div style='margin-top: 20px; padding: 16px; background: rgba(99,102,241,0.08);
                    border-radius: 12px; border-left: 3px solid #6366f1;'>
            <span style='color: #94a3b8;'>Current Dominant Interest:</span>
            <span style='color: #e2e8f0; font-weight: 700; font-size: 1.1em; margin-left: 8px;'>
                {dominant}
            </span>
        </div>
    """

    # Cluster distribution mini-bars
    dist = profile.get('cluster_distribution', {})
    if dist:
        max_count = max(dist.values())
        dist_html = "<div style='margin-top: 16px;'>"
        dist_html += "<div style='color: #94a3b8; font-size: 0.9em; margin-bottom: 10px;'>Interest Distribution:</div>"
        bar_colors = ['#6366f1', '#a78bfa', '#f59e0b', '#22c55e', '#ef4444', '#06b6d4', '#f472b6', '#84cc16']
        for i, (name, count) in enumerate(dist.items()):
            pct = (count / max_count) * 100
            color = bar_colors[i % len(bar_colors)]
            dist_html += f"""
            <div style='display: flex; align-items: center; gap: 10px; margin-bottom: 6px;'>
                <span style='color: #cbd5e1; font-size: 0.85em; min-width: 160px;'>{name}</span>
                <div style='flex-grow: 1; background: rgba(255,255,255,0.06); border-radius: 6px; height: 18px; overflow: hidden;'>
                    <div style='background: {color}; width: {pct}%; height: 100%; border-radius: 6px;
                                transition: width 0.8s ease;'></div>
                </div>
                <span style='color: #64748b; font-size: 0.85em; min-width: 24px; text-align: right;'>{count}</span>
            </div>
            """
        dist_html += "</div>"
        profile_html += dist_html

    profile_html += "</div>"

    # ── Curiosity Expansion Predictions ──
    expansion_html = """
    <div style='margin-bottom: 24px;'>
        <h2 style='color: #f1f5f9; font-size: 1.4em; margin-bottom: 16px;'>
            🔮 Predicted Curiosity Expansion
        </h2>
        <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px;'>
    """

    gradient_colors = [
        ('135deg', '#667eea', '#764ba2'),
        ('135deg', '#f093fb', '#f5576c'),
        ('135deg', '#4facfe', '#00f2fe'),
    ]

    for i, exp in enumerate(expansions):
        g = gradient_colors[i % len(gradient_colors)]
        score_pct = int(exp['exploration_score'] * 100)
        sample_list = ''.join(
            f"<li style='margin: 4px 0; font-size: 0.9em;'>{b}</li>"
            for b in exp['sample_books'][:3]
        )

        expansion_html += f"""
        <div style='background: linear-gradient({g[0]}, {g[1]}20, {g[2]}20);
                    border: 1px solid {g[1]}40; border-radius: 16px; padding: 24px;
                    transition: transform 0.3s ease, box-shadow 0.3s ease;'
             onmouseover="this.style.transform='translateY(-4px)'; this.style.boxShadow='0 12px 40px rgba(0,0,0,0.3)'"
             onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='none'">
            <div style='font-size: 1.2em; font-weight: 700; color: #f1f5f9; margin-bottom: 8px;'>
                {exp['area']}
            </div>
            <div style='font-size: 0.88em; color: #94a3b8; font-style: italic; margin-bottom: 12px;'>
                "{exp['pathway_description']}"
            </div>
            <div style='margin-bottom: 12px;'>
                <span style='color: #94a3b8; font-size: 0.85em;'>Match Score:</span>
                <div style='background: rgba(255,255,255,0.08); border-radius: 6px; height: 20px;
                            overflow: hidden; margin-top: 4px;'>
                    <div style='background: linear-gradient(90deg, {g[1]}, {g[2]}); width: {score_pct}%;
                                height: 100%; border-radius: 6px; transition: width 1s ease;'></div>
                </div>
                <div style='text-align: right; color: #cbd5e1; font-size: 0.8em; margin-top: 2px;'>{score_pct}%</div>
            </div>
            <div style='color: #94a3b8; font-size: 0.85em;'>Sample Books:</div>
            <ul style='color: #cbd5e1; margin: 4px 0; padding-left: 20px;'>
                {sample_list}
            </ul>
        </div>
        """

    expansion_html += "</div></div>"

    # ── Suggested Reading Journey ──
    journey_html = f"""
    <div style='background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                border-radius: 20px; padding: 30px; margin-bottom: 24px;'>
        <h2 style='color: #f1f5f9; font-size: 1.4em; margin: 0 0 6px 0;'>
            📦 Suggested Reading Journey
        </h2>
        <div style='color: #94a3b8; margin-bottom: 8px; font-size: 1em;'>
            <strong style='color: #a78bfa;'>{journey['title']}</strong>
        </div>
        <div style='color: #64748b; font-size: 0.92em; font-style: italic; margin-bottom: 24px;'>
            {journey['pathway']}
        </div>
    """

    for step in journey['steps']:
        title_encoded = quote(step['title'])
        cover_url = f"https://covers.openlibrary.org/b/title/{title_encoded}-M.jpg"

        desc = step['description']
        if len(desc) > 180:
            desc = desc[:180] + '...'

        journey_html += f"""
        <div style='display: flex; gap: 20px; margin-bottom: 20px; padding: 20px;
                    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
                    border-radius: 14px; border-left: 4px solid {step['novelty_color']};
                    transition: transform 0.2s ease;'
             onmouseover="this.style.transform='translateX(6px)'"
             onmouseout="this.style.transform='translateX(0)'">

            <!-- Step Number -->
            <div style='flex-shrink: 0; width: 48px; height: 48px; border-radius: 50%;
                        background: {step['novelty_color']}20; border: 2px solid {step['novelty_color']};
                        display: flex; align-items: center; justify-content: center;
                        font-size: 1.2em; font-weight: 800; color: {step['novelty_color']};'>
                {step['step']}
            </div>

            <!-- Cover -->
            <div style='flex-shrink: 0;'>
                <img src="{cover_url}" alt="{step['title']}"
                     style='width: 70px; height: 105px; object-fit: cover; border-radius: 8px;
                            box-shadow: 0 4px 12px rgba(0,0,0,0.3);'
                     onerror="this.src='https://via.placeholder.com/70x105/1e1b4b/a5b4fc?text=No+Cover'"/>
            </div>

            <!-- Info -->
            <div style='flex-grow: 1;'>
                <div style='color: #f1f5f9; font-weight: 700; font-size: 1.05em;'>{step['title']}</div>
                <div style='color: #94a3b8; font-size: 0.88em;'>✍️ {step['authors']} • 📂 {step['categories']}</div>
                <div style='margin-top: 6px;'>
                    <span style='background: {step['novelty_color']}20; color: {step['novelty_color']};
                                  padding: 2px 10px; border-radius: 6px; font-size: 0.78em; font-weight: 600;'>
                        {step['novelty_level']} Novelty
                    </span>
                </div>
                <div style='color: #64748b; font-size: 0.85em; margin-top: 6px; line-height: 1.5;'>
                    {desc}
                </div>
                <div style='color: #a78bfa; font-size: 0.82em; margin-top: 6px; font-style: italic;'>
                    💡 {step['rationale']}
                </div>
            </div>
        </div>
        """

        # Arrow connector between steps
        if step['step'] < len(journey['steps']):
            journey_html += """
            <div style='text-align: center; color: #4b5563; font-size: 1.5em; margin: -6px 0;'>↓</div>
            """

    journey_html += "</div>"

    # ── Curiosity Impact Score ──
    def gauge_html(label, value, color, icon):
        return f"""
        <div style='text-align: center; padding: 24px;
                    background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08);
                    border-radius: 16px;'>
            <div style='font-size: 1.4em; margin-bottom: 8px;'>{icon}</div>
            <div style='position: relative; width: 120px; height: 120px; margin: 0 auto 12px auto;'>
                <!-- Background circle -->
                <svg viewBox="0 0 120 120" style='transform: rotate(-90deg);'>
                    <circle cx="60" cy="60" r="52" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="10"/>
                    <circle cx="60" cy="60" r="52" fill="none" stroke="{color}" stroke-width="10"
                            stroke-dasharray="{value * 3.27} {327 - value * 3.27}"
                            stroke-linecap="round"
                            style="transition: stroke-dasharray 1.5s ease;"/>
                </svg>
                <div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
                            font-size: 1.6em; font-weight: 800; color: {color};'>
                    {value}
                </div>
            </div>
            <div style='color: #e2e8f0; font-weight: 600; font-size: 0.95em;'>{label}</div>
        </div>
        """

    impact_html = f"""
    <div style='margin-bottom: 24px;'>
        <h2 style='color: #f1f5f9; font-size: 1.4em; margin-bottom: 16px;'>
            📊 Curiosity Impact Score
        </h2>
        <div style='display: grid; grid-template-columns: repeat(3, 1fr); gap: 16px;'>
            {gauge_html('Exploration Level', impact['exploration_level'], '#6366f1', '🔭')}
            {gauge_html('Intellectual Diversity', impact['intellectual_diversity'], '#22c55e', '🌈')}
            {gauge_html('Growth Index', impact['growth_index'], '#f59e0b', '📈')}
        </div>
    </div>
    """

    # Full page
    return profile_html + expansion_html + journey_html + impact_html


def build_curiosity_tab(engine):
    """
    Build the Curiosity Path Gradio tab

    Args:
        engine: CuriosityEngine instance

    Returns:
        gr.Tab: The curiosity path tab
    """
    with gr.Tab("🧠 Curiosity Path", id="curiosity") as tab:
        gr.HTML("""
        <div style='text-align: center; padding: 25px 20px 15px 20px;'>
            <h1 style='font-size: 2.2em; margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #a78bfa 50%, #f093fb 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-weight: 800; letter-spacing: -0.5px;'>
                🧠 AI Curiosity Engine
            </h1>
            <p style='color: #94a3b8; font-size: 1.1em; margin-top: 8px;'>
                Predictive intellectual stimulation • Structured reading journeys • Knowledge discovery
            </p>
            <p style='color: #64748b; font-size: 0.9em; margin-top: 4px;'>
                Discover what you <em>should</em> read next — not just what's similar, but what will <strong>expand your mind</strong>
            </p>
        </div>
        """)

        analyze_btn = gr.Button(
            "🔬 Analyze My Curiosity & Generate Journey",
            variant="primary",
            size="lg"
        )

        curiosity_output = gr.HTML(
            value="<div style='text-align: center; padding: 60px; color: #64748b;'>"
                  "<div style='font-size: 3em; margin-bottom: 16px;'>🧠</div>"
                  "<h3 style='color: #94a3b8;'>Click the button above to discover your curiosity path!</h3>"
                  "<p>The AI will analyze your search history and generate a personalized reading journey.</p>"
                  "<p style='font-size: 0.9em;'>💡 Tip: Search for some books on the Discover tab first to build your profile.</p>"
                  "</div>",
            label=""
        )

        analyze_btn.click(
            fn=lambda: _build_curiosity_html(engine),
            inputs=[],
            outputs=curiosity_output
        )

    return tab
