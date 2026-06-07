#!/usr/bin/env node

/**
 * Импортируем необходимые модули
 */
const app = require('../app.js');
const http = require('http');
require('dotenv').config({ path: '../../../.env' });

/**
 * Получаем порт из dotenv и устанавливаем его в Express
 */
const port = normalizePort(process.env.SERVER_PORT || '3001');
app.set('port', port);

/**
 * Создаём HTTP сервер
 */
const server = http.createServer(app);

/**
 * Включаем прослушивание заданного порта, что примечательно
 * не указываем hostname, то есть ip с которого приходят запросы теоретически 0.0.0.0
 * следует задать, при необходимости(reverse proxy там всякие или если на другом хосте фронт)
 *  и устанавливаем обработчики событий
 */
server.listen(port);
server.on('error', onError);
server.on('listening', onListening);

/**
 * Нормализуем порт, на случай если будет не валидный или строка
 */
function normalizePort(val) {
  const port = parseInt(val, 10);
  if (isNaN(port)) return val;
  if (port >= 0) return port;
  return false;
}

/**
 * обработчики
 */
function onError(error) {
  if (error.syscall !== 'listen') {
    throw error;
  }
  // формируем адекватно выглядющую ошибку
  const bind = typeof port === 'string'
    ? 'Pipe ' + port
    : 'Port ' + port;

  switch (error.code) {
    // нет прав на порт, всё что ниже 1024 (если не из под рута запускаем (так лучше не делать :)  ))
    case 'EACCES':
      console.error(bind + ' requires elevated privileges');
      process.exit(1);
      break;
    // порт уже занят, если так то ввести на ubutu sudo netstat -tlnp | grep :<номер_порта> и посмотреть чем занят порт и через либо systemctl или htop убить))))
    case 'EADDRINUSE':
      console.error(bind + ' is already in use');
      process.exit(1);
      break;
    default:
      throw error;
  }
}

/**
 * Если сервер инициализировался выдаёт лог, что всё ОК
 */
function onListening() {
  const addr = server.address();
  const bind = typeof addr === 'string'
    ? 'pipe ' + addr
    : 'port ' + addr.port;
  console.log('Listening on ' + bind);

  console.log('Сервер запустился на порту:', addr.port);

}
