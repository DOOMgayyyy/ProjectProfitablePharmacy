require('dotenv').config({ path: '../../.env' });
const pgp = require('pg-promise')(/* options */);
const DBUSER = process.env.DB_USER
const DBPASS = process.env.DB_PASS
const DBHOST = process.env.DB_HOST
const DBPORT = process.env.DB_PORT
const DBNAME = process.env.DB_NAME
const connectionString = `postgres://${DBUSER}:${DBPASS}@${DBHOST}:${DBPORT}/${DBNAME}`;

const db = pgp(connectionString);
export default db;
