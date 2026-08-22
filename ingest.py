import os
import re
import yaml
import chromadb

# Notice we removed the Google GenAI imports and API key setup!

KB_FOLDER = "knowledge-base"
DB_DIR = "chroma_db"

def main():
    # 1. Setup ChromaDB with Local AI
    print("Setting up ChromaDB...")
    chroma_client = chromadb.PersistentClient(path=DB_DIR)
    
    # Delete the old table if it exists so we start fresh
    try:
        chroma_client.delete_collection(name="aster_row_policies")
    except Exception:
        pass
        
    # When we create a collection this way, ChromaDB automatically uses 
    # its default local AI model (all-MiniLM-L6-v2) to create embeddings.
    collection = chroma_client.create_collection(name="aster_row_policies")

    # 2. Read and Chunk the Markdown Files
    if not os.path.exists(KB_FOLDER):
        print(f"Error: Folder '{KB_FOLDER}' not found.")
        return

    md_files = [f for f in os.listdir(KB_FOLDER) if f.endswith('.md')]
    print(f"Found {len(md_files)} markdown files.")
    
    all_chunks = []
    
    for filename in md_files:
        file_path = os.path.join(KB_FOLDER, filename)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        frontmatter_match = re.match(r"^---\n(.*?)\n---\n", content, re.DOTALL)
        metadata = {}
        main_text = content
        
        if frontmatter_match:
            yaml_content = frontmatter_match.group(1)
            metadata = yaml.safe_load(yaml_content) or {}
            main_text = content[frontmatter_match.end():]
            
        sections = re.split(r'\n(?=## )', main_text)
        
        for section in sections:
            section = section.strip()
            if not section:
                continue
                
            all_chunks.append({
                "source_file": filename,
                "title": metadata.get("title", "Unknown"),
                "text": section
            })

    print(f"Created {len(all_chunks)} chunks. Saving to local database...")
    
    # 3. Batch Process and Save
    # Because we are using local CPU and have no API rate limits, 
    # we don't need a loop with time.sleep(). We can add everything at once!
    
    documents = []
    metadatas = []
    ids = []

    for i, chunk in enumerate(all_chunks):
        if not chunk["text"].strip():
            continue
            
        documents.append(chunk["text"])
        metadatas.append({"source": chunk["source_file"], "title": chunk["title"]})
        ids.append(f"chunk_{i}")

    if documents:
        # Save everything to the database in one single, fast command
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
    print("\nSuccess! Ingestion complete. Vector database is ready.")

if __name__ == "__main__":
    main()