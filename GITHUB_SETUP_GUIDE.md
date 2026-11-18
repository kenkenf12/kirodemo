# Complete GitHub Setup Guide

**Goal**: Push your Python project to GitHub with automatic workflows

---

## What You Get

✅ **3 Automated Workflows** that run on every push:
- Full analysis pipeline (lint, test, coverage)
- Web server integration tests
- Simple script execution

✅ **Automatic Testing** across Python versions

✅ **Artifact Downloads** with test reports and analysis results

✅ **Zero Cost** (GitHub provides 2,000 free minutes/month)

---

## Step-by-Step Setup

### 1️⃣ Prepare Your Local Repository

```bash
# Navigate to your project
cd c:\Users\kenke\agent_code_review

# Initialize git (if not done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit: Multi-agent security system with GitHub Actions"

# Rename branch to main (if on master)
git branch -M main
```

### 2️⃣ Create GitHub Repository

1. Go to **https://github.com/new**
2. Fill in details:
   - **Repository name**: `agent_code_review`
   - **Description**: Multi-Agent Security Monitoring System
   - **Public/Private**: Choose based on preference
   - **Initialize repo**: Leave UNCHECKED (don't add README/gitignore)
3. Click **"Create repository"**

### 3️⃣ Connect Local to GitHub

```bash
# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/agent_code_review.git

# Verify remote
git remote -v
# Should show:
# origin  https://github.com/YOUR_USERNAME/agent_code_review.git (fetch)
# origin  https://github.com/YOUR_USERNAME/agent_code_review.git (push)

# Push to GitHub
git push -u origin main
```

### 4️⃣ Verify Workflows

1. Go to your GitHub repository
2. Click **"Actions"** tab
3. You should see 3 workflows:
   - ✅ Run Security Analysis on Push
   - ✅ Web Server Integration Tests
   - ✅ Simple Python Script Run

### 5️⃣ Test Workflow Trigger

Make a small change to test:

```bash
# Make a change
echo "# Updated" >> README.md

# Commit and push
git add README.md
git commit -m "Test workflow trigger"
git push
```

Then:
1. Go to **Actions** tab on GitHub
2. Watch workflows run
3. Click on a running workflow to see logs
4. Wait for completion
5. Download artifacts

---

## Workflow Files Location

All workflow files are in your project:

```
Your Local Project
├── .github/
│   └── workflows/
│       ├── run-analysis.yml          ← Main analysis pipeline
│       ├── web-server-test.yml       ← Web server tests
│       ├── simple-run.yml            ← Basic validation
│       └── README.md                 ← Workflow info
│
├── web_app.py
├── synthesis_agent.py
├── log_analyzer.py
├── log_monitor.py
├── test_monitor.py
│
└── GITHUB_ACTIONS_SETUP.md          ← Detailed guide
```

---

## Understanding the Workflows

### Workflow 1: run-analysis.yml

**Triggers on**:
- Push to `main`, `master`, `develop` branches
- Changes to `.py` or `.log` files

**What it does**:
```
1. Checkout code
2. Set up Python 3.9, 3.10, 3.11 (matrix)
3. Install dependencies
4. Lint with Pylint
5. Check style with Flake8
6. Run tests with pytest
7. Generate coverage report
8. Run log analysis script
9. Upload artifacts
10. Comment on PR if applicable
```

**Artifacts generated**:
- `analysis-reports-py3.9.zip`
- `analysis-reports-py3.10.zip`
- `analysis-reports-py3.11.zip`

### Workflow 2: web-server-test.yml

**Triggers on**:
- Push to `main`, `master`, `develop` branches
- Any pull request

**What it does**:
```
1. Checkout code
2. Set up Python
3. Create test directories
4. Create test log file
5. Start web server
6. Test API endpoints:
   - /api/login
   - /api/status
   - /api/reports
7. Generate test results
8. Upload results
```

**Artifacts generated**:
- `web-server-test-results/test_results.txt`

### Workflow 3: simple-run.yml

**Triggers on**:
- Any push
- Any pull request

**What it does**:
```
1. Checkout code
2. Set up Python
3. Run log analyzer --help
4. Run tests
5. Create summary
6. Upload summary
```

**Artifacts generated**:
- `execution-summary/summary.txt`

---

## Customizing Workflows

### Change Trigger Branches

Edit `.github/workflows/run-analysis.yml`:

```yaml
# Before
on:
  push:
    branches: [ main, master, develop ]

# After (only main)
on:
  push:
    branches: [ main ]
```

Then:
```bash
git add .github/workflows/run-analysis.yml
git commit -m "Update workflow to trigger on main only"
git push
```

### Add New Python Version

Edit `.github/workflows/run-analysis.yml`:

```yaml
# Before
matrix:
  python-version: ['3.9', '3.10', '3.11']

# After (add 3.12)
matrix:
  python-version: ['3.9', '3.10', '3.11', '3.12']
```

### Add New Step

Edit any workflow, add:

```yaml
- name: My custom step
  run: |
    python my_script.py
    echo "Done!"
  continue-on-error: true
```

### Run on Schedule

Add to workflow `on:` section:

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM UTC
  push:
    branches: [ main ]
```

---

## Monitoring Workflows

### View on GitHub

1. Go to **Actions** tab
2. See all workflow runs
3. Click any run to see details
4. Click job to see steps
5. Check artifacts for downloads

### Workflow Status

- 🟢 **Green checkmark** = All jobs passed
- 🔴 **Red X** = One or more jobs failed
- 🟡 **Yellow circle** = Still running

### Download Artifacts

1. Click workflow run
2. Scroll to "Artifacts" section
3. Click download button
4. Unzip files locally

### Troubleshooting Failed Workflows

1. Click failed workflow
2. Click failed job
3. Click failed step
4. See error message
5. Fix issue locally and push

---

## Example: First Workflow Run

### Step 1: Push to GitHub
```bash
git push origin main
```

### Step 2: Go to GitHub
- Open https://github.com/YOUR_USERNAME/agent_code_review
- Click "Actions" tab

### Step 3: Watch Workflow
- See workflows running (yellow circle)
- Wait for completion (5-10 minutes typical)
- See green checkmark when done

### Step 4: Review Results
- Click on completed workflow
- See all jobs with ✅
- Click "Artifacts" section
- Download reports

### Step 5: View Locally
- Unzip downloaded file
- Open JSON/text reports
- Review analysis results

---

## Advanced: GitHub Settings

### Enable Branch Protection

1. Go to repository **Settings**
2. Click **Branches** → **Add rule**
3. Branch name: `main`
4. Check "Require status checks to pass before merging"
5. Select all workflow jobs
6. Save

**Effect**: PRs must have passing workflows before merge

### Add Secrets (If Needed)

1. Go to **Settings** → **Secrets and variables** → **Actions**
2. Click **New repository secret**
3. Add secret name and value
4. Use in workflow: `${{ secrets.SECRET_NAME }}`

### Email Notifications

1. Go to **Settings** → **Notifications**
2. Check "Email" for workflow failures
3. Choose frequency
4. Save

---

## Helpful Commands

### Push Changes
```bash
git add .
git commit -m "Your message"
git push origin main
```

### Check Remote
```bash
git remote -v
```

### View Log
```bash
git log --oneline -5
```

### Create Branch for Experimentation
```bash
git checkout -b experiment
# Make changes
git push -u origin experiment
# Create PR on GitHub
```

---

## Tips & Best Practices

### ✅ DO

- Commit regularly
- Write meaningful commit messages
- Test locally before pushing
- Review workflow logs
- Download and review artifacts
- Keep workflows simple and focused

### ❌ DON'T

- Commit secrets to repository
- Disable branch protection
- Ignore failed workflows
- Push to main without testing
- Commit large binary files

---

## Cost Breakdown

| Item | Cost |
|------|------|
| GitHub repository | Free |
| Workflows per month | 2,000 free minutes |
| Artifact storage | Free (90 days) |
| Total monthly cost | **FREE** |

---

## Common Questions

### Q: How often do workflows run?
**A**: Every time you push changes to trigger branches

### Q: Can I change when workflows run?
**A**: Yes! Edit the `on:` section in workflow files

### Q: Where do I see workflow results?
**A**: Actions tab → Click workflow run → View logs and artifacts

### Q: How long do workflows keep artifacts?
**A**: 90 days by default (can be configured)

### Q: Can I run workflows manually?
**A**: Yes! If you add `workflow_dispatch` to the `on:` section

### Q: What if a workflow fails?
**A**: Click the failing job to see error logs, fix issue, push again

### Q: Do I need special permissions?
**A**: No! Workflows use standard GitHub Actions permissions

### Q: Can multiple people use workflows?
**A**: Yes! All team members can see and trigger workflows

---

## Next Steps

### 1. Basic Setup ✅
- [ ] Create GitHub account
- [ ] Create repository
- [ ] Push code
- [ ] Verify workflows appear

### 2. First Test Run ✅
- [ ] Trigger workflow by pushing
- [ ] Watch it run
- [ ] Review results
- [ ] Download artifacts

### 3. Customization ✅
- [ ] Update workflow triggers
- [ ] Add Python versions
- [ ] Modify test steps
- [ ] Push changes

### 4. Team Setup ✅
- [ ] Add collaborators
- [ ] Share workflow guide
- [ ] Set branch protection
- [ ] Configure notifications

### 5. Maintenance ✅
- [ ] Monitor workflow runs
- [ ] Fix failing tests
- [ ] Update dependencies
- [ ] Review coverage reports

---

## Resources

### Official Documentation
- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Creating Workflows](https://docs.github.com/en/actions/quickstart)

### Validation Tools
- [ActionLint](https://github.com/rhysd/actionlint) - Lint workflows
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=GitHub.vscode-github-actions) - Workflow editor

### Community Help
- GitHub Discussions
- Stack Overflow `github-actions` tag
- GitHub Community Forum

---

## Troubleshooting

### Workflows Don't Show Up

**Check**:
1. Are files in `.github/workflows/`?
2. Do files end with `.yml` or `.yaml`?
3. Is syntax correct (YAML indentation)?
4. Did you push the `.github/` directory?

**Fix**:
```bash
# Verify files
ls -la .github/workflows/

# Push if missing
git add .github/
git commit -m "Add workflows"
git push
```

### Workflow Fails

**Check**:
1. Click failed job
2. Click failed step
3. Read error message
4. Test locally: `python script.py`

**Fix**:
1. Fix issue locally
2. Test locally
3. Commit and push
4. Workflow runs again

### Can't Download Artifacts

**Check**:
1. Did workflow complete?
2. Is there an "Artifacts" section?
3. Have artifacts expired (>90 days)?

**Fix**:
1. Run workflow again
2. Download immediately
3. Configure artifact retention

---

## Summary

### You Now Have:

✅ 3 automated workflows  
✅ Tests on every push  
✅ Coverage reports  
✅ Artifact downloads  
✅ API validation  
✅ Zero cost  
✅ Full documentation  

### Ready to:

✅ Push to GitHub  
✅ Monitor workflows  
✅ Share with team  
✅ Deploy with confidence  

---

## Files You Need

```
✅ .github/workflows/run-analysis.yml
✅ .github/workflows/web-server-test.yml
✅ .github/workflows/simple-run.yml
✅ .github/workflows/README.md
✅ GITHUB_ACTIONS_SETUP.md
✅ GITHUB_ACTIONS_CHECKLIST.md
```

All files are already created! ✨

---

**You're all set! Push to GitHub and workflows start automatically.** 🚀

See `GITHUB_ACTIONS_CHECKLIST.md` for verification steps.
