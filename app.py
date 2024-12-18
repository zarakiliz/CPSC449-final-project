from fastapi import FastAPI, HTTPException
from typing import List
from database import sub_plans_collection, db, permissions_collection, user_subs_collection, usage_collection
from bson import ObjectId
from routers import plans, permissions, subscriptions, access_control, usage, admin
app = FastAPI()
# Notes to self, move MongoDV logic to util.py


@app.on_event("startup")
async def startup_db_client():
    # Test MongoDB connection on startup
    try:
        await db.command("ping")  # Sends a ping command to MongoDB
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")




# Testing Routes
app.include_router(plans.router, prefix="/plans", tags=["Subscritpion Plans"])
app.include_router(permissions.router, prefix="/permissions", tags=["Permissions"])
app.include_router(subscriptions.router, prefix="/subscriptions", tags=["User Subscriptions"])
app.include_router(access_control.router, prefix="/access", tags=["Access Control"])
app.include_router(usage.router, prefix="/usage", tags =["Usage Tracking"])
app.include_router(admin.router, prefix="/admin", tags=["Admin"])
#HomePage
@app.get("/")
async def root():
    return {"message": "Welcome to the Cloud Service Management System. Use /plans in the URL to create a plan!"}








# Adding get to fetch users to test out
@app.get("/users/{user_id}")
async def get_user(user_id: str):
    # Query the 'users' collection for the user
    user = await db["users"].find_one({"user_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Convert ObjectId to string if needed
    user["_id"] = str(user["_id"])
    return {"message": "User found", "user": user}


@app.get("/users")
async def list_users():
    users = []
    cursor = db["users"].find({})
    async for user in cursor:
        user["_id"] = str(user["_id"])  # Convert ObjectId to string
        users.append(user)
    return {"users": users}

