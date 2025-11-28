## EnergyX_Team_4
### This is how i run the project, if you have troubles look further, 
### If any questions encountered just ask me :)

## Run first time
python3 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend/api/requirements.txt

$env:OPENAI_API_KEY= "OpenAi key"

$env:LANGCHAIN_API_KEY= "langchain key"

python backend/api/create_users_table.py

cd frontend
npm install
cd ..
cd db
docker compose up -d
cd ..
python run.py

## Run
.venv\Scripts\Activate.ps1
cd db
docker compose up -d
cd ..
python3 run.py

## Stop
*Press Ctrl + C
cd db
docker compose down

# Now shortly the main changes I made
- Reworked the LSTM model: it now accepts an input array and produces predictions. I kept the old provider function because the database currently lacks location data.
- User-level predictions now use the database (model saved as `model.pt`). The older provider model remains as `model_old.pt`.
- `api/retrieve_data.py` contains helpers that retrieve data from the database. `get_series()` returns the hourly series (meter readings or consumption values) for a specific meter ID, and `general_info()` computes current total usage and a simple metric for the number of smart-metered homes.
- Ignore `db/test.py`, `db/series.py` and `get_day_data.py` — they were created for quick local tests and can be removed if you don't need them.
- I added IoT server activation in `run.py` for the Smart House page. The page runs a short simulation (about 1 minute) demonstrating how temperature changes affect energy usage.
- Thus now I am using the new data for costumers and also made Smart House simulation.
- Added a "Device Simulation" workflow that combines `/pred/simulate` on the backend with a new frontend page so consumers can schedule devices, compare baseline versus simulated demand, and estimate cost impact in MDL.
- Extended the simple log handler to persist numbered entries `0)` through `4)` so RAG-aware assistants can read the latest device simulation summary alongside the existing monitoring events.

## Changes made during recent edits(more small and detailed)
The following files were modified or added while working on the project. This list helps you understand what changed and how to run/verify the edits.

- backend/api/retrieve_data.py
	- Updated `diff()` to clamp negative differences to 0.0 (energy usage can't be negative).
	- Added optional day filtering in some variants used by other scripts.
- backend/api/retrieve_user_id_data.py
	- Added and reverted some variants; primary purpose is to fetch whole-hour `energy_import` rows and compute diffs.
- backend/api/model/xlstm_runner.py
	- Fixed imports to use package-relative import for `retrieve_user_id_data`.
- backend/api/retrieve_data.py and backend/api/retrieve_user_id_data.py
	- Added parameterized SQL queries using SQLAlchemy `text()` to safely query `interpolated.contour_data`.
- db/series.py and db/test.py
	- Added helper scripts that fetch hourly `energy_import` rows for a contour id and print/return the series.
- frontend/src/components/HourlyConsumption.jsx
	- Fixed a client-side bug: parse fetch response JSON, guard and pad/truncate arrays to 24 values, and adjusted labels to 24 hours.
	- frontend/src/components/DeviceSimulation.jsx & DeviceSimulation.css
	- New consumer-facing page for configuring device intervals, running `/pred/simulate`, and visualizing results against the baseline forecast.
- backend/api/app.py (`/pred/simulate`)
	- Accepts URL-encoded JSON schedules, normalizes them to tuples, and returns clean JSON errors for invalid payloads.
- backend/api/simple_log_handler.py
	- Records up to five numbered log categories so the new simulation summary (`4)Device simulation ...`) is preserved for retrieval-augmented reasoning.
- frontend/package.json
	- Fixed duplicate `dev` script. Added `server` and `server:dev` scripts so the Node server and vite dev server can be run separately.
- run.py
	- Improved orchestrator to start both frontend dev (vite) and frontend server (Node) plus the Flask backend and stream their logs.

## Recommended environment & prerequisites
These are the minimal tools and versions used when running and testing the project locally on Windows (PowerShell):

- Python 3.10+ (used to create and run the virtual environment)
- Node.js 18+ and npm
- Docker & Docker Compose (for database container under `db/`)
- A Python virtual environment (venv) activated before running backend

Ensure the following are available on PATH: `python`, `pip`, `npm`, `docker` (and `docker compose`).

## Detailed Windows PowerShell run instructions (recommended)
Follow these steps the first time you run the project and to run it during development.

1) Create and activate Python venv (one-time):

```powershell
cd EnergyX_Team_4
python -m venv .venv
. .venv\Scripts\Activate.ps1
```

2) Install backend Python deps, frontend deps, and start DB container:

```powershell
pip install -r backend/api/requirements.txt
cd frontend
npm install
cd ..
cd db
docker compose up -d
cd ..
```

3) Start everything with the orchestrator (recommended):

