import requests

# Configuration
LM_STUDIO_URL = ""
MODEL_NAME = "qwen/qwen3-14b"

def get_prompt():
    """Get prompt from user input or a file."""
    choice = input("\nWould you like to:\n"
                   "1) Type in your own prompt\n"
                   "2) Load a prompt from a file\n"
                   "3) Exit\n"
                   "Enter your choice (1/2/3): ").strip()

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
        print("Exiting...")
        exit()
    else:
        print("Invalid choice. Please select 1, 2, or 3.")
        return get_prompt()

def send_to_llm(prompt):
    """Send the prompt to the LLM API and print the result."""
    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/v1/chat/completions",  # ✅ Correct endpoint for LM Studio
            json={
                "model": MODEL_NAME,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=120
        )

        response.raise_for_status()

        result = response.json()
        if "choices" in result and isinstance(result["choices"], list):
            for choice in result["choices"]:
                print(f"{choice.get('message', {}).get('content', '')}")
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

