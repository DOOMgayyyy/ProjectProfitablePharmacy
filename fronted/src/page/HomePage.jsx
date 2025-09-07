import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { searchMedicines } from '../services/api';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import CategoriesModal from '../components/CategoriesModal';
import MedicineCard from '../components/MedicineCard';
import './HomePage.css';

const HomePage = () => {
  const [recentMedicines, setRecentMedicines] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      const recentSearches = JSON.parse(saved).slice(0, 5);
      const fetchRecentMedicines = async () => {
        try {
          const medicines = [];
          for (const query of recentSearches) {
            const results = await searchMedicines(query, { limit: 1 });
            if (results && results.length > 0) {
              medicines.push(results[0]);
            }
          }
          setRecentMedicines(medicines.slice(0, 5));
        } catch (error) {
          console.error('Ошибка загрузки недавних товаров:', error);
        }
      };
      fetchRecentMedicines();
    }
  }, []);

  const handleCardClick = (id) => {
    navigate(`/medicine/${id}`);
  };

  return (
    <div className="home-page">
      <Helmet>
        <title>Главная | Выгодная аптека</title>
      </Helmet>
      <Header />
      <SearchBar />
      <CategoriesModal />
      {recentMedicines.length > 0 && (
        <div className="recent-searches-section">
          <h2>Недавно искали</h2>
          <div className="recent-searches-grid">
            {recentMedicines.map((medicine) => (
              <MedicineCard
                key={medicine.id}
                medicine={medicine}
                onClick={handleCardClick}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default HomePage;