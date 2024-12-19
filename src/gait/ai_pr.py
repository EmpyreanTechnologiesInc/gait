import subprocess
from typing import Tuple
from openai import OpenAI
from dotenv import load_dotenv
from .github_wrapper import create_pull_request, check_gh_auth
import os
from pydantic import BaseModel
import json
import re
from .linear_client import LinearClient

"""
AI-powered Pull Request creation module.
Handles generating and submitting pull requests using OpenAI for content generation.
"""
class PRContent(BaseModel):
    title: str
    body: str

def get_branch_changes(base_branch: str = None) -> Tuple[str, str]:
    """
    Get the diff and commit messages between current branch and base branch.
    
    Args:
        base_branch: Target base branch. If None, uses default branch.
    
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
        
        # Check if remote branch exists
        remote_exists = subprocess.run(
            ["git", "ls-remote", "--heads", "origin", current_branch],
            capture_output=True,
            text=True,
            check=True
        ).stdout.strip()
        
        if remote_exists:
            print(f"\nRemote branch 'origin/{current_branch}' exists.")
            
            unpushed = subprocess.run(
                ["git", "log", f"origin/{current_branch}..{current_branch}", "--oneline"],
                capture_output=True,
                text=True,
                check=True
            ).stdout.strip()
            
            if unpushed:
                print("You have unpushed commits.")
            
            while True:
                response = input(f"\033[1;33mWould you like to:\n"
                              f"1. Use/Push to existing remote branch 'origin/{current_branch}'\n"
                              f"2. Create a new remote branch\n"
                              f"Choose (1/2): \033[0m").strip()
                
                if response == '1':
                    if unpushed:
                        try:
                            subprocess.run(
                                ["git", "push", "origin", current_branch],
                                check=True
                            )
                            print(f"✅ Changes pushed to origin/{current_branch}")
                        except subprocess.CalledProcessError as e:
                            print(f"❌ Failed to push changes: {e}")
                            return "", ""
                    else:
                        print(f"✅ Using existing remote branch: origin/{current_branch}")
                    break
                elif response == '2':
                    new_branch_name = input("\033[1;32mEnter new remote branch name: \033[0m").strip()
                    if not new_branch_name:
                        print("Branch name cannot be empty")
                        continue
                    
                    try:
                        subprocess.run(
                            ["git", "push", "-u", "origin", f"{current_branch}:{new_branch_name}"],
                            check=True
                        )
                        print(f"✅ Created and pushed to remote branch: origin/{new_branch_name}")
                        current_branch = new_branch_name
                        break
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Failed to create remote branch: {e}")
                        return "", ""
                else:
                    print("Please choose 1 or 2")
        else:
            print(f"\nRemote branch 'origin/{current_branch}' doesn't exist.")
            while True:
                response = input(f"\033[1;33mWould you like to create a remote branch? (y/n): \033[0m").lower()
                if response == 'y':
                    new_branch_name = input("\033[1;32mEnter remote branch name (press Enter to use current branch name): \033[0m").strip()
                    remote_branch = new_branch_name if new_branch_name else current_branch
                    
                    try:
                        subprocess.run(
                            ["git", "push", "-u", "origin", f"{current_branch}:{remote_branch}"],
                            check=True
                        )
                        print(f"✅ Created and pushed to remote branch: origin/{remote_branch}")
                        current_branch = remote_branch
                        break
                    except subprocess.CalledProcessError as e:
                        print(f"❌ Failed to create remote branch: {e}")
                        return "", ""
                elif response == 'n':
                    print("\n❌ Please create a remote branch first using:")
                    print(f"git push -u origin {current_branch}:<new-branch-name>")
                    print("Or run this command again and choose 'y'")
                    return "", ""
                else:
                    print("Please answer 'y' (yes) or 'n' (no)")

        # Use provided base_branch or detect default branch
        if base_branch:
            default_branch = base_branch
        else:
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
        
        # Get the diff against the specified base branch
        print("Getting diff...")
        diff = subprocess.run(
            ["git", "diff", f"origin/{default_branch}...origin/{current_branch}"],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        
        # Get commit messages against the specified base branch
        print("Getting commit messages...")
        commits = subprocess.run(
            ["git", "log", f"origin/{default_branch}..origin/{current_branch}", "--pretty=format:%s"],
            capture_output=True,
            text=True,
            check=True
        ).stdout
        
        if not diff and not commits:
            print("❌ No changes detected to create PR.")
            print("Make sure you have:")
            print("1. Made some changes")
            print("2. Committed your changes")
            print("3. Pushed your changes to remote")
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
    
    # Reload environment variables, incase it was changed
    load_dotenv(override=True) 

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
        """
        
        system_prompt = """You are a helpful assistant specialized in creating clear 
        and informative pull request descriptions. You must format your response exactly as:
        TITLE: <title>
        BODY:
        <body>"""
        
        response = client.beta.chat.completions.parse(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            response_format=PRContent,
            temperature=0  
        )
        
        content = json.loads(response.choices[0].message.content)
        return content["title"], content["body"]
        
    except Exception as e:
        print(f"\nError generating PR content: {str(e)}")
        print("\nPlease check:")
        print("1. OPENAI_API_KEY is set in your environment")
        print("2. The API key is valid")
        print("3. You have access to the specified model")
        return "", ""

