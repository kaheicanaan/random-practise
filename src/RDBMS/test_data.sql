INSERT INTO articles (id, title, created_by)
VALUES
  -- two articles for determine which one has the most like in 1st Apr 2017
  ('111111', 'Hello World 1', '2017-04-01 01:00:00'),  -- this is the most liked article
  ('111112', 'Hello World 2', '2017-04-01 05:00:00'),
  -- irrelevant
  ('111113', 'Hello World 3', '2017-04-01 01:00:00');


INSERT INTO clickstream (userId, time, action, objectId)
VALUES
  -- install app
  ('00001', '2017-04-01 01:00:00', 'FIRST_INSTALL', NULL),
  ('00002', '2017-04-01 02:00:00', 'FIRST_INSTALL', NULL),
  ('00003', '2017-04-01 03:00:00', 'FIRST_INSTALL', NULL),
  ('00004', '2017-04-01 04:00:00', 'FIRST_INSTALL', NULL),
  ('00005', '2017-04-01 05:00:00', 'FIRST_INSTALL', NULL),
  ('00006', '2017-04-01 06:00:00', 'FIRST_INSTALL', NULL),
  ('00007', '2017-04-01 07:00:00', 'FIRST_INSTALL', NULL),
  ('00008', '2017-04-01 08:00:00', 'FIRST_INSTALL', NULL),
  -- for most liked article
  ('00006', '2017-04-01 08:00:00', 'LIKE_ARTICLE', '111111'),
  ('00007', '2017-04-01 09:00:00', 'LIKE_ARTICLE', '111111'),
  ('00008', '2017-04-01 10:00:00', 'LIKE_ARTICLE', '111112'),
  -- users that install app on 1st Apr AND used the app in 2nd - 8th Apr once
  ('00001', '2017-04-02 01:00:00', 'LIKE_ARTICLE', '111112'),
  ('00002', '2017-04-03 02:00:00', 'LIKE_ARTICLE', '111112'),
  ('00003', '2017-04-04 03:00:00', 'LIKE_ARTICLE', '111112'),
  ('00004', '2017-04-05 03:00:00', 'LOG_IN', NULL),
  -- irrelevant
  ('00005', '2017-04-10 03:00:00', 'LIKE_ARTICLE', '111111');
