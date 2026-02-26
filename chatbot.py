"""
Memory-Based Chatbot Module for Semantic Book Recommender
Conversational book discovery with session history and context awareness
"""

import gradio as gr
import re
import json
import os
from datetime import datetime
from pathlib import Path


class BookChatbot:
    """
    Conversational chatbot that uses the BookRecommender engine
    with session memory for context-aware responses
    """
    
    def __init__(self, recommender, tracker=None):
        """
        Initialize the chatbot
        
        Args:
            recommender: BookRecommender instance
            tracker: InteractionTracker instance (optional)
        """
        self.recommender = recommender
        self.tracker = tracker
        self.session_file = 'data/chat_sessions.json'
        self.last_recommendations = []
        Path('data').mkdir(parents=True, exist_ok=True)
    
    def _detect_intent(self, message):
        """
        Detect the user's intent from their message
        
        Returns:
            str: Intent type - 'recommend', 'detail', 'greeting', 'help', 'thanks', 'general'
        """
        msg = message.lower().strip()
        
        # Greeting patterns
        if any(g in msg for g in ['hello', 'hi', 'hey', 'good morning', 'good evening', 
                                    'howdy', 'greetings', 'namaste', 'hola', 'bonjour']):
            return 'greeting'
        
        # Help request
        if any(h in msg for h in ['help', 'what can you do', 'how to use', 'features',
                                    'what do you do', 'how does this work']):
            return 'help'
        
        # Thanks
        if any(t in msg for t in ['thank', 'thanks', 'thx', 'appreciate', 'great', 'awesome',
                                    'wonderful', 'perfect', 'nice']):
            return 'thanks'
        
        # Detail about a specific previously recommended book
        detail_patterns = [
            r'(tell me more|more about|details|info|information).*(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|\d+)',
            r'(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|\d+).*(one|book|option|choice|recommendation)',
            r'(what is|what\'s|describe|explain).*(first|1st|second|2nd|third|3rd|fourth|4th|fifth|5th|\d+)',
            r'(#\d+|number \d+|no\.?\s*\d+)',
            r'(tell me more|more details|elaborate|expand)',
        ]
        for pattern in detail_patterns:
            if re.search(pattern, msg):
                return 'detail'
        
        # Recommendation request (broad catch)
        recommend_words = ['recommend', 'suggest', 'find', 'search', 'look', 'want',
                          'need', 'give me', 'show me', 'any', 'book about', 'books about',
                          'novel', 'story', 'read', 'genre', 'mystery', 'romance', 
                          'fantasy', 'thriller', 'horror', 'adventure', 'sci-fi',
                          'science fiction', 'historical', 'comedy', 'drama',
                          'fiction', 'non-fiction', 'biography', 'autobiography']
        if any(w in msg for w in recommend_words):
            return 'recommend'
        
        # If message is long enough, probably a recommendation query
        if len(msg.split()) >= 3:
            return 'recommend'
        
        return 'general'
    
    def _extract_book_number(self, message):
        """Extract which book number the user is referring to"""
        msg = message.lower()
        
        ordinals = {
            'first': 1, '1st': 1, 'second': 2, '2nd': 2, 
            'third': 3, '3rd': 3, 'fourth': 4, '4th': 4, 
            'fifth': 5, '5th': 5
        }
        
        for word, num in ordinals.items():
            if word in msg:
                return num
        
        # Check for #N or number N patterns
        match = re.search(r'#(\d+)|number\s+(\d+)|no\.?\s*(\d+)', msg)
        if match:
            for g in match.groups():
                if g:
                    return int(g)
        
        # Default to 1 if just "tell me more"
        return 1
    
    def _format_recommendation_chat(self, rec):
        """Format a single recommendation for chat display"""
        exp = rec.get('explanation', {})
        themes = ', '.join(exp.get('themes', ['General']))
        match_level = exp.get('match_level', 'Good')
        
        desc = rec['description']
        if len(desc) > 250:
            desc = desc[:250] + "..."
        
        return (
            f"**#{rec['rank']} — {rec['title']}**\n"
            f"✍️ *{rec['authors']}* | 📂 {rec['categories']}\n"
            f"🎯 Match: **{match_level}** ({rec['similarity_score']:.0%}) | 🏷️ Themes: {themes}\n\n"
            f"> {desc}\n"
        )
    
    def _format_book_detail(self, book_data):
        """Format detailed book info for chat"""
        desc = book_data['description']
        return (
            f"## 📖 {book_data['title']}\n\n"
            f"**Author(s):** {book_data['authors']}\n"
            f"**Category:** {book_data['categories']}\n\n"
            f"**Description:**\n{desc}\n\n"
            f"---\n"
            f"Would you like me to find similar books, or do you have another query? 😊"
        )
    
    def respond(self, message, history):
        """
        Generate a response to the user's message
        
        Args:
            message: User's input message
            history: List of [user_msg, bot_msg] pairs (Gradio chat history)
        
        Returns:
            str: Bot's response
        """
        if not message or message.strip() == '':
            return "Please type a message! I'm here to help you find great books 📚"
        
        # Detect language
        try:
            from langdetect import detect
            lang = detect(message)
        except Exception:
            lang = 'en'
        
        intent = self._detect_intent(message)
        response = ""
        
        if intent == 'greeting':
            response = (
                "# 👋 Hello! Welcome to Book Chat!\n\n"
                "I'm your AI book companion. I can help you:\n\n"
                "- 📚 **Find book recommendations** based on your interests\n"
                "- 🔍 **Search by genre, theme, or mood**\n"
                "- 📖 **Get details** about specific books\n"
                "- 🌍 **Understand queries in multiple languages**\n\n"
                "Just describe what kind of book you're looking for! For example:\n"
                "*\"I want a mystery novel with lots of suspense\"*"
            )
        
        elif intent == 'help':
            response = (
                "# 🆘 How to Use Book Chat\n\n"
                "Here's what you can do:\n\n"
                "1. **Ask for recommendations:** *\"Suggest a fantasy book with dragons\"*\n"
                "2. **Search by mood:** *\"I'm feeling adventurous, what should I read?\"*\n"
                "3. **Get details:** After I recommend books, say *\"Tell me more about the first one\"*\n"
                "4. **Multilingual:** Ask in Hindi, French, Spanish, or any language!\n"
                "5. **Follow-up questions:** Our conversation has memory — I remember previous recommendations\n\n"
                "Go ahead, try asking me something! 😊"
            )
        
        elif intent == 'thanks':
            response = (
                "You're welcome! 😊 Happy reading! 📚\n\n"
                "Feel free to ask for more recommendations anytime. "
                "I'm always here to help you discover your next favorite book!"
            )
        
        elif intent == 'detail':
            book_num = self._extract_book_number(message)
            if self.last_recommendations and 1 <= book_num <= len(self.last_recommendations):
                rec = self.last_recommendations[book_num - 1]
                book_info = {
                    'title': rec['title'],
                    'authors': rec['authors'],
                    'categories': rec['categories'],
                    'description': rec['description']
                }
                response = self._format_book_detail(book_info)
            else:
                # Try searching by title from the message
                search_results = self.recommender.search_by_title(message)
                if search_results:
                    response = self._format_book_detail(search_results[0])
                else:
                    response = (
                        "I don't have a previous recommendation to refer to. "
                        "Could you ask me to recommend some books first? 📚\n\n"
                        "For example: *\"Recommend me a mystery novel\"*"
                    )
        
        elif intent == 'recommend':
            try:
                recommendations = self.recommender.recommend_books(message, k=5)
                self.last_recommendations = recommendations
                
                lang_name = recommendations[0].get('language_name', 'English') if recommendations else 'English'
                
                response = f"# 📚 Here are my top recommendations!\n"
                if lang_name != 'English':
                    response += f"*🌍 Detected language: {lang_name}*\n"
                response += "\n"
                
                for rec in recommendations:
                    response += self._format_recommendation_chat(rec) + "\n"
                
                response += (
                    "\n---\n"
                    "💡 **Tip:** Say *\"tell me more about #2\"* for details, "
                    "or describe another type of book you'd like!"
                )
                
                # Log interaction
                if self.tracker:
                    self.tracker.log_search(message, lang, len(recommendations), recommendations)
                    for rec in recommendations:
                        self.tracker.log_book_view(rec['title'], source='chatbot')
                
            except Exception as e:
                response = f"Oops! Something went wrong: {str(e)}\nPlease try rephrasing your query. 🔄"
        
        else:
            # General / fallback - try recommendation
            try:
                recommendations = self.recommender.recommend_books(message, k=3)
                self.last_recommendations = recommendations
                
                response = "I'm not entirely sure what you mean, but here are some books that might match:\n\n"
                for rec in recommendations:
                    response += self._format_recommendation_chat(rec) + "\n"
                
                response += "\n💡 Try being more specific about the genre or theme you're interested in!"
                
            except Exception:
                response = (
                    "I'm not sure I understand. Here are some things you can try:\n\n"
                    "- *\"Recommend a thriller book\"*\n"
                    "- *\"I want to read something romantic\"*\n"
                    "- *\"Find me a sci-fi adventure\"*\n\n"
                    "Just describe what you're in the mood for! 📚"
                )
        
        # Log chatbot message
        if self.tracker:
            self.tracker.log_chatbot_message(message, response, lang)
        
        return response


