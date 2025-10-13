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

## Step 2: Install Required Libraries ✅

**Date Completed:** October 14, 2025

### Installed Backend Libraries:

1. **✅ pdfplumber (v0.11.7)** - PDF text extraction and parsing
2. **✅ spaCy (v3.8.7)** - NLP and entity extraction
   - Downloaded model: `en_core_web_sm` (English language model)
3. **✅ OpenAI SDK (v2.3.0)** - LLM API for intelligent resume analysis
4. **✅ PyMongo (v4.15.3)** - MongoDB database driver
5. **✅ FastAPI (v0.119.0)** - Modern web framework for building APIs
6. **✅ Uvicorn (v0.37.0)** - ASGI server for running FastAPI
7. **✅ Pandas (v2.3.3)** - Data manipulation and analysis
8. **✅ python-multipart (v0.0.20)** - File upload handling for FastAPI

### Installation Commands Used:

```powershell
pip install pdfplumber
pip install spacy
python -m spacy download en_core_web_sm
pip install openai
pip install pymongo
pip install fastapi uvicorn[standard]
pip install pandas python-multipart
pip freeze > requirements.txt
```

### Verification:

Run the test script to verify all installations:
```powershell
python test_setup.py
```

**Result:** ✅ All 8/8 libraries installed and working correctly!

---

## Next Steps

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
