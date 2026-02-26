"""
AI Curiosity Engine for Semantic Book Recommender
Predictive intellectual stimulation system that:
- Analyzes user interaction history
- Performs semantic clustering on book embeddings
- Identifies adjacent unexplored topic areas
- Generates structured multi-step reading journeys
- Computes Curiosity Impact Scores
"""

import numpy as np
import faiss
from collections import Counter
from sklearn.cluster import KMeans


# ── Topic Labels for Clusters ──
# These are auto-assigned based on category majority in each cluster
THEME_LABELS = {
    'fiction': '📖 Literary Fiction',
    'mystery': '🔍 Mystery & Thriller',
    'fantasy': '🐉 Fantasy & Mythology',
    'science fiction': '🚀 Science Fiction',
    'romance': '💕 Romance',
    'horror': '👻 Horror & Dark Fiction',
    'history': '🏛️ Historical',
    'biography': '👤 Biography & Memoir',
    'self-help': '🧘 Self-Help & Growth',
    'philosophy': '🤔 Philosophy',
    'psychology': '🧠 Psychology',
    'science': '🔬 Science & Technology',
    'adventure': '⚔️ Adventure',
    'children': '👶 Children & Young Adult',
    'poetry': '✨ Poetry & Literature',
    'religion': '🙏 Religion & Spirituality',
    'education': '🎓 Education & Learning',
    'drama': '🎭 Drama',
    'humor': '😄 Comedy & Humor',
    'politics': '⚖️ Politics & Society',
}

# Expansion pathway descriptions
EXPANSION_PATHWAYS = {
    ('fantasy', 'history'): 'From magical worlds to the real myths that inspired them',
    ('fantasy', 'philosophy'): 'From epic quests to the philosophical questions they raise',
    ('fantasy', 'psychology'): 'From hero archetypes to understanding the human psyche',
    ('mystery', 'psychology'): 'From solving crimes to understanding criminal minds',
    ('mystery', 'philosophy'): 'From whodunits to questions of justice and morality',
    ('mystery', 'history'): 'From fictional cases to real historical mysteries',
    ('science fiction', 'science'): 'From imagined futures to real scientific frontiers',
    ('science fiction', 'philosophy'): 'From dystopian worlds to existential questions',
    ('science fiction', 'psychology'): 'From AI characters to understanding consciousness',
    ('romance', 'psychology'): 'From love stories to the psychology of relationships',
    ('romance', 'history'): 'From romantic fiction to great love stories in history',
    ('horror', 'psychology'): 'From fictional fear to understanding what terrifies us',
    ('horror', 'philosophy'): 'From dark tales to existential dread and meaning',
    ('fiction', 'philosophy'): 'From compelling narratives to deeper life questions',
    ('fiction', 'psychology'): 'From character studies to understanding human behavior',
    ('fiction', 'history'): 'From fictional worlds to the eras that shaped them',
    ('adventure', 'history'): 'From fictional expeditions to real explorations',
    ('adventure', 'science'): 'From quests in fiction to scientific discoveries',
}


