from rag import ask

question = input("Pose une question sur tes cours déjà indexés : ")
result = ask(question)

print("\n--- Réponse ---")
print(result["answer"])

print("\n--- Sources ---")
for s in result["sources"]:
    print(f"- {s['filename']} ({s['unit_type']} {s['unit_number']})")