-- liquibase formatted sql

-- changeset harish:insert_store_table_values_1
INSERT INTO LIQ_SCHEMA.stores (store_id, store_name, city_id)
VALUES (10, 'IBM_Bangalore', 111);
-- rollback DELETE FROM LIQ_SCHEMA.STORES WHERE store_id=10;