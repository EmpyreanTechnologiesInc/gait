import subprocess
import sys
from .ai_commit import handle_ai_commit
from .ai_pr import handle_ai_pr
from .github_wrapper import handle_pr_command

def run_git_command(command):
    if len(command) >= 1:
        if command[0] == "commit" and "--ai" in command:
            return handle_ai_commit()
        elif command[0] == "pr" and "create" in command:
            if "--ai" in command:
                # Remove --ai flag before passing additional args
                filtered_args = [arg for arg in command if arg != "--ai"]
                return handle_ai_pr(filtered_args)
            else:
                # Forward to github_wrapper
                return handle_pr_command(command)
    
    try:
        # Original git command handling
        full_command = ["git"] + command
        result = subprocess.run(
            full_command,
            check=True,
            stdout=sys.stdout, 
            stderr=sys.stderr,
        )        
        return result.returncode
    
    except subprocess.CalledProcessError as e:
        # Errors will also be automatically output to terminal
        return e.returncode

def main():
    if len(sys.argv) > 1:
        # Remove the script name from sys.argv
        git_args = sys.argv[1:]
        exit_code = run_git_command(git_args)
        sys.exit(exit_code)
    else:
        print("Usage: gait <git-command>")
        sys.exit(1)

if __name__ == "__main__":
    main()
