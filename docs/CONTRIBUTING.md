# Contributing Guidelines

We welcome contributions to the Empty Return Load Optimizer monorepo!

## Development Setup

1. **Clone repository**:
   ```bash
   git clone https://github.com/your-org/empty-return-load-optimizer.git
   cd empty-return-load-optimizer
   ```

2. **Engine Development**:
   ```bash
   cd engine
   pip install -e .[dev]
   pytest -v
   ```

3. **Backend Development**:
   ```bash
   cd backend
   pip install -e .[dev]
   pytest -v
   uvicorn app.main:app --reload --port 8000
   ```

4. **Frontend Development**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Pull Request Checklist
* All unit tests pass in `/engine` (`pytest`) and `/backend` (`pytest`).
* Code follows PEP 8 standards for Python and ESLint standards for React.
* New matching features include engine test coverage.
