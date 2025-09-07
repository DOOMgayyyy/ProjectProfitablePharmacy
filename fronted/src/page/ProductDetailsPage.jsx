import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import Header from '../components/Header';

const API_BASE_URL = '/api'; // Proxy will route this to http://localhost:8001

const ProductDetailsPage = () => {
  const { id } = useParams();
  const [product, setProduct] = useState(null);

  useEffect(() => {
    axios.get(`${API_BASE_URL}/medicine/${id}`)
      .then(response => setProduct(response.data.medicine))
      .catch(error => console.error('Ошибка загрузки товара:', error));
  }, [id]);

  if (!product) return <div>Загрузка...</div>;

  return (
    <div>
      <Header />
      <h2>{product.name}</h2>
      <p>{product.description}</p>
      <img src={product.image_url} alt={product.name} style={{ width: '200px' }} />
      <p>Цена: {product.price} руб. (в аптеке {product.pharmacy_name})</p>
    </div>
  );
};

export default ProductDetailsPage;