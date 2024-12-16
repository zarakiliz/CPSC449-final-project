from fastapi import APIRouter, HTTPException, Depends
from models import CreatePlan
from database import sub_plans_collection, permissions_collection
from utils import get_by_id
from bson import ObjectId
from utils import verify_admin
from bson.errors import InvalidId

router = APIRouter()

# ONly admins can modify plans logic
# Creating a plan
@router.post("/")
async def create_plan(plan: CreatePlan, user: dict = Depends(verify_admin)):
    existing_plan = await sub_plans_collection.find_one({"name": plan.name})
    if existing_plan:
        raise HTTPException(status_code=400, detail="Plan already exists")

    result = await sub_plans_collection.insert_one(plan.dict())
    return {"message": "Plan created successfully", "plan_id": str(result.inserted_id)}

# Get all plans so user can see
@router.get("/")
async def get_all_plans():
    plans = await sub_plans_collection.find().to_list(100)
    return [
        {
            "id": str(plan["_id"]),
            "name": plan["name"],
            "description": plan["description"],
            "permissions": plan["permissions"],
            "usage_limit": plan["usage_limit"],
        }
        for plan in plans
    ]

# Modifying the plan
# Implementing try methods to modify and Delete
@router.put("/{planId}")
async def modify_plan(planId: str, plan: CreatePlan, user: dict= Depends(verify_admin)): 
    try:
        object_id = ObjectId(planId)
    except:
        raise HTTPException(status_code=400, detail="Invalid plan ID")

    # Validate permissions
    for perm_name in plan.permissions:
        permission = await permissions_collection.find_one({"name": perm_name})
        if not permission:
            raise HTTPException(status_code=404, detail=f"Permission '{perm_name}' not found")

    result = await sub_plans_collection.update_one(
        {"_id": object_id},
        {"$set": {
            "name": plan.name,
            "description": plan.description,
            "permissions": plan.permissions,
            "usage_limit": plan.usage_limit
        }}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan updated successfully"}

# Deleting a plan
@router.delete("/{planId}")
async def delete_plan(planId: str, user: dict = Depends(verify_admin)):

    try: 
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")

    # Rewrote the logic
    result = await sub_plans_collection.delete_one({"_id": object_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}
