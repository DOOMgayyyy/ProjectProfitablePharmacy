import React from 'react';
import './MedicineCard.css';

const MedicineCard = ({ medicine, onClick, showDescription = false }) => {
  return (
    <div className="medicine-card" onClick={() => onClick(medicine.id)}>
      <div className="medicine-header">
        <h3>{medicine.name}</h3>
        {medicine.image_url && (
          <img
            src={medicine.image_url}
            alt={medicine.name}
            className="medicine-image"
          />
        )}
      </div>
      {showDescription && medicine.description && (
        <p className="description">{medicine.description}</p>
      )}
      <div className="prices">
        {medicine.price && (
          <div className="price">
            {medicine.price} руб.
            {medicine.pharmacy_name && (
              <span className="pharmacy"> в {medicine.pharmacy_name}</span>
            )}
            {medicine.amount && <span className="amount">({medicine.amount})</span>}
          </div>
        )}
      </div>
    </div>
  );
};

export default MedicineCard;