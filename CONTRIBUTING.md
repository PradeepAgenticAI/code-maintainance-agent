# Contributing to Java & Spring Boot Upgrader Agent

Thank you for your interest in contributing to the Java & Spring Boot Upgrader Agent! This document provides guidelines and information for contributors.

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Java Development Kit (JDK 11+)
- Maven or Gradle
- OpenAI API key (for testing)
- GitHub Personal Access Token (for testing)

### Development Setup

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/java-springboot-upgrader-agent.git
   cd java-springboot-upgrader-agent
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements-dev.txt  # If available
   ```

4. **Set Up Environment**
   ```bash
   cp .env.example .env
   # Add your API keys for testing
   ```

5. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Development Guidelines

### Code Style
- **Follow PEP 8** for Python code formatting
- **Use type hints** where appropriate
- **Add docstrings** for all public functions and classes
- **Keep functions focused** and single-purpose
- **Use descriptive variable names**

### Example Code Style
```python
def analyze_project(repo_path: str, build_tool: str) -> Dict[str, Any]:
    """
    Analyze a Java project to extract version information.
    
    Args:
        repo_path: Path to the repository root
        build_tool: Build tool type ('maven' or 'gradle')
        
    Returns:
        Dictionary containing project analysis results
        
    Raises:
        ValueError: If build tool is not supported
    """
    if build_tool not in ['maven', 'gradle']:
        raise ValueError(f"Unsupported build tool: {build_tool}")
    
    # Implementation here
    return analysis_results
```

### Commit Messages
Use conventional commit format:
```
type(scope): description

[optional body]

[optional footer]
```

Examples:
- `feat(ui): add real-time progress tracking to Gradio interface`
- `fix(tools): handle OpenRewrite CLI installation on Windows`
- `docs(readme): update installation instructions`
- `test(workflow): add unit tests for troubleshooting node`

## 🧪 Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run with coverage
python -m pytest --cov=agent

# Run specific test file
python -m pytest tests/test_workflow.py
```

### Writing Tests
- Place tests in the `tests/` directory
- Use descriptive test names: `test_should_detect_maven_when_pom_xml_exists`
- Mock external dependencies (OpenAI API, GitHub API, file system)
- Test both success and failure scenarios

### Test Example
```python
import pytest
from unittest.mock import Mock, patch
from agent.tools import BuildTool

class TestBuildTool:
    def test_should_detect_maven_when_pom_xml_exists(self):
        """Test Maven detection when pom.xml is present."""
        with patch('os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path.endswith('pom.xml')
            
            build_tool = BuildTool()
            result = build_tool._detect_build_tool('/fake/repo')
            
            assert result == "maven"
```

## 🎯 Areas for Contribution

### High Priority
- **Error Handling**: Improve robustness and error messages
- **Testing**: Add comprehensive test coverage
- **Documentation**: Improve inline documentation and examples
- **Performance**: Optimize workflow execution time

### Medium Priority
- **New Features**: Additional OpenRewrite recipes support
- **UI Improvements**: Enhanced user experience in web interfaces
- **Build Tools**: Support for SBT, Bazel, or other build systems
- **VCS Integration**: GitLab, Bitbucket support

### Low Priority
- **Internationalization**: Multi-language support
- **Themes**: Custom UI themes and styling
- **Analytics**: Usage metrics and reporting

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Clear Description**: What happened vs what you expected
2. **Steps to Reproduce**: Detailed steps to recreate the issue
3. **Environment**: OS, Python version, dependency versions
4. **Logs**: Relevant error messages and stack traces
5. **Repository**: Link to test repository (if public)

### Bug Report Template
```markdown
## Bug Description
Brief description of the issue

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should have happened

## Actual Behavior
What actually happened

## Environment
- OS: [e.g., Windows 11, macOS 12, Ubuntu 20.04]
- Python: [e.g., 3.9.7]
- Agent Version: [e.g., 1.0.0]

## Logs
```
Paste relevant logs here
```

## Additional Context
Any other relevant information
```

## 🚀 Feature Requests

For new features:

1. **Check existing issues** to avoid duplicates
2. **Describe the problem** the feature would solve
3. **Propose a solution** with implementation details
4. **Consider alternatives** and explain why your approach is best
5. **Provide examples** of how the feature would be used

## 🔄 Pull Request Process

### Before Submitting
- [ ] Code follows project style guidelines
- [ ] Tests pass locally
- [ ] New features include tests
- [ ] Documentation is updated
- [ ] Commit messages follow conventional format
- [ ] No merge conflicts with main branch

### PR Description Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process
1. **Automated Checks**: CI/CD pipeline runs tests and linting
2. **Code Review**: Maintainers review code quality and design
3. **Testing**: Manual testing of new features
4. **Approval**: At least one maintainer approval required
5. **Merge**: Squash and merge to main branch

## 📚 Documentation

### Types of Documentation
- **Code Comments**: Explain complex logic and algorithms
- **Docstrings**: Document all public APIs
- **README**: Keep installation and usage instructions current
- **Architecture**: Document design decisions and patterns
- **Examples**: Provide working examples for new features

### Documentation Standards
- Use clear, concise language
- Include code examples where helpful
- Keep documentation up-to-date with code changes
- Use proper Markdown formatting

## 🏗️ Architecture Guidelines

### Project Structure
```
agent/
├── __init__.py          # Package initialization
├── state.py            # LangGraph state management
├── workflow.py         # Main workflow orchestration
├── tools.py            # Individual tool implementations
├── llm_chains.py       # LLM interaction chains
└── github_integration.py # VCS integration
```

### Design Principles
- **Separation of Concerns**: Each module has a single responsibility
- **Dependency Injection**: Use dependency injection for testability
- **Error Handling**: Graceful error handling with informative messages
- **Logging**: Comprehensive logging for debugging
- **Configuration**: Externalize configuration via environment variables

### Adding New Tools
1. Create tool class inheriting from `BaseTool`
2. Implement `_run` method with proper error handling
3. Add comprehensive docstrings and type hints
4. Write unit tests with mocked dependencies
5. Update workflow to use the new tool

## 🤝 Community Guidelines

### Code of Conduct
- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Assume positive intent
- Report inappropriate behavior to maintainers

### Communication Channels
- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: Questions and general discussion
- **Pull Requests**: Code review and collaboration

## 🎉 Recognition

Contributors will be recognized in:
- **README**: Contributors section
- **Release Notes**: Major contributions highlighted
- **GitHub**: Contributor graphs and statistics

## 📞 Getting Help

If you need help:
1. **Check Documentation**: README and inline comments
2. **Search Issues**: Existing issues might have answers
3. **Ask Questions**: Use GitHub Discussions
4. **Contact Maintainers**: Tag maintainers in issues

## 🚀 Release Process

### Versioning
We use [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Version number bumped
- [ ] Release notes prepared
- [ ] Tag created
- [ ] PyPI package updated (if applicable)

---

Thank you for contributing to the Java & Spring Boot Upgrader Agent! 🚀
