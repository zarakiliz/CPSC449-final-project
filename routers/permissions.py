from fastapi import APIRouter, HTTPException, Depends
from models import Permission
from database import permissions_collection
from utils import verify_admin
from bson import ObjectId
from bson.errors import InvalidId


router = APIRouter()

# Add a new permission

@router.post("/")
async def add_permission(permission: Permission, user: dict = Depends(verify_admin)):
    # Check for existing permission
    existing_perm = await permissions_collection.find_one({"name": permission.name})
    if existing_perm:
        raise HTTPException(status_code=400, detail="Permission already exists")
    
    # Insert permission
    result = await permissions_collection.insert_one(permission.dict())
    return {"message": "Permission created successfully", "permission_id": str(result.inserted_id)}

# Modify a permission
@router.put("/{permissionId}")
async def modify_permission(permissionId: str, permission: Permission, user: dict = Depends(verify_admin)):
    try:
        object_id = ObjectId(permissionId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid permission ID format")
    
    # Update permission
    result = await permissions_collection.update_one(
        {"_id": object_id},
        {"$set": permission.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission updated successfully"}

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
