from dotenv import load_dotenv
from langchain_mistralai import ChatMistralAI

# Load environment variables
load_dotenv()

def get_mistral_model():
    """Returns a consistently configured Mistral model."""
    return ChatMistralAI(
        model_name="mistral-small-latest", 
        temperature=0, 
        max_tokens=2048
    )
