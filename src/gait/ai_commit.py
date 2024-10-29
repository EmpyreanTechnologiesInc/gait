import os
from openai import OpenAI
from dotenv import load_dotenv
import subprocess

def get_git_diff():
    """Get the staged changes diff"""
    try:
        result = subprocess.run(
            ["git", "diff", "--staged"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error getting git diff: {e}")
        return None

def handle_ai_commit():
    diff_text = get_git_diff()
    if not diff_text:
        print("No staged changes found.")
        return 1
    
    commit_message = generate_commit_message(diff_text)
    if not commit_message:
        return 1
    
    # Show the commit message and ask for confirmation
    print("\n--- Proposed commit message ---")
    print(f"└─→ {commit_message}")  # Bold green arrow and message
    while True:
        response = input("\n\033[0;36mDo you want to proceed with this commit message? (y[es]/n[o]/e[dit]): \033[0m").lower().strip()
        if response in ['y', 'yes']:  # Empty response defaults to yes
            break
        elif response in ['n', 'no']:
            print("\033[0;31mCommit cancelled.\033[0m")  # Bold red for cancellation
            return 1
        elif response in ['e', 'edit']:
            new_message = input("New commit message: ").strip()
            if new_message:
                commit_message = new_message
                break
            print("Invalid message. Please try again.")
        else:
            print("Please answer 'y' (yes), 'n' (no), or 'e' (edit)")
    
    try:
        subprocess.run(["git", "commit", "-m", commit_message], check=True)
        return 0
    except subprocess.CalledProcessError as e:
        print(f"Error creating commit: {e}")
        return e.returncode

def generate_commit_message(diff_text):
    """Generate commit message using OpenAI API"""
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
        return None
    
    client = OpenAI(api_key=api_key)
    
    user_prompt = f"""The following Git diff input is in Unified Diff format, 
    which displays changes made to files in a version control system. 
    Analyze the changes and generate a clear, concise commit message that summarizes the main modifications. 
    Focus on describing the purpose or function of the changes. 
    Generate a concise commit message following conventional commits format.
    Requirements:
    - Single line
    - Max 50 characters
    
    Git diff:
    {diff_text}
    """
    
    system_prompt = """You are a highly knowledgeable assistant specialized 
    in software development and version control systems.""" 
    
    try:
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),  # Default to gpt-4o-mini if not specified
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )

        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating commit message: {e}")
        return None