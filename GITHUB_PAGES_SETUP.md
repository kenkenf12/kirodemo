# GitHub Pages Publishing Setup Guide

## Overview

Automatically publish your generated HTML reports to GitHub Pages on every push!

---

## What This Workflow Does

✅ Generates test coverage reports  
✅ Creates HTML dashboards  
✅ Generates analysis reports  
✅ Publishes to GitHub Pages  
✅ Updates on every push  
✅ Creates shareable links  

---

## Quick Setup

### Step 1: Enable GitHub Pages

1. Go to your repository **Settings**
2. Click **Pages** (left sidebar)
3. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
4. Save

### Step 2: Push the Workflow

```bash
# The workflow file is already created at:
# .github/workflows/publish-to-pages.yml

git add .github/workflows/publish-to-pages.yml
git commit -m "Add GitHub Pages publishing workflow"
git push origin main
```

### Step 3: Verify Deployment

1. Go to repository **Actions** tab
2. Find workflow: "Publish Reports to GitHub Pages"
3. Wait for completion (check mark ✅)
4. Go to **Settings** → **Pages**
5. See your live site URL

### Step 4: Access Your Reports

Visit your GitHub Pages URL:
```
https://YOUR_USERNAME.github.io/agent_code_review/
```

---

## Workflow Details

### File Location
```
.github/workflows/publish-to-pages.yml
```

### Triggers
- **Push** to main, master, develop branches
- **Manual trigger** (workflow_dispatch button)
- **Python file changes**

### What Gets Generated

