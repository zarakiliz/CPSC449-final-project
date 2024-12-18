# Cloud Service Access Management System

A backend system for managing access to cloud services based on user subscriptions.

## Team Members

- Ariel Monterrosas
- Elizabeth Orellana

## Prerequisites

- Python 3.x
- MongoDB Atlas account
- pip (Python package installer)

## How to Setup

### 1. Clone the Repository

Clone the project repository to your local machine and navigate to the project directory:

```bash
git clone https://github.com/zarakiliz/CPSC449-final-project
cd CPSC449-final-project
```

### 2. Create a Virtual Environment

Set up a virtual environment to manage dependencies:

- On macOS/Linux:
  ```bash
  python3 -m venv venv
  source venv/bin/activate
  ```
- On Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
  ```

### 3. Install Dependencies

Install the required Python packages listed in the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Create a `.env` file in the project root directory with the following entries:

```plaintext
SECRET_KEY=your_secret_key
MONGO_URI=your_mongodb_connection_string
```

Replace `your_secret_key` with a unique secret key for your application and `your_mongodb_connection_string` with the connection string for your MongoDB Atlas database.

### 5. Configure MongoDB Atlas

1. Log in to your [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account and set up a cluster if you don’t already have one.
2. Create a database named `cloudservice` and collections as required by your application.
3. Update the `.env` file with your MongoDB connection string.

Note: If you can't test it out by creating your own database on MongoDB Atlas. Send an email to `eorellana96@csu.fullerton.edu` to be invited to the project's MongoDB Atlas account. 

### 6. Run the Application

Start the FastAPI server locally:

```bash
uvicorn main:app --reload
```

The application will be accessible at `http://127.0.0.1:8000`. You can test the API endpoints using tools like **Postman**.

## Video Demo
