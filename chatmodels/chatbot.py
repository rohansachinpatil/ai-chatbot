from model_loader import get_mistral_model
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage

model = get_mistral_model()

messages = [
    SystemMessage(content="You are a helpful assistant.")

]

print("\n-----------------------Welcome to Simple ChatBot-----------------------")

while True:
    prompt = input("You : ")
    messages.append(HumanMessage(content=prompt))
    if prompt == "0":
        print("Bye...")
        break
    # Invoke the model
    response = model.invoke(messages)
    messages.append(AIMessage(content=response.content))
    # Print the result
    print(f"Bot: {response.content}")