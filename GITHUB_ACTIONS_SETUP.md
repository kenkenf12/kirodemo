# GitHub Actions Workflow Setup Guide

## Overview

GitHub Actions workflows have been created to automatically run your Python scripts on push events. This guide explains how to set them up and use them.

---

## Created Workflows

### 1. **run-analysis.yml** - Full Analysis Pipeline
**Location**: `.github/workflows/run-analysis.yml`

**Triggers on:**
- Push to main, master, develop branches
- Changes to Python files or log files

**What it does:**
- Lints code with Pylint
- Checks code style with Flake8
- Runs unit tests with pytest
- Generates coverage reports
- Runs log analysis script
- Uploads artifacts
- Comments on PRs

**Matrix testing:** Python 3.9, 3.10, 3.11

---

### 2. **web-server-test.yml** - Web Server Integration Tests
**Location**: `.github/workflows/web-server-test.yml`

**Triggers on:**
- Push to main, master, develop branches
- Pull requests

**What it does:**
- Sets up test environment
- Creates test log files
- Starts web server
- Tests API endpoints
- Validates responses
- Generates test results

**Tests:**
- /api/login endpoint
- /api/status endpoint
- /api/reports endpoint

---

### 3. **simple-run.yml** - Basic Script Execution
**Location**: `.github/workflows/simple-run.yml`

**Triggers on:**
- Any push
- Any pull request

**What it does:**
- Runs log analyzer
- Executes tests
- Creates execution summary

**Best for:** Quick validation

---

## Quick Setup

### Step 1: Push to GitHub

First, make sure your repository is on GitHub:

```bash
git remote add origin https://github.com/YOUR_USERNAME/agent_code_review.git
git branch -M main
git push -u origin main
```

### Step 2: Verify Workflows

After pushing, GitHub automatically detects the workflows:

1. Go to your GitHub repository
2. Click "Actions" tab
3. You should see the workflows listed

### Step 3: Workflows Run Automatically

The workflows will run automatically on:
- Every push to main/master/develop
- Every pull request

---

## Viewing Workflow Results

### On GitHub

1. **Go to Actions tab** → See all workflow runs
2. **Click a workflow run** → See detailed logs
3. **Click a job** → See step-by-step output
4. **Check artifacts** → Download test reports

### Artifact Types Generated

- `analysis-reports-py3.x` - Analysis reports per Python version
- `web-server-test-results` - Web server test results
- `execution-summary` - Simple run summary

---

## Workflow Files Explained

### File Structure

```
.github/
└── workflows/
    ├── run-analysis.yml          (Full pipeline)
    ├── web-server-test.yml       (Integration tests)
    └── simple-run.yml            (Basic run)
```

### Each Workflow File Contains

```yaml
name: Workflow Name                    # Display name

on:                                    # Trigger events
  push:
    branches: [ main, develop ]
    paths: [ '**.py' ]

jobs:                                  # Jobs to run
  job-name:
    runs-on: ubuntu-latest             # OS to run on
    
    steps:                             # Steps in job
      - name: Step name
        run: command
```

---

## Customizing Workflows

### Edit a Workflow

1. Open `.github/workflows/run-analysis.yml`
2. Make changes
3. Push to GitHub
4. Changes take effect immediately

### Common Customizations

#### Change Python versions

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']  # Add 3.12
```

#### Change trigger branches

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add staging
```

#### Add new script to run

```yaml
- name: Run my script
  run: |
    python my_script.py --option value
```

#### Run only on specific path changes

```yaml
on:
  push:
    paths:
      - 'web_app.py'
      - 'synthesis_agent.py'
```

---

## Workflow YAML Breakdown

### run-analysis.yml

```yaml
name: Run Security Analysis on Push
# Display name shown in Actions tab

on:
  push:
    branches: [ main, master, develop ]  # Branches to trigger on
    paths:                                # Paths to trigger on
      - '**.py'                           # Any Python file
      - '**.log'                          # Any log file
      - '.github/workflows/run-analysis.yml'  # This file

jobs:
  security-analysis:                     # Job name
    runs-on: ubuntu-latest               # OS: ubuntu-latest, windows-latest, macos-latest
    
    strategy:
      matrix:
        python-version: ['3.9', '3.10', '3.11']  # Test 3 Python versions
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4        # GitHub action (built-in)
      
      - name: Set up Python
        uses: actions/setup-python@v4    # Set up Python
        with:
          python-version: ${{ matrix.python-version }}  # Use matrix value
          cache: 'pip'                   # Cache pip packages
      
      - name: Install dependencies
        run: |                           # Bash commands
          python -m pip install --upgrade pip
          pip install pytest pylint flake8 coverage
      
      - name: Lint with Pylint
        run: pylint web_app.py --exit-zero  # Run pylint
        continue-on-error: true          # Don't fail on error
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3  # Upload to codecov.io
        with:
          file: ./coverage.xml
        continue-on-error: true
```

---

## Common Actions Used

### Checkout Code
```yaml
- uses: actions/checkout@v4
```
Downloads your repository code

### Set up Python
```yaml
- uses: actions/setup-python@v4
  with:
    python-version: '3.11'
```
Installs specified Python version

### Upload Artifacts
```yaml
- uses: actions/upload-artifact@v3
  with:
    name: my-artifacts
    path: output/
```
Stores files from workflow for download

### Create Comments
```yaml
- uses: actions/github-script@v7
  with:
    script: |
      github.rest.issues.createComment({...})
```
Comments on PRs with results

---

## Workflow Examples

### Example 1: Run Only on main Branch

```yaml
on:
  push:
    branches: [ main ]  # Only main branch
```