def process_todos(diff: str) -> Tuple[str, list]:
    """Process TODOs in the diff and create Linear issues."""
    comment_prefix = r'[+-].*?(?:#|//|/\*)\s*'
    todo_pattern = fr'{comment_prefix}TODO\s*(?:\(([^)]*)\))?\s*:\s*(.+?)(?:\s*\*/)?\s*$'
    issue_id_pattern = r'^[A-Z]{2,}-\d+$'
    
    todos = []
    current_file = None
    updated_lines = []
    file_changes = {}
    linear_client = None
    
    try:
        linear_client = LinearClient()
    except ValueError as e:
        print(f"⚠️ Linear client initialization failed: {str(e)}")
        return diff, None  # Return original diff and None for todos to trigger the confirmation prompt

    removed_todos = [] 
    for line in diff.split('\n'):
        if line.startswith('+++'):
            current_file = line[6:]
            if current_file.startswith('b/'):
                current_file = current_file[2:]
            updated_lines.append(line)
            continue
            
        if line.startswith('-'):
            todo_match = re.search(todo_pattern, line)
            if todo_match and current_file:
                context = todo_match.group(1)
                if context and re.match(issue_id_pattern, context):
                    removed_todos.append((current_file, context))
            updated_lines.append(line)
            continue

        if not line.startswith('+'):
            updated_lines.append(line)
            continue
            
        todo_match = re.search(todo_pattern, line)
        if not todo_match or not current_file:
            updated_lines.append(line)
            continue
            
        context = todo_match.group(1)
        comment = todo_match.group(2).strip()
        
        if context and re.match(issue_id_pattern, context):
            todos.append((current_file, line, context, comment))
            updated_lines.append(line)
            continue
            
        issue_id = linear_client.create_issue(
            title=comment,
            file_path=current_file,
            context=context
        ) if linear_client else None
        
        if not issue_id:
            print(f"⚠️ Linear issue creation failed")
            return diff, None  # Return original diff and None to trigger confirmation prompt
            
        if issue_id:
            indent = re.match(r'^\+\s*', line).group()
            comment_symbol = '#' if '#' in line else '//'
            new_line = f"{indent}{comment_symbol} TODO({issue_id}):{comment}" if context is None else f"{indent}{comment_symbol} TODO({issue_id}):({context}):({comment})"
            
            if current_file not in file_changes:
                file_changes[current_file] = []
            file_changes[current_file].append((
                line.lstrip('+'),
                new_line.lstrip('+')
            ))
            
            todos.append((current_file, new_line, issue_id, comment))
            updated_lines.append(new_line)
        else:
            print(f"⚠️ Keeping original TODO line due to Linear issue creation failure")
            todos.append((current_file, line, context, comment))
            updated_lines.append(line)
    
    if removed_todos and linear_client:
        print("\nProcessing removed TODOs...")
        for file_path, issue_id in removed_todos:
            try:
                if linear_client.complete_issue(issue_id):
                    print(f"✅ Marked Linear issue {issue_id} as done (removed from {file_path})")
                else:
                    print(f"⚠️ Failed to mark Linear issue {issue_id} as done")
            except Exception as e:
                print(f"❌ Error updating Linear issue {issue_id}: {str(e)}")

    if file_changes:
        try:
            for file_path, changes in file_changes.items():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.readlines()
                    
                    updated_content = []
                    for line in content:
                        line_stripped = line.rstrip('\n')
                        matched = False
                        for old_line, new_line in changes:
                            if line_stripped.strip() == old_line.strip():
                                updated_content.append(new_line + '\n')
                                matched = True
                                break
                        if not matched:
                            updated_content.append(line)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.writelines(updated_content)
                    
                    # verify changes to ensure they were applied correctly
                    with open(file_path, 'r', encoding='utf-8') as f:
                        verify_content = f.read()
                        for _, new_line in changes:
                            if new_line not in verify_content:
                                print(f"⚠️ Warning: Failed to verify change: {new_line}") 
                        
                except Exception as e:
                    print(f"❌ Error updating {file_path}: {str(e)}")
                    print(f"Error details: {type(e).__name__}: {str(e)}")
                    return diff, None
            
            # Single commit for all changes to keep commit history clean
            total_changes = sum(len(changes) for changes in file_changes.values())
            file_list = ', '.join(file_changes.keys())
            
            for file_path in file_changes.keys():
                subprocess.run(["git", "add", file_path], check=True)
                
            commit_msg = f"Update {total_changes} TODOs with Linear issue IDs in {file_list}"
            subprocess.run(["git", "commit", "-m", commit_msg], check=True)
            subprocess.run(["git", "push"], check=True)
            print(f"✅ Updated and committed {total_changes} TODOs across {len(file_changes)} files")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Error committing changes: {str(e)}")
            return diff, None
    
    return '\n'.join(updated_lines), todos

