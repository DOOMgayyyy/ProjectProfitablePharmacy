import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import './Header.css';

export default function Header() {
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  const navLinks = [
    { path: '/', label: 'ГЛАВНАЯ' },
    { path: '/search', label: 'ПОИСК' },
    { path: '/map', label: 'КАРТА АПТЕК' },
  ];

  return (
    <header className="cp-header">
      <div className="cp-header__inner">
        <Link to="/" className="cp-header__logo">
          <span className="logo-bracket">[</span>
          <span className="logo-text glitch" data-text="PHARMA//NET">PHARMA//NET</span>
          <span className="logo-bracket">]</span>
        </Link>

        <nav className={`cp-header__nav ${menuOpen ? 'open' : ''}`}>
          {navLinks.map(l => (
            <Link
              key={l.path}
              to={l.path}
              className={`cp-nav-link ${location.pathname === l.path ? 'active' : ''}`}
              onClick={() => setMenuOpen(false)}
            >
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="cp-header__status">
          <span className="status-dot" />
          <span className="status-text">SYS_ONLINE</span>
        </div>

        <button className="cp-burger" onClick={() => setMenuOpen(!menuOpen)} aria-label="menu">
          <span /><span /><span />
        </button>
      </div>
      <div className="cp-header__line" />
    </header>
  );
}
