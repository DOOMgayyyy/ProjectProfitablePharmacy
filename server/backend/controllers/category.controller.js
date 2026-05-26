// server/backend/controllers/category.controller.js
const { getCategoryByUrl } = require('../models/category.model');
const { getMedicinesByCategoryId } = require('../models/medicine.model');

const getCategoryMedicines = async (req, res, next) => {
  try {
    const { slug } = req.params;

    const category = await getCategoryByUrl(`/catalog/${slug}/`);
    if (!category) {
      return res.status(404).json({ message: 'Категория не найдена' });
    }

    const medicines = await getMedicinesByCategoryId(category.id);

    res.json({
      category,
      medicines,
    });
  } catch (err) {
    next(err);
  }
};

module.exports = {
  getCategoryMedicines,
};
