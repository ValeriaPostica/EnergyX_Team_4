import React from "react";
import "./Footer.css";

const Footer = () => (
  <footer className="Footer">
    <div className="container">
      <div className="footer-top">
        <div className="footer-brand">
          <h4 className="fw-bold">EnergyX</h4>
          <p>Smart actions for a sustainable future.</p>
        </div>

        <div className="footer-contacts">
          <h5>Contacts</h5>
          <p><i className="fas fa-envelope me-2"></i> contact@energyx.md</p>
          <p><i className="fas fa-phone me-2"></i> +373 22 123 456</p>
        </div>
      </div>

      <hr className="mt-4 mb-4" />
      <div className="text-center">
        <p>&copy; 2023 EnergyX Moldova. All rights reserved.</p>
      </div>
    </div>
  </footer>
);

export default Footer;
