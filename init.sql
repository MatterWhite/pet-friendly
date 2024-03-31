CREATE TABLE user_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

COMMENT ON TABLE user_types IS 'Роли пользователей';
COMMENT ON COLUMN user_types.name IS 'Название роли';

CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    user_type INT NOT NULL REFERENCES user_types(id),
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(64) NOT NULL,
    phone VARCHAR(255) NOT NULL,
    bio VARCHAR(4095) DEFAULT NULL
);

CREATE INDEX ON users USING btree (ENCODE(SHA512(CAST((users.email || users.password) AS bytea)), 'HEX'));
CREATE UNIQUE INDEX ON users USING btree (email);

COMMENT ON TABLE users IS 'Таблица пользователей сервиса';
COMMENT ON COLUMN users.username IS 'Имя пользователя';
COMMENT ON COLUMN users.email IS 'Сырая почта пользователя';
COMMENT ON COLUMN users.phone IS 'Телефон для связи';
COMMENT ON COLUMN users.bio IS 'Раздел "о себе" (опциональный)';

CREATE TABLE wallets (
    owner_id INT8 PRIMARY KEY REFERENCES users(id),
    balance_real INT8 NOT NULL DEFAULT 0,
    balance_freezed INT8 NOT NULL DEFAULT 0,
    wallet_freezed BOOL NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT balance_gte_0 
        CHECK (balance_real >= 0)
);

COMMENT ON TABLE wallets IS 'Кошельки пользователей, максимум один на пользователя';
COMMENT ON COLUMN wallets.balance_real IS 'Сумма в копейках';
COMMENT ON COLUMN wallets.balance_freezed IS 'Хранилище средств на время выгула';
COMMENT ON COLUMN wallets.wallet_freezed IS 'Заморожен ли кошелек';

CREATE TABLE dogs (
    id BIGSERIAL PRIMARY KEY,
    owner_id INT8 NOT NULL REFERENCES users(id),
    name VARCHAR(255) NOT NULL,
    height VARCHAR(255) DEFAULT NULL,
    weight VARCHAR(255) DEFAULT NULL,
    breed VARCHAR(255) DEFAULT NULL,
    color VARCHAR(255) DEFAULT NULL
);

COMMENT ON COLUMN dogs.name IS 'Кличка питомца';
COMMENT ON COLUMN dogs.height IS 'Высота в холке, с указанием ед. изм.';
COMMENT ON COLUMN dogs.weight IS 'Вес, с указанием ед. изм.';
COMMENT ON COLUMN dogs.breed IS 'Порода';

CREATE TABLE walk_zones (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    district VARCHAR(255) NOT NULL,
    description VARCHAR(4095) DEFAULT NULL,
    square VARCHAR(255) DEFAULT NULL,
    has_special_equipment BOOL NOT NULL
);

COMMENT ON TABLE walk_zones IS 'Таблица зон для выгула';
COMMENT ON COLUMN walk_zones.description IS 'Описание зоны';
COMMENT ON COLUMN walk_zones.district IS 'Район города';
COMMENT ON COLUMN walk_zones.square IS 'Площадь зоны';
COMMENT ON COLUMN walk_zones.has_special_equipment IS 'Имеется ли специальное оборудование для выгула и тренировок';

CREATE TABLE dog_favor_zones (
    assign_id BIGSERIAL PRIMARY KEY,
    dog_id INT8 NOT NULL REFERENCES dogs(id),
    zone_id INT8 NOT NULL REFERENCES walk_zones(id)
);

COMMENT ON TABLE dog_favor_zones IS 'Перечень любимых зон собаки';

CREATE TABLE walk_requests (
    id BIGSERIAL PRIMARY KEY,
    start_at TIMESTAMP NOT NULL,
    end_at TIMESTAMP NOT NULL,
    price INT8 NOT NULL,
    issuer_id INT8 NOT NULL REFERENCES users(id),
    executor_id INT8 DEFAULT NULL REFERENCES users(id),
    transfer_addr VARCHAR(1023) NOT NULL,
    is_started BOOL NOT NULL DEFAULT FALSE,
    is_finished BOOL NOT NULL DEFAULT FALSE,
    CONSTRAINT price_gte_0
        CHECK (price >= 0),
    CONSTRAINT finish_started
        CHECK (is_started OR NOT is_finished)
);

COMMENT ON TABLE walk_requests IS 'Запросы на выгул (объявления)';
COMMENT ON COLUMN walk_requests.price IS 'В копейках';

CREATE TABLE walk_request_dogs (
    assign_id BIGSERIAL PRIMARY KEY,
    request_id INT8 NOT NULL REFERENCES walk_requests(id),
    dog_id INT8 NOT NULL REFERENCES dogs(id)
);

COMMENT ON TABLE walk_request_dogs IS 'Список собак для выгула в одном объявлении';

