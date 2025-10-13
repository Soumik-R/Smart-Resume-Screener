# Smart Resume Screener - Setup Guide

## Step 1: Python Installation and Virtual Environment ✅

**Date Completed:** October 14, 2025

### What We Did:

1. **✅ Verified Python Installation**
   - Checked Python version: **Python 3.13.4**
   - Location: System-wide installation
   - Requirement: Python 3.10+ ✓

2. **✅ Created Virtual Environment**
   - Environment name: `srs-env`
   - Command used: `python -m venv srs-env`
   - Purpose: Isolate project dependencies from system Python

3. **✅ Activated Virtual Environment**
   - Activation command (PowerShell): `.\srs-env\Scripts\Activate.ps1`
   - Indicator: `(srs-env)` prefix appears in terminal prompt

4. **✅ Upgraded pip**
   - Updated from pip 25.1.1 → pip 25.2
   - Command: `python -m pip install --upgrade pip`

5. **✅ Created Project Files**
   - `.gitignore`: Prevents committing unnecessary files
   - `requirements.txt`: Placeholder for future dependencies

---

## How to Use the Virtual Environment

### Activate the environment:
**Windows PowerShell:**
```powershell
.\srs-env\Scripts\Activate.ps1
```

**Windows Command Prompt:**
```cmd
srs-env\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source srs-env/bin/activate
```

### Deactivate the environment:
```
deactivate
```

### Install packages:
```
pip install package-name
```

### Save installed packages:
```
pip freeze > requirements.txt
```

### Install from requirements.txt:
```
pip install -r requirements.txt
```

---

## Project Structure (Current)

```
Smart-Resume-Screener/
├── srs-env/                # Virtual environment (not committed to Git)
├── .gitignore             # Git ignore rules
├── requirements.txt       # Python dependencies
├── README.md              # Project documentation
└── SETUP.md              # This file
```

---

## Next Steps

### Step 2: Install Core Dependencies
Once we determine which libraries to use (Phase 1 planning), install them:
```
pip install pypdf2 pdfplumber openai streamlit pandas numpy matplotlib
```

### Step 3: Create Project Structure
- Create `src/` directory for source code
- Create `tests/` directory for unit tests
- Create `data/` directory for sample resumes
- Create `docs/` directory for documentation

### Step 4: Initialize Git Repository (if not already done)
```
git init
git add .gitignore README.md requirements.txt
git commit -m "Initial project setup"
```

---

## Troubleshooting

### PowerShell Execution Policy Error
If you get an error activating the virtual environment:
```
.\srs-env\Scripts\Activate.ps1 : File cannot be loaded because running scripts is disabled
```

**Solution:**
Run PowerShell as Administrator and execute:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Python Command Not Found
If `python` command doesn't work, try:
- `python3` (Mac/Linux)
- `py` (Windows Python Launcher)

### Virtual Environment Not Activating
Ensure you're in the correct directory:
```powershell
cd D:\Study\Projects\Smart-Resume-Screener
```

---

## Important Notes

- **Always activate the virtual environment** before working on the project
- **Never commit** the `srs-env/` folder to Git (it's in `.gitignore`)
- **Update `requirements.txt`** whenever you install new packages: `pip freeze > requirements.txt`
- **Share `requirements.txt`** with team members so they can replicate the environment

---

**Status:** ✅ Environment Setup Complete  
**Ready for:** Phase 1 (Planning) → Phase 2 (Development)
