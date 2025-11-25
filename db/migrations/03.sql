DROP VIEW IF EXISTS v_diff_data;
CREATE OR REPLACE VIEW v_diff_data AS
SELECT cd.contour_id,
       fuel_coefficient,
       l.location_id,
       l.name                                                                             AS location_name,
       l.lat,
       l.lon,
       energy_export,
       energy_import,
       energy_export - LAG(energy_export) OVER (PARTITION BY c.contour_id ORDER BY clock) AS energy_export_diff,
       energy_import - LAG(energy_import) OVER (PARTITION BY c.contour_id ORDER BY clock) AS energy_import_diff,
       CAST(DATE_PART('minute', LEAD(clock) OVER (PARTITION BY c.contour_id ORDER BY clock) - clock) AS varchar) ||
       ' min'                                                                             AS time_diff,

       clock
FROM contour_data cd
         JOIN contour c ON c.contour_id = cd.contour_id
         JOIN locations l ON c.location_id = l.location_id;
