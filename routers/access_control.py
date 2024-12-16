from fastapi import APIRouter, HTTPException
from database import user_subs_collection, sub_plans_collection, usage_collection
from bson import ObjectId

router = APIRouter()

# Testing out the access control 
# Need to add the block mechanism
@router.get("/{userId}/{apiRequest}")
async def check_access_permission(userId: str, apiRequest: str):

    # Check if the user has a valid subscription
    subscription = await user_subs_collection.find_one({"user_id": userId})
    if not subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    # Fetch the subscribed plan details using plan_id
    plan = await sub_plans_collection.find_one({"_id": ObjectId(subscription["plan_id"])})
    if not plan:
        raise HTTPException(status_code=404, detail="Subscribed plan not found.")

    # User usage data
    usage = await usage_collection.find_one({"user_id": userId})
    if not usage:
        # If no usage data exists, initialize it
        await usage_collection.insert_one({
            "user_id": userId,
            "usage_limit": plan.get("usage_limit", 0),
            "used": 0,
            "blocked": False
        })
        usage = await usage_collection.find_one({"user_id": userId})

    # Check if the user is blocked
    if usage.get("blocked", False):
        raise HTTPException(status_code=403, detail="Access denied: Usage limit reached. Contact admin.")

    # Check if the usage limit has been exceeded
    if usage["used"] >= usage["usage_limit"]:
        # Update the blocked flag
        await usage_collection.update_one(
            {"user_id": userId},
            {"$set": {"blocked": True}}
        )
        raise HTTPException(status_code=403, detail="Access denied: Usage limit exceeded.")

    # Check if the API request exists in the plan permissions
    if apiRequest not in plan.get("permissions", []):
        raise HTTPException(status_code=403, detail="Access denied: API request not permitted.")

    # If access is allowed, increment the usage count
    await usage_collection.update_one(
        {"user_id": userId},
        {"$inc": {"used": 1}}
    )

    return {
        "user_id": userId,
        "api_request": apiRequest,
        "access": "granted",
        "used": usage["used"] + 1,
        "usage_limit": usage["usage_limit"]
    }



    # if apiRequest in plan.get("permissions", []):
    #     return {"user_id": userId, "api_request": apiRequest, "access": "granted"}
    # else:
    #     return {"user_id": userId, "api_request": apiRequest, "access": "denied"}


# Need to change access control in which it only tracks the usage only