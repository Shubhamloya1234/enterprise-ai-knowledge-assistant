from app.rag.rag_pipeline import ask_question


question = "How many days of annual leave do employees receive?"

result = ask_question(question)

print("\nQUESTION:")
print(result["question"])

print("\nANSWER:")
print(result["answer"])

print("\nSOURCES:")

for source in result["sources"]:
    print("-", source)