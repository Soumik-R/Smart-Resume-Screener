# Security Guidelines for Smart Resume Screener

## 🔒 Protecting Your API Keys and Secrets

### Important Files
- **`.env`** - Contains your actual API keys and secrets (NEVER commit this!)
- **`.env.example`** - Template file showing what variables are needed (safe to commit)

### Setup Instructions

1. **Initial Setup:**
   ```bash
   # Copy the example file
   cp .env.example .env
   
   # Edit .env and add your actual keys
   ```

2. **Verify .gitignore Protection:**
   The `.gitignore` file already includes `.env` to prevent accidental commits.

3. **Check Before Pushing:**
   ```bash
   # Always verify .env is not tracked
   git status
   
   # Should NOT show .env file
   ```

### What's Protected

✅ **These files are ignored by Git:**
- `.env` - Your secrets
- `srs-env/` - Virtual environment
- `*.log` - Log files
- `uploads/` - Uploaded files
- `*.pdf`, `*.docx` - Sample documents

### Emergency: If You Accidentally Pushed Keys

1. **Immediately rotate your API keys:**
   - OpenAI: https://platform.openai.com/api-keys
   - MongoDB Atlas: Regenerate connection string

2. **Remove from Git history:**
   ```bash
   # Remove .env from Git tracking (if accidentally added)
   git rm --cached .env
   git commit -m "Remove .env from tracking"
   git push origin main
   ```

3. **Use git-filter-branch (for complete removal from history):**
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch .env" \
     --prune-empty --tag-name-filter cat -- --all
   
   git push origin --force --all
   ```

### Best Practices

- ✅ Use `.env` for local development
- ✅ Use `.env.example` as a template (commit this)
- ✅ Use environment variables in production (Heroku, AWS, etc.)
- ✅ Keep `.gitignore` updated
- ❌ Never hardcode API keys in source code
- ❌ Never commit `.env` files
- ❌ Never share API keys in chat, email, or screenshots

### Current Status

✅ `.env` is in `.gitignore`
✅ `.env.example` template created
✅ Your API keys are protected
✅ Safe to push to GitHub

---

**Last Updated:** October 14, 2025
