---- Those are schemas of two tables used for auth

DROP table users;

CREATE TABLE users(
   id  SERIAL PRIMARY KEY,
   username       VARCHAR(50)    NOT NULL,
   password_hash  VARCHAR(500) NOT NULL
)


DROP table fitbit_tokens;

CREATE TABLE fitbit_tokens (
  id              SERIAL PRIMARY KEY,
  user_id		 INTEGER NOT NULL,
  refresh_token  VARCHAR(500) NOT NULL,
  access_token   VARCHAR(500) NOT NULL

);

