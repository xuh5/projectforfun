'use client';

export default function Footer() {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="site-footer">
      <div className="footer-container">
        <p className="footer-copyright">
          © {currentYear} <strong>HaichenXu - Project For Fun -project1</strong>. All rights reserved.
        </p>
        <p className="footer-notice">
          Unauthorized copying, distribution, or commercial use is strictly prohibited.
        </p>
      </div>
    </footer>
  );
}

