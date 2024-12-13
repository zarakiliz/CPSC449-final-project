from motor.motor_asyncio import AsyncIOMotorClient

# mongoDB connection string
MONGO_URI = 'mongodb+srv://eorellana02:CPSC449@cloudservice.3je2l.mongodb.net/cloudservice?retryWrites=true&w=majority&appName=cloudservice'
DATABASE_NAME = 'cloudservice'

# create mongoDB client and database
client = AsyncIOMotorClient(MONGO_URI)
db = client[DATABASE_NAME]

# collections
sub_plans_collection = db['plans']
permissions_collection = db['permissions']
user_subs_collection = db['user_subs']
access_collection = db['access']
usage_collection = db['usage']