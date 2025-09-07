import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { searchMedicines, searchSuggestions, getPopularSearches } from '../services/api';
import './SearchBar.css';

const SearchBar = () => {
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [popularSearches, setPopularSearches] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [recentSearches, setRecentSearches] = useState([]);
  const [showNoResults, setShowNoResults] = useState(false);
  const [suggestionsSource, setSuggestionsSource] = useState('api'); // 'api', 'fallback', 'recent'
  const searchRef = useRef(null);
  const navigate = useNavigate();

  // Загружаем недавние поиски и популярные запросы
  useEffect(() => {
    const saved = localStorage.getItem('recentSearches');
    if (saved) {
      setRecentSearches(JSON.parse(saved));
    }
    
    const loadPopularSearches = async () => {
      try {
        const popular = await getPopularSearches(5);
        setPopularSearches(popular);
      } catch (error) {
        console.error('Ошибка загрузки популярных поисков:', error);
        setPopularSearches([
          'анальгин',
          'парацетамол',
          'ибупрофен',
          'аспирин',
          'витамин c',
          'омега 3',
          'активированный уголь',
          'но-шпа',
          'цитрамон',
          'мезим'
        ]);
      }
    };
    loadPopularSearches();
  }, []);

  // Обработка клика вне поля поиска
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Поиск с задержкой (debounce)
  useEffect(() => {
    const timeoutId = setTimeout(() => {
      if (query.length >= 2) {
        fetchSuggestions();
      } else {
        setSuggestions([]);
        setShowNoResults(false);
      }
    }, 200);
    return () => clearTimeout(timeoutId);
  }, [query]);

  const fetchSuggestions = async () => {
    if (!query.trim()) return;
    
    setIsLoading(true);
    setShowNoResults(false);

    let apiSuggestions = [];

    // Функция для нормализации результатов API
    const normalizeResults = (results) => {
      if (!results || !Array.isArray(results)) return [];
      return results.map(item => ({
        ...item,
        name: item.name.toLowerCase(),
        originalName: item.name
      }));
    };

    // Пробуем разные варианты регистра запроса
    const queryVariations = [
      query,
      query.toLowerCase(),
      query.charAt(0).toUpperCase() + query.slice(1).toLowerCase(),
    ].filter((v, i, a) => a.indexOf(v) === i);

    try {
      for (const q of queryVariations) {
        const results = await searchMedicines(q, { limit: 5 });
        if (results && results.length > 0) {
          apiSuggestions = [...apiSuggestions, ...normalizeResults(results)];
        }

        const suggestionResults = await searchSuggestions(q, 5);
        if (suggestionResults && suggestionResults.length > 0) {
          apiSuggestions = [...apiSuggestions, ...normalizeResults(suggestionResults)];
        }
      }

      apiSuggestions = Array.from(
        new Map(apiSuggestions.map(item => [item.name, item])).values()
      );

      apiSuggestions = apiSuggestions.map(item => ({
        ...item,
        name: item.originalName,
        price: item.price ? String(item.price).replace(/₽/g, '').trim() : '0'
      }));
    } catch (error) {
      console.error('Ошибка при получении подсказок:', error);
    }

    if (apiSuggestions.length > 0) {
      setSuggestions(apiSuggestions.slice(0, 5));
      setSuggestionsSource('api');
    } else {
      const allSuggestions = [
        ...popularSearches
          .filter(popular => {
            const searchTerm = popular.query || popular;
            const queryLower = query.toLowerCase();
            const termLower = searchTerm.toLowerCase();
            return termLower.startsWith(queryLower) || termLower.includes(queryLower);
          })
          .map(popular => ({
            name: popular.query || popular,
            price: 'от 100',
            pharmacy_name: 'Разные аптеки',
            type: 'popular',
            priority: (popular.query || popular).toLowerCase().startsWith(query.toLowerCase()) ? 1 : 2
          })),
        ...recentSearches
          .filter(recent => {
            const queryLower = query.toLowerCase();
            const recentLower = recent.toLowerCase();
            return recentLower.startsWith(queryLower) || recentLower.includes(queryLower);
          })
          .map(recent => ({
            name: recent,
            price: 'от 100',
            pharmacy_name: 'Разные аптеки',
            type: 'recent',
            priority: recent.toLowerCase().startsWith(query.toLowerCase()) ? 1 : 2
          }))
      ];

      const fallbackSuggestions = allSuggestions
        .sort((a, b) => a.priority - b.priority)
        .slice(0, 3);
      setSuggestions(fallbackSuggestions);
      setSuggestionsSource(fallbackSuggestions.length > 0 ? 'fallback' : 'api');
      if (fallbackSuggestions.length === 0) {
        setTimeout(() => setShowNoResults(true), 500);
      }
    }

    setIsLoading(false);
  };

  const handleSearch = async (searchQuery = query) => {
    if (!searchQuery.trim()) return;

    // Нормализуем запрос для поиска (используем lowercase)
    const normalizedQuery = searchQuery.toLowerCase();
    
    // Сохраняем оригинальный запрос в recentSearches
    const newRecent = [...new Set([searchQuery, ...recentSearches])].slice(0, 10);
    setRecentSearches(newRecent);
    localStorage.setItem('recentSearches', JSON.stringify(newRecent));

    // Пробуем поиск с разными вариантами регистра
    let searchResults = [];
    const queryVariations = [
      searchQuery,
      normalizedQuery,
      searchQuery.charAt(0).toUpperCase() + searchQuery.slice(1).toLowerCase(),
    ].filter((v, i, a) => a.indexOf(v) === i);

    try {
      for (const q of queryVariations) {
        const results = await searchMedicines(q, { limit: 10 });
        if (results && results.length > 0) {
          searchResults = [...searchResults, ...results.map(item => ({
            ...item,
            name: item.name,
            price: item.price ? String(item.price).replace(/₽/g, '').trim() : '0'
          }))];
        }
      }

      // Убираем дубликаты по имени
      searchResults = Array.from(
        new Map(searchResults.map(item => [item.name.toLowerCase(), item])).values()
      );
    } catch (error) {
      console.error('Ошибка при поиске:', error);
    }

    // Если результатов нет, пробуем fuzzy search
    if (searchResults.length === 0) {
      try {
        const fuzzyResults = await searchMedicines(normalizedQuery, { fuzzy: true });
        if (fuzzyResults && fuzzyResults.length > 0) {
          searchResults = fuzzyResults.map(item => ({
            ...item,
            name: item.name,
            price: item.price ? String(item.price).replace(/₽/g, '').trim() : '0'
          }));
        }
      } catch (error) {
        console.error('Ошибка при fuzzy поиске:', error);
      }
    }

    // Передаем результаты через состояние URL или напрямую в navigate
    navigate(`/search?q=${encodeURIComponent(normalizedQuery)}`, {
      state: { searchResults: searchResults.length > 0 ? searchResults : null }
    });
    setShowSuggestions(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    handleSearch();
  };

  const handleSuggestionClick = (suggestion) => {
    setQuery(suggestion.name);
    handleSearch(suggestion.name);
  };

  const handleRecentClick = (recent) => {
    setQuery(recent);
    handleSearch(recent);
  };

  const clearRecentSearches = () => {
    setRecentSearches([]);
    localStorage.removeItem('recentSearches');
  };

  return (
    <div className="search-container" ref={searchRef}>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <input
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
              setShowNoResults(false);
            }}
            onFocus={() => setShowSuggestions(true)}
            placeholder="Поиск лекарств, препаратов, активных веществ..."
            className="search-input"
          />
          {isLoading && <div className="search-spinner"></div>}
          <button type="submit" className="search-button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="11" cy="11" r="8"></circle>
              <path d="m21 21-4.35-4.35"></path>
            </svg>
          </button>
        </div>
      </form>

      {showSuggestions && (suggestions.length > 0 || recentSearches.length > 0 || popularSearches.length > 0 || (query.length >= 2 && !isLoading)) && (
        <div className="suggestions-container">
          {suggestions.length > 0 && (
            <div className="suggestions-section">
              <h4>
                {suggestionsSource === 'api' ? 'Найденные товары' : 'Возможные варианты'}
              </h4>
              {suggestions.map((suggestion, index) => (
                <div
                  key={index}
                  className={`suggestion-item ${suggestion.type ? `suggestion-${suggestion.type}` : ''}`}
                  onClick={() => handleSuggestionClick(suggestion)}
                >
                  <div className="suggestion-name">{suggestion.name}</div>
                  <div className="suggestion-price">
                    {suggestion.price}
                    {!suggestion.price.includes('₽') && <span className="currency-symbol">₽</span>}
                  </div>
                  <div className="suggestion-pharmacy">{suggestion.pharmacy_name}</div>
                  {suggestion.type && (
                    <div className="suggestion-type">
                      {suggestion.type === 'popular' ? '🔥' : '🕒'}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}

          {recentSearches.length > 0 && query.length < 2 && (
            <div className="suggestions-section">
              <div className="suggestions-header">
                <h4>Недавние поиски</h4>
                <button onClick={clearRecentSearches} className="clear-button">
                  Очистить
                </button>
              </div>
              {recentSearches.map((recent, index) => (
                <div
                  key={index}
                  className="suggestion-item recent-item"
                  onClick={() => handleRecentClick(recent)}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  {recent}
                </div>
              ))}
            </div>
          )}

          {popularSearches.length > 0 && !query && (
            <div className="suggestions-section">
              <h4>Популярные поиски</h4>
              {popularSearches.map((popular, index) => (
                <div
                  key={index}
                  className="suggestion-item popular-item"
                  onClick={() => handleRecentClick(popular.query || popular)}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                  </svg>
                  {popular.query || popular}
                  {popular.count && (
                    <span className="popular-count">({popular.count})</span>
                  )}
                </div>
              ))}
            </div>
          )}

          {query.length >= 2 && suggestions.length === 0 && !isLoading && showNoResults && (
            <div className="suggestions-section">
              <div className="no-results">
                <p>По запросу "{query}" ничего не найдено</p>
                <p className="search-tips">
                  Попробуйте:
                  <br />• Проверить правильность написания
                  <br />• Использовать более общие термины
                  <br />• Поискать по активному веществу
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default SearchBar;