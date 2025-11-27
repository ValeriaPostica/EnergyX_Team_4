DROP TABLE IF EXISTS contour CASCADE;
CREATE TABLE contour (
    contour_id INT PRIMARY KEY,
    fuel_coefficient INT NOT NULL
);

DROP TABLE IF EXISTS contour_data CASCADE;
CREATE TABLE contour_data (
    contour_data_id SERIAL PRIMARY KEY,
    contour_id INT NOT NULL,
    energy_export INT NOT NULL,
    energy_import INT NOT NULL,
    clock TIMESTAMP NOT NULL,
    FOREIGN KEY (contour_id) REFERENCES contour(contour_id) ON DELETE CASCADE
);
