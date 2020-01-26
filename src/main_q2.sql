-- Find the top-10 articles (title, ID and like received) with most LIKE received from user
-- on 2017-04-01
SELECT title, id, like_received
FROM articles, (
  SELECT objectId, count(*) as like_received FROM clickstream
  WHERE date_trunc ('day', time) = timestamp '2017-04-01'
    AND action = 'LIKE_ARTICLE'
  GROUP BY objectId
  ORDER BY like_received DESC
  LIMIT 10
) AS grouped  -- top 10 liked articles can be found here
WHERE articles.id = grouped.objectId;

-- Find the count of users who install the app (i.e. with FIRST_INSTALL event) on
-- 2017-04-01 and use our app at least once (i.e. with any event) between 2017-04-02 and 2017-04-08
SELECT count(*)
FROM (
  -- user that first installed app on 1st Apr
  SELECT *
  FROM clickstream
  WHERE action = 'FIRST_INSTALL'
    AND date_trunc ('day', time) = timestamp '2017-04-01'
) as first_installed INNER JOIN (
  -- user that perform any action between 2nd Apr to 8th Apr
  SELECT *
  FROM clickstream
  WHERE
    -- no need to filter on their action
    date_trunc ('day', time) >= timestamp '2017-04-02'
    AND date_trunc ('day', time) <= timestamp '2017-04-08'
) as with_action ON first_installed.userId = with_action.userId;
