/* This file includes the SQL commands ran to make the initial tables in the database */
CREATE TYPE POKEMON_TYPE AS ENUM ('GRASS', 'FIRE', 'WATER', 'LIGHTNING', 'PSYCHIC', 'FIGHTING', 'DARKNESS', 'METAL', 'COLORLESS', 'DRAGON', 'NONE')

CREATE TABLE expansion_table (
	expansion_identifier VARCHAR(32) PRIMARY KEY,
	expansion_name VARCHAR(256) NOT NULL,
	release_date DATE NOT NULL,
	number_cards INTEGER NOT NULL
)

CREATE TABLE cards (
	id SERIAL PRIMARY KEY,
	pokemon_name VARCHAR(256) NOT NULL,
	health INTEGER,
	pokemon_type POKEMON_TYPE,
	stage INTEGER,
	weakness POKEMON_TYPE,
	rarity INTEGER NOT NULL,
	card_image TEXT NOT NULL,
	is_promo BOOLEAN NOT NULL,
	evolves_from VARCHAR(128),
	illustrated_by VARCHAR(128) NOT NULL,
	description TEXT,
	is_supporter BOOLEAN,
	expansion VARCHAR(32) REFERENCES expansion_table(expansion_identifier) NOT NULL,
	expansion_number INTEGER NOT NULL,
	ability INTEGER REFERENCES abilities(id),
	move1 INTEGER REFERENCES moves(id),
	move2 INTEGER REFERENCES moves(id)
)


CREATE TABLE abilities (
	id SERIAL PRIMARY KEY,
	ability_name VARCHAR(256) NOT NULL,
	description TEXT
)

CREATE TABLE moves (
	id SERIAL PRIMARY KEY,
	move_name VARCHAR(128) NOT NULL,
	damage VARCHAR(20),
	description TEXT
)