class CuriosityEngine:
    """
    AI-powered intellectual curiosity prediction and reading journey generator.
    Uses semantic clustering to identify user's comfort zone and discover
    adjacent but unexplored knowledge domains.
    """

    def __init__(self, recommender, tracker, n_clusters=8):
        """
        Initialize the Curiosity Engine

        Args:
            recommender: BookRecommender instance (has FAISS index + model)
            tracker: InteractionTracker instance
            n_clusters: Number of topic clusters to form
        """
        self.recommender = recommender
        self.tracker = tracker
        self.n_clusters = min(n_clusters, len(recommender.books_df) // 3)
        self.books_df = recommender.books_df.copy()

        # Build cluster map from book embeddings
        self._build_clusters()

    def _build_clusters(self):
        """
        Perform K-Means clustering on all book embeddings to identify
        semantic topic areas in the dataset.
        """
        # Extract all embeddings from the FAISS index
        n_books = self.recommender.index.ntotal
        dim = self.recommender.index.d
        self.all_embeddings = np.zeros((n_books, dim), dtype='float32')

        for i in range(n_books):
            self.all_embeddings[i] = self.recommender.index.reconstruct(i)

        # K-Means clustering
        self.kmeans = KMeans(
            n_clusters=self.n_clusters,
            random_state=42,
            n_init=10
        )
        self.cluster_labels = self.kmeans.fit_predict(self.all_embeddings)
        self.centroids = self.kmeans.cluster_centers_

        # Assign topic labels to each cluster based on dominant category
        self.cluster_names = {}
        self.cluster_categories = {}
        for c in range(self.n_clusters):
            mask = self.cluster_labels == c
            cluster_books = self.books_df[mask]
            if len(cluster_books) > 0:
                cats = cluster_books['categories'].str.lower().tolist()
                dominant_cat = Counter(cats).most_common(1)[0][0]
                label = THEME_LABELS.get(dominant_cat, f'📚 {dominant_cat.title()}')
                self.cluster_names[c] = label
                self.cluster_categories[c] = dominant_cat
            else:
                self.cluster_names[c] = f'📚 Cluster {c}'
                self.cluster_categories[c] = 'unknown'

        # Compute inter-cluster distances for adjacency
        self.cluster_distances = np.zeros((self.n_clusters, self.n_clusters))
        for i in range(self.n_clusters):
            for j in range(self.n_clusters):
                self.cluster_distances[i][j] = np.linalg.norm(
                    self.centroids[i] - self.centroids[j]
                )

    def _get_user_interacted_books(self):
        """Get list of books the user has interacted with from tracker history"""
        data = self.tracker._read_data()
        interacted_titles = set()

        # From searches (result titles)
        for s in data.get('searches', []):
            for title in s.get('result_titles', []):
                interacted_titles.add(title)

        # From book views
        for bv in data.get('book_views', []):
            interacted_titles.add(bv['title'])

        return list(interacted_titles)

    def _get_book_indices(self, titles):
        """Convert book titles to dataframe indices"""
        indices = []
        for title in titles:
            mask = self.books_df['title'] == title
            matches = self.books_df[mask]
            if len(matches) > 0:
                indices.append(matches.index[0])
        return indices

    def analyze_user_profile(self):
        """
        Analyze the user's intellectual profile based on interaction history.

        Returns:
            dict with keys:
                - dominant_interest: str (cluster name)
                - dominant_cluster_id: int
                - cluster_distribution: dict of cluster_name -> count
                - total_books_explored: int
                - exploration_breadth: float (0-1, fraction of clusters touched)
                - comfort_zone_books: list of book titles in dominant cluster
        """
        interacted_titles = self._get_user_interacted_books()

        if not interacted_titles:
            return {
                'dominant_interest': '🆕 New Explorer',
                'dominant_cluster_id': -1,
                'cluster_distribution': {},
                'total_books_explored': 0,
                'exploration_breadth': 0.0,
                'comfort_zone_books': [],
                'is_new_user': True
            }

        book_indices = self._get_book_indices(interacted_titles)
        if not book_indices:
            return {
                'dominant_interest': '🆕 New Explorer',
                'dominant_cluster_id': -1,
                'cluster_distribution': {},
                'total_books_explored': 0,
                'exploration_breadth': 0.0,
                'comfort_zone_books': [],
                'is_new_user': True
            }

        # Find which clusters the user has engaged with
        user_clusters = [self.cluster_labels[i] for i in book_indices]
        cluster_counts = Counter(user_clusters)

        # Build distribution
        cluster_distribution = {}
        for c, count in cluster_counts.most_common():
            cluster_distribution[self.cluster_names[c]] = count

        # Dominant cluster
        dominant_cluster_id = cluster_counts.most_common(1)[0][0]
        dominant_interest = self.cluster_names[dominant_cluster_id]

        # Comfort zone books
        dominant_mask = self.cluster_labels == dominant_cluster_id
        comfort_books = self.books_df[dominant_mask]['title'].tolist()

        # Exploration breadth (how many unique clusters touched)
        unique_clusters = len(set(user_clusters))
        exploration_breadth = unique_clusters / self.n_clusters

        return {
            'dominant_interest': dominant_interest,
            'dominant_cluster_id': dominant_cluster_id,
            'cluster_distribution': cluster_distribution,
            'total_books_explored': len(interacted_titles),
            'exploration_breadth': exploration_breadth,
            'comfort_zone_books': comfort_books[:5],
            'is_new_user': False
        }

    def predict_curiosity_expansion(self, profile=None):
        """
        Predict which topic areas the user is likely to find intellectually
        stimulating next, based on adjacency to their current interests
        and unexplored areas.

        Args:
            profile: User profile dict (from analyze_user_profile). 
                     Computed if not provided.

        Returns:
            list of dicts, each containing:
                - area: str (cluster name)
                - cluster_id: int
                - distance_score: float (semantic distance from dominant)
                - exploration_score: float (0=familiar, 1=novel)
                - pathway_description: str
                - sample_books: list of book titles
        """
        if profile is None:
            profile = self.analyze_user_profile()

        if profile.get('is_new_user', True):
            # For new users, suggest diverse starting points
            expansions = []
            for c in range(min(3, self.n_clusters)):
                mask = self.cluster_labels == c
                sample_books = self.books_df[mask]['title'].tolist()[:3]
                expansions.append({
                    'area': self.cluster_names[c],
                    'cluster_id': c,
                    'distance_score': 0.5,
                    'exploration_score': 0.5,
                    'pathway_description': 'Start your reading journey here!',
                    'sample_books': sample_books
                })
            return expansions

        dominant_id = profile['dominant_cluster_id']
        dominant_cat = self.cluster_categories.get(dominant_id, 'fiction')

        # Find user's visited clusters
        visited_clusters = set()
        interacted_titles = self._get_user_interacted_books()
        book_indices = self._get_book_indices(interacted_titles)
        for idx in book_indices:
            visited_clusters.add(self.cluster_labels[idx])

        # Score all unvisited or under-visited clusters
        candidates = []
        for c in range(self.n_clusters):
            if c == dominant_id:
                continue

            dist = self.cluster_distances[dominant_id][c]
            target_cat = self.cluster_categories.get(c, 'fiction')

            # Controlled exploration score:
            # Close clusters = more familiar (lower novelty)
            # Far clusters = more novel (higher novelty)
            max_dist = self.cluster_distances.max()
            novelty = dist / max_dist if max_dist > 0 else 0.5

            # We want the "sweet spot" — not too familiar, not too alien
            # Optimal exploration score peaks at ~0.4-0.7 novelty
            exploration_score = 1.0 - abs(novelty - 0.55) * 2
            exploration_score = max(0.1, min(1.0, exploration_score))

            # Bonus for unvisited clusters
            if c not in visited_clusters:
                exploration_score *= 1.2
                exploration_score = min(1.0, exploration_score)

            # Get pathway description
            key1 = (dominant_cat, target_cat)
            key2 = (target_cat, dominant_cat)
            pathway = EXPANSION_PATHWAYS.get(
                key1,
                EXPANSION_PATHWAYS.get(
                    key2,
                    f'Expand from {dominant_cat.title()} to {target_cat.title()}'
                )
            )

            # Sample books from this cluster
            mask = self.cluster_labels == c
            sample_books = self.books_df[mask]['title'].tolist()[:4]

            candidates.append({
                'area': self.cluster_names[c],
                'cluster_id': c,
                'distance_score': float(dist),
                'exploration_score': float(exploration_score),
                'pathway_description': pathway,
                'sample_books': sample_books
            })

        # Sort by exploration score (highest first = best expansion targets)
        candidates.sort(key=lambda x: x['exploration_score'], reverse=True)
        return candidates[:3]

    def generate_reading_journey(self, profile=None, steps=3):
        """
        Generate a structured multi-step reading journey that bridges the
        user's current interests to a predicted expansion area.

        Args:
            profile: User profile dict. Computed if not provided.
            steps: Number of books in the journey (3-5)

        Returns:
            dict containing:
                - title: str (journey name)
                - from_area: str (starting interest)
                - to_area: str (target expansion)
                - pathway: str (description of intellectual bridge)
                - steps: list of dicts, each with book info + step rationale
                - overall_novelty: float (0-1)
        """
        if profile is None:
            profile = self.analyze_user_profile()

        expansions = self.predict_curiosity_expansion(profile)

        if not expansions:
            return self._default_journey()

        # Pick the best expansion target
        target = expansions[0]
        target_id = target['cluster_id']

        if profile.get('is_new_user', True):
            return self._new_user_journey(target)

        dominant_id = profile['dominant_cluster_id']

        # Build journey: start from dominant → bridge → target
        journey_books = []

        # Step 1: A book from the user's comfort zone (familiar anchor)
        dominant_mask = self.cluster_labels == dominant_id
        dominant_books = self.books_df[dominant_mask]
        interacted = set(self._get_user_interacted_books())

        # Prefer a book they haven't seen yet from their comfort zone
        unseen_dominant = dominant_books[~dominant_books['title'].isin(interacted)]
        if len(unseen_dominant) > 0:
            anchor = unseen_dominant.iloc[0]
        elif len(dominant_books) > 0:
            anchor = dominant_books.iloc[0]
        else:
            anchor = self.books_df.iloc[0]

        journey_books.append({
            'step': 1,
            'title': anchor['title'],
            'authors': anchor['authors'],
            'categories': anchor['categories'],
            'description': str(anchor['description'])[:200],
            'rationale': f"Starting in your comfort zone — {profile['dominant_interest']}",
            'novelty_level': 'Familiar',
            'novelty_color': '#22c55e'
        })

        # Step 2: Bridge book(s) — semantically between dominant and target
        # Find the book whose embedding is closest to the midpoint between centroids
        midpoint = (self.centroids[dominant_id] + self.centroids[target_id]) / 2.0
        midpoint = midpoint.reshape(1, -1).astype('float32')

        # Search the full index for nearest to midpoint
        distances, indices = self.recommender.index.search(midpoint, 10)
        bridge_found = False
        for idx in indices[0]:
            book = self.books_df.iloc[idx]
            if book['title'] not in [jb['title'] for jb in journey_books]:
                journey_books.append({
                    'step': 2,
                    'title': book['title'],
                    'authors': book['authors'],
                    'categories': book['categories'],
                    'description': str(book['description'])[:200],
                    'rationale': f"A bridge book — connecting familiar themes to new territory",
                    'novelty_level': 'Moderate',
                    'novelty_color': '#f59e0b'
                })
                bridge_found = True
                break

        if not bridge_found and len(self.books_df) > 1:
            bridge = self.books_df.iloc[1]
            journey_books.append({
                'step': 2,
                'title': bridge['title'],
                'authors': bridge['authors'],
                'categories': bridge['categories'],
                'description': str(bridge['description'])[:200],
                'rationale': 'A bridge book connecting different themes',
                'novelty_level': 'Moderate',
                'novelty_color': '#f59e0b'
            })

        # Step 3+: Books from the target expansion area
        target_mask = self.cluster_labels == target_id
        target_books = self.books_df[target_mask]
        target_books_unseen = target_books[~target_books['title'].isin(
            [jb['title'] for jb in journey_books]
        )]

        remaining_steps = steps - len(journey_books)
        for i, (_, book) in enumerate(target_books_unseen.iterrows()):
            if i >= remaining_steps:
                break
            journey_books.append({
                'step': len(journey_books) + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': str(book['description'])[:200],
                'rationale': f"Exploring new territory — {target['area']}",
                'novelty_level': 'High' if i > 0 else 'Moderate-High',
                'novelty_color': '#ef4444' if i > 0 else '#f97316'
            })

        # If we didn't get enough steps, fill from general pool
        while len(journey_books) < steps:
            for _, book in self.books_df.iterrows():
                if book['title'] not in [jb['title'] for jb in journey_books]:
                    journey_books.append({
                        'step': len(journey_books) + 1,
                        'title': book['title'],
                        'authors': book['authors'],
                        'categories': book['categories'],
                        'description': str(book['description'])[:200],
                        'rationale': 'Broadening your intellectual horizons',
                        'novelty_level': 'Moderate',
                        'novelty_color': '#f59e0b'
                    })
                    break
            else:
                break

        return {
            'title': f"{profile['dominant_interest']} → {target['area']}",
            'from_area': profile['dominant_interest'],
            'to_area': target['area'],
            'pathway': target['pathway_description'],
            'steps': journey_books,
            'overall_novelty': target['exploration_score']
        }

    def _default_journey(self):
        """Generate a default journey for edge cases"""
        books = self.books_df.head(3)
        steps = []
        for i, (_, book) in enumerate(books.iterrows()):
            steps.append({
                'step': i + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': str(book['description'])[:200],
                'rationale': 'A great starting point for your reading journey',
                'novelty_level': 'Moderate',
                'novelty_color': '#f59e0b'
            })
        return {
            'title': 'Start Your Journey',
            'from_area': '🆕 New Explorer',
            'to_area': self.cluster_names.get(0, '📚 General'),
            'pathway': 'Begin exploring the world of books!',
            'steps': steps,
            'overall_novelty': 0.5
        }

    def _new_user_journey(self, target):
        """Generate a journey for new users"""
        mask = self.cluster_labels == target['cluster_id']
        cluster_books = self.books_df[mask]
        steps = []
        for i, (_, book) in enumerate(cluster_books.head(3).iterrows()):
            novelty = ['Familiar', 'Moderate', 'High'][min(i, 2)]
            color = ['#22c55e', '#f59e0b', '#ef4444'][min(i, 2)]
            steps.append({
                'step': i + 1,
                'title': book['title'],
                'authors': book['authors'],
                'categories': book['categories'],
                'description': str(book['description'])[:200],
                'rationale': f"Discover {target['area']}",
                'novelty_level': novelty,
                'novelty_color': color
            })
        return {
            'title': f"Discover {target['area']}",
            'from_area': '🆕 New Explorer',
            'to_area': target['area'],
            'pathway': 'Start your intellectual journey here!',
            'steps': steps,
            'overall_novelty': 0.5
        }

    def compute_curiosity_impact_score(self, profile=None):
        """
        Compute the Curiosity Impact Score — three metrics that measure
        the user's intellectual exploration.

        Returns:
            dict with:
                - exploration_level: int (0-100) — how far beyond comfort zone
                - intellectual_diversity: int (0-100) — how many distinct areas
                - growth_index: int (0-100) — overall growth indicator
        """
        if profile is None:
            profile = self.analyze_user_profile()

        if profile.get('is_new_user', True):
            return {
                'exploration_level': 0,
                'intellectual_diversity': 0,
                'growth_index': 0
            }

        # Exploration level: based on exploration breadth
        exploration_level = int(profile['exploration_breadth'] * 100)

        # Intellectual diversity: based on number of unique clusters touched
        dist = profile['cluster_distribution']
        n_clusters_touched = len(dist)
        # Diversity is higher when distribution is more even (entropy-based)
        if n_clusters_touched > 0:
            counts = list(dist.values())
            total = sum(counts)
            probs = [c / total for c in counts]
            import math
            entropy = -sum(p * math.log2(p) for p in probs if p > 0)
            max_entropy = math.log2(self.n_clusters) if self.n_clusters > 1 else 1
            intellectual_diversity = int((entropy / max_entropy) * 100)
        else:
            intellectual_diversity = 0

        # Growth index: weighted combination
        books_factor = min(profile['total_books_explored'] / 20, 1.0)  # caps at 20 books
        growth_index = int(
            (exploration_level * 0.4 +
             intellectual_diversity * 0.3 +
             books_factor * 100 * 0.3)
        )

        return {
            'exploration_level': min(100, exploration_level),
            'intellectual_diversity': min(100, intellectual_diversity),
            'growth_index': min(100, growth_index)
        }
