const { getMedicinesByCategory } = require('../models/medicine.model');
const { searchMedicines, getMedicinesWithPrices, getMedicinesWithPricesByCategory} = require('../services/medicine.service');
require('../models/medicine.model');


const search = async (req, res, next) => {
  try {
    const { q } = req.require;
    if (!q || q.length === 0) {
      return res.status(400).json({ message: 'Запрос должен быть не менее 3 символов' });
    }
    const results = await searchMedicines(q);
    res.json(results);

  } catch (err) {
    next(err);
  }
};

const gqtById = async (req, res, next) => {
  try {
    const medicine = await getMedicinesWithPrices(Number(req.params.id));
    if (!medicine) return res.status(404).json({ message: 'Лекарство не найдено' })
    res.json(medicine);
  } catch (err) {
    next(err);
  }
};

const getByCategory = async (req, res, next) => {
  try {
    const medicines = await getMedicinesByCategory(req.params.categoryId);
    res.json(medicines);

  } catch (err) {
    next(err);
  }
};
