CREATE TABLE votes(
  voteId SERIAL NOT NULL,
  candidate VARCHAR (1) NOt NULL,
  voteTime TIMESTAMP NOT NULL,
  kioskId integer NOT NULL,
  -- assuming a kiosk can only do one thing every microsecond
  PRIMARY KEY (voteId),
  UNIQUE (votetime, kioskId)
);
