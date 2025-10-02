import React, { useEffect, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import "./SearchPage.css";

const SearchPage = () => {
  const [time, setTime] = useState("08.06.2025 12:00:00");
  const [cityData, setCityData] = useState({});
  const [loading, setLoading] = useState(true);

  const defaultPosition = [47.0, 28.5];
  const zoom = 7;

  useEffect(() => {
    const fetchCityColors = async () => {
      setLoading(true);
      try {
        const response = await fetch("http://localhost:5000/color", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ time }),
        });
        const result = await response.json();
        setCityData(result || {});
      } catch (error) {
        console.error("Error fetching city color data:", error);
        setCityData({});
      } finally {
        setLoading(false);
      }
    };

    fetchCityColors();
  }, [time]);

  if (loading) {
    return (
      <section id="search" className="page-section py-5">
        <div className="container text-center">
          <h2>Loading data...</h2>
        </div>
      </section>
    );
  }

  return (
    <section id="search" className="page-section py-5">
      <div className="container-fluid">
        <h2 className="section-title text-center mb-4">Search Localities</h2>

        <div className="row">
          <div className="col-lg-4 mb-4">
            <div className="mb-4">
              <label className="form-label fw-bold">Select Time</label>
              <input
                type="text"
                className="form-control"
                value={time}
                onChange={(e) => setTime(e.target.value)}
              />
            </div>

            {Object.entries(cityData).map(([city, data]) => (
              <div key={city} className="data-card mb-3">
                <h3 className="data-title">{city}</h3>
                <p className="data-label">Consumption</p>
                <div className="data-value">{data.consumption} MW</div>
                <p className="data-label">Color</p>
                <div
                  className="color-box"
                  style={{
                    width: "30px",
                    height: "30px",
                    backgroundColor: `rgb(${data.color.join(",")})`,
                  }}
                ></div>
                <p className="data-label">Coordinates</p>
                <div className="data-value">
                  {data.coordonates.join(", ")}
                </div>
              </div>
            ))}
          </div>

          <div className="col-lg-8">
            <MapContainer
              center={defaultPosition}
              zoom={zoom}
              style={{ height: "600px", width: "100%" }}
            >
              <TileLayer
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                attribution='&copy; <a href="http://osm.org/copyright">OpenStreetMap</a> contributors'
              />

              {Object.entries(cityData).map(([city, data]) => (
                <CircleMarker
                  key={city}
                  center={data.coordonates}
                  radius={15}
                  pathOptions={{ color: `rgb(${data.color.join(",")})` }}
                >
                  <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                    <div>
                      <strong>{city}</strong>
                      <br />
                      Consumption: {data.consumption} MW
                    </div>
                  </Tooltip>
                </CircleMarker>
              ))}
            </MapContainer>
          </div>
        </div>
      </div>
    </section>
  );
};

export default SearchPage;
