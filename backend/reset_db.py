from vectorstore import get_client, COLLECTION_NAME

client = get_client()
client.delete_collection(COLLECTION_NAME)
print("Base vidée. Elle sera recréée automatiquement au prochain ajout.")