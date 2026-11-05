WITH recorte AS (
    SELECT area, prazo_em,
           CASE WHEN fechado_em <= :referencia THEN fechado_em END AS resolvido_em
    FROM chamado
    WHERE aberto_em <= :referencia
)
SELECT area,
       COUNT(*) AS total,
       COUNT(resolvido_em) AS resolvidos,
       SUM(CASE WHEN resolvido_em <= prazo_em THEN 1 ELSE 0 END) AS no_prazo,
       SUM(CASE WHEN resolvido_em IS NULL THEN 1 ELSE 0 END) AS abertos,
       SUM(CASE WHEN resolvido_em IS NULL AND prazo_em < :referencia THEN 1 ELSE 0 END) AS vencidos
FROM recorte
GROUP BY area
ORDER BY vencidos DESC, total DESC, area;
