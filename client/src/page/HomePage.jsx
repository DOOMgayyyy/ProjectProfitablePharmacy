import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { searchMedicines, getTopProducts } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import SearchBar from '../components/SearchBar';
import MedicineCard from '../components/MedicineCard';
import './HomePage.css';

const HomePage = () => {
  const [recentMedicines, setRecentMedicines] = useState([]);
  const [topProducts, setTopProducts] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      const recentSearches = JSON.parse(saved).slice(0, 5);
      const fetchRecentMedicines = async () => {
        try {
          const medicines = [];
          const seenIds = new Set(); // Для отслеживания уникальных ID
          
          for (const query of recentSearches) {
            const results = await searchMedicines(query, { limit: 1 });
            if (results && results.length > 0) {
              const medicine = results[0];
              // Проверяем, не был ли уже добавлен товар с таким ID
              if (!seenIds.has(medicine.id)) {
                medicines.push(medicine);
                seenIds.add(medicine.id);
              }
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

  // Загрузка топ товаров
  useEffect(() => {
    const loadTopProducts = async () => {
      try {
        const topProductsData = await getTopProducts();
        if (topProductsData && topProductsData.length > 0) {
          setTopProducts(topProductsData.slice(0, 6));
        }
      } catch (error) {
        console.error('Ошибка загрузки топ товаров:', error);
      }
    };

    loadTopProducts();
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
      
      {/* Информационная секция */}
      <div className="info-section">
        <div className="info-cards">
          <div className="info-card">
            <h3>🔍 Найти дешевле</h3>
            <p>Сравнивайте цены в разных аптеках и экономьте на покупках</p>
          </div>
          <div className="info-card">
            <h3>📱 Удобный поиск</h3>
            <p>Быстро находите нужные лекарства по названию или действующему веществу</p>
          </div>
          <div className="info-card">
            <h3>💊 Актуальные цены</h3>
            <p>Всегда актуальная информация о наличии и ценах в аптеках</p>
          </div>
        </div>
      </div>

      {/* Топ товары */}
      {topProducts.length > 0 && (
        <div className="top-products-section">
          <h2>Популярные товары</h2>
          <div className="top-products-grid">
            {topProducts.map((medicine) => (
              <MedicineCard
                key={medicine.id}
                medicine={medicine}
                onClick={handleCardClick}
              />
            ))}
          </div>
        </div>
      )}

      {/* Недавно искали */}
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

      <Footer />
    </div>
  );
};

export default HomePage;