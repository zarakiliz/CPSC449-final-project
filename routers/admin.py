from fastapi import APIRouter, HTTPException, Depends
from database import usage_collection
from utils import verify_admin

router = APIRouter()

# Reset Usage Limit (Admin Only)
@router.put("/usage/{userId}/reset")
async def reset_usage_limit(userId: str, admin: dict = Depends(verify_admin)):
    
    # Fetch the usage data for the user
    usage = await usage_collection.find_one({"user_id": userId})
    if not usage:
        raise HTTPException(status_code=404, detail="Usage record not found.")
    
    # Reset the 'used' value and unblock the user
    await usage_collection.update_one(
        {"user_id": userId},
        {"$set": {"used": 0, "blocked": False}}
    )

    return {
        "message": f"Usage for user '{userId}' has been reset successfully.",
        "user_id": userId,
        "usage_limit": usage["usage_limit"],
        "used": 0,
        "status": "active"
    }
