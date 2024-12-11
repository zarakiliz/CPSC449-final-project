from motor.motor_asyncio import AsyncIOMotorClient

# mongoDB connection string
MONGO_URI = 'mongodb://127.0.0.1:27017'
DATABASE_NAME = 'cloud_service_access'

# create mongoDB client and database
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# collections
plans_collection = db['plans']