from pydantic import BaseModel, Field
from typing import List, Optional


# Moving models for cleaner code
# Factoring as well

# Plan Model
class CreatePlan(BaseModel):
    name: str = Field(..., min_length=3, max_length=50) # Basic length for string; needed in order to create the admin and users
    description: str
    permissions: List[str]
    usage_limit: int


class Permission(BaseModel):
    name: str # read, write, admin, etc
    description: str # describes what the permission does

class UserSub(BaseModel):
    user_id: str #unique id for user
    plan_id: str # Plan name provied by the User
    start_date: str

class Usage(BaseModel):
    used: int # amount of usage consumed
    limit: int # usage limit for the plan 