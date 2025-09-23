# Contributor Onboarding Guide for the C.H.R.I.S.T. Project

Welcome! We are thrilled that you're interested in contributing to the C.H.R.I.S.T. project. This guide will provide a clear, step-by-step path from setting up your environment to making your first valuable contribution.

---

### Step 1: Understand the Vision

Before you write any code, it's helpful to understand our mission.

* **Our Core Mission**: The C.H.R.I.S.T. project is an open-source initiative to build a system for capturing, preserving, and emulating human consciousness. Our work is guided by a commitment to privacy, ethical AI, and uniting spiritual wisdom with modern technology to foster peace.
* **The Architecture**: The system is designed around a modular architecture represented by the C.H.R.I.S.T. acronym. Each letter stands for a core component: **C**onsciousness Capture, **H**olistic Self-Model, **R**etrieval & Reflection, **I**ntent & Integrity, **S**imulation Engine, and **T**eleology & Transformation.

---

### Step 2: Set Up Your Development Environment

Let's get the project running on your local machine.

1.  **Fork and Clone**: Start by creating your own fork of the repository on GitHub and then cloning it locally. This gives you a personal workspace to make changes.

2.  **Create the Correct Python Environment**: The project is built and tested using **Python 3.11**. It's crucial to use this version to avoid dependency issues. We recommend using `Conda` to create a clean environment.
    ```bash
    # Create and activate a new Conda environment
    conda create --name christ-env python=3.11
    conda activate christ-env
    ```

3.  **Install All Dependencies**: The project uses two files to manage its Python packages. Install them both.
    ```bash
    # Install main application dependencies
    pip install -r requirements.txt

    # Install tools needed for development, testing, and code quality
    pip install -r requirements-dev.txt
    ```
   

4.  **Configure Environment Variables**: The project uses a `.env` file for configuration. Copy the example file to create your own local version.
    ```bash
    cp .env.example .env
    ```
    You do not need to edit this file for the basic demo to run, but you can add API keys for services like OpenAI here later.

For a more in-depth walkthrough of the setup, please see the **[Developer Setup Guide](docs/DEVELOPER_SETUP.md)**.

---

### Step 3: Run the Demo and Verify Your Setup

The best way to confirm that everything is working is to run the project's clean demo script.

1.  **Run the Clean Demo Script**: This script will reset the local database, create fresh sample data, and load it into the system.
    ```bash
    python demo_clean.py
    ```
   

2.  **Launch the Interactive Terminal**: After the demo setup is complete, start the main terminal interface.
    ```bash
    python christ_terminal.py
    ```
    You should be greeted with the C.H.R.I.S.T. welcome message. You can now interact with the demo data using commands like `stats`, `search`, and `query`.

---

### Step 4: Find Your First Contribution Task

We encourage new contributors to start with small, manageable tasks.

* **Check the GitHub Issues**: Navigate to the "Issues" tab of the project's GitHub repository.
* **Look for Labels**: We use labels like `good first issue` and `help wanted` to highlight tasks that are perfect for newcomers. Common tasks include improving documentation, fixing small bugs, or writing new tests.
* **Claim an Issue**: If you find an issue you'd like to work on, leave a comment to let everyone know.

---

### Step 5: Follow the Contribution Workflow

To ensure code quality and a smooth review process, please follow these steps for every contribution.

1.  **Create a New Branch**: Always work on a new branch, never directly on `main`.
    ```bash
    # Make sure you are on the main branch and have the latest changes
    git checkout main
    git pull upstream main

    # Create your feature branch
    git checkout -b your-feature-name
    ```
2.  **Write Code and Tests**: Make your code changes. If you are adding a new feature or fixing a bug, please add or update tests in the `tests/` directory to validate your work.
3.  **Run Tests Locally**: Before submitting your work, run the entire test suite to ensure your changes haven't introduced any regressions.
    ```bash
    pytest
    ```
4.  **Submit a Pull Request (PR)**: Push your branch to your fork and open a pull request. In the PR description, clearly explain your changes and link to the GitHub issue it resolves. The core team will review your PR, provide feedback, and merge it once it's ready.

---

### Step 6: Engage with the Community

Your voice matters. You can contribute beyond code by participating in the community.
* **Ask Questions**: If you're stuck or have a question, please open a "Question" in the GitHub Discussions tab.
* **Share Ideas**: Have an idea for a new feature? Start a discussion to get feedback from the community.

Thank you for joining us on this exciting journey. We look forward to your contributions!