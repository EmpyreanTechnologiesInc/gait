# Gait（g-AI-t）: An AI enhanced git command line utility

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
  - [Basic Git Commands](#basic-git-commands)
- [Project Structure](#project-structure)
- [License](#license)

## Installation

On macOS:
1. Prerequisites:
   - Python 3.7 or later (install from [python.org](https://www.python.org/downloads/))
     ```bash
     python3 --version  # Verify Python installation
     ```
   - Git
     ```bash
     git --version    # Verify Git installation
     ```

2. Clone the repository:
   ```bash
   git clone https://github.com/EmpyreanTechnologiesInc/gait.git
   ```

3. Install the package:
   ```bash
   pip install gait
   ```

4. Verify the installation:
   ```bash
   gait --version    # Should display the Git version number
   ```

You can now use the `gait` command in your terminal when your Python environment is active.

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
