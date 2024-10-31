import subprocess
from typing import Tuple
from openai import OpenAI
from dotenv import load_dotenv
from .github_wrapper import create_pull_request, check_gh_auth
import os

"""
AI-powered Pull Request creation module.
Handles generating and submitting pull requests using OpenAI for content generation.
"""

def get_branch_changes() -> Tuple[str, str]:
    """
    Get the diff and commit messages between current branch and default branch.
    
    Returns:
        Tuple[str, str]: (diff content, commit messages)
    """
    try:
        print("Getting branch changes...")
        
        # Get current branch name
        current_branch = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        print(f"Current branch: {current_branch}")
        
        # Get default branch (usually main or master)
        try:
            default_branch = subprocess.run(
                ["git", "rev-parse", "--abbrev-ref", "origin/HEAD"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip().replace('origin/', '')
        except subprocess.CalledProcessError:
            # Fallback to common default branch names
            for branch in ['main', 'master']:
                try:
                    subprocess.run(
                        ["git", "rev-parse", f"origin/{branch}"],
                        capture_output=True,
                        check=True
                    )
                    default_branch = branch
                    break
                except subprocess.CalledProcessError:
                    continue
            else:
                print("Could not determine default branch. Using 'main'")
                default_branch = 'main'
        
        print(f"Base branch: {default_branch}")
        
        # Get the diff
        print("Getting diff...")
        diff = subprocess.run(
            ["git", "diff", f"origin/{default_branch}...origin/{current_branch}"],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        
        # Get commit messages
        print("Getting commit messages...")
        commits = subprocess.run(
            ["git", "log", f"origin/{default_branch}..origin/{current_branch}", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        
        if not diff and not commits:
            print("No changes detected. Have you pushed your changes?")
            return "", ""
            
        return diff, commits
        
    except subprocess.CalledProcessError as e:
        print(f"Error getting branch changes: {e}")
        print("Make sure you:")
        print("1. Are in a git repository")
        print("2. Have a remote named 'origin' or 'main'")
        print("3. Have pushed your changes")
        return "", ""

def generate_pr_content(diff: str, commits: str) -> Tuple[str, str]:
    """
    Generate Pull Request title and body using OpenAI API.
    
    Args:
        diff: Git diff content
        commits: Commit messages
        
    Returns:
        Tuple[str, str]: (PR title, PR body)
        Empty strings if generation fails.
    """
    # Load environment variables
    load_dotenv(override=True) 

    # Validate API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables. Please set it in .env file.")
        return "", ""
    
    try:
        client = OpenAI(api_key=api_key) 
        
        user_prompt = f"""Based on the following git diff and commit messages, generate a pull request title and detailed body.
        The body should include:
        - A summary of changes
        - Key modifications
        - Any important notes
        
        Commits:
        {commits}
        
        Diff:
        {diff}
        
        Format the response exactly as:
        TITLE: <title>
        BODY:
        <body>
        """
        
        system_prompt = """You are a helpful assistant specialized in creating clear 
        and informative pull request descriptions. Focus on making the changes 
        easy to understand and review."""
        
        response = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0  
        )
        
        content = response.choices[0].message.content
        
        try:
            title = content.split('TITLE:')[1].split('BODY:')[0].strip()
            body = content.split('BODY:')[1].strip()
        except IndexError:
            print("Error: AI response format was incorrect")
            return "", ""
            
        return title, body
        
    except Exception as e:
        print(f"\nError generating PR content: {str(e)}")
        print("\nPlease check:")
        print("1. OPENAI_API_KEY is set in your environment")
        print("2. The API key is valid")
        print("3. You have access to the specified model")
        return "", ""

def handle_ai_pr(additional_args: list = None) -> int:              
    """
    Handle the AI PR creation process.
    
    Args:
        additional_args: Additional arguments to pass to gh pr create
        
    Returns:
        int: 0 for success, 1 for failure
    """
    print("\n🚀 Starting AI PR creation process...")
    
    # Check GitHub CLI status first
    print("\nChecking GitHub CLI status...")
    auth_status, message = check_gh_auth()
    if not auth_status:
        print(f"❌ {message}")
        return 1
    print("✅ GitHub CLI check passed")
    
    try:
        # Get changes
        print("\nGetting branch changes...")
        diff, commits = get_branch_changes()
        if not diff and not commits:
            print("❌ No changes detected to create PR.")
            print("Make sure you have:")
            print("1. Made some changes")
            print("2. Committed your changes")
            print("3. Pushed your changes to remote")
            return 1
        print("✅ Got branch changes")
            
        # Generate content
        print("\nGenerating PR content using AI...")
        title, body = generate_pr_content(diff, commits)
        if not title or not body:
            print("❌ Failed to generate PR content")
            return 1
        print("✅ PR content generated")
        
        # Show preview
        print("\nGenerated PR Title:", title)
        print("\nGenerated PR Body:")
        print("-------------------")
        print(body)
        print("-------------------")
        
        # Get user confirmation
        while True:
            response = input("\033[1;32m\nWould you like to create this PR? (y[es]/n[o]/e[dit]): \033[0m").lower()
            
            if response == 'n':
                print("\n\033[1;31mPR creation cancelled.\033[0m")
                return 0
            elif response == 'e':
                # Allow editing
                print("\n\033[1mEnter new title (press Enter to keep current):\033[0m")
                new_title = input().strip()
                
                print("\n\033[1mEnter new body (press Enter to keep current)\033[0m")
                print("\033[1mEnter your text (Ctrl+D or Ctrl+Z to finish):\033[0m")
                
                try:
                    # 收集多行输入
                    lines = []
                    while True:
                        try:
                            line = input()
                            lines.append(line)
                        except EOFError:  # users press Ctrl+D or Ctrl+Z
                            break
                    new_body = '\n'.join(lines)
                except KeyboardInterrupt:  # users press Ctrl+C
                    print("\n\033[1;31mEditing cancelled.\033[0m")
                    continue
                
                # update title and body
                title = new_title if new_title else title
                body = new_body if new_body else body
                
                # display updated content preview
                print("\n\033[1mUpdated PR content:\033[0m")
                print(f"\nTitle: {title}")
                print("\n\033[1mBody:\033[0m")
                print("-------------------")
                print(body)
                print("-------------------")
                continue  # back to confirmation prompt
                
            elif response == 'y':
                break
            else:
                print("Please answer 'y' (yes), 'n' (no), or 'e' (edit)")
        
        # filter out 'pr create' arguments
        if additional_args:
            filtered_args = [arg for arg in additional_args if arg not in ['pr', 'create']]
        else:
            filtered_args = None
            
        # Create PR
        success, message = create_pull_request(title, body, filtered_args)
        print(message)
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error creating PR: {str(e)}")
        return 1