def handle_ai_pr(additional_args: list = None) -> int:              
    """
    Handle the AI PR creation process.
    
    Args:
        additional_args: Additional arguments to pass to gh pr create
        
    Returns:
        int: 0 for success, 1 for failure
    """
    print("\n🚀 Starting AI PR creation process...")
    
    print("\nChecking GitHub CLI status...")
    auth_status, message = check_gh_auth()
    if not auth_status:
        print(f"❌ {message}")
        return 1
    print("✅ GitHub CLI check passed")
    
    try:
        base_branch = None
        if additional_args:
            try:
                base_idx = -1
                if '--base' in additional_args:
                    base_idx = additional_args.index('--base')
                elif '-B' in additional_args:
                    base_idx = additional_args.index('-B')
                
                if base_idx >= 0 and len(additional_args) > base_idx + 1:
                    base_branch = additional_args[base_idx + 1]
            except ValueError:
                pass 
        
        diff, commits = get_branch_changes(base_branch)
        if not diff and not commits:
            return 1
        print("✅ Got branch changes")
            
        print("\n\033[1mChecking for new TODOs...\033[0m")
        diff, todos = process_todos(diff)
        if todos is None:
            print("⚠️ TODO processing failed.")
            while True:
                response = input("\033[1;33mWould you like to continue creating PR without processing TODOs? (y/n): \033[0m").lower()
                if response == 'n':
                    print("❌ Aborting PR creation.")
                    return 1
                elif response == 'y':
                    print("Continuing without TODO processing...")
                    break
                else:
                    print("Please answer 'y' (yes) or 'n' (no)")
        
        print("\nGenerating PR content using AI...")
        title, body = generate_pr_content(diff, commits)
        if not title or not body:
            print("❌ Failed to generate PR content")
            return 1
        print("✅ PR content generated")
        
        # Show preview so user can edit if needed
        print("\nGenerated PR Title:", title)
        print("\nGenerated PR Body:")
        print("-------------------")
        print(body)
        print("-------------------")
        
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
                    lines = []
                    while True:
                        try:
                            line = input()
                            lines.append(line)
                        except EOFError: 
                            break
                    new_body = '\n'.join(lines)
                except KeyboardInterrupt:  
                    print("\n\033[1;31mEditing cancelled.\033[0m")
                    continue
                
                title = new_title if new_title else title
                body = new_body if new_body else body
                
                print("\n\033[1mUpdated PR content:\033[0m")
                print(f"\nTitle: {title}")
                print("\n\033[1mBody:\033[0m")
                print("-------------------")
                print(body)
                print("-------------------")
                continue  
                
            elif response == 'y':
                break
            else:
                print("Please answer 'y' (yes), 'n' (no), or 'e' (edit)")
        
        if additional_args:
            filtered_args = [arg for arg in additional_args if arg not in ['pr', 'create']]
        else:
            filtered_args = None
            
        success, message = create_pull_request(title, body, filtered_args)
        print(message)
        return 0 if success else 1
        
    except Exception as e:
        print(f"Error creating PR: {str(e)}")
        return 1