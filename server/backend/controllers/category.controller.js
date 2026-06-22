const { getCategoryByUrl } = require('../models/category.model');
const { getMedicinesByCategoryId, searchMedicines, getMedicineById } = require('../models/medicine.model');

// GET /api/v1/catalog/:slug?sort=name&order=asc
const getCatalog = async (req, res, next) => {
  try {
    const { slug } = req.params;
    const { sort, order } = req.query;
    const page  = Number(req.query.page)  || 1;
    const limit = Number(req.query.limit) || 20;
    if (limit > 200) return res.status(400).json({ message: 'Введите не более 200 товаров на странице' });

    const offset = (page - 1) * limit;
    const category = await getCategoryByUrl(`/catalog/${slug}/`);
    if (!category) return res.status(404).json({ message: 'Категория не найдена' });

    const medicines = await getMedicinesByCategoryId(category.id, sort, order, limit, offset);

    res.json({ category, medicines });
  } catch (err) {
    next(err);
  }
};

// GET /api/v1/search?q=аспирин&sort=price&order=asc
const search = async (req, res, next) => {
  try {
    const { q, sort, order } = req.query;
    const page  = Number(req.query.page)  || 1;
    const limit = Number(req.query.limit) || 20;
    if (limit > 200) return res.status(400).json({ message: 'Введите не более 200 товаров на странице' });
    if (!q || q.trim().length < 2)
      return res.status(400).json({ message: 'Введите не менее 2 символов' });
    const offset = (page - 1) * limit;
    const medicines = await searchMedicines(q.trim(), sort, order, limit, offset);
    res.json({ medicines });
  } catch (err) {
    next(err);
  }
};

// GET /api/v1/medicine/:id
const getMedicine = async (req, res, next) => {
  try {
    const medicine = await getMedicineById(Number(req.params.id));
    if (!medicine) return res.status(404).json({ message: 'Товар не найден' });
    res.json(medicine);
  } catch (err) {
    next(err);
  }
};

module.exports = { getCatalog, search, getMedicine };
