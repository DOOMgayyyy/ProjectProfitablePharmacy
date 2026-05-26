const db = require('../config/db');

// Все категории конкретной аптеки

const getCategoryById = (id) =>
  db.oneOrNone(
    'SELECT * FROM categories WHERE id = $1',
    [id]
  );

const getCategoryByUrl = (url) =>
  db.oneOrNone(
    'SELECT * FROM categories WHERE categories_url = $1',
    [url]
  );

module.exports = {
  getCategoryById,
  getCategoryByUrl,
};
