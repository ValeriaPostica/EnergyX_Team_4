DROP VIEW IF EXISTS v_data;
CREATE OR REPLACE VIEW v_data AS
	SELECT c.contour_id,
	       c.fuel_coefficient,
	       cd.energy_export,
	       cd.energy_import,
	       cd.clock,
	       l.name,
	       l.lat,
	       l.lon
    FROM contour c
    JOIN contour_data cd on c.contour_id = cd.contour_id
    JOIN locations l on l.location_id = c.location_id
    ORDER BY contour_id, clock

