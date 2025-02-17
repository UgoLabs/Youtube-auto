import subprocess

def generate_script(topic: str) -> str:
    prompt = (
        f"Write an engaging, well-structured script (around 200 words) for a faceless video about '{topic}'. "
        "The script should begin with a compelling hook, include 3-4 interesting facts, be conversational in tone, "
        "and end with a clear conclusion that encourages viewers to learn more."
    )
    try:
        result = subprocess.run(
            ["ollama", "run", "mistral", prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",  # Replace problematic characters
            check=True
        )
        output = result.stdout.strip()
        return output
    except subprocess.CalledProcessError as e:
        print("Ollama error:", e)
        return f"This is a default script about {topic}. Please check Ollama configuration."

