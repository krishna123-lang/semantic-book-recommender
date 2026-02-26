"""
Embedding Generation Module for Semantic Book Recommender
Converts book descriptions to vector embeddings and builds FAISS index
"""

import pandas as pd
import numpy as np
import faiss
import os
import sys
from pathlib import Path
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def generate_embeddings(input_path='data/books_cleaned.csv', 
                       index_path='embeddings/faiss.index',
                       metadata_path='embeddings/books_metadata.csv',
                       model_name='sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'):
    """
    Generate embeddings for book descriptions and create FAISS index
    
    Args:
        input_path: Path to cleaned books CSV
        index_path: Path to save FAISS index
        metadata_path: Path to save book metadata
        model_name: Sentence transformer model to use
    
    Returns:
        tuple: (faiss_index, dataframe)
    """
    print("=" * 60)
    print("STARTING EMBEDDING GENERATION")
    print("=" * 60)
    
    # Load cleaned dataset
    print(f"\n[1/5] Loading cleaned dataset from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   ✓ Loaded {len(df)} books")
    
    # Load the sentence transformer model
    print(f"\n[2/5] Loading embedding model: {model_name}")
    print("   (This may take a moment on first run...)")
    model = SentenceTransformer(model_name)
    print(f"   ✓ Model loaded successfully")
    print(f"   ✓ Embedding dimension: {model.get_sentence_embedding_dimension()}")
    
    # Generate embeddings for all book descriptions
    print(f"\n[3/5] Generating embeddings for {len(df)} books...")
    descriptions = df['description'].tolist()
    
    # Use tqdm for progress bar
    embeddings = []
    batch_size = 32
    for i in tqdm(range(0, len(descriptions), batch_size), desc="   Processing batches"):
        batch = descriptions[i:i+batch_size]
        batch_embeddings = model.encode(batch, show_progress_bar=False)
        embeddings.extend(batch_embeddings)
    
    embeddings = np.array(embeddings).astype('float32')
    print(f"   ✓ Generated embeddings with shape: {embeddings.shape}")
    
    # Create FAISS index
    print(f"\n[4/5] Building FAISS index...")
    dimension = embeddings.shape[1]
    
    # Use IndexFlatL2 for exact L2 distance search
    # This is simple and works well for datasets of this size
    index = faiss.IndexFlatL2(dimension)
    
    # Add embeddings to the index
    index.add(embeddings)
    print(f"   ✓ FAISS index created")
    print(f"   ✓ Index contains {index.ntotal} vectors")
    
    # Save FAISS index and metadata
    print(f"\n[5/5] Saving index and metadata...")
    
    # Create embeddings directory if it doesn't exist
    index_dir = os.path.dirname(index_path)
    if index_dir:
        Path(index_dir).mkdir(parents=True, exist_ok=True)
    
    # Save FAISS index
    faiss.write_index(index, index_path)
    print(f"   ✓ FAISS index saved to: {index_path}")
    
    # Save metadata (book information for retrieval)
    df.to_csv(metadata_path, index=False)
    print(f"   ✓ Metadata saved to: {metadata_path}")
    
    # Display summary
    print("\n" + "=" * 60)
    print("EMBEDDING GENERATION SUMMARY")
    print("=" * 60)
    print(f"Total books indexed: {index.ntotal}")
    print(f"Embedding dimension: {dimension}")
    print(f"Index type: L2 (Euclidean distance)")
    print(f"Model used: {model_name}")
    print("=" * 60)
    
    return index, df

if __name__ == "__main__":
    # Generate embeddings and build index
    index, df = generate_embeddings()
    print("\n✓ Embedding generation complete! Ready for recommendations.")
