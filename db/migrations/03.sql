DROP VIEW IF EXISTS v_diff_data;
CREATE OR REPLACE VIEW v_diff_data AS
	SELECT cd.contour_id,
	       fuel_coefficient,
	       l.location_id,
	       l.name as location_name,
	       l.lat,
	       l.lon,
	       energy_export,
	       energy_import,
	       LEAD(energy_export) OVER (PARTITION BY c.contour_id ORDER BY clock) - energy_export    AS energy_export_diff,
	       LEAD(energy_import) OVER (PARTITION BY c.contour_id ORDER BY clock) -
	       energy_import                                                                          AS energy_import_diff,
	       CAST(DATE_PART('minute', LEAD(clock) OVER (PARTITION BY c.contour_id ORDER BY clock) - clock) AS varchar) || ' min' AS time_diff,

	       clock,
	       LEAD(clock) OVER (PARTITION BY c.contour_id ORDER BY clock)                            AS next_clock
	FROM contour_data     cd
		     JOIN contour c ON c.contour_id = cd.contour_id
			 JOIN locations l ON c.location_id = l.location_id;
