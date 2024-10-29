# Gait（g-AI-t）: An AI enhanced git command line utility

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Git Commands](#basic-git-commands)
- [Project Structure](#project-structure)
- [License](#license)

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

### Basic Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/EmpyreanTechnologiesInc/gait.git
   ```

2. Install the package:
   ```bash
   pip install gait
   ```

3. Verify the installation:
   ```bash
   gait --version    # Should display the Git version number
   ```

### Setting up AI Features
1. Configure OpenAI API:
   - Locate `.env.example` in the gait directory
   - Rename it to `.env`
   - Add your OpenAI API key:
     ```bash
     OPENAI_API_KEY=your_api_key_here
     ```

2. (Optional) Configure the AI model in `.env`:
   ```bash
   OPENAI_MODEL=gpt-4  # Default model
   ```

3. Verify API Connection:
   ```bash
   gait test-api
   ```
   You should see "API connection successful!". If not, verify your API key and internet connection.

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

### AI-Powered Commit Messages
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
