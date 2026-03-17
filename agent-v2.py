import requests

# Configuration
LM_STUDIO_URL = ""
MODEL_NAME = "qwen/qwen3.5-9b"

def get_prompt():
    """Get prompt from user input or a file."""
    choice = input("\nWould you like to:\n"
                   "1) Type in your own prompt\n"
                   "2) Load a prompt from a file\n"
                   "3) Ask a question about a file\n"  # New option
                   "4) Exit\n"
                   "Enter your choice (1/2/3/4): ").strip()

    if choice == '1':
        return input("Enter your prompt: ")
    elif choice == '2':
        filename = input("Enter the full path to your text file: ")
        try:
            with open(filename, 'r') as f:
                content = f.read()
                print(f"\nLoaded {len(content)} characters from '{filename}'")
                return content
        except FileNotFoundError:
            print(f"Error: File not found at '{filename}'")
            return get_prompt()  # Re-ask for prompt or file
        except Exception as e:
            print(f"Error reading file: {e}")
            return get_prompt()
    elif choice == '3':
        question = input("Enter your question about the file: ")
        filename = input("Enter the full path to your text file: ")
        try:
            with open(filename, 'r') as f:
                content = f.read()
                print(f"\nLoaded {len(content)} characters from '{filename}'")
                # Combine the user's question and the file content into a prompt
                combined_prompt = f"What is the answer to the following question: '{question}' based on this text? {content}"
                return combined_prompt
        except FileNotFoundError:
            print(f"Error: File not found at '{filename}'")
            return get_prompt()
        except Exception as e:
            print(f"Error reading file: {e}")
            return get_prompt()
    elif choice == '4':
        print("Exiting...")
        exit()
    else:
        print("Invalid choice. Please select 1, 2, 3, or 4.")
        return get_prompt()

def send_to_llm(prompt):
    """Send the prompt to the LLM API and print the result."""
    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/api/v1/chat",
            json={
                "model": MODEL_NAME,
                "input": prompt,
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        response.raise_for_status()
        result = response.json()

        # Check for the correct structure from LM Studio
        if "output" in result and isinstance(result["output"], list):
            for item in result["output"]:
                if item.get("type") == "message":
                    print(f"{item.get('content', '')}")
        else:
            print("Unexpected response format from LLM.")

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")


def main():
    """Main loop of the application."""
    while True:
        prompt = get_prompt()
        if not prompt:
            continue
        send_to_llm(prompt)

if __name__ == "__main__":
    main()

