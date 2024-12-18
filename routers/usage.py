from fastapi import APIRouter, HTTPException, Depends
from database import usage_collection
from utils import verify_customer

router = APIRouter()

# Combined usage tracking and status endpoint
# Rewrote uasge to one single endpoint for GET
@router.get("/{userId}")
async def track_and_check_usage(userId: str, user: dict = Depends(verify_customer)):
    # Fetch the user's usage data
    usage = await usage_collection.find_one({"user_id": userId})
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found.")
    
    # Check if the user has reached their usage limit
    if usage["used"] >= usage["usage_limit"]:
        # Return the usage status without incrementing
        return {
            "user_id": userId,
            "used": usage["used"],
            "usage_limit": usage["usage_limit"],
            "remaining": 0,
            "status": "blocked",
            "message": "Usage limit reached. Contact admin for assistance."
        }

    # Forgot to take out the increment -.- was using the limit on it
    # Fetch the updated usage data
    updated_usage = await usage_collection.find_one({"user_id": userId})

    # Return the updated usage status
    return {
        "user_id": userId,
        "used": updated_usage["used"],
        "usage_limit": updated_usage["usage_limit"],
        "remaining": updated_usage["usage_limit"] - updated_usage["used"],
        "status": "active",
        "message": "Usage tracked successfully."
    }