```powershell
# from repo root with venv active
python run.py
```

This will attempt to run:
- `npm run dev` (vite frontend dev server)
- `npm run server` (Express Node server at frontend/server.js)
- `flask run` (the Flask backend from `backend/api`)

4) Alternatively run components separately:

- Frontend vite (hot-reload UI):
```powershell
cd frontend
npm run dev
```
- Frontend Node server (API used by some tests or local mock endpoints):
```powershell
cd frontend
npm run server       # production-mode Node server
npm run server:dev   # nodemon auto-restart on change (requires nodemon installed)
```
- Backend (Flask): activate venv and run inside `backend/api` (you can set FLASK_APP explicitly if needed):
```powershell
cd backend\api
$env:FLASK_APP = 'app'
flask run
```

Note: `run.py` tries to detect the venv and will use the venv's `flask` executable when available. Using `run.py` avoids manual FLASK_APP handling in many cases.

## How to run mobile version

Follow these in order whenever you need the Android build to talk to your local backend.

1. **Start backend stack**
	```powershell
	cd EnergyX_Team_4
	.\.venv\Scripts\Activate.ps1
	cd backend\api
	flask run
	```
	Leave the window open; Flask must stay running on port 5000.

2. **(Optional) Mock IoT server**
	```powershell
	cd EnergyX_Team_4\frontend
	npm install    # first time only
	npm run server
	```
	Provides `/api/status` on port 4000 for the Smart House screen.

3. **Point frontend to accessible hosts**
	Create `frontend/src/config.js` so components import shared URLs:
	```javascript
	export const API_BASE_URL = "http://10.0.2.2:5000"; // use LAN IP for a real device
	export const IOT_BASE_URL = "http://10.0.2.2:4000";
	```
	Replace direct `http://localhost:5000` / `4000` usage with these constants.

4. **Allow cleartext HTTP in Android**
	Edit `frontend/android/app/src/main/AndroidManifest.xml` `<application>` tag:
	```xml
	<application
		 android:usesCleartextTraffic="true"
		 ...>
	```

5. **Build web assets and sync Capacitor**
	```powershell
	cd EnergyX_Team_4\frontend
	npm run build
	npx cap sync android
	```

6. **Expose backend ports to emulator**
	Ensure an emulator or USB-debuggable device is connected, then:
	```powershell
	adb devices          # confirms the target is visible
	adb reverse tcp:5000 tcp:5000
	adb reverse tcp:4000 tcp:4000
	```
	Skip the `adb reverse` commands when using a physical device with LAN URLs.

7. **Open Android Studio**
	```powershell
	npx cap open android
	```
	Pick an emulator/device in Android Studio and click Run. Verify API requests in Logcat and the Flask console.

8. **Live reload (optional)**
	```powershell
	npm run dev
	npx cap run android -l --external --host <PC-IP>
	```
	Keeps the React app updating while the native shell stays open.

## Database and connection
- The project uses a Postgres database schema located under `db/`. Start it with:
```powershell
cd db
docker compose up -d
```
- The default connection string used in the repo is `postgresql://postgres:11111@localhost:5433/postgres`. If your DB uses different credentials or port, update the scripts that create engines (e.g. `backend/api/retrieve_data.py`, `backend/api/retrieve_user_id_data.py`, `db/test.py`, `db/series.py`).

## How to inspect table columns (quick)
Use psql or the included Python helper pattern — from repo root run:

PowerShell + psql:
```powershell
psql "postgresql://postgres:11111@localhost:5433/postgres" -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_schema='interpolated' AND table_name='contour_data' ORDER BY ordinal_position;"
```

Python helper snippet (works inside repo using SQLAlchemy):
```python
from sqlalchemy import create_engine, inspect
engine = create_engine("postgresql://postgres:11111@localhost:5433/postgres")
insp = inspect(engine)
cols = insp.get_columns('contour_data', schema='interpolated')
for c in cols:
		print(c['name'], c.get('type'))
```

## Verification & smoke-tests
- Open browser to Vite dev server URL (usually http://localhost:5173) after `npm run dev`.
- Check Express server: http://localhost:4000/api/status
- Check Flask backend endpoints used by frontend, for example `http://localhost:5000/diff/<userId>/<day>` or `http://localhost:5000/pred/<userId>`.

## Troubleshooting
- If `npm run server` fails, run `npm install` in the `frontend` folder and ensure `nodemon` is installed (dev dependency). Use `npm run server:dev` to run with nodemon.
- If Flask import errors appear (ModuleNotFoundError), confirm you activated the `.venv` virtual environment and that `backend/api` is in Python path; prefer using `run.py` which handles detection.
- If DB connection fails, verify Docker container is running and ports match the connection string.
