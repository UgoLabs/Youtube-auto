import ollama
import pyttsx3
import subprocess

# Initialize TTS engine
engine = pyttsx3.init()

def configure_voice(engine):
    """Configure voice settings"""
    voices = engine.getProperty('voices')
    # Voice selection logic here
    engine.setProperty('rate', 150)

def check_requirements():
    """Verify Ollama is installed and running"""
    try:
        subprocess.run(["ollama", "--version"], check=True, capture_output=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: Install Ollama first from https://ollama.ai/")
        exit(1)

def main():
    check_requirements()
    configure_voice(engine)
    
    CONVERSATION_HISTORY = []
    MAX_HISTORY = 3

    print("Chat with Mistral (type 'exit' to quit)")
    while True:
        try:
            user_input = input("\nYou: ").strip()
            if user_input.lower() == "exit":
                print("Goodbye!")
                break

            # Generate response
            response = ollama.chat(
                model='mistral',
                messages=[
                    *CONVERSATION_HISTORY[-MAX_HISTORY:],
                    {"role": "user", "content": user_input}
                ]
            )

            # Store conversation
            CONVERSATION_HISTORY.extend([
                {"role": "user", "content": user_input},
                {"role": "assistant", "content": response["message"]["content"]}
            ])

            # Speak response
            engine.say(response["message"]["content"])
            engine.runAndWait()

        except KeyboardInterrupt:
            print("\nInterrupted by user")
            break
        except Exception as e:
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
