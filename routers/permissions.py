from fastapi import APIRouter, HTTPException, Depends
from models import Permission
from database import permissions_collection, sub_plans_collection, user_subs_collection
from utils import verify_admin, verify_customer
from bson import ObjectId
from bson.errors import InvalidId


router = APIRouter()

# Add a new permission
@router.post("/add-to-user-plan")
async def add_permission_to_user_plan(userId: str, permission_name: str, admin: dict = Depends(verify_admin)):
    """
    Add a permission to the user's plan instance by its name without modifying the global plan.
    """
    # Fetch user subscription
    subscription = await user_subs_collection.find_one({"user_id": userId})
    if not subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    # Fetch the permission details by name
    permission = await permissions_collection.find_one({"name": permission_name})
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found in the global permissions list.")

    # Fetch global plan details
    plan = await sub_plans_collection.find_one({"_id": ObjectId(subscription["plan_id"])})
    if not plan:
        raise HTTPException(status_code=404, detail="Subscribed plan not found.")

    # Ensure the permission doesn't already exist in user's subscription
    permissions = subscription.get("permissions", plan.get("permissions", []))
    if any(p["name"] == permission_name for p in permissions):
        raise HTTPException(status_code=400, detail="Permission already exists in the user's plan.")

    # Add the permission instance to the user's subscription
    permission_to_add = {
        "name": permission["name"],
        "description": permission["description"],
        "api_endpoint": permission["api_endpoint"]
    }

    await user_subs_collection.update_one(
        {"user_id": userId},
        {"$addToSet": {"permissions": permission_to_add}}
    )

    return {"message": f"Permission '{permission_name}' added to the user's plan successfully."}

# Modify a permission
@router.put("/remove-from-user-plan")
async def remove_permission_from_user_plan(userId: str, permission_name: str, admin: dict = Depends(verify_admin)):

    # Fetch user subscription
    subscription = await user_subs_collection.find_one({"user_id": userId})
    if not subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    # Remove the specified permission from the user's instance
    result = await user_subs_collection.update_one(
        {"user_id": userId},
        {"$pull": {"permissions": {"name": permission_name}}}
    )

    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Permission not found in the user's plan.")

    return {"message": f"Permission '{permission_name}' removed successfully from the user's plan."}

# Delete a permission
@router.delete("/{permissionId}")
async def delete_permission(permissionId: str, admin: dict = Depends(verify_admin)):
    """
    Delete a global permission from the database.
    """
    try:
        object_id = ObjectId(permissionId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid permission ID format.")

    # Delete the permission
    result = await permissions_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found.")

    return {"message": "Global permission deleted successfully."}


# Creating a new permission
# Will add it to the permissions cluster
@router.post("/create")
async def create_permission(permission: Permission, admin: dict = Depends(verify_admin)):

    # Check for existing permission
    existing_permission = await permissions_collection.find_one({"name": permission.name})
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists.")

    # Insert the permission into the database
    new_permission = {
        "name": permission.name,
        "description": permission.description,
        "api_endpoint": permission.api_endpoint
    }
    result = await permissions_collection.insert_one(new_permission)

    return {"message": "Permission created successfully", "permission_id": str(result.inserted_id)}



# =============================================
# 4. View All Permissions for a User's Plan
# =============================================
@router.get("/{userId}/permissions")
async def view_user_plan_permissions(userId: str, user: dict = Depends(verify_admin)):
    """
    Fetch all permissions (global + any modifications) for the user's plan.
    """
    # Fetch user subscription
    subscription = await user_subs_collection.find_one({"user_id": userId})
    if not subscription:
        raise HTTPException(status_code=404, detail="User subscription not found.")

    # Fetch the global plan details
    plan = await sub_plans_collection.find_one({"_id": ObjectId(subscription["plan_id"])})
    if not plan:
        raise HTTPException(status_code=404, detail="Subscribed plan not found.")

    # Combine global permissions with user-specific modifications
    global_permissions = plan.get("permissions", [])
    user_permissions = subscription.get("permissions", [])

    return {
        "user_id": userId,
        "global_permissions": global_permissions,
        "user_modified_permissions": user_permissions,
        "effective_permissions": global_permissions + user_permissions
    }
