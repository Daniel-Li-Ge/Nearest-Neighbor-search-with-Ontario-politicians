CREATE TABLE `steady-triumph-343200.mesh.flat_edgelist` AS
  SELECT 
    p.id,
    ARRAY_AGG(
      e.id
    ) as followers
    
FROM `steady-triumph-343200.mesh.edgelist` AS e
  JOIN `steady-triumph-343200.mesh.pillars` AS p
    on P.id = e.following_id
 GROUP BY p.id
