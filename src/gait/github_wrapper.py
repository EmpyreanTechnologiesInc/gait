# Wrapper for GitHub CLI (gh)
import subprocess
from typing import Tuple, Optional, List
import sys

def check_gh_auth() -> Tuple[bool, str]:
    """Check if GitHub CLI is installed and authenticated"""
    try:
        result = subprocess.run(
            ["gh", "auth", "status"], 
            capture_output=True, 
            text=True
        )
        if result.returncode == 0:
            return True, "GitHub CLI authenticated"
        else:
            return False, f"GitHub CLI not authenticated. Error: {result.stderr}"
    except FileNotFoundError:
        return False, """"GitHub CLI (gh) not installed. Please follow the instructions in README or install it first: https://cli.github.com"""
    except Exception as e:
        return False, f"Error checking GitHub CLI: {str(e)}"

def guide_auth() -> bool:
    """Guide user through GitHub authentication process by launching interactive login."""
    print("\nStarting GitHub authentication process...")
    try:
        subprocess.run(["gh", "auth", "login"], check=True)
        return True
    except subprocess.CalledProcessError:
        print("Authentication failed.")
        return False

def create_pull_request(
    title: str, 
    body: str, 
    additional_args: Optional[List[str]] = None
) -> Tuple[bool, str]:
    """Create a pull request using GitHub CLI"""
    # Check authentication first
    auth_status, message = check_gh_auth()
    if not auth_status:
        return False, message

    # Base command
    cmd = ["gh", "pr", "create", "-t", title, "-b", body]
    
    # Add additional arguments if provided    
    if additional_args:
        filtered_args = [arg for arg in additional_args if arg not in ['pr', 'create']]
        if filtered_args:
            cmd.extend(filtered_args)

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            pr_url = result.stdout.strip()
            return True, f"Successfully created PR: {pr_url}"
        else:
            return False, f"Failed to create PR:\n{result.stderr}"
    except Exception as e:
        return False, f"Error creating PR: {str(e)}"

def handle_pr_command(args: List[str]) -> int:
    """Handle PR related commands by passing them to GitHub CLI."""
    # Check authentication first
    auth_status, message = check_gh_auth()
    if not auth_status:
        print(message)
        if "not installed" in message:
            return 1
        if not guide_auth():
            return 1

    command = ["gh"] + args

    try:
        result = subprocess.run(
            command,
            check=True,
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        return result.returncode
    except subprocess.CalledProcessError as e:
        return e.returncode
    except FileNotFoundError:
        print("GitHub CLI (gh) not installed. Please follow the instructions in README or install it first: https://cli.github.com")
        return 1