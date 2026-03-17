import requests
import argparse
from datetime import datetime

# Configuration
LM_STUDIO_URL = ""
MODEL_NAME=""

def get_prompt(file_handle):
    """Get prompt from user input or a file/URL."""
    choice = input("\nWould you like to:\n"
                   "1) Type in your own prompt\n"
                   "2) Load a prompt from a file\n"
                   "3) Ask a question about a file\n"  # Existing option
                   "4) Ask a question about a URL\n"   # New option
                   "5) Exit\n"
                   "Enter your choice (1/2/3/4/5): ").strip()

    if choice == '1':
        print(f"[LOG] Prompt received: {choice}", file=file_handle, flush=True)
        return input("Enter your prompt: ")
    elif choice == '2':
        filename = input("Enter the full path to your text file: ")
        try:
            with open(filename, 'r') as f:
                content = f.read()
                print(f"\nLoaded {len(content)} characters from '{filename}'")
                print(f"[LOG] Prompt received: {content}", file=file_handle, flush=True)
                return content
        except FileNotFoundError:
            print(f"Error: File not found at '{filename}'")
            return get_prompt(file_handle)  # Re-ask for prompt or file
        except Exception as e:
            print(f"Error reading file: {e}")
            return get_prompt(file_handle)
    elif choice == '3':
        question = input("Enter your question about the file: ")
        filename = input("Enter the full path to your text file: ")
        try:
            with open(filename, 'r') as f:
                content = f.read()
                print(f"\nLoaded {len(content)} characters from '{filename}'")
                # Combine the user's question and the file content into a prompt
                combined_prompt = f"What is the answer to the following question: '{question}' based on this text? {content}"
                print(f"[LOG] Prompt received: {combined_prompt}", file=file_handle, flush=True)
                return combined_prompt
        except FileNotFoundError:
            print(f"Error: File not found at '{filename}'")
            return get_prompt(file_handle)
        except Exception as e:
            print(f"Error reading file: {e}")
            return get_prompt(file_handle)
    elif choice == '4':
        # Option 4: Read from URL instead of a file (similar structure to Option 3)
        question = input("Enter your question about the URL content: ")
        url_input = input("Enter the full URL (e.g., https://example.com): ")
        try:
            # Fetch content from the URL
            response = requests.get(url_input, timeout=30)
            response.raise_for_status() # Check for HTTP errors
            
            content = response.text
            print(f"\nLoaded {len(content)} characters from URL: '{url_input}'")
            
            # Combine the user's question and the fetched text into a prompt
            combined_prompt = f"What is the answer to the following question: '{question}' based on this text? {content}"
            print(f"[LOG] Prompt received: {combined_prompt}", file=file_handle, flush=True)
            return combined_prompt
        except requests.exceptions.RequestException as e:
            print(f"Error fetching URL: {e}")
            return get_prompt(file_handle)
        except Exception as e:
            print(f"Error reading URL content: {e}")
            return get_prompt(file_handle)
    elif choice == '5':
        print("Exiting...")
        exit()
    else:
        print("Invalid choice. Please select 1, 2, 3, 4, or 5.")
        return get_prompt(file_handle)

def send_to_llm(prompt, model_name, file_handle):
    """Send the prompt to the LLM API and print the result."""
    try:
        response = requests.post(
            f"{LM_STUDIO_URL}/api/v1/chat",
            json={
                "model": model_name,
                "input": prompt,
                "stream": False
            },
            headers={"Content-Type": "application/json"},
            timeout=300
        )
        response.raise_for_status()
        result = response.json()

        # Handle LM Studio's output format
        if "output" in result:
            for item in result["output"]:
                if "content" in item and item["content"]:
                    print(item["content"])
                    print(item["content"], file=file_handle, flush=True)
        # Check for the correct structure from LM Studio
        elif "output" in result and isinstance(result["output"], list):
            for item in result["output"]:
                if item.get("type") == "message":
                    print(f"{item.get('content', '')}")
                    print(f"{item.get('content', '')}", file=file_handle, flush=True)
        else:
            print("Unexpected response format from LLM.")

    except requests.exceptions.RequestException as e:
        print(f"API error: {e}")


def main():
    """Main loop of the application."""
    
    # --- NEW SECTION: Argument Parsing ---
    parser = argparse.ArgumentParser(description="LLM Chat Script")
    parser.add_argument('--model_name', type=str, help='Name of the model to use')
    args = parser.parse_args()
    
    # Check if --model_name was provided in the command line
    if args.model_name:
        MODEL_NAME = args.model_name  # Use CLI argument
        print(f"Using model from command line: {MODEL_NAME}")
    else:
        # Only ask for input if no model was specified on the command line
        MODEL_NAME = input("Enter your preferred Model Name (e.g., qwen/qwen3.5-9b): ").strip()
    
    # --- END NEW SECTION ---
    # --- MODIFIED LOGGING SETUP ---
    session_start_time = datetime.now()
    timestamp_str = session_start_time.strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"agent{timestamp_str}.log"
    
    # 1. Open the file in append mode ('a')
    # Note: 'a' creates the file if it doesn't exist, but does NOT overwrite existing content.
    # If you want to start fresh for every run session, use 'w'. 
    log_file = open(log_filename, 'a', encoding='utf-8') 

    try:
        while True:
            # 2. Pass the file handle as an argument to get_prompt
            prompt = get_prompt(file_handle=log_file) 

            if not prompt:
                continue
            
            # 3. Pass the file handle as an argument to send_to_llm
            send_to_llm(prompt, MODEL_NAME, file_handle=log_file)

    except Exception as e:
        print(f"An error occurred in the loop: {e}")
    finally:
        # 4. Close the file handle to prevent resource leaks
        log_file.close() 


if __name__ == "__main__":
    main()

