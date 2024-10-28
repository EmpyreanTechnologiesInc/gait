import subprocess
import sys
from .ai_commit import handle_ai_commit

def run_git_command(command):
    if len(command) >= 1 and command[0] == "commit" and "--ai" in command:
        return handle_ai_commit()
        
    try:
        # Construct the full command
        full_command = ["git"] + command
        
        # Run the Git command and direct its output to terminal
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
