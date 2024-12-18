from bson import ObjectId
from fastapi import HTTPException
from fastapi import Request
from database import db

# Logic for MongoDB

async def get_by_id(collection, object_id: str):
    try:
        # Attemtping to valdiate and fetch the ObjectID from MongoDB
        obj = await collection.find_one({'_id': ObjectId(object_id)})

        # conditions
        if not obj:
            raise HTTPException(status_code=404, detail="Object not found")
    
        # string for serilziaton
        obj['_id'] = str(obj['_id'])
        return obj
    
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ID format")


async def verify_admin(request: Request):
    user_id = request.headers.get("user_id")
    print(f"Header user_id: {user_id}")  # Debugging step

    if not user_id:
        raise HTTPException(status_code=401, detail="User ID is required")

    # Check user in MongoDB
    user = await db["users"].find_one({"user_id": user_id})
    print(f"Fetched user: {user}")  # Debugging step

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Ensure the user role is 'admin'
    if user.get("role") != "admin":
        print(f"User role: {user.get('role')} - Access Denied")  # Debugging step
        raise HTTPException(status_code=403, detail="Admin access required")

    print(f"Admin verified: {user_id}")  # Debugging step
    return user  # Return user for reference if needed


# For user funciton to subscribe to the plan of choice
async def get_plan_by_name(plan_name: str):
    from database import sub_plans_collection
    plan = await sub_plans_collection.find_one({"name": plan_name})
    return plan


# Verfiying if the user exists or not
# Verify Customer from headers
async def verify_customer(request: Request):
    user_id = request.headers.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID is required in headers")
    
    # Check the user role in MongoDB
    user = await db["users"].find_one({"user_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Ensure the role is "customer"
    if user.get("role") != "customer":
        raise HTTPException(status_code=403, detail="Customer access required")
    
    return user  # Return user details if needed