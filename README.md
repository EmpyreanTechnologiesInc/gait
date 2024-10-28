# Gait（g-AI-t）: An AI enhanced git command line utility

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Git Commands](#basic-git-commands)
- [Project Structure](#project-structure)
- [License](#license)

## Installation
To install gait, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/EmpyreanTechnologiesInc/gait.git
   cd gait
   ```

2. Install the package:
   ```bash
   pip install -e .
   ```

3. You can now use the `gait` command from anywhere in your terminal.

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

## Project Structure
```
gait/
├── src/
│   └── gait/
│       ├── __init__.py
│       ├── main.py
│       └── git_wrapper.py
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```
