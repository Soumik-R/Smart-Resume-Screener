# MongoDB Atlas Setup Guide

**Date:** October 14, 2025

---

## 🎯 What You Need to Do in MongoDB Atlas

Follow these steps in your MongoDB Atlas web interface:

### Step 1: Create a Free Cluster (if not done)
1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign in or create an account
3. Click **"Build a Database"** or **"Create"**
4. Choose **FREE** tier (M0 Sandbox - 512 MB storage)
5. Select a cloud provider (AWS, Google Cloud, or Azure)
6. Choose a region closest to you
7. Name your cluster (default is fine, e.g., "Cluster0")
8. Click **"Create Cluster"** (takes 1-3 minutes)

---

### Step 2: Create Database User
1. In the Atlas dashboard, click **"Database Access"** (left sidebar)
2. Click **"Add New Database User"**
3. Choose **"Password"** authentication
4. Enter:
   - Username: `resume_screener_user` (or any name you prefer)
   - Password: Generate a strong password or create your own
   - **⚠️ IMPORTANT:** Save this username and password - you'll need it!
5. Database User Privileges: Select **"Read and write to any database"**
6. Click **"Add User"**

---

### Step 3: Whitelist Your IP Address
1. Click **"Network Access"** (left sidebar)
2. Click **"Add IP Address"**
3. **Option A (Recommended for development):**
   - Click **"Allow Access from Anywhere"**
   - Confirm (0.0.0.0/0 will be added)
4. **Option B (More secure):**
   - Click **"Add Current IP Address"**
   - Your IP will be auto-detected
5. Click **"Confirm"**

---

### Step 4: Get Your Connection String
1. Go back to **"Database"** (left sidebar)
2. Click **"Connect"** button on your cluster
3. Choose **"Drivers"**
4. Select **"Python"** and version **"3.12 or later"**
5. Copy the connection string - it looks like:
   ```
   mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
6. **IMPORTANT:** Replace `<username>` and `<password>` in the connection string with your actual credentials

---

### Step 5: Provide Your Connection String

**Once you have your connection string, paste it here and I'll add it to your `.env` file.**

Example format:
```
mongodb+srv://resume_screener_user:YourPassword123@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

---

## 📝 What Happens Next (I'll do this for you)

Once you provide the connection string, I will:
1. ✅ Add it securely to your `.env` file
2. ✅ Create a test script to verify the connection
3. ✅ Create the `resume_screener` database
4. ✅ Create the `candidates` collection
5. ✅ Test inserting and reading data
6. ✅ Clean up the test data
7. ✅ Update documentation

---

## 🔒 Security Notes

- Your connection string contains your password - **NEVER share it publicly**
- The `.env` file is already in `.gitignore` so it won't be committed to Git
- For production, always restrict IP addresses instead of allowing all (0.0.0.0/0)

---

## ❓ Having Issues?

**Common Problems:**

1. **"Authentication failed"** → Check username/password in connection string
2. **"Network timeout"** → Check Network Access whitelist in Atlas
3. **"Server selection timeout"** → Check your internet connection

---

## 📸 Visual Guide (What to Look For)

In MongoDB Atlas, you should see:
- Left sidebar with: **Database**, **Database Access**, **Network Access**
- A cluster named something like "Cluster0" with a green "Connect" button
- After setup: Username in Database Access, Your IP in Network Access

---

**Ready?** Once you complete the steps above and have your connection string, paste it in the chat and I'll handle the rest! 🚀
