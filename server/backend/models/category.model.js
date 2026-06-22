const db = require('../config/db');

const getCategoryByUrl = (url) =>
  db.oneOrNone(
    'SELECT * FROM categories WHERE categories_url = $1 AND pharmacy_id = $2',
    [url, 1]
  );

// const getCategoryById = (id) =>
//   db.oneOrNone(
//     'SELECT * FROM categories WHERE id = $1',
//     [id]
//   );

module.exports = {
  getCategoryByUrl,
// getCategoryById,
};
