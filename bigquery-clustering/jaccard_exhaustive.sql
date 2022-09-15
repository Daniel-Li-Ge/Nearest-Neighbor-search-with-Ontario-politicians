CREATE TEMP FUNCTION intersec(set1 ARRAY<INT64>, set2 ARRAY<INT64>)
  AS((
    SELECT COUNT(inter) FROM 
    (
      SELECT * FROM (SELECT * FROM UNNEST(set1))
        INTERSECT DISTINCT
      SELECT * FROM (SELECT * FROM UNNEST(set2))
     ) as inter
    ));
           
CREATE TEMP FUNCTION jacc(set1 ARRAY<INT64>, set2 ARRAY<INT64>, f1 INT64, f2 INT64)
  AS((
        SELECT ((select intersec(set1, set2)) / (f1 + f2)
      ) as index
    ));

SELECT 
  e1.id as node_1, 
  e2.id as node_2,
  jacc(e1.followers, e2.followers, e1.f_count, e2.f_count) as jacc
 FROM 
  `steady-triumph-343200.mesh.elist` e1
 INNER JOIN
  `steady-triumph-343200.mesh.elist` e2
 ON
  e1.id < e2.id
