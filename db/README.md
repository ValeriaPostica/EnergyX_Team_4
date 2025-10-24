This folder contains [docker-compose](docker-compose.yaml) to run the database

To run
```bash
docker compose up -d
```

To stop it
```bash
docker compose down
```

This commands work on every system...

The included [data.sql](data.sql) file is the last dump with the interpolated data and a usefull view for visualizing the energy_import / energy_export over time.

This one example to a connection string for the given docker-compose file
```bash
postgresql://postgres:11111@localhost:5433/postgres
```