from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import sub_plans_collection, db
from bson import ObjectId

app = FastAPI()

class CreatePlan(BaseModel):
    name: str
    description: str
    permissions: List[str]
    usage_limit: int

@app.on_event("startup")
async def startup_db_client():
    # Test MongoDB connection on startup
    try:
        await db.command("ping")  # Sends a ping command to MongoDB
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

# Subscription Plan Management

#HoemPage
@app.get("/")
async def root():
    return {"message": "Welcome to the Cloud Service Management System. Use /plans in the URL to create a plan!"}

#POST/plans (create plan)
@app.post('/plans')
async def create_plan(plan: CreatePlan):
    existing_plan = await sub_plans_collection.find_one({'name': plan.name})
    if existing_plan:
        raise HTTPException(status_code=400, detail='Plan already exists')
    result = await sub_plans_collection.insert_one(plan.dict())
    return {"message": "Plan created successfully"}

# Modify Plans
@app.put('/plans/{planId}')
async def modify_plan(planId: str, plan: CreatePlan):
    try:
        object_id = ObjectId(planId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid planId format")
    result = await sub_plans_collection.update_one(
        {'_id': object_id},
        {"$set": plan.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {'message': 'Plan updated successfully'}

# Delete Plans
@app.delete('/plans/{planId}')
async def delete_plan(planId: str):
    try:
        object_id = ObjectId(planId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid planId format")
    result = await sub_plans_collection.delete_one(
        {'_id': object_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {"message": "Plan deleted successfully"}
