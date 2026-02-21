# Contributing to Reddit SaaS Validator

Thank you for your interest in contributing! 🎉

## How to Contribute

### 🐛 Bug Reports

If you find a bug, please open an issue with:
- Description of the bug
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

### 💡 Feature Requests

We welcome feature suggestions! Please open an issue describing:
- The feature and use case
- Why it would be valuable
- Implementation ideas (optional)

### 🔧 Pull Requests

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Add comments for complex logic
   - Update documentation if needed
4. **Test your changes**
   ```bash
   python -m pytest tests/
   ```
5. **Commit with clear messages**
   ```bash
   git commit -m "feat: add new feature"
   ```
6. **Push and create PR**
   ```bash
   git push origin feature/your-feature-name
   ```

### 📝 Commit Message Convention

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Adding tests
- `chore:` Maintenance tasks

### 🧪 Testing

Before submitting a PR, ensure:
- Code follows PEP 8 style guide
- All tests pass
- New features have tests
- Documentation is updated

### 🤝 Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Help others learn and grow

## Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/reddit-saas-validator.git
cd reddit-saas-validator

# Install dependencies
pip install -r requirements.txt

# Run tests
python -m pytest tests/

# Run linter
flake8 src/
```

## Questions?

Feel free to open an issue or reach out to the maintainers.

Thank you for contributing! 🚀
