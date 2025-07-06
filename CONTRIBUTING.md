# Contributing to BTC Portfolio Tracker

Thank you for considering contributing to BTC Portfolio Tracker! 🎉

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Testing](#testing)
- [Submitting Changes](#submitting-changes)
- [Style Guidelines](#style-guidelines)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

## Getting Started

### Types of Contributions

We welcome many types of contributions:

- 🐛 **Bug Reports**: Help us identify and fix issues
- 💡 **Feature Requests**: Suggest new features or improvements
- 📖 **Documentation**: Improve or add to our documentation
- 🔧 **Code Contributions**: Fix bugs or implement new features
- 🎨 **Design**: Improve the user interface and experience
- 🧪 **Testing**: Add or improve test coverage

### Before You Start

1. **Check existing issues** to avoid duplicates
2. **Open an issue** to discuss major changes before implementing
3. **Fork the repository** and create a feature branch
4. **Follow our coding standards** and commit message format

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment (recommended)

### Setup Instructions

```bash
# Clone your fork
git clone https://github.com/yourusername/btc-portfolio-tracker.git
cd btc-portfolio-tracker

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

### Running the Application

```bash
# Terminal 1: Start backend server
cd backend
python app.py

# Terminal 2: Start frontend GUI
cd frontend
python btc_gui.py
```

### Project Structure

```
btc-portfolio-tracker/
├── frontend/
│   ├── btc_gui.py          # Main GUI application
│   └── utils/              # GUI utilities
├── backend/
│   ├── app.py              # Flask backend server
│   └── portfolio.db        # SQLite database
├── tests/
│   ├── test_backend.py     # Backend tests
│   └── test_frontend.py    # Frontend tests
├── docs/                   # Documentation
├── assets/                 # Icons and images
└── build_executable.py     # Build script
```

## Making Changes

### Branch Naming

Use descriptive branch names:
- `feature/add-new-currency`
- `bugfix/fix-login-issue`
- `docs/update-readme`
- `refactor/improve-error-handling`

### Commit Messages

Follow conventional commit format:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Test additions or changes
- `chore`: Maintenance tasks

Examples:
```
feat(currency): add EUR support to transaction forms

fix(auth): resolve JWT token expiration handling

docs(readme): update installation instructions
```

### Code Changes

1. **Write clear, readable code**
2. **Add comments for complex logic**
3. **Follow existing code patterns**
4. **Update documentation if needed**
5. **Add tests for new features**

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_backend.py

# Run with coverage
pytest --cov=.

# Run frontend tests (if applicable)
python -m pytest tests/test_frontend.py
```

### Test Guidelines

- Write tests for new features
- Ensure tests pass before submitting
- Include both positive and negative test cases
- Test edge cases and error conditions
- Mock external dependencies (APIs, databases)

### Manual Testing

Before submitting:

1. **Test the UI**: Ensure all interface elements work correctly
2. **Test Data Flow**: Verify backend-frontend communication
3. **Test Edge Cases**: Try invalid inputs and error scenarios
4. **Test Cross-Platform**: If possible, test on different operating systems

## Submitting Changes

### Pull Request Process

1. **Create a Pull Request** from your feature branch
2. **Fill out the PR template** with detailed information
3. **Link related issues** using GitHub keywords
4. **Request review** from maintainers
5. **Address feedback** promptly and professionally

### Pull Request Template

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] Added tests for new features
- [ ] Manual testing completed

## Screenshots (if applicable)
Add screenshots for UI changes.

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or breaking changes documented)
```

### Review Process

1. **Automated checks** must pass (CI/CD, linting, tests)
2. **Code review** by at least one maintainer
3. **Approval** required before merging
4. **Merge** using squash and merge for clean history

## Style Guidelines

### Python Code Style

- **Follow PEP 8**: Use standard Python style guidelines
- **Use Black**: Automatic code formatting
- **Use type hints**: For function parameters and return values
- **Docstrings**: Use Google-style docstrings

```python
def calculate_portfolio_value(btc_amount: float, btc_price: float) -> float:
    """Calculate the current value of a Bitcoin portfolio.
    
    Args:
        btc_amount: Amount of Bitcoin owned
        btc_price: Current Bitcoin price
        
    Returns:
        Current portfolio value in the specified currency
        
    Raises:
        ValueError: If btc_amount or btc_price is negative
    """
    if btc_amount < 0 or btc_price < 0:
        raise ValueError("Amount and price must be non-negative")
    
    return btc_amount * btc_price
```

### Frontend Guidelines

- **Consistent naming**: Use clear, descriptive variable names
- **Modular design**: Break complex UIs into smaller components
- **Error handling**: Provide user-friendly error messages
- **Accessibility**: Consider users with disabilities

### Documentation Style

- **Clear headings**: Use hierarchical heading structure
- **Code examples**: Include practical examples
- **Screenshots**: Add visual aids where helpful
- **Links**: Link to relevant resources

## Community

### Getting Help

- **GitHub Issues**: Ask questions or report problems
- **Discussions**: General questions and community chat
- **Documentation**: Check the wiki and README

### Recognition

Contributors are recognized in:
- README.md contributors section
- Release notes
- GitHub contributors page

### Communication

- **Be respectful**: Treat all community members with respect
- **Be constructive**: Provide helpful feedback and suggestions
- **Be patient**: Maintainers are volunteers with limited time
- **Be collaborative**: Work together to improve the project

## Development Guidelines

### Adding New Features

1. **Discuss first**: Open an issue to discuss major features
2. **Design document**: Create a design document for complex features
3. **Incremental development**: Break large features into smaller PRs
4. **Backward compatibility**: Avoid breaking existing functionality

### Database Changes

- **Migrations**: Include database migration scripts
- **Backward compatibility**: Ensure existing data remains accessible
- **Testing**: Test migrations on sample data

### API Changes

- **Versioning**: Consider API versioning for breaking changes
- **Documentation**: Update API documentation
- **Testing**: Add comprehensive API tests

### UI/UX Changes

- **Consistency**: Maintain consistent design patterns
- **Accessibility**: Ensure accessibility compliance
- **Responsiveness**: Test on different screen sizes
- **User feedback**: Consider user experience impact

---

## Questions?

If you have questions about contributing, please:

1. Check the [FAQ](https://github.com/yourusername/btc-portfolio-tracker/wiki/FAQ)
2. Search existing [issues](https://github.com/yourusername/btc-portfolio-tracker/issues)
3. Open a new [discussion](https://github.com/yourusername/btc-portfolio-tracker/discussions)

Thank you for contributing to BTC Portfolio Tracker! 🚀
