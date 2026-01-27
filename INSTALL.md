# CAD Export Workflow - Installation Guide

This guide walks you through setting up automated STEP file generation for your FreeCAD projects. Once installed, every time you open a Pull Request with changes to `.FCStd` files, the workflow will automatically generate STEP exports and commit them back to your branch.

---

## What You'll Get

- **Automatic STEP exports** when you create/update PRs containing FreeCAD files
- **STEP files committed** directly to your branch (no manual export needed)
- **PR comments** with a summary of exported files
- **Downloadable artefacts** for each workflow run
- **Manual trigger** option to export all designs on demand

---

## Prerequisites

- A GitHub repository with your FreeCAD files
- Git installed on your computer
- Admin access to the repository

---

## Installation Steps

### Step 1: Install Git LFS

Git Large File Storage (LFS) is required because STEP files can be very large (100MB+). GitHub has a 100MB file size limit for regular files.

**On macOS:**
```bash
brew install git-lfs
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install git-lfs
```

**On Windows:**
Download and run the installer from: https://git-lfs.github.com/

**Then initialise LFS (run once per machine):**
```bash
git lfs install
```

---

### Step 2: Clone Your Repository

If you haven't already, clone your repository:

```bash
git clone https://github.com/YOUR_ORG/YOUR_REPO.git
cd YOUR_REPO
```

If you already have it cloned, make sure you're up to date:

```bash
git checkout main
git pull origin main
```

---

### Step 3: Extract the Workflow Files

Download and extract the `cad-workflow-package.zip` file into your repository root. This will create:

```
your-repo/
├── .github/
│   ├── scripts/
│   │   └── export_step.py
│   └── workflows/
│       └── cad-export.yml
└── .gitattributes  (will be merged if exists)
```

**Important:** If you already have a `.gitattributes` file, add these lines to it instead of replacing it:

```
*.step filter=lfs diff=lfs merge=lfs -text
*.STEP filter=lfs diff=lfs merge=lfs -text
*.stp filter=lfs diff=lfs merge=lfs -text
*.STP filter=lfs diff=lfs merge=lfs -text
*.FCStd filter=lfs diff=lfs merge=lfs -text
*.fcstd filter=lfs diff=lfs merge=lfs -text
```

---

### Step 4: Migrate Existing Large Files to LFS (If Needed)

If your repository already contains large `.FCStd` or `.step` files, you need to migrate them to LFS:

```bash
# This rewrites history to move large files to LFS
git lfs migrate import --include="*.step,*.STEP,*.stp,*.STP,*.FCStd,*.fcstd" --everything

# Force push the migrated history (coordinate with your team first!)
git push --force-with-lease origin main
```

⚠️ **Warning:** This rewrites Git history. Make sure all team members know to re-clone the repository after this step.

If you're starting fresh or don't have large files yet, skip this step.

---

### Step 5: Commit and Push the Workflow Files

```bash
# Add all the new files
git add .github/
git add .gitattributes

# Commit
git commit -m "Add automated CAD export workflow"

# Push to GitHub
git push origin main
```

---

### Step 6: Verify the Installation

1. Go to your repository on GitHub
2. Click the **Actions** tab
3. You should see **CAD Export** in the left sidebar
4. Click on it - you should see the "Run workflow" button (for manual runs)

---

## Directory Structure Requirements

The workflow expects your CAD files to be organised like this:

```
your-repo/
├── */CAD_INTERNAL/
│   ├── FREECAD_FILES/
│   │   ├── Design001.FCStd    ← Source files (you edit these)
│   │   └── Design002.FCStd
│   └── STEP_FILES/
│       ├── Design001.step     ← Auto-generated (don't edit)
│       └── Design002.step
```

- Put your FreeCAD `.FCStd` files in `CAD_INTERNAL/FREECAD_FILES/`
- The workflow creates `CAD_INTERNAL/STEP_FILES/` automatically
- STEP files are named to match their source FCStd file

---

## How to Use

### Normal Workflow (Automatic)

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/my-design-changes
   ```

2. Make changes to your FreeCAD files in `CAD_INTERNAL/FREECAD_FILES/`

3. Commit and push:
   ```bash
   git add .
   git commit -m "Updated camera housing design"
   git push -u origin feature/my-design-changes
   ```

4. Open a Pull Request on GitHub

5. The workflow runs automatically and:
   - Exports STEP files from your changed FCStd files
   - Commits the STEP files to your branch
   - Posts a summary comment on your PR

6. Review and merge your PR - both FCStd and STEP files are included!

### Manual Export (On Demand)

To export all designs (not just changed ones):

1. Go to **Actions** → **CAD Export**
2. Click **Run workflow**
3. Tick "Export all designs" if you want everything exported
4. Click the green **Run workflow** button

---

## Troubleshooting

### "File exceeds GitHub's file size limit"
Your repository doesn't have LFS set up correctly. Make sure:
- `.gitattributes` contains the LFS tracking rules
- You ran `git lfs install`
- Large files were migrated with `git lfs migrate import`

### Workflow doesn't trigger on PR
Check that your FCStd files are in the correct path:
- Must be in `*/CAD_INTERNAL/FREECAD_FILES/*.FCStd`
- The path is case-sensitive

### "No exportable solid bodies found"
The FreeCAD file might use a structure the script doesn't recognise. The script looks for objects with solid geometry (bodies, parts with solids). Contact support if this happens.

### Workflow fails at "Install FreeCAD"
This occasionally happens if the Ubuntu PPA is temporarily unavailable. Re-run the workflow - it usually works on retry.

---

## LFS Storage Limits

GitHub Free accounts include:
- **1 GB** of LFS storage
- **1 GB** of bandwidth per month

GitHub Pro/Team accounts include:
- **2 GB** of storage and bandwidth

You can purchase additional data packs if needed. Check your usage at:
https://github.com/settings/billing

---

## Support

If you encounter issues:
1. Check the **Actions** tab for detailed error logs
2. Ensure your directory structure matches the expected layout
3. Verify LFS is working: `git lfs status`

---

## Files Included

| File | Purpose |
|------|---------|
| `.github/workflows/cad-export.yml` | The GitHub Actions workflow |
| `.github/scripts/export_step.py` | Python script that exports STEP files |
| `.gitattributes` | Configures Git LFS for large files |

