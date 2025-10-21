## EnergyX_Team_4

To run the application you need to run two seperate executables one is the api and the second one is the web server

#### Api 
Located in backend/api to run the api you need to first install the packages that are needed i strongly recomend when using python to have a virtual enviroment setup you can setup virtual envirement and install the reqired packages using

```bash
python3 -m venv .venv
```
```bash
.venv\Scripts\Activate.ps1
```
__For the first run__\
This command only works with powershell and not with cmd!
```bash
cd backend/api
```
```bash
pip install -r requirements.txt
```
__For the first run__
```bash
flask run
```

For the frontend you need to have another terminal and run
```bash
cd frontend
```
```bash
npm i
```
```bash
npm run dev
```