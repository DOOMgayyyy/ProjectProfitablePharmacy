// server/backend/routes/v1.js
const express = require('express');
const router = express.Router();
const categoryController = require('../controllers/category.controller');

router.get('/catalog/:slug', categoryController.getCategoryMedicines);

module.exports = router;
