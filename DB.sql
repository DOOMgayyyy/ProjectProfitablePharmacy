CREATE DATABASE db_farm;

CREATE USER user_farm WITH PASSWORD 'root';

GRANT CONNECT, CREATE, TEMPORARY ON DATABASE db_farm TO user_farm;
GRANT ALL PRIVILEGES ON DATABASE db_farm TO user_farm;

CREATE TABLE pharmacies (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    url TEXT NOT NULL UNIQUE
);

CREATE TABLE categories (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    category_name VARCHAR(255) NOT NULL,
    pharmacy_id INTEGER NOT NULL,
    categories_url TEXT,
    CONSTRAINT fk_categories_pharmacy
        FOREIGN KEY (pharmacy_id)
        REFERENCES pharmacies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE medicines (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    normalize_name VARCHAR(255),
    description TEXT,
    manufacturer VARCHAR(255),
    image_url TEXT,
    category_id INTEGER,
    CONSTRAINT fk_medicines_category
        FOREIGN KEY (category_id)
        REFERENCES categories(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE prices (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    price DOUBLE PRECISION,
    pharmacy_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    date_parse DATE,
    medicine_url TEXT,
    CONSTRAINT fk_prices_pharmacy
        FOREIGN KEY (pharmacy_id)
        REFERENCES pharmacies(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_prices_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES medicines(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

GRANT USAGE, CREATE ON SCHEMA public TO user_farm;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO user_farm;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO user_farm;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON TABLES TO user_farm;

ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT ALL PRIVILEGES ON SEQUENCES TO user_farm;