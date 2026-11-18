# GitHub Actions - Quick Start (5 Minutes)

## TL;DR - In 3 Steps

### 1️⃣ Create Repository
Go to https://github.com/new → Name: `agent_code_review` → Create

### 2️⃣ Push Code
```bash
git remote add origin https://github.com/YOUR_USERNAME/agent_code_review.git
git branch -M main
git push -u origin main
```

### 3️⃣ Done! 
Go to "Actions" tab on GitHub. Workflows run automatically. ✅

---

## What Gets Created

✅ 3 automated workflows  
✅ Runs on every push  
✅ Tests Python 3.9, 3.10, 3.11  
✅ Lint + test + coverage  
✅ API validation  
✅ Artifact downloads  
✅ Zero cost  

---

## File Locations

```
.github/workflows/
├── run-analysis.yml          ← Main pipeline
├── web-server-test.yml       ← Integration tests
├── simple-run.yml            ← Quick check
└── README.md                 ← Workflow reference
```

---

## View Results

1. Go to GitHub repository
2. Click "Actions" tab
3. See workflow runs
4. Click any run to see logs
5. Download artifacts

---

## Troubleshooting

**Workflows not showing?**
- Verify `.github/workflows/` directory pushed
- Wait 30 seconds
- Refresh page

**Workflow failed?**
- Click failed job
- Read error message
- Fix locally and push again

---

## Documentation

- **Setup**: GITHUB_SETUP_GUIDE.md (20 min read)
- **Details**: GITHUB_ACTIONS_SETUP.md (15 min read)  
- **Verify**: GITHUB_ACTIONS_CHECKLIST.md (10 min read)

---

## That's It!

Your workflows are now automated. Every push triggers tests and analysis.

✅ Ready to go! 🚀
