from langchain_huggingface import HuggingFaceEmbeddings
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"},
    encode_kwargs={"normalize_embeddings": False}
)
tests = [
    "my name is deepak",
    "i am a student",
    "i love machine learning"
]

vector = embeddings.embed_documents(tests)
print(vector)