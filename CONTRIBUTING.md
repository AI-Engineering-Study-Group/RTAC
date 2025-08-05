# 🤝 Contributing to RTAC

Welcome to RTAC! We're excited to have you contribute to making event organization more intelligent and accessible. This guide will help you get started and understand how to contribute effectively.

## 🎯 What is RTAC?

RTAC ("répondrai toujours avec certitude" - French for "will always respond with certainty") is a plug-and-play AI assistant platform for event organizers. It transforms any event into an intelligent, conversational experience.

## 🚀 Quick Start

### Prerequisites

- Python 3.13 or higher
- Node.js 18+ (for frontend development)
- Git
- Docker (optional, but recommended)

### Setting Up Your Development Environment

1. **Fork and Clone**
   ```bash
   git clone https://github.com/your-username/RTAC.git
   cd RTAC
   ```

2. **Set up Python Environment**
   ```bash
   # Install Poetry if you haven't already
   curl -sSL https://install.python-poetry.org | python3 -
   
   # Install dependencies
   poetry install
   ```

3. **Set up Frontend**
   ```bash
   cd frontend
   npm install
   ```

4. **Configure Environment**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Run the Application**
   ```bash
   # Terminal 1 - Backend
   poetry run python main.py
   
   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

## 📋 Development Workflow

### 1. Choose an Issue

- Browse our [Issues](https://github.com/your-username/RTAC/issues) page
- Look for issues labeled with your skill level (easy, medium, hard)
- Comment on an issue to claim it
- Wait for maintainer approval

### 2. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-bug-fix
```

### 3. Make Your Changes

- Follow the coding standards below
- Write tests for new functionality
- Update documentation as needed

### 4. Test Your Changes

```bash
# Backend tests
poetry run pytest

# Frontend tests
cd frontend
npm run lint
npm run test
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new tool for event registration"
```

We follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New features
- `fix:` - Bug fixes
- `docs:` - Documentation changes
- `style:` - Code style changes (formatting, etc.)
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

### 6. Push and Create a Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request with:
- Clear description of changes
- Link to related issues
- Screenshots (if UI changes)
- Test results

## 🏗️ Project Structure

```
RTAC/
├── app/                    # Backend application
│   ├── agents/            # AI agent implementation
│   ├── api/               # FastAPI routes
│   ├── config/            # Configuration
│   ├── schemas/           # Pydantic models
│   └── services/          # Business logic
├── frontend/              # React application
├── data/                  # Event data files
├── docker/                # Docker configuration
├── scripts/               # Utility scripts
└── tests/                 # Test files
```

## 🛠️ Development Guidelines

### Backend (Python)

#### Code Style
- Follow PEP 8
- Use Black for formatting: `poetry run black .`
- Use isort for imports: `poetry run isort .`
- Use mypy for type checking: `poetry run mypy .`

#### Adding New Tools

1. Create a new file in `app/agents/tools/`
2. Follow the existing tool patterns
3. Register your tool in `app/agents/apiconf_agent.py`
4. Add tests in `tests/`

Example tool structure:
```python
from google.adk.tools import FunctionTool
from typing import Dict, Any

def my_tool_function(param: str, **kwargs) -> Dict[str, Any]:
    """Description of what this tool does."""
    # Your tool logic here
    return {
        "success": True,
        "result": "Your result"
    }

def get_my_tools() -> List[FunctionTool]:
    """Get tools for this module."""
    return [
        FunctionTool(
            name="my_tool",
            description="What this tool does",
            function=my_tool_function
        )
    ]
```

### Frontend (React/TypeScript)

#### Code Style
- Use ESLint and Prettier
- Follow React best practices
- Use TypeScript for type safety
- Write component tests

#### Adding New Components

1. Create component in `frontend/src/components/`
2. Add corresponding CSS module
3. Export from index if needed
4. Add tests

### Testing

#### Backend Tests
```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=app

# Run specific test file
poetry run pytest tests/test_agent.py
```

