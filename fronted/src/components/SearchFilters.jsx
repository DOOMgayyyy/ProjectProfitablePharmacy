import React from 'react';
import './SearchFilters.css';

const SearchFilters = ({ 
  filters, 
  onFilterChange, 
  onApplyFilters, 
  onClearFilters, 
  isVisible = false 
}) => {
  const hasActiveFilters = filters.minPrice || filters.maxPrice || filters.sortBy !== 'relevance';

  return (
    <div className={`search-filters ${isVisible ? 'visible' : ''}`}>
      <div className="filters-header">
        <h3>Фильтры</h3>
        {hasActiveFilters && (
          <button onClick={onClearFilters} className="clear-all-filters">
            Очистить все
          </button>
        )}
      </div>

      <div className="filter-section">
        <label className="filter-label">Сортировка</label>
        <select 
          name="sortBy" 
          value={filters.sortBy} 
          onChange={onFilterChange}
          className="filter-select"
        >
          <option value="relevance">По релевантности</option>
          <option value="price_asc">Цена: по возрастанию</option>
          <option value="price_desc">Цена: по убыванию</option>
          <option value="name_asc">Название: А-Я</option>
          <option value="name_desc">Название: Я-А</option>
          <option value="popularity">По популярности</option>
        </select>
      </div>

      <div className="filter-section">
        <label className="filter-label">Цена</label>
        <div className="price-range">
          <div className="price-input-group">
            <input
              type="number"
              name="minPrice"
              value={filters.minPrice}
              onChange={onFilterChange}
              placeholder="От"
              min="0"
              className="price-input"
            />
            <span className="price-separator">—</span>
            <input
              type="number"
              name="maxPrice"
              value={filters.maxPrice}
              onChange={onFilterChange}
              placeholder="До"
              min="0"
              className="price-input"
            />
          </div>
          <div className="price-presets">
            <button 
              type="button"
              onClick={() => {
                onFilterChange({ target: { name: 'minPrice', value: '0' } });
                onFilterChange({ target: { name: 'maxPrice', value: '100' } });
              }}
              className="price-preset"
            >
              До 100₽
            </button>
            <button 
              type="button"
              onClick={() => {
                onFilterChange({ target: { name: 'minPrice', value: '100' } });
                onFilterChange({ target: { name: 'maxPrice', value: '500' } });
              }}
              className="price-preset"
            >
              100-500₽
            </button>
            <button 
              type="button"
              onClick={() => {
                onFilterChange({ target: { name: 'minPrice', value: '500' } });
                onFilterChange({ target: { name: 'maxPrice', value: '' } });
              }}
              className="price-preset"
            >
              500₽+
            </button>
          </div>
        </div>
      </div>


      <div className="filters-actions">
        <button onClick={onApplyFilters} className="apply-filters-btn">
          Применить фильтры
        </button>
        {hasActiveFilters && (
          <button onClick={onClearFilters} className="clear-filters-btn">
            Сбросить
          </button>
        )}
      </div>
    </div>
  );
};

export default SearchFilters;
