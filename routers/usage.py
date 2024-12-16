from fastapi import APIRouter, HTTPException, Depends
from database import usage_collection, user_subs_collection
from utils import verify_customer

router = APIRouter()

# Tracking the API request usage
@router.post("/{userId}")
async def track_usage(userId: str, user: dict = Depends(verify_customer)):
    # Fetching for the user record
    usage = await usage_collection.find_one({"user_id": userId})
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found.")
    
    if usage["used"] >= usage["usage_limit"]:
        raise HTTPException(status_code=403, detail="Usage limit exceeded")
    
    # Incrementing to keep track of the limit
    new_used = usage["used"] + 1
    await usage_collection.update_one(
        {"user_id": userId},
        {"$set": {"used": new_used}}
    )

    return {
        "message": "API usage tracked successfully.",
        "user_id": userId,
        "used": new_used,
        "usage_limit": usage["usage_limit"]
    }


# Creating the limit
@router.get("/{userId}/limit")
async def check_usage_limit(userId: str, user: dict = Depends(verify_customer)):
    # Fetch the user's usage data
    usage_data = await usage_collection.find_one({"user_id": userId})
    if not usage_data:
        raise HTTPException(status_code=404, detail="Usage data not found.")

    return {
        "user_id": userId,
        "used": usage_data["used"],
        "usage_limit": usage_data["usage_limit"],
        "remaining": usage_data["usage_limit"] - usage_data["used"]
    }