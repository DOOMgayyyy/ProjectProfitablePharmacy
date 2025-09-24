import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <Link to="/" className="banner-link">
        <div className="banner">
          <img src="/logo.svg" alt="Выгодная аптека" className="banner-logo" />
          <div className="banner-text">
            <h1>Выгодная аптека</h1>
            <p className="banner-slogan">Здоровье доступное каждому</p>
          </div>
        </div>
      </Link>
    </header>
  );
};

export default Header;