**reports/** directory contains:
```
reports/
├── index.html              ← Main dashboard
├── test_results.json       ← Test data
├── coverage/
│   ├── index.html          ← Coverage HTML
│   └── summary.txt         ← Coverage text
└── analysis/
    └── report.html         ← Analysis report
```

### Two Jobs

**Job 1: generate-reports**
- Generates all reports locally
- Creates HTML dashboard
- Uploads as artifact for download

**Job 2: deploy-pages**
- Builds reports again
- Deploys to GitHub Pages
- Creates public URL

---

## Access Your Reports

### Dashboard URL
```
https://YOUR_USERNAME.github.io/agent_code_review/
```

### Individual Reports
```
Coverage Report:
https://YOUR_USERNAME.github.io/agent_code_review/coverage/

Analysis Report:
https://YOUR_USERNAME.github.io/agent_code_review/analysis/

Test Results:
https://YOUR_USERNAME.github.io/agent_code_review/test_results.json
```

---

## Features

### Automatic Updates
- Reports update on every push
- No manual deployment needed
- Always shows latest results

### Professional Dashboard
- Statistics cards
- Report links
- Test results summary
- Coverage metrics

### Multiple Report Formats
- HTML (interactive)
- JSON (structured data)
- Text (summary)

### Public Access
- Share links with team
- No authentication needed
- Works from anywhere

---

## Customization

### Change Update Frequency

Edit `.github/workflows/publish-to-pages.yml`:

```yaml
on:
  push:
    branches: [ main, develop, staging ]  # Add branches
    paths:
      - '**.py'
      - '**.log'
```

### Add More Reports

In the `generate-reports` job, add:

```yaml
- name: Generate custom report
  run: |
    python my_report_generator.py
    mv report.html reports/my_report.html
  continue-on-error: true
```

Then add to dashboard HTML in the "Available Reports" section.

### Change Site Branding

In dashboard HTML generation, modify:

```python
<h1>🔒 Your Custom Title Here</h1>
<p>Your custom description</p>
```

---

## Troubleshooting

### Pages Not Updating

**Problem**: Changes don't appear after push

**Solutions**:
1. Check workflow passed (green ✅ in Actions)
2. Check job "deploy-pages" completed
3. Clear browser cache
4. Wait 5 minutes for GitHub CDN update
5. Force refresh: Ctrl+Shift+R (Cmd+Shift+R on Mac)

### Can't Access GitHub Pages URL

**Problem**: 404 error on GitHub Pages URL

**Solutions**:
1. Verify Pages is enabled (Settings → Pages)
2. Check "Source" is set to "GitHub Actions"
3. Wait for first deployment to complete
4. Verify workflow ran successfully

### Reports Look Empty

**Problem**: Dashboard shows "N/A" for metrics

**Solutions**:
1. Check test files exist
2. Run tests locally: `pytest test_monitor.py`
3. Check workflow logs for errors
4. Verify Python dependencies installed

### Deployment Takes Too Long

**Problem**: Workflow running >5 minutes

**Solutions**:
1. This is normal first time
2. Subsequent deployments faster
3. Can skip coverage generation to speed up
4. Remove unneeded report generation

---

## Sharing Reports

### Share URL
```
Send this link:
https://YOUR_USERNAME.github.io/agent_code_review/
```

### Share Specific Report
```
Coverage:
https://YOUR_USERNAME.github.io/agent_code_review/coverage/

Analysis:
https://YOUR_USERNAME.github.io/agent_code_review/analysis/
```

### Embed in README
```markdown
[![Reports](https://img.shields.io/badge/Reports-Live-green)](https://YOUR_USERNAME.github.io/agent_code_review/)

[View Latest Reports](https://YOUR_USERNAME.github.io/agent_code_review/)
```

---

## File Structure

### Local (Before Deployment)
```
reports/
├── index.html
├── test_results.json
├── coverage/
│   ├── index.html
│   └── summary.txt
└── analysis/
    └── report.html
```

### GitHub Pages (After Deployment)
```
https://YOUR_USERNAME.github.io/agent_code_review/
├── index.html
├── test_results.json
├── coverage/index.html
├── coverage/summary.txt
└── analysis/report.html
```

---

## Security & Privacy

### Public Access
- Anyone can view your reports
- Reports are public (no auth needed)
- Consider content before publishing

### Hide Sensitive Data
- Don't commit secrets
- Don't include credentials
- Sanitize test data

### Private Repository
- GitHub Pages still public even if repo private
- Consider what you publish

---

## Advanced Features

### Manual Trigger

You can manually trigger deployment:

1. Go to **Actions** tab
2. Find "Publish Reports to GitHub Pages"
3. Click **Run workflow** button
4. Select branch and click **Run workflow**

### Workflow Status

Check deployment status:

1. Go to **Actions** tab
2. Click on workflow run
3. See job progress
4. View logs if needed

### Check Deployment URL

In GitHub Actions job output:
```
GitHub Pages URL:
https://YOUR_USERNAME.github.io/agent_code_review/
```

---

## Performance Tips

### Reduce Report Size
- Remove large data files
- Compress images
- Minify HTML/CSS

### Speed Up Builds
- Skip coverage on some branches
- Use caching
- Parallelize jobs

### Optimize for Mobile
- Dashboard is responsive
- All reports mobile-friendly
- Touch-friendly links

---

## Next Steps

### 1. Enable Pages
- Go to Settings → Pages
- Select "GitHub Actions" source
- Save

### 2. Push Workflow
```bash
git add .github/workflows/publish-to-pages.yml
git commit -m "Add GitHub Pages publishing"
git push origin main
```

### 3. Monitor Deployment
- Go to Actions tab
- Watch workflow run
- Wait for completion

### 4. Access Reports
```
https://YOUR_USERNAME.github.io/agent_code_review/
```

### 5. Share Links
- Share dashboard URL
- Share individual reports
- Embed in README

---

## Support

### Official Docs
- [GitHub Pages Guide](https://docs.github.com/en/pages)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Deploy to Pages](https://github.com/actions/deploy-pages)

### Troubleshooting
- Check workflow logs
- Verify Pages enabled
- Test locally first

---

## Summary

✅ Workflow created: `publish-to-pages.yml`  
✅ Generates HTML reports  
✅ Publishes to GitHub Pages  
✅ Automatic on every push  
✅ Professional dashboard  
✅ Shareable links  

**You're all set! Push to GitHub and reports go live automatically.** 🚀

---

## Example URLs

Once deployed, access your reports:

```
Main Dashboard:
https://YOUR_USERNAME.github.io/agent_code_review/

Coverage Report:
https://YOUR_USERNAME.github.io/agent_code_review/coverage/

Analysis Report:
https://YOUR_USERNAME.github.io/agent_code_review/analysis/

Test Results:
https://YOUR_USERNAME.github.io/agent_code_review/test_results.json
```

Replace `YOUR_USERNAME` with your actual GitHub username.
