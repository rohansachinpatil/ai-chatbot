from dotenv import load_dotenv
load_dotenv()


from langchain_mistralai import ChatMistralAI

model = ChatMistralAI(model_name="mistral-small-latest", temperature=0.5, max_tokens=50)

# Invoke the model
response = model.invoke("what is machine learning")

# Print the result
print(f"Response: {response.content}")

# Print token usage details
usage = response.response_metadata.get("token_usage", {})
print("\n--- Token Usage ---")
print(f"Input Tokens:  {usage.get('prompt_tokens')}")
print(f"Output Tokens: {usage.get('completion_tokens')}")
print(f"Total Tokens:  {usage.get('total_tokens')}")
