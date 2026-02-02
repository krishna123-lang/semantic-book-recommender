"""
Data Preprocessing Module for Semantic Book Recommender
Cleans and prepares the books dataset for embedding generation
"""

import pandas as pd
import os
import sys
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def preprocess_books(input_path='data/books.csv', output_path='data/books_cleaned.csv'):
    """
    Clean and preprocess the books dataset
    
    Args:
        input_path: Path to raw books CSV file
        output_path: Path to save cleaned CSV file
    
    Returns:
        DataFrame: Cleaned books data
    """
    print("=" * 60)
    print("STARTING DATA PREPROCESSING")
    print("=" * 60)
    
    # Load the dataset
    print(f"\n[1/5] Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"   ✓ Loaded {len(df)} books")
    
    # Check initial data
    print(f"\n[2/5] Initial data shape: {df.shape}")
    print(f"   Columns: {list(df.columns)}")
    
    # Remove rows with missing descriptions (critical for embeddings)
    print(f"\n[3/5] Removing rows with missing descriptions...")
    initial_count = len(df)
    df = df.dropna(subset=['description'])
    df = df[df['description'].str.strip() != '']
    removed = initial_count - len(df)
    print(f"   ✓ Removed {removed} rows with missing descriptions")
    print(f"   ✓ Remaining: {len(df)} books")
    
    # Normalize text data
    print(f"\n[4/5] Normalizing text data...")
    # Lowercase descriptions for consistency
    df['description'] = df['description'].str.strip()
    # Fill missing authors and categories with 'Unknown'
    df['authors'] = df['authors'].fillna('Unknown')
    df['categories'] = df['categories'].fillna('Unknown')
    print(f"   ✓ Text normalization complete")
    
    # Remove duplicate books (based on title)
    print(f"\n[5/5] Removing duplicate books...")
    initial_count = len(df)
    df = df.drop_duplicates(subset=['title'], keep='first')
    removed = initial_count - len(df)
    print(f"   ✓ Removed {removed} duplicate books")
    print(f"   ✓ Final dataset: {len(df)} unique books")
    
    # Save cleaned dataset
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    df.to_csv(output_path, index=False)
    print(f"\n✓ Cleaned dataset saved to: {output_path}")
    
    # Display summary statistics
    print("\n" + "=" * 60)
    print("PREPROCESSING SUMMARY")
    print("=" * 60)
    print(f"Total books: {len(df)}")
    print(f"Unique categories: {df['categories'].nunique()}")
    print(f"Average description length: {df['description'].str.len().mean():.0f} characters")
    print("\nTop 5 categories:")
    print(df['categories'].value_counts().head())
    print("=" * 60)
    
    return df

if __name__ == "__main__":
    # Run preprocessing
    cleaned_df = preprocess_books()
    print("\n✓ Preprocessing complete! Ready for embedding generation.")
