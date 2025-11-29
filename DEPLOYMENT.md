# Quick Deployment Guide

Follow these steps to get the EnergyX project up and running quickly after cloning the repository.

## Prerequisites

Ensure you have the following installed on your machine:
- **Docker Desktop** (for the database)
- **Python 3.10+**
- **Node.js** (v16+ recommended)

## 1. Start the Database

The project uses a PostgreSQL database running in Docker.

1. Open a terminal in the project root.
2. Navigate to the database folder:
   ```bash
   cd db
   ```
3. Start the database container:
   ```bash
   docker-compose up -d
   ```

## 2. Backend Setup

1. Navigate to the project root.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Mac/Linux
   source .venv/bin/activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r backend/api/requirements.txt
   ```
4. **Configuration**: Create a `.env` file in `backend/api/` and add your API keys:
   ```env
   OPENAI_API_KEY=your_openai_key_here
   LANGCHAIN_API_KEY=your_langchain_key_here
   ```

## 3. Frontend Setup

1. Navigate to the frontend folder:
   ```bash
   cd frontend
   ```
2. Install Node.js dependencies:
   ```bash
   npm install
   ```

## 4. Run the Application

The project includes a helper script `run.py` that starts the Backend (Flask), Frontend (Vite), and IoT Server (Node) simultaneously.

1. Navigate back to the project root.
2. Run the start script:
   ```bash
   python run.py
   ```

## 5. Access the App

Once the script is running, you can access the application at:
- **Frontend**: [http://localhost:5173](http://localhost:5173)
- **Backend API**: [http://localhost:5000](http://localhost:5000)
- **IoT Server**: [http://localhost:4000](http://localhost:4000)

> **Note:** If you are deploying to share with others via VS Code Port Forwarding, ensure port **5173** is set to **Public** visibility.
