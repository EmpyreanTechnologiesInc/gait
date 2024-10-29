from .git_wrapper import main
from .git_wrapper import run_git_command
from .utils import test_openai_connection
import sys

def main():
    if len(sys.argv) > 1:
        git_args = sys.argv[1:] # Remove the "gait" from the command
        if git_args[0] == 'test-api':
            success, message = test_openai_connection()
            print(message)
            sys.exit(0 if success else 1)
        else:
            exit_code = run_git_command(git_args) # pass only the command
            sys.exit(exit_code)
    else:
        print("Usage: gait <git-command>")
        sys.exit(1)

if __name__ == "__main__":
    main()