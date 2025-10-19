## DATA

How data is stored in data.json:

```json
{
    "15005828"/*This number is a valid contor-id*/: {
        "Active Energy Export (3:1-0:2.8.0*255:2)"/*This is the export amount till this moment meaning this number is not a delta*/: 337,
        "Active Energy Import (3:1-0:1.8.0*255:2)"/*Similar to export this number is also not a delta*/: 105918,
        "Clock (8:0-0:1.0.0*255:2)": "01.06.2025 13:00:00",
        "TransFullCoef"/*There are alot of contors wich the coef is not 1*/: 1
    },
    ...
}
```

This data strcuture was later written to a posgres instance with the [schema](schema.sql)

#### How to restore backup
This command only for unix-like systems
```bash
cat db_backup.sql | docker exec -i postgres_db psql -U postgres -d postgres
```

#### How to backup
This command probably as well
```bash
docker exec -t postgres_db \
pg_dump -U postgres -d postgres > data.sql
```

I dont really know an easy todo this commands on windows systems :)
The straitgh forward method would be to use docker cp then pass in the file -f flag for the first command.