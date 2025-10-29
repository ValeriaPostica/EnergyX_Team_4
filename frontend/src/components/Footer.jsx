import React, { useState, useEffect, useRef } from "react";
import "./Footer.css";

const Footer = () => {
  const [isVisible, setIsVisible] = useState(false);
  const footerRef = useRef(null);

  useEffect(() => {
    const handleScroll = () => {
      const isAtBottom = 
        window.innerHeight + window.scrollY >= document.body.offsetHeight - 100;
      setIsVisible(isAtBottom);
    };

    window.addEventListener("scroll", handleScroll);
    handleScroll();

    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      {/* Invisible spacer that maintains the space */}
      <div 
        style={{ 
          height: footerRef.current ? footerRef.current.offsetHeight : '100px',
          width: '100%'
        }} 
      />
      
      {/* Actual footer */}
      <footer 
        ref={footerRef} 
        className={`Footer ${isVisible ? 'visible' : ''}`}
        style={{ 
          position: 'fixed',
          bottom: isVisible ? 0 : '-100px',
          left: 0,
          right: 0,
          transition: 'bottom 0.3s ease-in-out',
          zIndex: 1000
        }}
      >
        <div className="container">
          <div className="footer-top">
            <div className="footer-brand">
              <h4 className="fw-bold">EnergiX</h4>
              <p style ={{width: "200px"}}>Smart actions for a sustainable future.</p>
            </div>

            <div className="footer-contacts">
              <h5 style ={{padding: "0 0 0 0.5rem"}}>Contacts</h5>
              <p><i className="fas fa-envelope me-2"></i> contact@energix.md</p>
              <p><i className="fas fa-phone me-2"></i> +373 22 123 456</p>
            </div>
          </div>

          <hr className="mt-4 mb-4" />
          <div className="text-center">
            <p>&copy; 2023 EnergiX Moldova. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </>
  );
};

export default Footer;