import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate, Link } from 'react-router-dom';
import { Helmet } from 'react-helmet';
import { searchMedicines, getCategories } from '../services/api';
import Header from '../components/Header';
import SearchBar from '../components/SearchBar';
import CategoriesModal from '../components/CategoriesModal';
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
  const categoryId = params.get('category_id') || '';
  const sortBy = params.get('sort') || 'relevance';

  const [results, setResults] = useState(location.state?.searchResults || []);
  const [categories, setCategories] = useState([]);
  const [filters, setFilters] = useState({ 
    minPrice, 
    maxPrice, 
    categoryId,
    sortBy,
    inStock: false,
    onlineOnly: false
  });
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const loadCategories = async () => {
      try {
        const cats = await getCategories();
        setCategories(cats || []);
      } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
      }
    };
    loadCategories();
  }, []);

  useEffect(() => {
    const searchProducts = async () => {
      if (!query.trim() || location.state?.searchResults) return;

      setIsLoading(true);
      setError(null);

      try {
        const searchParams = {
          limit: 10,
          ...(filters.minPrice && { minPrice: filters.minPrice }),
          ...(filters.maxPrice && { maxPrice: filters.maxPrice }),
          ...(filters.categoryId && { categoryId: filters.categoryId }),
          ...(filters.sortBy && { sortBy: filters.sortBy }),
        };

        const results = await searchMedicines(query, searchParams);
        
        let filteredResults = results;
        
        if (filters.minPrice) {
          filteredResults = filteredResults.filter(item => 
            parseFloat(item.price) >= parseFloat(filters.minPrice)
          );
        }
        
        if (filters.maxPrice) {
          filteredResults = filteredResults.filter(item => 
            parseFloat(item.price) <= parseFloat(filters.maxPrice)
          );
        }
        
        if (filters.categoryId) {
          filteredResults = filteredResults.filter(item => 
            item.category_id === parseInt(filters.categoryId)
          );
        }

        switch (filters.sortBy) {
          case 'price_asc':
            filteredResults.sort((a, b) => parseFloat(a.price) - parseFloat(b.price));
            break;
          case 'price_desc':
            filteredResults.sort((a, b) => parseFloat(b.price) - parseFloat(a.price));
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
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  const applyFilters = () => {
    const params = new URLSearchParams();
    if (query) params.append('q', query);
    if (filters.minPrice) params.append('min_price', filters.minPrice);
    if (filters.maxPrice) params.append('max_price', filters.maxPrice);
    if (filters.categoryId) params.append('category_id', filters.categoryId);
    if (filters.sortBy) params.append('sort', filters.sortBy);

    navigate(`/search?${params.toString()}`, { state: { searchResults: results } });
  };

  const clearFilters = () => {
    setFilters({
      minPrice: '',
      maxPrice: '',
      categoryId: '',
      sortBy: 'relevance',
      inStock: false,
      onlineOnly: false
    });
    navigate(`/search?q=${encodeURIComponent(query)}`, { state: { searchResults: results } });
  };

  const hasActiveFilters = filters.minPrice || filters.maxPrice || filters.categoryId || filters.sortBy !== 'relevance';

  return (
    <div className="search-results-page">
      <Helmet>
        <title>{query ? `Поиск: ${query} | Выгодная аптека` : 'Поиск | Выгодная аптека'}</title>
      </Helmet>
      <Header />
      <SearchBar />
      <CategoriesModal />
      <div className="search-results-container">
        <div className="search-header">
          <div className="search-header-left">
            <h2>Результаты поиска {query && `"${query}"`}</h2>
            <span className="results-count">{results.length} товаров</span>
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
          categories={categories}
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

        {!isLoading && !error && results.length === 0 && query && (
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
              <button onClick={clearFilters} className="clear-all-filters">
                Очистить все фильтры
              </button>
              <Link to="/" className="home-button">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/>
                  <polyline points="9,22 9,12 15,12 15,22"/>
                </svg>
                На главную
              </Link>
            </div>
          </div>
        )}

        <SearchResults 
          results={results}
          isLoading={isLoading}
          error={error}
          query={query}
        />
      </div>
    </div>
  );
};

export default SearchResultsPage;