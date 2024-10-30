# Gait（g-AI-t）: An AI enhanced git command line utility

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Git Commands](#basic-git-commands)
  - [Automatically Generate Git Commits with AI](#automatically-generate-git-commits-with-ai)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

1. Clone and Install
  For macOS:
   ```bash
   # Clone the repository
   git clone https://github.com/EmpyreanTechnologiesInc/gait.git

   # Navigate to directory and install
   cd gait
   pip install .
   
   # Verify installation
   gait --version
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

## Project Structure
```
gait/
├── src/
│   └── gait/
│       ├── __init__.py
│       ├── main.py
│       ├── git_wrapper.py
│       ├── ai_commit.py
│       └── utils.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```