def build_chatbot_tab(recommender, tracker=None):
    """
    Build the Chatbot tab for the Gradio app
    
    Args:
        recommender: BookRecommender instance
        tracker: InteractionTracker instance
    
    Returns:
        gr.Tab: The chatbot tab component
    """
    chatbot_engine = BookChatbot(recommender, tracker)
    
    with gr.Tab("🤖 Book Chat", id="chatbot") as tab:
        gr.HTML("""
        <div style='text-align: center; padding: 25px 20px 15px 20px;'>
            <h1 style='font-size: 2.2em; margin: 0; 
                        background: linear-gradient(135deg, #00d2ff 0%, #7b2ff7 100%);
                        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                        font-weight: 800; letter-spacing: -0.5px;'>
                🤖 Book Chat Assistant
            </h1>
            <p style='color: #94a3b8; font-size: 1.1em; margin-top: 8px;'>
                Your AI-powered conversational book companion • Supports 50+ languages • Remembers context
            </p>
        </div>
        """)
        
        chatbot_ui = gr.Chatbot(
            value=[],
            height=520,
            show_label=False,
        )
        
        with gr.Row():
            chat_input = gr.Textbox(
                placeholder="Ask me anything about books... (try: 'recommend a mystery novel', 'tell me about Harry Potter')",
                show_label=False,
                scale=8,
                container=False
            )
            send_btn = gr.Button("Send 📨", variant="primary", scale=1, min_width=100)
        
        with gr.Row():
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", size="sm")
            example1 = gr.Button("💡 Mystery novels", size="sm")
            example2 = gr.Button("💡 Fantasy adventure", size="sm")
            example3 = gr.Button("💡 Romantic fiction", size="sm")
            example4 = gr.Button("💡 Sci-fi books", size="sm")
        
        def user_send(message, history):
            if not message or message.strip() == '':
                return "", history
            
            # Add user message
            history = history + [{"role": "user", "content": message}]
            
            # Generate response
            # Convert history to the format expected by the chatbot engine
            legacy_history = []
            for i in range(0, len(history) - 1, 2):
                if i + 1 < len(history):
                    legacy_history.append([
                        history[i].get("content", ""),
                        history[i+1].get("content", "")
                    ])
            
            response = chatbot_engine.respond(message, legacy_history)
            
            # Add bot response
            history = history + [{"role": "assistant", "content": response}]
            
            return "", history
        
        def example_click(example_text):
            return example_text
        
        # Wire up interactions
        send_btn.click(
            fn=user_send,
            inputs=[chat_input, chatbot_ui],
            outputs=[chat_input, chatbot_ui]
        )
        
        chat_input.submit(
            fn=user_send,
            inputs=[chat_input, chatbot_ui],
            outputs=[chat_input, chatbot_ui]
        )
        
        clear_btn.click(
            fn=lambda: ([], ""),
            inputs=[],
            outputs=[chatbot_ui, chat_input]
        )
        
        example1.click(fn=lambda: "Recommend me a mystery novel with suspense", outputs=[chat_input])
        example2.click(fn=lambda: "I want a fantasy adventure with magic and dragons", outputs=[chat_input])
        example3.click(fn=lambda: "Suggest a romantic fiction book", outputs=[chat_input])
        example4.click(fn=lambda: "Find me a sci-fi book about space exploration", outputs=[chat_input])
    
    return tab
