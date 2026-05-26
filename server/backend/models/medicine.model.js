const db = require('../config/db');
const { get } = require('../routes/v1');

// Поиск по нормализованному имени через pg_trgm
const searchMedicines = (query) =>
  db.any(
    `SELECT m.*, MIN(p.price) as min_price, COUNT(p.pharmacy_id) as pharmacy_count
    FROM medicines m
    JOIN prices p ON m.id = p.medicine_id
    WHERE similarity(m.normalize_name, $1) > 0.2
    GROUP BY m.id
    ORDER BY similarity(m.normalize_name, $1) DESC
    LIMIT 20`,
    [query]
  );
// детали лекарства + цены по всем аптекам
const getMedicinesWithPrices = (id) =>
  db.task(async (t) => {
    const medicine = await t.OneOrNone(`SELECT * FROM medicines WHERE id = $1`, [id])
    if (!medicine) return null
    const prices = await t.any(
      `SELECT p.price, ph.name AS pharmacy_name, p.medicine_url
      FROM prices p
      JOIN pharmacies ph ON p.pharmacy_id = ph.id
      WHERE p.medicine_id = $1
      ORDER BY p.price`,
      [id]
    );
    return { ...medicine, prices }
  });

const getMedicinesByCategoryId = (categoryId) =>
  db.any(
    `SELECT
        m.id,
        m.name,
        m.description,
        m.manufacturer,
        m.image_url,
        m.category_id,
        MIN(p.price) AS min_price
     FROM medicines m
     LEFT JOIN prices p ON p.medicine_id = m.id
     WHERE m.category_id = $1
     GROUP BY m.id
     ORDER BY m.name`,
    [categoryId]
  );
module.exports = {
  searchMedicines,
  getMedicinesWithPrices,
  getMedicinesByCategory,
}