CREATE TABLE walk_request_zones (
    assign_id BIGSERIAL PRIMARY KEY,
    request_id INT8 NOT NULL REFERENCES walk_requests(id),
    zone_id INT8 NOT NULL REFERENCES walk_zones(id)
);

COMMENT ON TABLE walk_request_zones IS 'Перечень зон для выгула';


CREATE OR REPLACE FUNCTION function_init_wallet() RETURNS TRIGGER AS 
$BODY$
BEGIN
    IF (NEW.id IS NOT NULL) THEN
        INSERT INTO wallets (owner_id) VALUES (NEW.id);
    END IF;
    RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE OR REPLACE TRIGGER init_wallet
    AFTER INSERT ON users
    FOR EACH ROW
    EXECUTE PROCEDURE function_init_wallet();


CREATE OR REPLACE FUNCTION function_walk_done() RETURNS TRIGGER AS
$BODY$
BEGIN
    IF (NEW.is_started AND NOT OLD.is_started AND NOT NEW.is_finished AND NEW.executor_id IS NOT NULL) THEN
        -- Замораживаем средства на стороне заказчика
        UPDATE wallets 
        SET balance_real = balance_real - NEW.price,
            balance_freezed = balance_freezed + NEW.price,
            updated_at = CURRENT_TIMESTAMP
        WHERE owner_id = NEW.issuer_id;

        -- Замораживаем средства на стороне исполнителя
        UPDATE wallets 
        SET balance_freezed = balance_freezed + NEW.price,
            updated_at = CURRENT_TIMESTAMP
        WHERE owner_id = NEW.executor_id;
    ELSE 
        IF (NEW.is_started AND NEW.is_finished AND NOT OLD.is_finished AND NEW.executor_id IS NOT NULL) THEN
            -- Размораживаем средства на стороне заказчика
            UPDATE wallets 
            SET balance_freezed = balance_freezed - NEW.price,
                updated_at = CURRENT_TIMESTAMP
            WHERE owner_id = NEW.issuer_id;

            -- Размораживаем средства на стороне исполнителя
            UPDATE wallets 
            SET balance_real = balance_real + NEW.price,
                balance_freezed = balance_freezed - NEW.price,
                updated_at = CURRENT_TIMESTAMP
            WHERE owner_id = NEW.executor_id;
        END IF;
    END IF;
    RETURN NEW;
END;
$BODY$
language plpgsql;

CREATE OR REPLACE TRIGGER walk_done
    BEFORE UPDATE ON walk_requests
    FOR EACH ROW
    EXECUTE PROCEDURE function_walk_done();





CREATE USER "doge_guest";
CREATE USER "doge_user";
CREATE USER "doge_admin";

ALTER ROLE "doge_guest" PASSWORD 'simple_password';
ALTER ROLE "doge_user" PASSWORD 'wG3ZNVd8Snn1bvqf';
ALTER ROLE "doge_admin" PASSWORD '6CTzbeWqLUjP25CeMDbDDTHoUrwCGUGIIwUb6WdEK1pJYaIbV3IdjhgytG4ZL4YA';

GRANT SELECT ON user_types TO doge_user;
GRANT SELECT ON SEQUENCE user_types_id_seq TO doge_user;

GRANT SELECT, INSERT ON users TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE users_id_seq TO doge_user;

GRANT SELECT, INSERT, UPDATE ON wallets TO doge_user;

GRANT SELECT, INSERT, UPDATE ON dogs TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE dogs_id_seq TO doge_user;


GRANT SELECT ON walk_zones TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE walk_zones_id_seq TO doge_user;


GRANT SELECT, INSERT, UPDATE, DELETE ON dog_favor_zones TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE dog_favor_zones_assign_id_seq TO doge_user;


GRANT SELECT, INSERT, UPDATE ON walk_requests TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE walk_requests_id_seq TO doge_user;


GRANT SELECT, INSERT, UPDATE, DELETE ON walk_request_dogs TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE walk_request_dogs_assign_id_seq TO doge_user;


GRANT SELECT, INSERT, UPDATE, DELETE ON walk_request_zones TO doge_user;
GRANT USAGE, SELECT ON SEQUENCE walk_request_zones_assign_id_seq TO doge_user;



ALTER ROLE "doge_admin" SUPERUSER;



-- Base data:
INSERT INTO user_types (name) VALUES ('Заказчик'), ('Исполнитель');
insert into walk_zones (name, district, description, square, has_special_equipment) values ('Парк', 'Восточный', 'Самый обычный парк', '100 м^2', FALSE);
insert into walk_zones (name, district, description, square, has_special_equipment) values ('Лес', 'Область', 'Много места, мало людей, природа', '3 км^2', FALSE);
insert into walk_zones (name, district, description, square, has_special_equipment) values ('Спецплощадка', 'Центральный', 'С оборудованием', '30 м^2', TRUE);
insert into walk_zones (name, district, description, square, has_special_equipment) values ('Запад-1', 'Западный', 'Спальный район на западе города', '1000 м^2', FALSE);
