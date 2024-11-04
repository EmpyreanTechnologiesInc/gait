# Gait（g-AI-t）: An AI enhanced git command line utility

## Table of Contents
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Basic Installation and Configuration](#basic-installation-and-configuration)
  - [Installing GitHub CLI](#installing-github-cli)
- [Usage](#usage)
  - [Basic Git Commands](#basic-git-commands)
  - [AI-Generated Commits](#ai-generated-commits)
  - [AI-Generated Pull Requests](#ai-generated-pull-requests)
- [Project Structure](#project-structure)


## Installation

### Prerequisites
- Python 3.7 or later ([Download from python.org](https://www.python.org/downloads/))
  ```bash
  python3 --version  # Verify Python installation
  ```
- Git
  ```bash
  git --version    # Verify Git installation
  ```
- GitHub CLI (for PR features)
- OpenAI (requires API key)

### BasicInstallation and Configuration
For macOS:
1. Clone the repository and install:
   ```bash
   # Clone the repository
   git clone https://github.com/EmpyreanTechnologiesInc/gait.git


   # Navigate to directory and install
   cd gait
   pip install -e .
   
   # Verify installation
   gait --version # should display the git version number
   ```

2. Configure AI Features

   ```bash
   # Find the .env.example file in gait directory 
   # Copy and rename it to .env
   cp .env.example .env
   
   # Open the .env file in your preferred editor
   nano .env   # or vim .env, code .env, etc.
   
   # Add your OpenAI API key to .env file
   OPENAI_API_KEY=your_api_key_here
   
   # (Optional) Configure AI model
   OPENAI_MODEL=gpt-4o-mini  # Default model
   
   # Test your OpenAI API connection
   gait test-api # If successful, you'll see: "API connection successful!"
   ```

### Installing GitHub CLI
For macOS:
   ```bash
   # Install Homebrew if you haven't
   pip install brew
   
   # Use brew to install GitHub CLI
   brew install gh
   ```

After installation, authenticate with GitHub:
```bash
gh auth login # Follow the prompts to complete the authentication process
```

## Usage

### Basic Git Commands
Any git command you know can be used with gait:

```bash
# Basic git commands
gait status
gait add .
gait commit -m "your message"
gait push

# All git commands are supported
gait branch -a
gait checkout -b feature/new-branch
gait merge main
```

### Automatically Generate Git Commits with AI

The `gait commit --ai` command analyzes your staged changes and uses AI to generate a descriptive commit message. This feature helps maintain consistent and informative commit messages across your project.

```bash
# Stage your changes first
gait add .

# Generate AI commit message
gait commit --ai

# You'll be prompted to:
# 1. Review the generated message
# 2. Accept (y), reject (n), or edit (e) the message
# 3. Once accepted or edited, 'git commit -m "<message>"' will be executed automatically
```

### AI-Generated Pull Requests
The `gait pr create --ai` command analyzes your branch changes and uses AI to generate a descriptive pull request title and body. This feature helps create comprehensive and well-structured pull requests. All standard `gh pr create` options (like `--draft`, `--base`, etc.) are supported.

```bash
# Make sure your changes are committed and pushed
gait push

# Generate AI pull request
gait pr create --ai                           # Basic AI-generated PR
# Other options
gait pr create --ai --draft                   # Create as draft PR
gait pr create --ai --base main               # Set target branch

# You'll be prompted to:
# 1. Review the generated PR title and body
# 2. Accept (y), reject (n), or edit (e) the content
# 3. Once accepted or edited, the PR will be created automatically using GitHub CLI
```

## Project Structure
```
gait/
├── src/
│   └── gait/
│       ├── __init__.py
│       ├── main.py
│       ├── git_wrapper.py
│       ├── github_wrapper.py
│       ├── ai_commit.py
│       ├── ai_pr.py
│       └── utils.py
├── README.md
├── LICENSE
├── setup.py
├── pyproject.toml
├── requirements.txt
├── .gitignore
└── .env.example
```