#### Frontend Tests
```bash
cd frontend
npm run test
npm run test:coverage
```

## 🎨 Design Guidelines

### UI/UX Principles
- **Accessibility First**: Ensure all features are accessible
- **Mobile Responsive**: Design for mobile-first
- **Consistent Design**: Follow existing design patterns
- **User-Friendly**: Intuitive and easy to use

### Design System
- Use existing CSS modules
- Follow the established color scheme
- Maintain consistent spacing and typography
- Use React Icons for consistency

## 📚 Documentation

### Writing Documentation
- Use clear, concise language
- Include code examples
- Add screenshots for UI changes
- Keep documentation up to date

### Documentation Types
- **API Documentation**: Update OpenAPI specs
- **User Guides**: Help users understand features
- **Developer Guides**: Help contributors understand the codebase
- **README Updates**: Keep main README current

## 🔧 Common Development Tasks

### Adding a New Tool

1. **Create the tool file**
   ```bash
   touch app/agents/tools/my_new_tool.py
   ```

2. **Implement the tool**
   ```python
   # Follow the tool template above
   ```

3. **Register the tool**
   ```python
   # In app/agents/apiconf_agent.py
   from app.agents.tools.my_new_tool import get_my_new_tools
   ```

4. **Add tests**
   ```bash
   touch tests/test_my_new_tool.py
   ```

### Adding a New API Endpoint

1. **Create the route**
   ```python
   # In app/api/v1/agents_router.py
   @router.post("/my-endpoint")
   async def my_endpoint(request: MyRequest):
       # Your endpoint logic
   ```

2. **Add the schema**
   ```python
   # In app/schemas/agents.py
   class MyRequest(BaseModel):
       field: str
   ```

3. **Add tests**
   ```python
   # In tests/test_api.py
   ```

### Adding Frontend Features

1. **Create component**
   ```bash
   touch frontend/src/components/MyComponent.tsx
   touch frontend/src/components/MyComponent.module.css
   ```

2. **Add to app**
   ```typescript
   // In App.tsx or relevant parent
   import MyComponent from './components/MyComponent'
   ```

3. **Add tests**
   ```bash
   touch frontend/src/components/__tests__/MyComponent.test.tsx
   ```

## 🐛 Bug Reports

When reporting bugs, please include:

1. **Environment details**
   - OS and version
   - Python version
   - Node.js version
   - Browser (if frontend issue)

2. **Steps to reproduce**
   - Clear, step-by-step instructions
   - Expected vs actual behavior

3. **Additional context**
   - Error messages
   - Screenshots
   - Console logs

## 💡 Feature Requests

When requesting features:

1. **Describe the problem**
   - What issue does this solve?
   - Who would benefit?

2. **Propose a solution**
   - How should it work?
   - Any technical considerations?

3. **Provide context**
   - Use cases
   - Mockups (if UI feature)

## 🏷️ Issue Labels

We use the following labels to categorize issues:

### Difficulty
- `easy` - Good for beginners
- `medium` - Some experience needed
- `hard` - Advanced skills required

### Type
- `documentation` - Documentation improvements
- `enhancement` - New features
- `bug` - Bug fixes
- `good first issue` - Perfect for newcomers
- `help wanted` - Needs community help

### Area
- `frontend` - React/TypeScript changes
- `backend` - Python/FastAPI changes
- `aiops` - AI/ML improvements
- `devops` - Infrastructure/deployment
- `design` - UI/UX improvements
- `testing` - Test improvements

## 🎉 Recognition

We appreciate all contributions! Contributors will be:

- Listed in our contributors file
- Mentioned in release notes
- Invited to join our community

## 📞 Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and ideas
- **Documentation**: Check our docs first
- **Community**: Join our community channels

## 📄 License

By contributing to RTAC, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for contributing to RTAC! 🎤✨**

*Together, we're making event organization more intelligent and accessible.* 