from fastapi import APIRouter, HTTPException, Depends
from models import Permission
from database import permissions_collection, sub_plans_collection
from utils import verify_admin
from bson import ObjectId
from bson.errors import InvalidId


router = APIRouter()

# Add a new permission

@router.post("/")
async def add_permission_to_plan(planId: str, permission_name: str, user: dict = Depends(verify_admin)):
    try:
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    
    # Check if the plan exists
    plan = await sub_plans_collection.find_one({"_id": object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Check if the permission exists
    permission = await permissions_collection.find_one({"name": permission_name})
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")
    
    # Add the permission to the plan with the description
    # Forgot to add api endpoint -.-
    new_permission = {
        "name": permission_name,
        "description": permission["description"],
        "api_endpiont": permission["api_endpoint"]
    }
    
    if new_permission not in plan.get("permissions", []):
        await sub_plans_collection.update_one(
            {"_id": object_id},
            {"$addToSet": {"permissions": new_permission}}
        )
        return {"message": f"Permission '{permission_name}' added to the plan successfully"}
    else:
        raise HTTPException(status_code=400, detail="Permission already exists in the plan")


# Modify a permission
@router.put("/")
async def remove_permission_from_plan(planId: str, permission_name: str, user: dict = Depends(verify_admin)):
    try:
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")

    # Check if the plan exists
    plan = await sub_plans_collection.find_one({"_id": object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Check if the permission exists in the plan's permissions
    permissions = plan.get("permissions", [])
    if not any(perm.get("name") == permission_name for perm in permissions):
        raise HTTPException(status_code=400, detail="Permission not found in the plan")

    # Remove the permission by matching the 'name' field
    await sub_plans_collection.update_one(
        {"_id": object_id},
        {"$pull": {"permissions": {"name": permission_name}}}
    )

    return {"message": f"Permission '{permission_name}' removed from the plan successfully"}

# Delete a permission
@router.delete("/{permissionId}")
async def delete_permission(permissionId: str, user: dict = Depends(verify_admin)):
    try:
        object_id = ObjectId(permissionId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid permission ID format")
    
    # Delete permission
    result = await permissions_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted successfully"}


# Adding to create a new permission string
@router.post("/create")
async def create_permission(permission: Permission, user: dict = Depends(verify_admin)):
    # Check for existing permission by name
    existing_permission = await permissions_collection.find_one({"name": permission.name})
    if existing_permission:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # Insert the new permission into the database
    new_permission = {
        "name": permission.name,
        "api_endpoint": permission.api_endpoint,
        "description": permission.description
    }
    result = await permissions_collection.insert_one(new_permission)
    return {
        "message": "Permission created successfully",
        "permission_id": str(result.inserted_id)
    }