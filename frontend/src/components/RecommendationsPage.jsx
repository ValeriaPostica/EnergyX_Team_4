import React, { useEffect, useState } from "react";
import "./RecommendationsPage.css";

const RecommendationsPage = () => {
  const [recommendations, setRecommendations] = useState([]);

  useEffect(() => {
    const fetchRecommendations = async () => {
      try {
        const response = await fetch("http://localhost:5000/ai");
        const data = await response.json();
        setRecommendations(data);
      } catch (error) {
        console.error("Error fetching recommendations:", error);
      }
    };

    fetchRecommendations();
  }, []);

  return (
    <section id="recommendations" className="page-section py-5">
      <div className="container">
        <h2 className="section-title text-center">Recommendations</h2>

        <div className="recommendations-grid">
          {recommendations.map((rec, index) => (
            <div key={index} className="alert-card">
              <h4 className="alert-title">
                <i
                  className={`bi ${
                    index % 4 === 0
                      ? "bi-exclamation-triangle-fill text-danger"
                      : index % 4 === 1
                      ? "bi-activity text-warning"
                      : index % 4 === 2
                      ? "bi-lightning-fill text-primary"
                      : "bi-sun-fill text-success"
                  }`}
                ></i>{" "}
                {rec.title.replace(/^Title:\s*/, "")}
              </h4>
              <p>{rec.recommendation.replace(/^Recommendation:\s*/, "")}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default RecommendationsPage;
