"""
Interaction Tracker Module for Semantic Book Recommender
Tracks user searches, mood selections, chatbot conversations, and surprise clicks
Stores data in a lightweight JSON file for dashboard analytics
"""

import json
import os
import threading
from datetime import datetime
from pathlib import Path


class InteractionTracker:
    """
    Lightweight JSON-based user interaction tracking system
    Thread-safe file I/O for concurrent access
    """
    
    def __init__(self, data_path='data/interactions.json'):
        self.data_path = data_path
        self._lock = threading.Lock()
        self._ensure_file()
    
    def _ensure_file(self):
        """Create the interactions file if it doesn't exist"""
        Path(os.path.dirname(self.data_path)).mkdir(parents=True, exist_ok=True)
        if not os.path.exists(self.data_path):
            self._write_data({
                'searches': [],
                'mood_selections': [],
                'surprise_clicks': [],
                'chatbot_conversations': [],
                'book_views': [],
                'journey_starts': []
            })
    
    def _read_data(self):
        """Read interaction data from JSON file"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return {
                'searches': [],
                'mood_selections': [],
                'surprise_clicks': [],
                'chatbot_conversations': [],
                'book_views': [],
                'journey_starts': []
            }
    
    def _write_data(self, data):
        """Write interaction data to JSON file"""
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def log_search(self, query, language='en', num_results=5, results=None):
        """Log a search interaction"""
        with self._lock:
            data = self._read_data()
            data['searches'].append({
                'query': query,
                'language': language,
                'num_results': num_results,
                'result_titles': [r['title'] for r in (results or [])],
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    def log_mood_selection(self, mood):
        """Log a mood button click"""
        with self._lock:
            data = self._read_data()
            data['mood_selections'].append({
                'mood': mood,
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    def log_surprise_click(self):
        """Log a surprise-me button click"""
        with self._lock:
            data = self._read_data()
            data['surprise_clicks'].append({
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    def log_chatbot_message(self, user_message, bot_response, language='en'):
        """Log a chatbot conversation turn"""
        with self._lock:
            data = self._read_data()
            data['chatbot_conversations'].append({
                'user_message': user_message,
                'bot_response': bot_response[:200],  # Truncate for storage
                'language': language,
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    def log_book_view(self, book_title, source='search'):
        """Log when a book is viewed/recommended"""
        with self._lock:
            data = self._read_data()
            data['book_views'].append({
                'title': book_title,
                'source': source,
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    # ─── Aggregation Methods for Dashboard ───
    
    def get_search_trends(self):
        """Get search count grouped by date"""
        data = self._read_data()
        trends = {}
        for s in data.get('searches', []):
            date = s['timestamp'][:10]  # YYYY-MM-DD
            trends[date] = trends.get(date, 0) + 1
        return dict(sorted(trends.items()))
    
    def get_category_stats(self):
        """Get category distribution from search result titles"""
        data = self._read_data()
        titles = []
        for s in data.get('searches', []):
            titles.extend(s.get('result_titles', []))
        # Count title occurrences as a proxy for category interest
        title_counts = {}
        for t in titles:
            title_counts[t] = title_counts.get(t, 0) + 1
        return dict(sorted(title_counts.items(), key=lambda x: x[1], reverse=True)[:15])
    
    def get_popular_books(self, limit=10):
        """Get most frequently recommended/viewed books"""
        data = self._read_data()
        book_counts = {}
        for bv in data.get('book_views', []):
            title = bv['title']
            book_counts[title] = book_counts.get(title, 0) + 1
        for s in data.get('searches', []):
            for title in s.get('result_titles', []):
                book_counts[title] = book_counts.get(title, 0) + 1
        return dict(sorted(book_counts.items(), key=lambda x: x[1], reverse=True)[:limit])
    
    def get_mood_distribution(self):
        """Get mood selection distribution"""
        data = self._read_data()
        moods = {}
        for m in data.get('mood_selections', []):
            mood = m['mood']
            moods[mood] = moods.get(mood, 0) + 1
        return moods
    
    def get_language_stats(self):
        """Get language distribution from searches"""
        data = self._read_data()
        langs = {}
        for s in data.get('searches', []):
            lang = s.get('language', 'en')
            langs[lang] = langs.get(lang, 0) + 1
        for c in data.get('chatbot_conversations', []):
            lang = c.get('language', 'en')
            langs[lang] = langs.get(lang, 0) + 1
        return langs
    
    def get_recent_activity(self, limit=20):
        """Get recent activity feed"""
        data = self._read_data()
        activities = []
        
        for s in data.get('searches', []):
            activities.append({
                'type': '🔍 Search',
                'detail': s['query'][:50],
                'language': s.get('language', 'en'),
                'timestamp': s['timestamp']
            })
        
        for m in data.get('mood_selections', []):
            activities.append({
                'type': '🎭 Mood',
                'detail': m['mood'],
                'language': '-',
                'timestamp': m['timestamp']
            })
        
        for sc in data.get('surprise_clicks', []):
            activities.append({
                'type': '🎲 Surprise',
                'detail': 'Random discovery',
                'language': '-',
                'timestamp': sc['timestamp']
            })
        
        for c in data.get('chatbot_conversations', []):
            activities.append({
                'type': '🤖 Chat',
                'detail': c['user_message'][:50],
                'language': c.get('language', 'en'),
                'timestamp': c['timestamp']
            })
        
        # Sort by timestamp descending
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        return activities[:limit]
    
    def get_summary_stats(self):
        """Get summary statistics for dashboard cards"""
        data = self._read_data()
        
        # Unique languages
        languages = set()
        for s in data.get('searches', []):
            languages.add(s.get('language', 'en'))
        for c in data.get('chatbot_conversations', []):
            languages.add(c.get('language', 'en'))
        
        # Most popular category/mood
        moods = self.get_mood_distribution()
        top_mood = max(moods, key=moods.get) if moods else 'N/A'
        
        return {
            'total_searches': len(data.get('searches', [])),
            'total_chats': len(data.get('chatbot_conversations', [])),
            'total_moods': len(data.get('mood_selections', [])),
            'total_surprises': len(data.get('surprise_clicks', [])),
            'unique_languages': len(languages),
            'top_mood': top_mood,
            'total_interactions': (
                len(data.get('searches', [])) + 
                len(data.get('mood_selections', [])) +
                len(data.get('surprise_clicks', [])) +
                len(data.get('chatbot_conversations', []))
            )
        }
    
    def log_journey_start(self, journey_data):
        """Log when a user starts a curiosity journey"""
        with self._lock:
            data = self._read_data()
            if 'journey_starts' not in data:
                data['journey_starts'] = []
            data['journey_starts'].append({
                'title': journey_data.get('title', ''),
                'from_area': journey_data.get('from_area', ''),
                'to_area': journey_data.get('to_area', ''),
                'num_steps': len(journey_data.get('steps', [])),
                'timestamp': datetime.now().isoformat()
            })
            self._write_data(data)
    
    def get_curiosity_history(self):
        """Get journey start history"""
        data = self._read_data()
        return data.get('journey_starts', [])
