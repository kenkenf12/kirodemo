# GitHub Actions Workflows

This directory contains automated workflows that run on GitHub.

## Workflows

### 1. run-analysis.yml
**Full Security Analysis Pipeline**
- Lints code with Pylint
- Checks style with Flake8
- Runs tests with pytest
- Generates coverage reports
- Runs log analysis
- Tests across Python 3.9, 3.10, 3.11

**Triggers on:** Push to main/master/develop, changes to .py/.log files

**Artifacts:** Analysis reports, coverage data

### 2. web-server-test.yml
**Web Server Integration Tests**
- Starts web server
- Tests API endpoints
- Validates responses
- Tests login, status, reports endpoints

**Triggers on:** Push, Pull Requests

**Artifacts:** Test results

### 3. simple-run.yml
**Simple Python Script Execution**
- Runs log analyzer
- Executes tests
- Creates summary

**Triggers on:** Any push, any pull request

**Artifacts:** Execution summary

## Quick Setup

1. Push code to GitHub
2. Go to Actions tab
3. Workflows run automatically
4. Check results and artifacts

## Customization

Edit any `.yml` file to customize:
- Python versions
- Trigger branches
- Additional steps
- Environment variables

See `GITHUB_ACTIONS_SETUP.md` for detailed guide.

## Cost

FREE - GitHub provides 2,000 free Action minutes per month per account
