const db = require('../config/db');

// Whitelist для сортировки — никогда не подставляй sort/order напрямую в SQL
const SORT_COLUMNS = { name: 'm.name', price: 'min_price' };
const ORDER_DIRS   = { asc: 'ASC',    desc: 'DESC' };

// Карточки по категории + сортировка
const getMedicinesByCategoryId = (categoryId, sort = 'name', order = 'asc', limit = 30, offset = 0) => {
  const col = SORT_COLUMNS[sort]  || 'm.name';
  const dir = ORDER_DIRS[order]   || 'ASC';

  return db.any(
    `SELECT
        m.id,
        m.name,
        m.image_url,
        MIN(p.price) AS min_price
     FROM medicines m
     LEFT JOIN prices p ON p.medicine_id = m.id
     WHERE m.category_id = $1
     GROUP BY m.id
     ORDER BY ${col} ${dir}
     LIMIT $2 OFFSET $3`,
    [categoryId, limit, offset]
  );
};

// Поиск через pg_trgm + сортировка
const searchMedicines = (query, sort = 'name', order = 'asc', limit = 30, offset = 0) => {
  const col = SORT_COLUMNS[sort] || 'm.name';
  const dir = ORDER_DIRS[order]  || 'ASC';

  return db.any(
    `SELECT
        m.id,
        m.name,
        m.image_url,
        MIN(p.price) AS min_price
     FROM medicines m
     LEFT JOIN prices p ON p.medicine_id = m.id
     WHERE similarity(m.normalize_name, $1) > 0.2
     GROUP BY m.id
     ORDER BY ${col} ${dir}
     LIMIT $2 OFFSET $3`,
    [query, limit, offset]
  );
};

// Страница конкретного товара — полные данные + цены всех аптек
const getMedicineById = (id) =>
  db.task(async (t) => {
    const medicine = await t.oneOrNone(
      `SELECT
          m.id,
          m.name,
          m.description,
          m.manufacturer,
          m.image_url
       FROM medicines m
       WHERE m.id = $1`,
      [id]
    );
    if (!medicine) return null;

    const prices = await t.any(
      `SELECT
          p.price,
          p.medicine_url,
          p.date_parse,
          ph.name AS pharmacy_name
       FROM prices p
       JOIN pharmacies ph ON p.pharmacy_id = ph.id
       WHERE p.medicine_id = $1
       ORDER BY p.price ASC`,
      [id]
    );

    return { ...medicine, prices };
  });

module.exports = {
  getMedicinesByCategoryId,
  searchMedicines,
  getMedicineById,
};
