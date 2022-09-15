WITH set1 as(
    SELECT * 
    FROM UNNEST((
      SELECT followers FROM `steady-triumph-343200.mesh.elist`
      WHERE id = 17073913)) as followers
  ),
set2 as (
    SELECT * 
    FROM UNNEST((
      SELECT followers FROM `steady-triumph-343200.mesh.elist`
      WHERE id = 253340075)) as followers
  ),
intersection as(
  SELECT COUNT(inter) as inter
  FROM
  (
    SELECT * FROM (SELECT followers FROM set1)
      INTERSECT DISTINCT
    SELECT * FROM (SELECT followers FROM set2)
   ) as inter
 )

SELECT ( (select inter FROM intersection) / ((select f_count FROM `steady-triumph-343200.mesh.elist`
  WHERE id = 17073913) + (SELECT f_count FROM `steady-triumph-343200.mesh.elist`
  WHERE id = 253340075))
) as index
