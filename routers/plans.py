from fastapi import APIRouter, HTTPException, Depends
from models import CreatePlan
from database import sub_plans_collection
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


# Modifying the plan
# Implementing try methods to modify and Delete
@router.put("/{planId}")
async def modify_plan(planId: str, plan: CreatePlan, user: dict= Depends(verify_admin)): 
    try: 
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    
    # Check to see if the ObjectID is valid and fetch the plan from the database
    existing_plan = await get_by_id(sub_plans_collection, planId)
    # Condition to see if plants exits or not
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plan not found")


    # Update the plan
    await sub_plans_collection.update_one(
       {"_id": ObjectId(planId)},
       {"$set": plan.dict()}
   )
    return {"message": "Plan updated successfully"}

# Deleting a plan
@router.delete("/{planId}")
async def delete_plan(planId: str, user: dict = Depends(verify_admin)):

    try: 
        object_id = ObjectId(planId)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    existing_plan = await get_by_id(sub_plans_collection, planId)
    if not existing_plan:
        raise HTTPException(status_code=404, detail="Plant not found")
    
    # Deleting the plan from the database
    await sub_plans_collection.delete_one({"_id": ObjectId(planId)})
    return {"message": "Plan deleted successfully"}
