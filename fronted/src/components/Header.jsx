import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="header">
      <div className="banner">
        <img src="/logo.svg" alt="Выгодная аптека" className="banner-logo" />
        <div className="banner-text">
          <h1>Выгодная аптека</h1>
          <p className="banner-slogan">Здоровье доступное каждому</p>
        </div>
      </div>
    </header>
  );
};

export default Header;