// тут пишется так называемое api и в общем путь url и какой js файл исполняется
//
const express = require("express");
const router = express.Router();




//********* API DOCUMENTATION **********
router.use(
  "/docs/api.json",
  express.static(path.join(__dirname, "/../public/v1/documentation/api.json"))
);
module.exports = router;

const CategoryController = require("../controllers/CategoryController");

router.get("/catalog/*", CategoryController.getCategories);
