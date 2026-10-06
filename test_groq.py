from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0
)

print("Calling Groq...")

response = llm.invoke(
    "Tell me in one sentence what robotics is."
)

print("\nRESULT:\n")
print(response.content)