# 🤖 AI-Powered Java & Spring Boot Upgrader Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![OpenRewrite](https://img.shields.io/badge/OpenRewrite-Compatible-green.svg)](https://docs.openrewrite.org/)

An open-source autonomous agent that automatically upgrades Java and Spring Boot projects using OpenRewrite recipes and AI-powered analysis. This tool streamlines the complex process of upgrading legacy codebases by combining the power of AI with proven automated refactoring tools.

## ✨ Features

- 🤖 **AI-Powered Analysis**: Uses GPT to analyze projects and create intelligent upgrade strategies
- 🔄 **Automated OpenRewrite Integration**: Installs and applies OpenRewrite recipes automatically
- 🛠️ **Build Tool Detection**: Auto-detects Maven or Gradle projects with zero configuration
- 🩺 **Intelligent Troubleshooting**: Generates custom fixes for build errors using AI
- 🚀 **GitHub Integration**: Creates professional pull requests automatically
- 🖥️ **Web UI**: Beautiful Gradio and Streamlit interfaces for easy interaction
- 🔒 **Secure**: Uses environment variables for API keys and tokens
- 🌐 **Open Source**: MIT licensed and community-driven

## Prerequisites

- Python 3.8+
- Java Development Kit (JDK 11+)
- Maven or Gradle (must be installed and available in PATH)
- Git command-line client
- OpenAI API key
- GitHub Personal Access Token

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/java-springboot-upgrader-agent.git
cd java-springboot-upgrader-agent
```

### 2. Install Dependencies
```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your credentials
# OPENAI_API_KEY=your_openai_api_key_here
# GITHUB_TOKEN=your_github_token_here
```

### 4. Launch the Web UI
```bash
# Gradio UI (recommended for real-time progress)
python launch_gradio.py

# OR Streamlit UI (clean dashboard interface)
python launch_streamlit.py
```

### 5. Start Upgrading!
1. Open the web interface (http://localhost:7860 for Gradio or http://localhost:8501 for Streamlit)
2. Enter your repository URL and configuration
3. Click "Start Upgrade" and monitor the progress
4. Review the automatically created pull request

## 📋 Requirements

**System Requirements:**
- Python 3.8 or higher
- Java Development Kit (JDK 11+)
- Maven or Gradle (must be in PATH)
- Git command-line client

**API Keys:**
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))
- GitHub Personal Access Token with `repo` permissions ([Create one here](https://github.com/settings/tokens))

## Usage

You can use the agent in three ways:

### 🖥️ Web UI (Recommended)

**Gradio UI (Interactive with real-time progress):**
```bash
python launch_gradio.py
# Opens at http://localhost:7860
```

**Streamlit UI (Clean dashboard interface):**
```bash
python launch_streamlit.py  
# Opens at http://localhost:8501
```

### 📟 Command Line Interface

**Basic Usage:**
```bash
python main.py --repository-url https://github.com/owner/repo.git --base-branch main
```

**Advanced Usage:**
```bash
python main.py \
  --repository-url https://github.com/owner/repo.git \
  --base-branch main \
  --target-version "Java 17" \
  --llm-model gpt-4 \
  --max-attempts 3 \
  --new-branch-name upgrade-to-java17
