from fastapi import APIRouter, HTTPException, Depends
from models import UserSub
from database import user_subs_collection, sub_plans_collection
from utils import get_plan_by_name, verify_admin, verify_customer
from bson import ObjectId

router = APIRouter()

# We need to fetch by Plan name
# Adding new funciton to utils to grab by plan name

# Subscribe to a Plan
@router.post("/")
async def subscribe_to_plan(plan_name: str, user: dict = Depends(verify_customer)):
    # Verify that the plan exists by its name
    plan = await get_plan_by_name(plan_name)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")

    # Check if the user already has a subscription
    existing_sub = await user_subs_collection.find_one({"user_id": user["user_id"]})
    if existing_sub:
        raise HTTPException(status_code=400, detail="User already subscribed to a plan.")
    
    # Add the subscription
    new_sub = {
        "user_id": user["user_id"],
        "plan_id": str(plan["_id"]),
    }
    result = await user_subs_collection.insert_one(new_sub)
    return {"message": "Subscription created successfully", "subscription_id": str(result.inserted_id)}

# View Subscription Details
@router.get("/{userId}")
async def get_subscription(userId: str):
   # Fetch the user's subscription
    sub = await user_subs_collection.find_one({"user_id": userId})
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    
    # Fetch the plan details
    plan = await sub_plans_collection.find_one({"_id": ObjectId(sub["plan_id"])})
    if not plan:
        raise HTTPException(status_code=404, detail="Subscribed plan not found.")
    
    return {
        "user_id": sub["user_id"],
        "plan_name": plan["name"],
        "plan_description": plan["description"],
        "permissions": plan["permissions"],
    }

# Adding admin permision modficaiton
# Modify a User's Subscription - Admin Only
@router.put("/{userId}/modify")
async def modify_subscription(userId: str, plan_name: str, admin: dict = Depends(verify_admin)):
    # Check if the user has an existing subscription
    existing_sub = await user_subs_collection.find_one({"user_id": userId})
    if not existing_sub:
        raise HTTPException(status_code=404, detail="Subscription not found.")
    
    # Verify that the new plan exists
    plan = await get_plan_by_name(plan_name)
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found.")
    
    # Update the user's subscription
    await user_subs_collection.update_one(
        {"user_id": userId},
        {"$set": {"plan_id": str(plan["_id"])}}
    )
    return {"message": f"Subscription for user {userId} updated to plan '{plan_name}' successfully."}