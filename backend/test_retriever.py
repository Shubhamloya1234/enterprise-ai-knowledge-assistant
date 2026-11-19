
from app.rag.retriever import retrieve_documents

queries = [
    "How many days of annual leave do employees receive?",
    "How many days per week can employees work remotely?",
    "How often must employees complete security training?",
]

for query in queries:
    print("\n" + "=" * 70)
    print("QUERY:", query)

    results = retrieve_documents(query, top_k=3)

    if not results:
        print("No documents retrieved.")
        continue

    for i, document in enumerate(results, start=1):
        print(f"\nResult {i}")
        print("Content:", document["content"])
        print("Source:", document["source"])
        print("Distance:", document["distance"])
