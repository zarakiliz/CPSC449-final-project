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
    # Check if the plan already exists
    existing_plan = await sub_plans_collection.find_one({"name": plan.name})
    if existing_plan:
        raise HTTPException(status_code=400, detail="Plan already exists")
    
    # Construct permissions list
    permissions_list = [
        {
            "name": perm.name,
            "description": perm.description,
            "api_endpoint": perm.api_endpoint
        }
        for perm in plan.permissions
    ]

    # Insert the new plan
    new_plan = {
        "name": plan.name,
        "description": plan.description,
        "permissions": permissions_list,
        "usage_limit": plan.usage_limit
    }
    result = await sub_plans_collection.insert_one(new_plan)
    return {"message": "Plan created successfully", "plan_id": str(result.inserted_id)}


# Modifying the plan
# Implementing try methods to modify and Delete
# Modifying a plan with partial updates
@router.patch("/{planId}")
async def modify_plan_partial(planId: str, update_fields: dict, user: dict = Depends(verify_admin)):
    try:
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")

    # Check if the plan exists
    existing_plan = await sub_plans_collection.find_one({"_id": object_id})
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    # Update the plan using the provided fields
    result = await sub_plans_collection.update_one(
        {"_id": object_id},
        {"$set": update_fields}  # Only update the fields provided in the body
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not updated")
    
    return {"message": "Plan updated successfully", "updated_fields": update_fields}


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


# Get all plans so user can see
@router.get("/")
async def get_all_plans():
    plans = await sub_plans_collection.find().to_list(100)
    return [
        {
            "id": str(plan["_id"]),
            "name": plan["name"],
            "description": plan["description"],
            "permissions": [
                {
                    "name": perm.get("name", "N/A"),
                    "description": perm.get("description", "No description available"),
                    "api_endpoint": perm.get("api_endpoint", "N/A")
                }
                for perm in plan.get("permissions", [])  # Safely iterate over permissions
            ],
            "usage_limit": plan.get("usage_limit", 0)
        }
        for plan in plans
    ]

# Get a specific plan by ID
@router.get("/{planId}")
async def get_plan_by_id(planId: str):
    try:
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")

    # Fetch the specific plan
    plan = await sub_plans_collection.find_one({"_id": object_id})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")

    return {
        "id": str(plan["_id"]),
        "name": plan["name"],
        "description": plan["description"],
        "permissions": [
            {
                "name": perm.get("name", "N/A"),
                "description": perm.get("description", "No description available"),
                "api_endpoint": perm.get("api_endpoint", "N/A")
            }
            for perm in plan.get("permissions", [])  # Safely iterate over permissions
        ],
        "usage_limit": plan.get("usage_limit", 0)
    }

