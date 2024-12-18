from fastapi import APIRouter, HTTPException
from database import user_subs_collection, sub_plans_collection, usage_collection
from bson import ObjectId

router = APIRouter()

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

    # Fetch usage data
    usage = await usage_collection.find_one({"user_id": userId})
    if not usage:
        await usage_collection.insert_one({
            "user_id": userId,
            "usage_limit": plan.get("usage_limit", 0),
            "used": 0,
            "blocked": False
        })
        usage = await usage_collection.find_one({"user_id": userId})

    # Check for block mechanism
    if usage.get("blocked", False) or usage["used"] >= usage["usage_limit"]:
        await usage_collection.update_one({"user_id": userId}, {"$set": {"blocked": True}})
        raise HTTPException(status_code=403, detail="Access denied: Usage limit exceeded.")

    # Combine permissions (global + user-specific)
    global_permissions = plan.get("permissions", [])
    user_permissions = subscription.get("permissions", [])
    effective_permissions = global_permissions + user_permissions

    # Normalize and check API endpoint access
    api_allowed = any(apiRequest.lstrip("/") == perm["api_endpoint"].lstrip("/") 
                      for perm in effective_permissions)

    if not api_allowed:
        raise HTTPException(status_code=403, detail="Access denied: API request not permitted.")

    # Increment usage count
    await usage_collection.update_one({"user_id": userId}, {"$inc": {"used": 1}})

    return {
        "user_id": userId,
        "api_request": apiRequest,
        "access": "granted"
    }



    # if apiRequest in plan.get("permissions", []):
    #     return {"user_id": userId, "api_request": apiRequest, "access": "granted"}
    # else:
    #     return {"user_id": userId, "api_request": apiRequest, "access": "denied"}


# Need to change access control in which it only tracks the usage only