### Example 2: Run on Schedule

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  push:
    branches: [ main ]
```

### Example 3: Run Only on Specific Files

```yaml
on:
  push:
    paths:
      - 'web_app.py'
      - 'synthesis_agent.py'
      - 'tests/**'
```

### Example 4: Different Jobs for Different Tasks

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Run tests
        run: pytest
  
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Lint code
        run: pylint *.py
  
  deploy:
    runs-on: ubuntu-latest
    needs: [test, lint]  # Wait for test and lint to pass
    steps:
      - name: Deploy
        run: ./deploy.sh
```

---

## Troubleshooting

### Workflows Not Running

**Problem**: Workflows don't run automatically

**Solutions**:
1. Check workflows are in `.github/workflows/` directory
2. Verify file names end with `.yml` or `.yaml`
3. Check workflow YAML syntax (use [validator](https://github.com/rhysd/actionlint))
4. Ensure you pushed `.github/workflows/` directory

### Workflow Fails

**Problem**: Workflow run shows red X

**Solutions**:
1. Click on failed job to see logs
2. Check error messages in step output
3. Verify Python dependencies are installed
4. Check file paths are correct
5. Ensure commands work locally first

### Can't Find Artifacts

**Problem**: Artifacts not available

**Solutions**:
1. Check workflow completed successfully
2. Click "Artifacts" on workflow run page
3. Artifacts expire after 90 days by default
4. Verify steps that upload artifacts ran

---

## Best Practices

### ✅ DO

- Use `continue-on-error: true` for non-critical steps
- Cache dependencies with `cache: 'pip'`
- Use matrix for multiple Python versions
- Upload test reports as artifacts
- Add meaningful step names
- Use specific action versions (@v3, @v4)

### ❌ DON'T

- Commit secrets to repository
- Use `always()` unless necessary
- Have very long workflows (keep < 2 hours)
- Hardcode file paths (use variables)
- Forget to add required dependencies

---

## Advanced Features

### Environment Variables

```yaml
env:
  PYTHONUNBUFFERED: 1
  LOG_LEVEL: INFO

steps:
  - name: Run script
    run: python script.py
    env:
      OUTPUT_DIR: /tmp/output
```

### Conditional Steps

```yaml
- name: Comment on PR
  if: github.event_name == 'pull_request'
  run: echo "This runs only on PRs"

- name: Run on main only
  if: github.ref == 'refs/heads/main'
  run: echo "This runs only on main"
```

### Strategy Matrix

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, windows-latest, macos-latest]
    python-version: ['3.9', '3.10', '3.11']
# Runs on all combinations (3x3 = 9 jobs)
```

### Secrets

```yaml
- name: Deploy
  run: deploy.sh
  env:
    API_KEY: ${{ secrets.API_KEY }}
    # Add secrets in GitHub repo settings
```

---

## GitHub Repository Setup

### Enable Actions (Usually Enabled by Default)

1. Go to repository Settings
2. Click "Actions" → "General"
3. Ensure "Allow all actions and reusable workflows" is selected

### Add Secrets (If Needed)

1. Go to repository Settings
2. Click "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Add secret name and value

---

## Monitoring Workflows

### GitHub Dashboard

1. Go to "Actions" tab
2. See all workflow runs
3. Click any run for details
4. Check logs for each step

### Notifications

- GitHub sends email notifications on workflow failure
- Can configure in repository settings
- Check "Actions" tab for status

### Badge

Add workflow status badge to README:

```markdown
[![Run Security Analysis](https://github.com/YOUR_USERNAME/agent_code_review/actions/workflows/run-analysis.yml/badge.svg)](https://github.com/YOUR_USERNAME/agent_code_review/actions)
```

---

## Next Steps

### 1. Push to GitHub

```bash
git push origin main
```

### 2. Go to Actions Tab

View workflow runs in GitHub UI

### 3. Monitor Results

- Check logs
- Download artifacts
- Review test coverage

### 4. Customize

Edit workflows as needed for your project

---

## Quick Reference

| Task | Command |
|------|---------|
| Push changes | `git push origin main` |
| View workflows | GitHub → Actions tab |
| Check logs | Click workflow run → job → step |
| Download artifacts | Click workflow run → Artifacts |
| Edit workflow | Edit `.github/workflows/*.yml` |

---

## File Locations

```
Your Repository
├── .github/
│   └── workflows/
│       ├── run-analysis.yml         ← Full pipeline
│       ├── web-server-test.yml      ← Integration tests
│       └── simple-run.yml           ← Basic run
├── web_app.py
├── synthesis_agent.py
├── log_analyzer.py
├── log_monitor.py
└── test_monitor.py
```

---

## Support & Resources

### Official Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Available Actions](https://github.com/marketplace?type=actions)

### Validation
- [ActionLint](https://github.com/rhysd/actionlint) - Lint workflow files
- [Workflow Validator](https://github.com/actions/starter-workflows) - Check syntax

### Community
- GitHub Discussions
- Stack Overflow `github-actions` tag
- GitHub Community Forum

---

## Summary

**You now have 3 workflows:**

1. ✅ `run-analysis.yml` - Full analysis with testing and coverage
2. ✅ `web-server-test.yml` - Web server integration tests
3. ✅ `simple-run.yml` - Basic script execution

**Workflows automatically run on:**
- Every push to main/master/develop
- Every pull request

**Results visible in:**
- GitHub Actions tab
- Artifacts for download
- PR comments

**Cost:** FREE (GitHub provides 2,000 free Action minutes per month)

---

**Ready to use! Push your code to GitHub and workflows start automatically.** 🚀
