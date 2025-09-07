import React from 'react';
import MedicineCard from './MedicineCard';
import './SearchResults.css';

const SearchResults = ({ results, isLoading, error, query }) => {
  if (isLoading) {
    return (
      <div className="loading-container">
        <div className="loading-spinner"></div>
        <p>Поиск товаров...</p>
      </div>
    );
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  if (!results.length && query) {
    return (
      <div className="no-results">
        <div className="no-results-icon">🔍</div>
        <h3>По запросу "{query}" ничего не найдено</h3>
        <p>Попробуйте:</p>
        <ul>
          <li>Проверить правильность написания</li>
          <li>Использовать более общие термины</li>
          <li>Поискать по активному веществу</li>
          <li>Очистить фильтры</li>
        </ul>
      </div>
    );
  }

  return (
    <div className="search-results-grid">
      {results.map((medicine) => (
        <MedicineCard
          key={medicine.id}
          medicine={medicine}
          onClick={() => window.location.href = `/medicine/${medicine.id}`}
          showDescription={false}
        />
      ))}
    </div>
  );
};

export default SearchResults;