```

### Command Line Arguments

**Required:**
- `--repository-url`: SSH or HTTPS URL of the Git repository
- `--base-branch`: Starting branch to work from (e.g., main)

**Optional:**
- `--target-version`: Desired Java or Spring Boot version
- `--llm-model`: LLM model to use (default: gpt-4)
- `--max-attempts`: Maximum troubleshooting attempts (default: 5)
- `--new-branch-name`: Name for the new feature branch

## How It Works

The agent follows a structured workflow implemented using LangGraph:

1. **🚀 Setup**: Installs OpenRewrite CLI and clones the repository
2. **🧠 Analysis**: Detects build tool, analyzes current versions, creates upgrade strategy
3. **🛠️ Apply Recipes**: Executes OpenRewrite recipes to transform code
4. **⚙️ Verification**: Builds and tests the project
5. **🩺 Troubleshooting**: If build fails, generates custom fixes using AI
6. **✅ Finalization**: Commits changes and creates a pull request

## Architecture

- **LangGraph**: Manages the workflow state and orchestrates the upgrade process
- **LangChain**: Provides LLM integration for analysis and troubleshooting
- **OpenRewrite**: Performs automated code transformations
- **GitHub API**: Creates pull requests for human review

## Output

The agent outputs a JSON object with:
```json
{
  "pull_request_url": "https://github.com/owner/repo/pull/123",
  "summary_report": "Detailed summary of the upgrade process..."
}
```

## Security

- All credentials are provided via environment variables
- The agent cannot merge its own pull requests
- All changes go through human review via pull requests

## Troubleshooting

### Common Issues

1. **OpenRewrite CLI installation fails**: Ensure you have Java installed and internet access
2. **Build tool not detected**: Make sure `pom.xml` or `build.gradle` exists in the repository root
3. **GitHub API errors**: Verify your `GITHUB_TOKEN` has the necessary permissions
4. **OpenAI API errors**: Check your `OPENAI_API_KEY` and API quota

### Logs

The agent provides detailed console output during execution. Monitor the logs for:
- Setup progress
- Analysis results
- Recipe application status
- Build results
- Troubleshooting attempts

## 🏗️ Project Structure

```
java-springboot-upgrader-agent/
├── agent/                      # Core agent implementation
│   ├── __init__.py
│   ├── state.py               # LangGraph state management
│   ├── workflow.py            # Main LangGraph workflow
│   ├── tools.py               # Custom tools (Git, OpenRewrite, Build)
│   ├── llm_chains.py          # LLM chains for analysis
│   └── github_integration.py  # GitHub API integration
├── ui_gradio.py               # Gradio web interface
├── ui_streamlit.py            # Streamlit web interface
├── launch_gradio.py           # Gradio launcher script
├── launch_streamlit.py        # Streamlit launcher script
├── main.py                    # Command-line interface
├── requirements.txt           # Python dependencies
├── .env.example              # Environment variables template
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Getting Started
1. **Fork the repository** on GitHub
2. **Clone your fork** locally
3. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
4. **Make your changes** and test them
5. **Commit your changes** (`git commit -m 'Add amazing feature'`)
6. **Push to your branch** (`git push origin feature/amazing-feature`)
7. **Open a Pull Request**

### Development Setup
```bash
# Clone your fork
git clone https://github.com/your-username/java-springboot-upgrader-agent.git
cd java-springboot-upgrader-agent

# Create development environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up pre-commit hooks (optional)
pip install pre-commit
pre-commit install
```

### Areas for Contribution
- 🐛 **Bug fixes** and error handling improvements
- 🚀 **New features** and OpenRewrite recipe support
- 📚 **Documentation** improvements
- 🧪 **Testing** and test coverage
- 🎨 **UI/UX** enhancements
- 🔧 **Performance** optimizations

### Code Style
- Follow PEP 8 for Python code
- Add docstrings for new functions and classes
- Include type hints where appropriate
- Write descriptive commit messages

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support & Community

### Getting Help
- 📖 **Documentation**: Check this README and inline code comments
- 🐛 **Bug Reports**: [Open an issue](https://github.com/your-username/java-springboot-upgrader-agent/issues) with:
  - Steps to reproduce
  - Expected vs actual behavior
  - System information (OS, Python version, etc.)
  - Log output and error messages

### Community
- 💬 **Discussions**: Use GitHub Discussions for questions and ideas
- 🔄 **Updates**: Watch the repository for updates
- ⭐ **Star**: If you find this useful, please star the repository!

### Troubleshooting
Common issues and solutions:

**OpenRewrite CLI installation fails:**
- Ensure Java is installed and in PATH
- Check internet connectivity
- Try running with administrator/sudo privileges

**Build tool not detected:**
- Verify `pom.xml` or `build.gradle` exists in repository root
- Ensure Maven/Gradle is installed and in PATH

**GitHub API errors:**
- Verify GitHub token has `repo` permissions
- Check token hasn't expired
- Ensure repository URL is accessible

**OpenAI API errors:**
- Verify API key is correct and active
- Check API quota and billing
- Try a different model (gpt-3.5-turbo vs gpt-4)

## 🙏 Acknowledgments

- [OpenRewrite](https://docs.openrewrite.org/) - Automated code refactoring
- [LangChain](https://python.langchain.com/) - LLM application framework  
- [LangGraph](https://python.langchain.com/docs/langgraph) - Stateful agent workflows
- [Gradio](https://gradio.app/) - Machine learning web interfaces
- [Streamlit](https://streamlit.io/) - Data app framework

## 📈 Roadmap

- [ ] Support for additional build tools (SBT, Bazel)
- [ ] Integration with more VCS platforms (GitLab, Bitbucket)
- [ ] Custom OpenRewrite recipe generation
- [ ] Batch processing for multiple repositories
- [ ] Integration with CI/CD pipelines
- [ ] Advanced conflict resolution strategies
- [ ] Support for more programming languages

---

**Made with ❤️ by the open source community**
