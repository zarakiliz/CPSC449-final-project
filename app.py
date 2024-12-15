from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import sub_plans_collection, db, permissions_collection, user_subs_collection, usage_collection
from bson import ObjectId

app = FastAPI()

class CreatePlan(BaseModel):
    name: str
    description: str
    permissions: List[str]
    usage_limit: int

class Permission(BaseModel):
    name: str # read, write, admin, etc
    description: str # describes what the permission does

class UserSub(BaseModel):
    user_id: str #unique id for user
    plan_id: str # id of subscribed plan
    start_date: str

class Usage(BaseModel):
    used: int # amount of usage consumed
    limit: int # usage limit for the plan 

@app.on_event("startup")
async def startup_db_client():
    # Test MongoDB connection on startup
    try:
        await db.command("ping")  # Sends a ping command to MongoDB
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"Error connecting to MongoDB: {e}")

# Subscription Plan Management

#HomePage
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

# Permissions Management

# Add Permission
@app.post('/permissions')
async def add_permission(permission: Permission):
    # check for existing permission
    existing_perm = await permissions_collection.find_one({'name': permission.name})
    if existing_perm:
        raise HTTPException(status_code=400, detail='Permission already exists')
    
    await permissions_collection.insert_one(permission.dict())
    return {"message": "Permission created successfully"}

# Modify Permission
@app.put('/permissions/{permissionId}')
async def modify_perm(permissionId: str, permission: Permission):
    try:
        object_id = ObjectId(permissionId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid permissionId format")
    result = await permissions_collection.update_one(
        {'_id': object_id},
        {"$set": permission.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Plan not found")
    return {'message': 'Permission updated successfully'}

# Delete Permission
@app.delete('/permissions/{permissionId}')
async def delete_perm(permissionId: str):
    try:
        object_id = ObjectId(permissionId)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid permissionId format")
    result = await permissions_collection.delete_one(
        {'_id': object_id}
    )
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Permission not found")
    return {"message": "Permission deleted successfully"}

# User Subscription Handling

# Subscribe to Plan
@app.post('/subscriptions')
async def subscribe(subscription: UserSub):
    # Check if the user is already subscribed to a plan
    existing_sub = await user_subs_collection.find_one({'user_id': subscription.user_id})
    if existing_sub:
        raise HTTPException(status_code=400, detail=f"User {subscription.user_id} already subscribed to a plan")
    
    await user_subs_collection.insert_one(subscription.dict())
    return {"message": f"Subscription for user {subscription.user_id} created successfully"}

# View subscription details
@app.get('/subscriptions/{userId}')
async def get_subscription(userId: str):
    sub = await user_subs_collection.find_one({'user_id': userId})
    if not sub:
        raise HTTPException(status_code=404, detail=f"Subscription for user {userId} not found")
    
    # Include the subscription plan details
    try:
        plan = await sub_plans_collection.find_one({'_id': ObjectId(sub['plan_id'])})
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid plan ID format")
    
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan with ID {sub['plan_id']} not found")
    
    sub['_id'] = str(sub['_id'])
    plan['_id'] = str(plan['_id'])
    sub['plan'] = plan
    return sub

# View usage statistics
@app.get('/subscriptions/{userId}/usage')
async def get_usage(userId: str):
    sub = await user_subs_collection.find_one({'user_id': userId})
    if not sub:
        raise HTTPException(status_code=404, detail=f"Subscription for user {userId} not found")
    
    usage = await usage_collection.find_one({'user_id': userId})
    if not usage:
        raise HTTPException(status_code=404, detail=f"Usage data for user {userId} not found")
    
    plan = await sub_plans_collection.find_one({'_id': ObjectId(sub['plan_id'])})
    if not plan:
        raise HTTPException(status_code=404, detail=f"Plan with ID {sub['plan_id']} not found")
    
    usage_stats = Usage(used=usage['used'], limit=plan['usage_limit'])
    return usage_stats.dict()


# Assign/modify user plan
@app.put('/subscriptions/{userId}/modify')
async def modify_sub(userId: str, subscription:UserSub):
    # check if plan exists
    plan = await sub_plans_collection.find_one({'_id': ObjectId(subscription.plan_id)})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # update/modify user plan
    result = await user_subs_collection.update_one(
        {'user_id': userId},
        {'$set': {
            'plan_id': subscription.plan_id,
            'start_date': subscription.start_date,
        }}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Subscription not found")
    return {"message": "Subscription updated successfully"}

# Access Control

# checks access permissions
@app.get('/access/{userId}/{apiRequest}')
async def check_access(userId:str, apiRequest:str):
    # get user subscription
    user_subscription = await user_subs_collection.find_one({'user_id': userId})
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User not subscribed to any plan")
    
    plan = await sub_plans_collection.find_one({'_id': ObjectId(user_subscription['plan_id'])})
    if not plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")
    
    # check if apiRequest is in the user's permissions
    if apiRequest in plan['permissions']:
        return {"access_granted": True}
    else:
        raise HTTPException(status_code=403, detail="Access Denied")
    
# Usage Tracking and Limit Enforcement

# track API request
@app.post('/usage/{userId}')
async def track_api(userId: str):
    # check if user has a subscription
    user_subscription = await user_subs_collection.find_one({'user_id': userId})
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User not subscribed to any plan")

    # get current usage
    usage = await usage_collection.find_one({'user_id': userId})
    if not usage:
        usage = {"user_id": userId, "used": 0, "limit": 0}

    
    # Increment usage
    usage['used'] += 1

    # Save the updated usage data
    await usage_collection.replace_one({'user_id': userId}, usage, upsert=True)

    return {"message": "Usage tracked", "usage_count": usage['used']}

# check limit status
@app.get('/usage/{userId}/limit')
async def check_limit(userId: str):
    # check if user has a subscription
    user_subscription = await user_subs_collection.find_one({'user_id': userId})
    if not user_subscription:
        raise HTTPException(status_code=404, detail="User not subscribed to any plan")

    plan = await sub_plans_collection.find_one({'_id': ObjectId(user_subscription['plan_id'])})
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
     # get current usage
    usage = await usage_collection.find_one({'user_id': userId})
    if not usage:
        usage = {"user_id": userId, "used": 0}

    
    # check if usage exceeds the plan's limit
    if usage['used'] >= plan['usage_limit']:
        raise HTTPException(status_code=403, detail="Usage limit exceeded")

    remaining_limit = plan['usage_limit'] - usage['used']
    return {"usage_count": usage['used'], "remaining_limit": remaining_limit}