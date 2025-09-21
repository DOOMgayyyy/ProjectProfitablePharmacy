import React from 'react';
import { Link } from 'react-router-dom';
import MedicineCard from './MedicineCard';
import './SearchResults.css';

const SearchResults = ({ results, isLoading, error, query, onClearFilters }) => {
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
        <div className="no-results-actions">
          {onClearFilters && (
            <button onClick={onClearFilters} className="clear-all-filters">
              Очистить все фильтры
            </button>
          )}
          <Link to="/" className="home-button">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9,22 9,12 15,12 15,22"/>
            </svg>
            На главную
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="search-results-grid">
      {results.map((medicine) => (
        <MedicineCard
          key={medicine.id}
          medicine={medicine}
          showDescription={false}
          searchQuery={query}
          hidePrice={true}
        />
      ))}
    </div>
  );
};

export default SearchResults;