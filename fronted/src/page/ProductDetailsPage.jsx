import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link, useLocation } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { getMedicineDetails } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import './ProductDetailsPage.css';

const ProductDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const location = useLocation();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  
  // Получаем информацию о поисковом запросе из state
  const searchQuery = location.state?.searchQuery;
  const fromSearch = location.state?.fromSearch;

  // Функция для обрезки описания до 2-3 предложений
  const getTruncatedDescription = (description) => {
    if (!description) return '';
    const sentences = description.split(/[.!?]+/).filter(s => s.trim().length > 0);
    return sentences.slice(0, 3).join('. ') + (sentences.length > 3 ? '...' : '');
  };

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        setLoading(true);
        setError(null);
        console.log('Fetching medicine details for ID:', id);
        const response = await getMedicineDetails(id);
        console.log('API response:', response);
        setProduct({
          ...response.details,
          prices: response.prices
        });
      } catch (err) {
        console.error('Error fetching medicine details:', err);
        setError(err.message || 'Ошибка при загрузке товара');
      } finally {
        setLoading(false);
      }
    };

    fetchProduct();
  }, [id]);

  if (loading) {
    return (
      <div className="product-details-page">
        <Header />
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Загрузка товара...</p>
        </div>
        <Footer />
      </div>
    );
  }

  if (error) {
    return (
      <div className="product-details-page">
        <Header />
        <div className="error-container">
          <h2>Ошибка загрузки</h2>
          <p>{error}</p>
          {fromSearch && searchQuery ? (
            <Link to={`/search?q=${encodeURIComponent(searchQuery)}`} className="back-button">
              Вернуться к поиску "{searchQuery}"
            </Link>
          ) : (
            <Link to="/" className="back-button">
              Вернуться на главную
            </Link>
          )}
        </div>
        <Footer />
      </div>
    );
  }

  if (!product) {
    return (
      <div className="product-details-page">
        <Header />
        <div className="not-found-container">
          <h2>Товар не найден</h2>
          <p>Запрашиваемый товар не существует или был удален</p>
          {fromSearch && searchQuery ? (
            <Link to={`/search?q=${encodeURIComponent(searchQuery)}`} className="back-button">
              Вернуться к поиску "{searchQuery}"
            </Link>
          ) : (
            <Link to="/" className="back-button">
              Вернуться на главную
            </Link>
          )}
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="product-details-page">
      <Helmet>
        <title>{product.name} | Выгодная аптека</title>
        <meta name="description" content={product.description || `Купить ${product.name} по выгодной цене в аптеках`} />
      </Helmet>
      
      <Header />
      
      <div className="product-details-container">
        <div className="product-main">
          <div className="product-image-section">
            {product.image_url ? (
              <img
                src={product.image_url}
                alt={product.name}
                className="product-image"
              />
            ) : (
              <div className="product-image-placeholder">
                <svg width="80" height="80" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1">
                  <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21,15 16,10 5,21"/>
                </svg>
                <span>Изображение недоступно</span>
              </div>
            )}
          </div>
          
          <div className="product-info-section">
            <h1 className="product-title">{product.name}</h1>
            
            {product.prices && product.prices.length > 0 && (
              <div className="pharmacies-section">
                <h3>Доступно в аптеках:</h3>
                <div className="pharmacies-list">
                  {product.prices.map((price, index) => (
                    <div key={index} className="pharmacy-item">
                      <div className="pharmacy-info">
                        <span className="pharmacy-name">{price.pharmacy_name}</span>
                        <span className="pharmacy-price">{price.price} руб.</span>
                      </div>
                      {price.availability && (
                        <span className="availability-status available">В наличии</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {product.description && (
              <div className="description-section">
                <h3>Описание:</h3>
                <div className="product-description">
                  {isDescriptionExpanded ? product.description : getTruncatedDescription(product.description)}
                </div>
                {product.description.split(/[.!?]+/).filter(s => s.trim().length > 0).length > 3 && (
                  <button 
                    className="expand-description-btn"
                    onClick={() => setIsDescriptionExpanded(!isDescriptionExpanded)}
                  >
                    {isDescriptionExpanded ? 'Свернуть' : 'Читать полностью'}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
        
        <div className="product-actions">
          {fromSearch && searchQuery ? (
            <Link to={`/search?q=${encodeURIComponent(searchQuery)}`} className="back-to-search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M19 12H5M12 19l-7-7 7-7"/>
              </svg>
              Вернуться к поиску "{searchQuery}"
            </Link>
          ) : (
            <Link to="/" className="back-to-search">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                <polyline points="9,22 9,12 15,12 15,22"/>
              </svg>
              На главную
            </Link>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default ProductDetailsPage;