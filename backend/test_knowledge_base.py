from app.rag.knowledge_base import ingest_folder


results = ingest_folder("uploads")

print("\nKnowledge base ingestion completed.")

for result in results:
    print(result)