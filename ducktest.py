from langchain_community.tools import DuckDuckGoSearchRun

search = DuckDuckGoSearchRun()

print("Starting search...")

result = search.run("robotics companies in India")

print("\nSEARCH RESULT:\n")
print(result)