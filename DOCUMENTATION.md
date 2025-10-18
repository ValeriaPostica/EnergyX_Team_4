# Project documentation

## Overview

This repository contains a web application that helps explore and predict electricity consumption. The server side is a Python based API that runs model code and serves data. The client side is a modern JavaScript single page app built with React and Vite. Sample data and a trained model are stored in the data folder for local experiments.

## Architecture

1. Backend

   The backend is a Flask application located in the api folder under backend. It provides endpoints for inference and for reading processed data. Model runner code sits inside the model subfolder.

2. Frontend

   The frontend is a React app under frontend. It uses Vite for local development and can be packaged for mobile with Capacitor.

3. Data and model

   Project sample data and model artifacts live in the data folder under backend. Use those files to reproduce predictions and to test the server locally.

## Quick start

Follow README

## API notes

The backend exposes endpoints that accept JSON and return JSON. The precise endpoint paths and payload shapes are implemented in the api folder. For quick experiments use the app UI or a small fetch request from a browser console.

Example fetch snippet to call a JSON endpoint from the front end or from a small script

```javascript
fetch('/api/predict', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ exampleInput: 123 })
})
.then(r => r.json())
.then(result => console.log(result))
```

Adjust the path above if the backend is mounted at a different base path when deployed.

## Development notes

1. Use the requirements file in backend\base to recreate the Python environment.
2. Keep model artifacts under backend\data\model_data when retraining or swapping models.
3. The frontend uses package.json for scripts and dependencies. Add or update scripts there for CI or packaging tasks.

## Troubleshooting

1. If the backend does not start check that the required Python packages are installed and that the environment variables are set as shown above.
2. If the frontend dev server fails to start check node version and run npm install again.

## Changes did from the last time

1. Implemented RAG for customer AI
2. Improved Provider AI so it gives always 4 answers. It is now faster and corelates with the data on Top Consumers, is no longer random