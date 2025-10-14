"""
Simple MongoDB connection test - TESTING PURPOSE ONLY
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import os
from dotenv import load_dotenv

load_dotenv()

# Get connection string from .env
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI", "mongodb://localhost:27017/")

print("=" * 60)
print("MongoDB Connection Test")
print("=" * 60)
print(f"\nTrying to connect to: {MONGO_URI[:50]}...")

try:
    # Create client with short timeout
    client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    
    # Test connection with ping
    client.admin.command('ping')
    
    print("\n✅ SUCCESS - MongoDB server is running!")
    print(f"✓ Connected to: {client.address}")
    
    # List databases
    db_list = client.list_database_names()
    print(f"\n📊 Available databases: {db_list}")
    
    # Check our database
    db = client['resume_screener']
    collections = db.list_collection_names()
    print(f"📁 Collections in 'resume_screener': {collections if collections else 'None'}")
    
    client.close()
    print("\n✓ Connection test complete!")
    
except ConnectionFailure as e:
    print("\n❌ FAILED - MongoDB server is NOT running!")
    print(f"Error: {e}")
    print("\nPossible solutions:")
    print("1. If using local MongoDB: Run 'mongod' in terminal")
    print("2. If using Atlas: Check your MONGO_URI in .env file")
    print("3. If using Atlas: Whitelist your IP address in Atlas dashboard")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print(f"Error type: {type(e).__name__}")

print("=" * 60)
