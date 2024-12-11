# Cloud Service Access Management System

A backend system for managing access to cloud services based on user subscriptions.

## Team Members
- Ariel Monterrosas 
- Elizabeth Orellana

## Prerequisites
- Python 3.x
- MySQL server
- pip (Python package installer)

## How to Setup
1. **Clone the Repository**
   ```bash 
   git clone https://github.com/zarakiliz/CPSC449-midterm-project
   cd CPSC449-midterm-project

2. **Create a Virtual Enviornment**
    - python3 -m venv venv
    source venv/bin/activate    
    On Windows, use `venv\Scripts\activate`

3. **Install Dependencies**
    - pip install -r requirements.txt

4. **Set up Environment Variables**
   - Create a `.env` file in the project root with the following entries:
     ```plaintext
     SECRET_KEY=your_secret_key
     MYSQL_USER=your_mysql_user
     MYSQL_PASSWORD=your_mysql_password
     MYSQL_DB=your_mysql_db_name
     MYSQL_HOST=localhost
     ```
   - Replace `your_secret_key`, `your_mysql_user`, `your_mysql_password`, and `your_mysql_db_name` with your actual MySQL credentials.
   
<!-- 5. **Set up MySQL Database**
   - Start your MySQL server and create a database. You can use **MySQL Workbench** or the MySQL command line.
   - Run the following command to create the database:
     ```sql
     CREATE DATABASE `CPSC449-midterm-project`;
     ```
   - Update the `.env` file to match your MySQL credentials.

6. **Create the User Table**
   - Open MySQL Workbench (or use the MySQL command line) and run the following commands to create a `users` table and insert test data:
     ```sql

     CREATE TABLE users (
       id INT AUTO_INCREMENT PRIMARY KEY,
       username VARCHAR(255) UNIQUE NOT NULL,
       password VARCHAR(255) NOT NULL
     );

     INSERT INTO users (username, password) VALUES ('Ariel_Monterrosas', 'password123');
     INSERT INTO users (username, password) VALUES ('Elizabeth_Orellana', 'password456');
     ```
   - This will set up the `users` table with two sample entries.

7. **Run Database Migrations (if necessary)**
   - If additional migrations or database setup steps are needed, include them here or use a tool like Flask-Migrate.

8. **Test the Database Connection**
   - Start the Flask application (see next step) and test the database connection by accessing `/public` or using **Postman** to verify data retrieval. -->

9. **Run the Application**
   - Start the Flask server with the following command:
     ```bash
     flask run
     ```
   - The application should now be running locally on `http://127.0.0.1:5000`.
   - You can test the API endpoints using **Postman** or **cURL**. Make sure your MySQL server is running and that the `.env` file is configured correctly.

# Video Demo
