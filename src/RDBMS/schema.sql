-- postgresql
CREATE TYPE actions AS ENUM ('FIRST_INSTALL', 'LIKE_ARTICLE', 'LOG_IN');

CREATE TABLE articles(
  id VARCHAR (32) NOT NULL,
  title VARCHAR (32) NOT NULL,
  created_by TIMESTAMP NOT NULL,
  updated_by TIMESTAMP,
  PRIMARY KEY (id)
);

CREATE TABLE clickstream(
  userId VARCHAR (32) NOT NULL,
  time TIMESTAMP NOT NULL,
  action actions NOT NULL,
  objectId VARCHAR (32),
  -- assuming a user can only do one thing every microsecond
  PRIMARY KEY (userId, time),
  FOREIGN KEY (objectId) references articles (id)
);
