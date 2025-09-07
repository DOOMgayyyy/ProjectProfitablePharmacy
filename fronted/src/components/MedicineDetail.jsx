import React, { useState, useEffect } from 'react';
import { getMedicineDetails } from '../services/api';

const MedicineDetail = ({ medicineId, onBack }) => {
  const [medicine, setMedicine] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchMedicine = async () => {
      try {
        setLoading(true);
        const data = await getMedicineDetails(medicineId);
        setMedicine(data);
      } catch (err) {
        setError('Не удалось загрузить детали лекарства');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchMedicine();
  }, [medicineId]);

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return <div>{error}</div>;
  }

  if (!medicine) {
    return <div>Лекарство не найдено</div>;
  }

  return (
    <div className="medicine-detail">
      <button onClick={onBack}>← Назад к результатам</button>
      <h2>{medicine.medicine.name}</h2>
      <div className="detail-content">
        {medicine.medicine.image_url && (
          <img 
            src={medicine.medicine.image_url} 
            alt={medicine.medicine.name} 
            className="detail-image"
          />
        )}
        <div className="detail-info">
          <p>{medicine.medicine.description}</p>
          <h3>Наличие в аптеках:</h3>
          <ul className="prices-list">
            {medicine.prices.map((priceInfo, index) => (
              <li key={index}>
                <span className="pharmacy">{priceInfo.pharmacy_name}</span>: 
                <span className="price">{priceInfo.price} руб.</span>
                <span className="address"> ({priceInfo.address || 'Адрес не указан'})</span>
                <span className="updated"> (обновлено: {new Date(priceInfo.last_updated).toLocaleDateString()})</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default MedicineDetail;