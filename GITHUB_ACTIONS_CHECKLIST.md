# GitHub Actions Setup Checklist

## Pre-Deployment Steps

### Step 1: Prepare Your Repository

- [ ] Initialize git in project directory
  ```bash
  git init
  ```

- [ ] Add all files
  ```bash
  git add .
  ```

- [ ] Make initial commit
  ```bash
  git commit -m "Initial commit: Multi-agent security monitoring system"
  ```

- [ ] Rename branch to main (if needed)
  ```bash
  git branch -M main
  ```

### Step 2: Create GitHub Repository

- [ ] Go to [github.com/new](https://github.com/new)
- [ ] Create new repository
  - Repository name: `agent_code_review`
  - Description: Multi-Agent Security Monitoring System
  - Public or Private: Choose based on preference
  - DO NOT initialize with README, gitignore, license
- [ ] Click "Create repository"

### Step 3: Connect Local to GitHub

- [ ] Add remote origin
  ```bash
  git remote add origin https://github.com/YOUR_USERNAME/agent_code_review.git
  ```

- [ ] Push to GitHub
  ```bash
  git push -u origin main
  ```

### Step 4: Verify Workflows

- [ ] Go to GitHub repository
- [ ] Click "Actions" tab
- [ ] You should see 3 workflows listed:
  - [ ] Run Security Analysis on Push
  - [ ] Web Server Integration Tests
  - [ ] Simple Python Script Run

### Step 5: First Workflow Run

- [ ] Make a small change to a .py file
  ```bash
  # Example: add a comment to web_app.py
  ```

- [ ] Commit and push
  ```bash
  git add .
  git commit -m "Test workflow trigger"
  git push
  ```

- [ ] Go to Actions tab
- [ ] You should see workflows starting to run

### Step 6: Monitor Results

- [ ] Click on the running workflow
- [ ] Watch the jobs execute
- [ ] Check "Artifacts" after completion
- [ ] Download and review reports

## Workflow Details

### Run Security Analysis

**File**: `.github/workflows/run-analysis.yml`

**Configuration**:
- [ ] Triggers on: push to main/master/develop
- [ ] Triggers on: changes to .py and .log files
- [ ] Tests: Python 3.9, 3.10, 3.11
- [ ] Artifacts: analysis-reports-py*.zip

**Review**:
- [ ] Check pylint output
- [ ] Check flake8 style warnings
- [ ] Review test coverage
- [ ] Download analysis reports

### Web Server Tests

**File**: `.github/workflows/web-server-test.yml`

**Configuration**:
- [ ] Triggers on: push and pull requests
- [ ] Starts web server
- [ ] Tests 3 API endpoints
- [ ] Artifacts: web-server-test-results

**Review**:
- [ ] Check API response codes
- [ ] Verify login works
- [ ] Check reports endpoint

### Simple Run

**File**: `.github/workflows/simple-run.yml`

**Configuration**:
- [ ] Triggers on: any push, any pull request
- [ ] Quick validation
- [ ] Artifacts: execution-summary

**Review**:
- [ ] Check script runs without errors
- [ ] Review execution summary

## Customization Options

### Change Trigger Branches

Edit `.github/workflows/run-analysis.yml`:

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add/remove branches
```

- [ ] Update branch names
- [ ] Commit changes
- [ ] Push to GitHub

### Change Python Versions

Edit `.github/workflows/run-analysis.yml`:

```yaml
strategy:
  matrix:
    python-version: ['3.9', '3.10', '3.11', '3.12']  # Add 3.12
```

- [ ] Add/remove Python versions
- [ ] Commit changes
- [ ] Push to GitHub

### Add More Tests

Edit any workflow file:

```yaml
- name: Run my test
  run: |
    python my_test.py
  continue-on-error: true
```

- [ ] Add new steps
- [ ] Commit changes
- [ ] Push to GitHub

### Change Schedule

Add scheduled trigger:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  push:
    branches: [ main ]
```

- [ ] Choose schedule (cron format)
- [ ] Add to workflow
- [ ] Commit changes
- [ ] Push to GitHub

## Common Issues & Solutions

### Workflow Not Running

**Symptom**: No workflows appear in Actions tab

**Checklist**:
- [ ] Files are in `.github/workflows/` directory
- [ ] File names end with `.yml` or `.yaml`
- [ ] YAML syntax is correct (check indentation)
- [ ] Pushed `.github/` directory to GitHub
- [ ] Waited 30 seconds for workflows to sync

**Solution**:
```bash
# Verify files exist locally
ls -la .github/workflows/

# Push if missing
git add .github/
git commit -m "Add GitHub Actions workflows"
git push
```

### Workflow Fails

**Symptom**: Red X on workflow run

**Checklist**:
- [ ] Click on failed job to see logs
- [ ] Check error message in step output
- [ ] Verify Python dependencies installed
- [ ] Check file paths correct
- [ ] Run command locally to test

**Solution**:
```bash
# Test locally first
python web_app.py --help
pytest test_monitor.py
python log_analyzer.py --help
```

### Artifacts Not Found

**Symptom**: Can't download artifacts

**Checklist**:
- [ ] Workflow completed successfully
- [ ] Clicked "Artifacts" on workflow run page
- [ ] Artifacts not expired (90 day limit)
- [ ] Upload step actually ran

**Solution**:
- Run workflow again
- Check upload artifact steps in workflow

### Python Version Mismatch

**Symptom**: "python" command not found

**Checklist**:
- [ ] Workflow includes `Set up Python` step
- [ ] Python version is valid (3.8+)
- [ ] Using `python` not `python3` command

**Solution**:
Edit workflow to add Python setup:
```yaml
- name: Set up Python
  uses: actions/setup-python@v4
  with:
    python-version: '3.11'
```

## Features Checklist

### Core Workflows
- [ ] Run Security Analysis workflow created
- [ ] Web Server Tests workflow created
- [ ] Simple Run workflow created

### Triggers
- [ ] Workflows trigger on push
- [ ] Workflows trigger on pull requests
- [ ] Workflows trigger on file changes

### Testing
- [ ] Unit tests run
- [ ] Code linting runs
- [ ] Style checks run
- [ ] Coverage reports generated

### Artifacts
- [ ] Test reports uploaded
- [ ] Analysis results saved
- [ ] Can download artifacts

### Documentation
- [ ] `.github/workflows/README.md` created
- [ ] `GITHUB_ACTIONS_SETUP.md` created
- [ ] This checklist created

## Post-Setup Verification

### Test Workflow Execution

- [ ] Make a commit
- [ ] Push to GitHub
- [ ] Go to Actions tab
- [ ] See workflows running
- [ ] Wait for completion
- [ ] Check results
- [ ] Review artifacts

### Add Badge to README

Add to `README.md`:

```markdown
## CI/CD Status

[![Run Security Analysis](https://github.com/YOUR_USERNAME/agent_code_review/actions/workflows/run-analysis.yml/badge.svg)](https://github.com/YOUR_USERNAME/agent_code_review/actions)

[![Web Server Tests](https://github.com/YOUR_USERNAME/agent_code_review/actions/workflows/web-server-test.yml/badge.svg)](https://github.com/YOUR_USERNAME/agent_code_review/actions)

[![Simple Run](https://github.com/YOUR_USERNAME/agent_code_review/actions/workflows/simple-run.yml/badge.svg)](https://github.com/YOUR_USERNAME/agent_code_review/actions)
```

- [ ] Replace YOUR_USERNAME
- [ ] Commit changes
- [ ] Push to GitHub
- [ ] Verify badges display

## Final Steps

### Enable Notifications

1. [ ] Go to GitHub Settings
2. [ ] Click "Notifications"
3. [ ] Check "Email" for workflow failures
4. [ ] Choose frequency

### Create Issue for Workflow Setup

- [ ] Optional: Create GitHub issue to track workflow setup
- [ ] Document any customizations made
- [ ] Link to workflow runs

### Team Communication

- [ ] Share workflow documentation with team
- [ ] Explain what workflows do
- [ ] Show how to monitor results
- [ ] Provide troubleshooting guide

## Success Criteria

✅ All items checked = Workflows are properly set up!

### You know it's working when:

1. ✅ Workflows appear in Actions tab
2. ✅ Workflows trigger on push
3. ✅ Jobs complete successfully
4. ✅ Artifacts are generated
5. ✅ Can download and view results
6. ✅ Tests pass
7. ✅ Code style passes
8. ✅ No errors in logs

## Maintenance

### Weekly
- [ ] Check Actions tab for failed runs
- [ ] Fix any failing tests
- [ ] Review new warnings

### Monthly
- [ ] Review workflow performance
- [ ] Check for Python version updates
- [ ] Update dependencies if needed

### As Needed
- [ ] Add new tests
- [ ] Modify triggers
- [ ] Customize workflows
- [ ] Update documentation

## Next Steps

Once workflows are running:

1. [ ] Share with team
2. [ ] Document in project wiki
3. [ ] Add to onboarding docs
4. [ ] Set up Codecov integration (optional)
5. [ ] Add badges to README
6. [ ] Monitor and maintain

---

**Status**: Ready to deploy! ✅

Use this checklist to verify each step is complete.
