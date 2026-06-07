const express = require('express');
const app = express();

// библиотека которая позволяета отправлять запросы с фронта на бэк
const cors = require('cors');
// подключаем роутер для v1 версии API
const v1Router = require('./routes/v1');
const errorMiddleware = require('./middlewares/error.midleware');


// middleware
app.use(cors()); // позволяет отправлять запросы с фронта на бэк
app.use(express.json()); // позволяет парсить JSON в теле запроса
app.use(express.urlencoded({ extended: false }));

// routes
app.use('/api/v1', v1Router);

// подхватываем если ни один из маршрутов не подошел
app.use((req, res) => {
  res.status(404).json({ error: 'Not Found' });
});

// error middleware
app.use(errorMiddleware);
module.exports = app;
