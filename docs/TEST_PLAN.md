# Test Plan

*Last updated: 2025-12-26*

Comprehensive testing strategy for braidMgr covering unit, integration, E2E, and demo recording.

---

## Test Distribution

| Type | Target % | Location | Purpose |
|------|----------|----------|---------|
| Unit | 80% | `backend/tests/unit/`, `frontend/src/**/*.test.ts` | Fast, isolated logic tests |
| Integration | 15% | `backend/tests/integration/` | Database and service integration |
| E2E | 5% | `frontend/e2e/` | Full user flows |

---

## Backend Testing

### Unit Tests

**Location**: `backend/tests/unit/`

**Framework**: pytest + pytest-asyncio

**Run**:
```bash
cd backend
pytest tests/unit -v
```

**Coverage areas**:
- [ ] Indicator calculation logic
- [ ] Budget calculations
- [ ] Date utilities
- [ ] Input validation
- [ ] Service business logic (mocked repositories)
- [ ] Auth token generation/validation

### Integration Tests

**Location**: `backend/tests/integration/`

**Requirements**: PostgreSQL running (Docker)

**Run**:
```bash
docker-compose up -d postgres
pytest tests/integration -v
```

**Coverage areas**:
- [ ] Repository CRUD operations
- [ ] Database constraints and triggers
- [ ] Transaction handling
- [ ] Soft delete behavior
- [ ] Query filtering and pagination

### API Tests

**Location**: `backend/tests/e2e/`

**Run**:
```bash
pytest tests/e2e -v
```

**Coverage areas**:
- [ ] Authentication endpoints (login, register, refresh)
- [ ] Project CRUD with RBAC
- [ ] Item CRUD with project scoping
- [ ] Workstream operations
- [ ] Error responses (401, 403, 404, 422)

---

## Frontend Testing

### Unit Tests

**Location**: `frontend/src/**/*.test.ts`

**Framework**: Vitest + React Testing Library

**Run**:
```bash
cd frontend
npm run test          # Watch mode
npm run test -- --run # Single run
npm run test:coverage # With coverage
```

**Current coverage**:
- [x] Auth context (5 tests)
- [x] LoginForm (7 tests)
- [x] RegisterForm (8 tests)
- [x] ForgotPasswordForm (7 tests)

**Planned coverage**:
- [ ] useItems hook
- [ ] useProjects hook
- [ ] ItemTable component
- [ ] ItemFilters component
- [ ] SummaryCard component
- [ ] Indicator utilities

### E2E Tests (BDD)

**Location**: `frontend/e2e/`

**Framework**: Playwright + playwright-bdd (Gherkin)

**Run**:
```bash
cd frontend
npx bddgen              # Generate tests from features
npm run test:e2e        # Run e2e tests
```

**Feature files**: `e2e/features/*.feature`
**Step definitions**: `e2e/steps/*.ts`

**Current coverage**:
- [x] Login scenarios (4 tests)
- [x] Dashboard navigation (7 tests)

**Planned scenarios**:
- [ ] Item CRUD operations
- [ ] Filtering and search
- [ ] Timeline interactions
- [ ] Chronology navigation
- [ ] Chat interface
- [ ] Multi-project navigation

---

## Test Users

| Email | Password | Role | Purpose |
|-------|----------|------|---------|
| `e2e-test@example.com` | `E2eTestPass123` | Admin | E2E automated tests |
| `demo@braidmgr.com` | `demo123` | Member | Demo recordings |
| `admin@northwind.com` | `admin123` | Admin | Manual testing |

---

## Test Data

### Seed Data

Located in `backend/scripts/` or created via YAML import:

**Organizations**:
- Northwind Industries (ID: `11111111-1111-1111-1111-111111111111`)

**Projects**:
- Website Modernization (ID: `22222222-2222-2222-2222-222222222222`)

**Workstreams**:
- Development, Testing, Deployment, Documentation

**Items**:
- 21 items across all BRAID types with various indicators

### Data Reset

```bash
# Reset database (removes all data)
docker-compose down -v
docker-compose up -d postgres

# Re-run migrations and seed
cd backend
python scripts/migrate.py
python scripts/import_yaml.py
```

---

## Demo Recording

### Purpose

Automated video capture for stakeholder demos and marketing.

### Run

```bash
cd frontend
npx playwright test tests/demo-walkthrough.spec.ts --project=demo-recording
```

### Output

Video: `test-results/demo-walkthrough-.../video.webm` (1920x1080)

### Demo Checklist

Before recording:
- [ ] Backend running on port 8000
- [ ] Frontend running on port 5173/5174
- [ ] Demo user exists with project access
- [ ] Project has 20+ items with varied indicators
- [ ] Project dates are current (not in the past)

### Demo Sections

1. Login page with branding
2. Project selection
3. Dashboard overview with BRAID cards
4. All Items table with filtering
5. Active Items severity grouping
6. Timeline view with zoom
7. Farewell screen

---

## CI/CD Integration

### Pre-commit

```bash
# Backend
cd backend
pytest tests/unit -v --tb=short

# Frontend
cd frontend
npm run lint
npm run test -- --run
```

### Pull Request

```yaml
# .github/workflows/test.yml (planned)
jobs:
  backend-tests:
    - pytest tests/unit
    - pytest tests/integration (with postgres service)

  frontend-tests:
    - npm run lint
    - npm run test -- --run
    - npm run test:e2e
```

### Pre-deploy

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] E2E smoke tests pass
- [ ] No TypeScript errors
- [ ] No ESLint errors

---

## Test Environments

| Environment | Database | Backend | Frontend |
|-------------|----------|---------|----------|
| Local | localhost:5434 | localhost:8000 | localhost:5173 |
| E2E | localhost:5434 | localhost:8000 | localhost:5174 |
| Docker | postgres:5432 | api:8000 | frontend:5173 |

---

## Known Issues

| Issue | Impact | Workaround |
|-------|--------|------------|
| Auth token in memory | E2E tests lose auth on page reload | Use client-side navigation |
| WebSocket in tests | Chat tests need special handling | Use REST fallback |

---

## Test Maintenance

### Adding New Tests

1. **Unit test**: Create `*.test.ts` next to source file
2. **Integration test**: Add to `tests/integration/` with DB fixtures
3. **E2E test**: Create `.feature` file, add step definitions, run `npx bddgen`

### Updating Demo

1. Edit `tests/demo-walkthrough.spec.ts`
2. Update narration text and timing
3. Run demo recording to verify
4. Check video output before committing

---

## Related Documents

- [Testing Patterns](patterns/testing.md) - Test templates and fixtures
- [Frontend Architecture](architecture/frontend.md) - Component testing info
- [AI Integration](architecture/ai-integration.md) - Chat testing considerations
