const express = require('express');
const router = express.Router();
const { getCatalog, search, getMedicine } = require('../controllers/category.controller');

router.get('/catalog/:slug', getCatalog);   // каталог категории
router.get('/search',        search);       // поиск
router.get('/medicine/:id',  getMedicine);  // страница товара

module.exports = router;
