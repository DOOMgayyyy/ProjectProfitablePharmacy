import React from 'react';
import { useNavigate } from 'react-router-dom';
import './MedicineCard.css';

const MedicineCard = ({ medicine, showDescription = false, searchQuery = null, hidePrice = false }) => {
  const navigate = useNavigate();
  
  // Поддержка двух форматов данных: /search и /medicine/{medicine_id}
  const details = medicine.details || medicine; // Для /medicine/{medicine_id} используем details
  const prices = medicine.prices || []; // Для /medicine/{medicine_id} используем prices

  const handleCardClick = () => {
    navigate(`/medicine/${details.id}`, { 
      state: { 
        searchQuery: searchQuery,
        fromSearch: true 
      } 
    });
  };

  return (
    <div className="medicine-card" onClick={handleCardClick}>
      <div className="medicine-header">
        <h3>{details.name}</h3>
        {details.image_url && (
          <img
            src={details.image_url}
            alt={details.name}
            className="medicine-image"
          />
        )}
      </div>
      {showDescription && details.description && (
        <p className="description">{details.description}</p>
      )}
      {!hidePrice && (
        <div className="prices">
          {prices.length > 0 ? (
            // Для /medicine/{medicine_id} отображаем список цен
            prices.map(price => (
              <div key={price.pharmacy_name} className="price">
                {price.price} руб.
                <span className="pharmacy"> в {price.pharmacy_name}</span>
              </div>
            ))
          ) : details.min_price ? (
            // Для /search отображаем минимальную цену
            <div className="price">
              {details.min_price} руб.
              {details.pharmacy_count && (
                <span className="pharmacy"> в {details.pharmacy_count} аптеках</span>
              )}
            </div>
          ) : (
            <div className="price">Цена недоступна</div>
          )}
        </div>
      )}
    </div>
  );
};

export default MedicineCard;