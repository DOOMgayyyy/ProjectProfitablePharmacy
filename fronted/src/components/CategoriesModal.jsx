import React, { useState, useEffect } from 'react';
import { getCategories } from '../services/api';
import { useNavigate } from 'react-router-dom';
import './CategoriesModal.css';

const CategoriesModal = () => {
  const [open, setOpen] = useState(false);
  const [categories, setCategories] = useState([]);
  const [currentPath, setCurrentPath] = useState([]);
  const [breadcrumbs, setBreadcrumbs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // Моковые данные для категорий (если API не работает)
  const mockCategories = [
    {
      id: 1,
      name: 'Лекарственные препараты',
      name_ru: 'Лекарственные препараты',
      icon: '💊',
      children: [
        {
          id: 11,
          name: 'Обезболивающие',
          name_ru: 'Обезболивающие',
          icon: '🩹',
          children: [
            { id: 111, name: 'Парацетамол', name_ru: 'Парацетамол', icon: '💊' },
            { id: 112, name: 'Ибупрофен', name_ru: 'Ибупрофен', icon: '💊' },
            { id: 113, name: 'Аспирин', name_ru: 'Аспирин', icon: '💊' },
            { id: 114, name: 'Анальгин', name_ru: 'Анальгин', icon: '💊' }
          ]
        },
        {
          id: 12,
          name: 'Противовирусные',
          name_ru: 'Противовирусные',
          icon: '🦠',
          children: [
            { id: 121, name: 'Арбидол', name_ru: 'Арбидол', icon: '💊' },
            { id: 122, name: 'Кагоцел', name_ru: 'Кагоцел', icon: '💊' },
            { id: 123, name: 'Ингавирин', name_ru: 'Ингавирин', icon: '💊' }
          ]
        },
        {
          id: 13,
          name: 'Антибиотики',
          name_ru: 'Антибиотики',
          icon: '🦠',
          children: [
            { id: 131, name: 'Амоксициллин', name_ru: 'Амоксициллин', icon: '💊' },
            { id: 132, name: 'Азитромицин', name_ru: 'Азитромицин', icon: '💊' }
          ]
        }
      ]
    },
    {
      id: 2,
      name: 'Витамины и БАДы',
      name_ru: 'Витамины и БАДы',
      icon: '🥗',
      children: [
        {
          id: 21,
          name: 'Витамины',
          name_ru: 'Витамины',
          icon: '🍊',
          children: [
            { id: 211, name: 'Витамин C', name_ru: 'Витамин C', icon: '🍊' },
            { id: 212, name: 'Витамин D', name_ru: 'Витамин D', icon: '☀️' },
            { id: 213, name: 'Витамины группы B', name_ru: 'Витамины группы B', icon: '🥜' }
          ]
        },
        {
          id: 22,
          name: 'Минералы',
          name_ru: 'Минералы',
          icon: '💎',
          children: [
            { id: 221, name: 'Кальций', name_ru: 'Кальций', icon: '🥛' },
            { id: 222, name: 'Магний', name_ru: 'Магний', icon: '🥜' },
            { id: 223, name: 'Железо', name_ru: 'Железо', icon: '🥩' }
          ]
        },
        {
          id: 23,
          name: 'Омега-3',
          name_ru: 'Омега-3',
          icon: '🐟',
          children: [
            { id: 231, name: 'Рыбий жир', name_ru: 'Рыбий жир', icon: '🐟' },
            { id: 232, name: 'Омега-3 капсулы', name_ru: 'Омега-3 капсулы', icon: '💊' }
          ]
        }
      ]
    },
    {
      id: 3,
      name: 'Уход за телом',
      name_ru: 'Уход за телом',
      icon: '🧴',
      children: [
        {
          id: 31,
          name: 'Косметика',
          name_ru: 'Косметика',
          icon: '💄',
          children: [
            { id: 311, name: 'Кремы для лица', name_ru: 'Кремы для лица', icon: '🧴' },
            { id: 312, name: 'Шампуни', name_ru: 'Шампуни', icon: '🧴' },
            { id: 313, name: 'Зубные пасты', name_ru: 'Зубные пасты', icon: '🦷' }
          ]
        },
        {
          id: 32,
          name: 'Гигиена',
          name_ru: 'Гигиена',
          icon: '🧼',
          children: [
            { id: 321, name: 'Мыло', name_ru: 'Мыло', icon: '🧼' },
            { id: 322, name: 'Гели для душа', name_ru: 'Гели для душа', icon: '🚿' },
            { id: 323, name: 'Дезодоранты', name_ru: 'Дезодоранты', icon: '🧴' }
          ]
        }
      ]
    },
    {
      id: 4,
      name: 'Медицинские изделия',
      name_ru: 'Медицинские изделия',
      icon: '🩺',
      children: [
        {
          id: 41,
          name: 'Перевязочные материалы',
          name_ru: 'Перевязочные материалы',
          icon: '🩹',
          children: [
            { id: 411, name: 'Бинты', name_ru: 'Бинты', icon: '🩹' },
            { id: 412, name: 'Пластыри', name_ru: 'Пластыри', icon: '🩹' },
            { id: 413, name: 'Вата', name_ru: 'Вата', icon: '🩹' }
          ]
        },
        {
          id: 42,
          name: 'Термометры',
          name_ru: 'Термометры',
          icon: '🌡️',
          children: [
            { id: 421, name: 'Электронные', name_ru: 'Электронные', icon: '🌡️' },
            { id: 422, name: 'Ртутные', name_ru: 'Ртутные', icon: '🌡️' }
          ]
        }
      ]
    }
  ];

  useEffect(() => {
    if (open) {
      loadCategories();
    }
  }, [open]);

  const loadCategories = async () => {
    setIsLoading(true);
    try {
      const data = await getCategories();
      if (data && data.length > 0) {
        setCategories(data);
      } else {
        // Используем моковые данные если API не работает
        setCategories(mockCategories);
      }
    } catch (error) {
      console.error('Ошибка загрузки категорий:', error);
      // Используем моковые данные при ошибке
      setCategories(mockCategories);
    } finally {
      setIsLoading(false);
    }
  };

  const getCurrentLevelCategories = () => {
    if (currentPath.length === 0) {
      return categories;
    }
    
    let current = categories;
    for (let i = 0; i < currentPath.length; i++) {
      const pathId = currentPath[i];
      const found = current.find(cat => cat.id === pathId);
      if (found && found.children) {
        current = found.children;
      } else {
        return [];
      }
    }
    return current;
  };

  const handleCategoryClick = (category) => {
    if (category.children && category.children.length > 0) {
      // Это категория с подкатегориями - переходим глубже
      setCurrentPath([...currentPath, category.id]);
      setBreadcrumbs([...breadcrumbs, { id: category.id, name: category.name_ru || category.name }]);
    } else {
      // Это конечная категория - выполняем поиск
      setOpen(false);
      navigate(`/search?category_id=${category.id}`);
      // Сбрасываем путь
      setCurrentPath([]);
      setBreadcrumbs([]);
    }
  };

  const handleBreadcrumbClick = (index) => {
    const newPath = currentPath.slice(0, index + 1);
    const newBreadcrumbs = breadcrumbs.slice(0, index + 1);
    setCurrentPath(newPath);
    setBreadcrumbs(newBreadcrumbs);
  };

  const handleBackClick = () => {
    if (currentPath.length > 0) {
      const newPath = currentPath.slice(0, -1);
      const newBreadcrumbs = breadcrumbs.slice(0, -1);
      setCurrentPath(newPath);
      setBreadcrumbs(newBreadcrumbs);
    }
  };

  const handleClose = () => {
    setOpen(false);
    setCurrentPath([]);
    setBreadcrumbs([]);
  };

  const currentCategories = getCurrentLevelCategories();

  return (
    <>
      <button className="categories-button" onClick={() => setOpen(true)}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>
        Категории
      </button>

      {open && (
        <div className="categories-modal-overlay" onClick={handleClose}>
          <div className="categories-modal" onClick={(e) => e.stopPropagation()}>
            <div className="categories-modal-header">
              <h2>Категории товаров</h2>
              <button className="close-button" onClick={handleClose}>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="18" y1="6" x2="6" y2="18"></line>
                  <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
              </button>
            </div>

            {breadcrumbs.length > 0 && (
              <div className="breadcrumbs">
                <button className="back-button" onClick={handleBackClick}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="15,18 9,12 15,6"></polyline>
                  </svg>
                  Назад
                </button>
                <div className="breadcrumbs-path">
                  {breadcrumbs.map((crumb, index) => (
                    <React.Fragment key={crumb.id}>
                      <button 
                        className="breadcrumb-item"
                        onClick={() => handleBreadcrumbClick(index)}
                      >
                        {crumb.name}
                      </button>
                      {index < breadcrumbs.length - 1 && (
                        <span className="breadcrumb-separator">/</span>
                      )}
                    </React.Fragment>
                  ))}
                </div>
              </div>
            )}

            <div className="categories-content">
              {isLoading ? (
                <div className="loading-categories">
                  <div className="loading-spinner"></div>
                  <p>Загрузка категорий...</p>
                </div>
              ) : (
                <div className="categories-grid">
                  {currentCategories.map((category) => (
                    <div
                      key={category.id}
                      className={`category-item ${category.children && category.children.length > 0 ? 'has-children' : ''}`}
                      onClick={() => handleCategoryClick(category)}
                    >
                      <div className="category-icon">{category.icon}</div>
                      <div className="category-info">
                        <h3 className="category-name">{category.name_ru || category.name}</h3>
                        {category.children && category.children.length > 0 && (
                          <span className="category-count">
                            {category.children.length} подкатегори{category.children.length === 1 ? 'я' : category.children.length < 5 ? 'и' : 'й'}
                          </span>
                        )}
                      </div>
                      {category.children && category.children.length > 0 && (
                        <svg className="arrow-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                          <polyline points="9,18 15,12 9,6"></polyline>
                        </svg>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
};

export default CategoriesModal;