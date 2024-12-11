from fastapi import FastAPI, HTTPException
import asyncio
from pydantic import BaseModel
from typing import List
from database import plans_collection
app = FastAPI()

class CreatePlan(BaseModel):
    name: str
    description: str
    permissions: List[str]
    usage_limit: int
# Subscription Plan Management 

# POST/plans (create plan)
@app.get('/plans')
async def create_plan(plan: CreatePlan):
    # check to see if there is an existing plan. If yes, raise an exception
    existing_plan = await plans_collection.find_one({'name': 'plan.name'})
    if existing_plan:
        raise HTTPException(status_code=400, details='Plan already exists')

# import os
# from flask import Flask, jsonify, abort, request, url_for, redirect
# from flask_mysqldb import MySQL
# from werkzeug.utils import secure_filename
# import jwt
# from dotenv import load_dotenv
# from datetime import datetime, timedelta

# # To load the ennvrionment variables from the .env file
# load_dotenv()

# app = Flask(__name__)
# app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_secret_key')
# app.config['extensions'] = ['.jpg','.pdf','.png']
# app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 #limiting the size of uploaded files
# app.config['UPLOAD_PATH'] = 'uploads'

# # MySQL configurations Testing
# app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
# app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
# app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
# app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'flask_app')
# app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# mysql = MySQL(app)

# # Checking to see if the folder exists
# if not os.path.exists(app.config['UPLOAD_PATH']):
#     os.makedirs(app.config['UPLOAD_PATH'])

# # Root route
# @app.route('/')
# def home():
#     return jsonify(message="Welcome to the Flask App! Try accessing /public, /login, or /upLoadFile.")


# # Public Route to get usernmane and ID
# @app.route('/public', methods=['GET'])
# def public_view():
#     # Using the usernamen and ID value from MySQL workbench
#     cursor = mysql.connection.cursor()
#     query = "SELECT id, username FROM users"
#     cursor.execute(query)
#     users = cursor.fetchall()
#     cursor.close()
#     return jsonify(users)

# #error 400
# @app.errorhandler(400)
# def bad_request(e):

#     return jsonify(error=str(e)), 400

# #error 401
# @app.errorhandler(401)
# def unauthorized(e):

#     return jsonify(error=str(e)), 401

# #error 404
# @app.errorhandler(404)
# def page_not_found(e):

#     return jsonify(error=str(e)), 404

# #error 500
# @app.errorhandler(500)
# def internal_server_error(e):

#     return jsonify(error=str(e)), 500


# # File Handling 

# #upload file

# @app.route('/upLoadFile', methods=['POST', 'GET'])
# def upLoadFile():
#     #Seems easier to check what files are being uploaded
#     if request.method == 'POST':
#         uploaded_file = request.files.get('file')
#         # Test via PostMan incase we forget to input file
#         if not uploaded_file:
#             return jsonify({'error': 'No file provided'}), 400

#         # Invalid file 
#         filename = secure_filename(uploaded_file.filename)
#         if not filename or os.path.splitext(filename)[1].lower() not in app.config['extensions']:
#             return jsonify({'error': 'Invalid file extension'}), 400

#         # File uploaded succesfully
#         upload_path = os.path.join(app.config['UPLOAD_PATH'], filename)
#         uploaded_file.save(upload_path)
#         return jsonify({'message': 'File uploaded successfully', 'filename': filename}), 201
    
#     #Logic to access via Endpoint through the URL
#     elif request.method == 'GET':
#         #Listing all of the files in 'uploads' folder in root directory
#         if not os.path.exists(app.config['UPLOAD_PATH']) or not os.listdir(app.config['UPLOAD_PATH']):
#             return jsonify({'message': 'No files have been uploaded yet.'}), 404
        
#         #Return the files uploaded in JSON format
#         files = os.listdir(app.config['UPLOAD_PATH'])
#         return jsonify({'uploaded_files': files})

#  # Delete file route
# @app.route('/deleteFile', methods=['DELETE'])
# def delete_file():
#     data = request.json
#     filename = data.get('filename')

