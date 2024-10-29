from .git_wrapper import main
from .git_wrapper import run_git_command
import sys

def main():
    if len(sys.argv) > 1:
        git_args = sys.argv[1:] # Remove the "gait" from the command
        exit_code = run_git_command(git_args) # pass only the command
        sys.exit(exit_code)
    else:
        print("Usage: gait <git-command>")
        sys.exit(1)

if __name__ == "__main__":
    main()