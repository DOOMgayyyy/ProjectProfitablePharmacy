
import axios from 'axios';

// Универсальное определение API_URL для Node.js и Vite
let API_URL = '/api';
try {
  if (import.meta && import.meta.env && import.meta.env.VITE_API_URL) {
    API_URL = import.meta.env.VITE_API_URL;
  }
} catch (e) {
  if (typeof process !== 'undefined' && process.env && process.env.VITE_API_URL) {
    API_URL = process.env.VITE_API_URL;
  }
}

const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Интерцептор ошибок
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    if (error.response?.status === 404) {
      throw new Error('Товар не найден');
    } else if (error.response?.status === 500) {
      throw new Error('Ошибка сервера. Попробуйте позже.');
    } else if (error.code === 'ECONNABORTED') {
      throw new Error('Превышено время ожидания. Проверьте соединение.');
    } else {
      throw new Error('Произошла ошибка при загрузке данных');
    }
  }
);

// 🔍 Поиск лекарств
export const searchMedicines = async (query, filters = {}) => {
  try {
    const params = new URLSearchParams();
    params.append('q', query);

    if (filters.minPrice) params.append('min_price', filters.minPrice);
    if (filters.maxPrice) params.append('max_price', filters.maxPrice);
    if (filters.categoryId) params.append('category_id', filters.categoryId);
    if (filters.limit) params.append('limit', filters.limit);

    const response = await apiClient.get(`/search?${params.toString()}`);
    return response.data;
  } catch (error) {
    console.error('Search error:', error);
    throw error;
  }
};

// ✍️ Автодополнение
export const searchSuggestions = async (query) => {
  try {
    const response = await apiClient.get('/autocomplete', {
      params: { q: query }
    });
    return response.data;
  } catch (error) {
    console.error('Suggestions error:', error);
    return [];
  }
};

// 📦 Детали лекарства
export const getMedicineDetails = async (id) => {
  try {
    const response = await apiClient.get(`/medicine/${id}`);
    return response.data;
  } catch (error) {
    console.error('Details error:', error);
    throw error;
  }
};

// 📂 Список категорий
export const getCategories = async () => {
  try {
    const response = await apiClient.get('/categories');
    return response.data;
  } catch (error) {
    console.error('Categories error:', error);
    return [];
  }
};

//
// ⚠️ Остальное — заглушки, чтобы фронт не падал
//

// Похожие товары
export const searchSimilar = async () => {
  return [];
};

// Поиск по категории
export const searchByCategory = async () => {
  return [];
};

// Поиск по активному веществу
export const searchByActiveIngredient = async () => {
  return [];
};

// Подкатегории
export const getSubcategories = async () => {
  return [];
};

// Иерархия категорий
export const getCategoryHierarchy = async () => {
  return [];
};

// Топ-товары
export const getTopProducts = async () => {
  try {
    const response = await apiClient.get('/top-products');
    return response.data;
  } catch (error) {
    console.error('Top products error:', error);
    return [];
  }
};

// Популярные поиски
export const getPopularSearches = async () => {
  return [];
};

// Fuzzy search
export const fuzzySearch = async () => {
  return [];
};

// Статистика поиска
export const getSearchStats = async () => {
  return null;
};

// Экспортируем axios клиент напрямую
export { apiClient };