#     if not filename:
#         return jsonify({'error': 'No filename provided'}), 400

#     file_path = os.path.join(app.config['UPLOAD_PATH'], secure_filename(filename))

#     if not os.path.exists(file_path):
#         return jsonify({'error': 'File not found'}), 404

#     try:
#         os.remove(file_path)
#         return jsonify({'message': f'{filename} has been deleted successfully.'}), 200
#     except Exception as e:
#         return jsonify({'error': 'Could not delete the file', 'details': str(e)}), 500


# # Authentication
# # login route to generate JWT token for the user in MySQL to test via POSTMAN
# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     # Confirmed 
#     if request.method == 'GET':
#         # Serve the HTML login form
#         return '''
#             <html>
#             <body>
#                 <h2>Login</h2>
#                 <form action="/login" method="POST">
#                     <label for="username">Username:</label>
#                     <input type="text" id="username" name="username" required><br><br>
                    
#                     <label for="password">Password:</label>
#                     <input type="password" id="password" name="password" required><br><br>
                    
#                     <input type="submit" value="Login">
#                 </form>
#             </body>
#             </html>
#         '''
    
#     elif request.method == 'POST':
#         # Checking if JSON data is provided 
#         # Retrieve credentials from the form
#         # Forgot to test for POST 
#         if request.is_json:
#             data = request.json
#             username = data.get('username')
#             password = data.get('password')
#         else:
#             username = request.form.get('username')
#             password = request.form.get('password')

#         # Validate that username and password are provided
#         if not username or not password:
#             return jsonify({'message': 'Invalid credentials!'}), 400

#         # Query the database for the user via MySQL workbench
#         # Need to ride documentation to test
#         cursor = mysql.connection.cursor()
#         query = "SELECT * FROM users WHERE username = %s AND password = %s"
#         cursor.execute(query, (username, password))
#         user = cursor.fetchone()
#         cursor.close()

#         # Check if user is found
#         if user:
#             # Generate a JWT token with a 30-minute expiration time
#             token = jwt.encode(
#                 {
#                     'username': user['username'],
#                     'exp': datetime.utcnow() + timedelta(minutes=2)  # Token expiration time 1 to test out for 
#                 },
#                 app.config['SECRET_KEY'],
#                 algorithm='HS256'
#             )
#             #Testing to see if this works for uploading file
#             #Had to make this to a response in order to store the token in the cookie
#             #Why is debugging so hard
#             response = jsonify({
#                 'message': f'Welcome, {username}! You have successfully logged in.',
#                 'token': token  #Token will be printed to copy and past into postman to test it out
               
#             })
#             #Storing the JWT token in a cookie to access the /protected endpoint via url
#             response.set_cookie('token', token)
#             return response

#         # If password is wrong
#         else:
#             return jsonify({'message': 'Invalid credentials!'}), 401


# #Confirmed via PostMan JWT Bearer Token Works
# # protected endpoint that requires a valid jwt token to access
# @app.route('/protected', methods=['GET'])
# def protected():

#     # Release in order to access proctected, we can do either through POSTMAN or through the endpoint via cookie
#     # token = request.cookies.get('token') or request.headers.get('Authorization')\
#     token = request.headers.get('Authorization')
#     if token and token.startswith("Bearer "):
#         token = token.split(" ")[1]
#     else:
#         # If not found in headers, look for it as a query parameter in the URL
#         token = request.args.get('token')
#     # token = request. headers.get('Authorization')
#     # if not token:
#     #     return jsonify({'message': 'Token is missing.'}), 401
    

#     #Keep this for now
#     # Strip "Bearer " prefix if it exists
#     if token.startswith("Bearer "):
#         token = token.split(" ")[1]

#     #Confirmed it works now
#     try:
#         data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
#         #To show in the 
#         return jsonify({'message': f"Welcome, {data['username']}!"})
#     except jwt.ExpiredSignatureError:
#         return jsonify({'message': 'Token has expired'}), 401
#     except jwt.InvalidTokenError:
#         return jsonify({'message': 'Invalid token'}), 401
    
# if __name__ == '__main__':
#     app.run(debug=True)
    

