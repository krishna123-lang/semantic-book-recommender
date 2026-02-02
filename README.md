# 📚 Semantic Book Recommendation System

An intelligent content-based book recommender that uses **semantic embeddings** and **vector similarity search** to find books matching your interests. Built with Python, Sentence Transformers, FAISS, and Gradio.

## 🎯 Project Overview

This system converts book descriptions into high-dimensional vector embeddings that capture semantic meaning. When you describe what you're looking for, the system finds books with similar semantic content—even if they don't share exact keywords!

### Key Features

- ✨ **Semantic Search**: Understands meaning, not just keywords
- 🚀 **Fast Vector Search**: FAISS enables efficient similarity search
- 🎨 **Beautiful Web UI**: Interactive Gradio interface
- 📊 **150+ Books**: Diverse dataset across multiple genres
- 🔢 **Similarity Scoring**: See how well each book matches your query

## 🧠 How It Works

### 1. Semantic Embeddings

**What are embeddings?**
Embeddings are dense vector representations of text that capture semantic meaning. Similar concepts are positioned close together in vector space.

```
"mystery detective crime" → [0.23, -0.45, 0.67, ...]
"thriller investigation"  → [0.21, -0.43, 0.69, ...]  (similar!)
"romantic comedy"         → [-0.67, 0.89, -0.12, ...] (different!)
```

**Our Model**: We use `sentence-transformers/all-MiniLM-L6-v2`, which:
- Converts text to 384-dimensional vectors
- Trained on 1B+ sentence pairs
- Captures semantic relationships effectively
- Fast and lightweight (80MB)

### 2. Vector Similarity Search

**What is FAISS?**
FAISS (Facebook AI Similarity Search) is a library for efficient similarity search in high-dimensional spaces.

**How it works:**
1. All book descriptions are converted to embeddings
2. Embeddings are indexed in FAISS
3. User query is converted to an embedding
4. FAISS finds the k-nearest neighbors using L2 distance
5. Results are ranked by similarity

**Distance Metric**: We use L2 (Euclidean) distance:
```
distance = sqrt(sum((query_vector - book_vector)²))
```

Smaller distance = More similar books

### 3. Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     USER QUERY                              │
│          "mystery novel with detective"                     │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              SENTENCE TRANSFORMER                           │
│         (all-MiniLM-L6-v2 Model)                           │
│                                                             │
│  Text → [0.23, -0.45, 0.67, ..., 0.12]  (384 dims)        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                  FAISS INDEX                                │
│          (Vector Similarity Search)                         │
│                                                             │
│  Book 1: [0.21, -0.43, 0.69, ...]  ← distance: 0.15       │
│  Book 2: [0.19, -0.41, 0.71, ...]  ← distance: 0.18       │
│  Book 3: [-0.67, 0.89, -0.12, ...] ← distance: 2.45       │
│  ...                                                        │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│              TOP-K RECOMMENDATIONS                          │
│                                                             │
│  1. "The Girl with the Dragon Tattoo" (similarity: 0.89)   │
│  2. "Gone Girl" (similarity: 0.85)                         │
│  3. "The Da Vinci Code" (similarity: 0.82)                 │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
antigravity_semantic_book_recommender/
│
├── data/
│   ├── books.csv              # Original dataset (150+ books)
│   └── books_cleaned.csv      # Preprocessed dataset
│
├── embeddings/
│   ├── faiss.index           # FAISS vector index
│   └── books_metadata.csv    # Book metadata for retrieval
│
├── preprocess.py             # Data cleaning pipeline
├── embed.py                  # Embedding generation & FAISS indexing
├── recommender.py            # Recommendation engine
├── app.py                    # Gradio web interface
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Installation & Usage

### Prerequisites

- Python 3.10 or higher
- pip package manager

### Step 1: Install Dependencies

```bash
cd antigravity_semantic_book_recommender
pip install -r requirements.txt
```

This will install:
- `sentence-transformers` - For semantic embeddings
- `faiss-cpu` - For vector similarity search
- `gradio` - For web interface
- `pandas`, `numpy` - For data processing
- `torch`, `transformers` - ML framework
- `tqdm` - Progress bars

### Step 2: Run the Pipeline

**Option A: Run All Steps Automatically**

