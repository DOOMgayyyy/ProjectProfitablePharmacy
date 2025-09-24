import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { searchMedicines } from '../services/api';
import Header from '../components/Header';
import Footer from '../components/Footer';
import SearchBar from '../components/SearchBar';
import SearchResults from '../components/SearchResults';
import SearchFilters from '../components/SearchFilters';
import './SearchResultsPage.css';

const SearchResultsPage = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const params = new URLSearchParams(location.search);
  const query = params.get('q') || '';
  const minPrice = params.get('min_price') || '';
  const maxPrice = params.get('max_price') || '';
  const sortBy = params.get('sort') || 'relevance';

  const [results, setResults] = useState(location.state?.searchResults || []);
  const [filters, setFilters] = useState({ 
    minPrice, 
    maxPrice, 
    sortBy
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const searchProducts = async () => {
      if (!query.trim() || location.state?.searchResults) return;

      setIsLoading(true);
      setError(null);

      try {
        const searchParams = {
          limit: 10,
          ...(filters.sortBy && { sortBy: filters.sortBy }),
        };

        const results = await searchMedicines(query, searchParams);
        
        let filteredResults = results;
        
        // Применяем фильтрацию по цене локально
        if (filters.minPrice) {
          filteredResults = filteredResults.filter(item => 
            parseFloat(item.min_price) >= parseFloat(filters.minPrice)
          );
        }
        
        if (filters.maxPrice) {
          filteredResults = filteredResults.filter(item => 
            parseFloat(item.min_price) <= parseFloat(filters.maxPrice)
          );
        }
        

        switch (filters.sortBy) {
          case 'price_asc':
            filteredResults.sort((a, b) => parseFloat(a.min_price) - parseFloat(b.min_price));
            break;
          case 'price_desc':
            filteredResults.sort((a, b) => parseFloat(b.min_price) - parseFloat(a.min_price));
            break;
          case 'name_asc':
            filteredResults.sort((a, b) => a.name.localeCompare(b.name));
            break;
          case 'name_desc':
            filteredResults.sort((a, b) => b.name.localeCompare(a.name));
            break;
          default:
            break;
        }

        setResults(filteredResults);
      } catch (error) {
        setError(error.message || 'Ошибка при загрузке результатов поиска');
      } finally {
        setIsLoading(false);
      }
    };

    searchProducts();
  }, [query, filters, location.state]);

  const handleFilterChange = (event) => {
    const { name, value } = event.target;
    const newFilters = { ...filters, [name]: value };
    setFilters(newFilters);
    
    // Автоматически применяем фильтры для сортировки и цены
    if (name === 'sortBy' || name === 'minPrice' || name === 'maxPrice') {
      applyFiltersWithNewState(newFilters);
    }
  };

  const applyFiltersWithNewState = (newFilters) => {
    // Получаем исходные данные из location.state или делаем новый запрос
    const originalResults = location.state?.searchResults || results;
    let filteredResults = [...originalResults];
    
    // Применяем фильтрацию по цене
    if (newFilters.minPrice) {
      filteredResults = filteredResults.filter(item => 
        parseFloat(item.min_price) >= parseFloat(newFilters.minPrice)
      );
    }
    
    if (newFilters.maxPrice) {
      filteredResults = filteredResults.filter(item => 
        parseFloat(item.min_price) <= parseFloat(newFilters.maxPrice)
      );
    }
    
    // Применяем сортировку
    switch (newFilters.sortBy) {
      case 'price_asc':
        filteredResults.sort((a, b) => parseFloat(a.min_price) - parseFloat(b.min_price));
        break;
      case 'price_desc':
        filteredResults.sort((a, b) => parseFloat(b.min_price) - parseFloat(a.min_price));
        break;
      case 'name_asc':
        filteredResults.sort((a, b) => a.name.localeCompare(b.name));
        break;
      case 'name_desc':
        filteredResults.sort((a, b) => b.name.localeCompare(a.name));
        break;
      default:
        break;
    }

    setResults(filteredResults);
  };

  const applyFilters = () => {
    applyFiltersWithNewState(filters);
    
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (filters.minPrice) params.append('min_price', filters.minPrice);
    if (filters.maxPrice) params.append('max_price', filters.maxPrice);
    if (filters.sortBy) params.append('sort', filters.sortBy);

    navigate(`/search?${params.toString()}`, { state: { searchResults: results } });
  };

  const clearFilters = () => {
    const clearedFilters = {
      minPrice: '',
      maxPrice: '',
      sortBy: 'relevance'
    };
    setFilters(clearedFilters);
    
    // Получаем исходные данные и применяем только сортировку по релевантности
    const originalResults = location.state?.searchResults || results;
    setResults([...originalResults]);
    
    navigate(`/search?q=${encodeURIComponent(query)}`, { state: { searchResults: originalResults } });
  };

  const hasActiveFilters = filters.minPrice || filters.maxPrice || filters.sortBy !== 'relevance';

  return (
    <div className="search-results-page">
      <Helmet>
        <title>{query ? `Поиск: ${query} | Выгодная аптека` : 'Поиск | Выгодная аптека'}</title>
      </Helmet>
      <Header />
      <SearchBar />
      <div className="search-results-container">
        <div className="search-header">
          <div className="search-header-left">
            <h2>Результаты поиска {query && `"${query}"`}</h2>
            {results.length > 0 && <span className="results-count">{results.length} товаров</span>}
          </div>
          <Link to="/" className="home-button">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
              <polyline points="9,22 9,12 15,12 15,22"/>
            </svg>
            На главную
          </Link>
        </div>

        <div className="search-controls">
          <button 
            className={`filter-toggle ${showFilters ? 'active' : ''}`}
            onClick={() => setShowFilters(!showFilters)}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polygon points="22,3 2,3 10,12.46 10,19 14,21 14,12.46"/>
            </svg>
            Фильтры {hasActiveFilters && <span className="filter-badge">•</span>}
          </button>

          <div className="sort-controls">
            <select 
              name="sortBy" 
              value={filters.sortBy} 
              onChange={handleFilterChange}
              className="sort-select"
            >
              <option value="relevance">По релевантности</option>
              <option value="price_asc">Цена: по возрастанию</option>
              <option value="price_desc">Цена: по убыванию</option>
              <option value="name_asc">Название: А-Я</option>
              <option value="name_desc">Название: Я-А</option>
            </select>
          </div>
        </div>

        <SearchFilters
          filters={filters}
          onFilterChange={handleFilterChange}
          onApplyFilters={applyFilters}
          onClearFilters={clearFilters}
          isVisible={showFilters}
        />

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {isLoading && (
          <div className="loading-container">
            <div className="loading-spinner"></div>
            <p>Поиск товаров...</p>
          </div>
        )}


        <SearchResults 
          results={results}
          isLoading={isLoading}
          error={error}
          query={query}
          onClearFilters={clearFilters}
        />
      </div>
      <Footer />
    </div>
  );
};

export default SearchResultsPage;