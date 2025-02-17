import ollama

response = ollama.chat(model='mistral', messages=[{"role": "user", "content": "Write a haiku about AI"}])

print(response["message"]["content"])