```bash
# 1. Preprocess data
python preprocess.py

# 2. Generate embeddings and build FAISS index
python embed.py

# 3. Launch Gradio web app
python app.py
```

**Option B: Quick Test**

If embeddings are already generated, just run:
```bash
python app.py
```

### Step 3: Use the Web Interface

1. The Gradio app will launch at `http://127.0.0.1:7860`
2. Enter a description of the book you want (e.g., "mystery with detective")
3. Choose number of recommendations (1-10)
4. Click "Find Books" or press Enter
5. View your personalized recommendations!

## 💡 Example Queries

Try these queries to see semantic search in action:

- **Genre-based**: "science fiction with space travel"
- **Theme-based**: "story about friendship and loyalty"
- **Mood-based**: "dark and mysterious thriller"
- **Plot-based**: "adventure with treasure hunting"
- **Setting-based**: "historical fiction in Victorian era"
- **Character-based**: "strong female protagonist"
- **Hybrid**: "dystopian future with rebellion and romance"

## 🔧 Technical Details

### Data Preprocessing (`preprocess.py`)

1. Removes books with missing descriptions
2. Normalizes text (strips whitespace)
3. Fills missing authors/categories with "Unknown"
4. Removes duplicate books by title
5. Saves cleaned dataset

### Embedding Generation (`embed.py`)

1. Loads cleaned book data
2. Initializes sentence transformer model
3. Converts descriptions to 384-dim vectors (batch processing)
4. Creates FAISS L2 index
5. Saves index and metadata

### Recommendation Engine (`recommender.py`)

1. Loads FAISS index and metadata
2. Converts user query to embedding
3. Performs k-nearest neighbor search
4. Calculates similarity scores
5. Returns ranked recommendations

### Web Interface (`app.py`)

- Built with Gradio for easy deployment
- HTML-formatted output with color-coded scores
- Real-time search with adjustable parameters
- Example queries for inspiration
- Responsive design

## 📊 Dataset

The `books.csv` dataset contains **150+ books** with:

- **Title**: Book name
- **Authors**: Author name(s)
- **Description**: Detailed plot summary (used for embeddings)
- **Categories**: Genre classification

**Genres included:**
- Fiction, Science Fiction, Fantasy
- Mystery, Thriller, Horror
- Romance, Historical Fiction
- Adventure, Children's Literature
- And more!

## 🎓 Learning Resources

### Understanding Embeddings

- [Sentence Transformers Documentation](https://www.sbert.net/)
- [What are Word Embeddings?](https://jalammar.github.io/illustrated-word2vec/)

### Understanding FAISS

- [FAISS GitHub](https://github.com/facebookresearch/faiss)
- [FAISS Tutorial](https://www.pinecone.io/learn/faiss-tutorial/)

### Vector Similarity Search

- [Introduction to Vector Search](https://www.pinecone.io/learn/vector-search/)

## 🔮 Future Enhancements

Potential improvements:

- [ ] **Genre Classification**: Zero-shot classification of book genres
- [ ] **Book Covers**: Fetch covers from OpenLibrary API
- [ ] **User Ratings**: Incorporate collaborative filtering
- [ ] **Advanced Filters**: Filter by category, author, publication year
- [ ] **Hybrid Search**: Combine semantic + keyword search
- [ ] **Larger Dataset**: Expand to thousands of books
- [ ] **Multi-language**: Support non-English books
- [ ] **Deployment**: Deploy to Hugging Face Spaces

## 🐛 Troubleshooting

### "No module named 'sentence_transformers'"
```bash
pip install sentence-transformers
```

### "FAISS index not found"
Make sure you've run:
```bash
python preprocess.py
python embed.py
```

### "Model download is slow"
First run downloads the model (~80MB). Subsequent runs use cached version.

### Port 7860 already in use
Edit `app.py` and change `server_port=7860` to another port.

## 📝 License

This project is for educational purposes. Book data is used for demonstration only.

## 🙏 Acknowledgments

- **Sentence Transformers**: For excellent embedding models
- **FAISS**: For efficient vector search
- **Gradio**: For easy-to-use web interfaces
- **Hugging Face**: For model hosting

## 👨‍💻 Author

Built with ❤️ by **Antigravity AI**

---

**Happy Reading! 📖✨**
