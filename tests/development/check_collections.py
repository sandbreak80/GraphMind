#!/usr/bin/env python3
"""Check ChromaDB collections"""

import chromadb

def check_collections():
    print("🔍 Checking ChromaDB collections...")
    
    try:
        client = chromadb.HttpClient(host="localhost", port=8003)
        collections = client.list_collections()
        
        print(f"📚 Found {len(collections)} collections:")
        for collection in collections:
            print(f"   - {collection.name} (id: {collection.id})")
            
            # Get some stats about each collection
            try:
                count = collection.count()
                print(f"     Documents: {count}")
            except Exception as e:
                print(f"     Error getting count: {e}")
        
    except Exception as e:
        print(f"❌ Error connecting to ChromaDB: {e}")

if __name__ == "__main__":
    check_collections()