-- Motor utilizado: PostgreSQL

-- B1
SELECT c.id, c.nombre
FROM cliente c
WHERE c.tipo = 'E'
  AND NOT EXISTS (
      SELECT 1 
      FROM oportunidad o 
      WHERE o.cliente_id = c.id 
        AND o.etapa NOT IN ('GANADA', 'PERDIDA')
  )
ORDER BY c.nombre;


-- B2
SELECT 
    a.id, 
    a.nombre,
    COUNT(CASE WHEN o.etapa = 'GANADA' THEN 1 END) AS cantidad_ganadas,
    COUNT(CASE WHEN o.etapa = 'PERDIDA' THEN 1 END) AS cantidad_perdidas,
    COALESCE(SUM(CASE WHEN o.etapa = 'GANADA' THEN o.valor END), 0) AS valor_total_ganado,
    ROUND(
        COALESCE(
            COUNT(CASE WHEN o.etapa = 'GANADA' THEN 1 END) * 100 / NULLIF(COUNT(o.id), 0), 
            0
        ), 1
    ) AS tasa_conversion
FROM asesor a
LEFT JOIN oportunidad o 
    ON a.id = o.asesor_id 
    AND EXTRACT(YEAR FROM o.fecha_cierre) = 2026
    AND o.etapa IN ('GANADA', 'PERDIDA')
WHERE a.activo = TRUE
GROUP BY a.id, a.nombre
ORDER BY valor_total_ganado DESC;


-- B3
SELECT 
    o.id, 
    o.titulo, 
    a.nombre AS nombre_asesor,
    MAX(act.fecha) AS fecha_ultima_actividad,
    CURRENT_DATE - COALESCE(CAST(MAX(act.fecha) AS DATE), o.fecha_creacion) AS dias_sin_actividad
FROM oportunidad o
JOIN asesor a ON o.asesor_id = a.id
LEFT JOIN actividad act ON o.id = act.oportunidad_id
WHERE o.etapa NOT IN ('GANADA', 'PERDIDA')
GROUP BY o.id, o.titulo, a.nombre, o.fecha_creacion
HAVING (CURRENT_DATE - COALESCE(CAST(MAX(act.fecha) AS DATE), o.fecha_creacion)) > 15
ORDER BY dias_sin_actividad DESC;


-- B4
WITH AcumuladoPorCliente AS (
    SELECT 
        c.ciudad, 
        c.nombre AS nombre_cliente, 
        SUM(o.valor) AS total_ganado
    FROM cliente c
    JOIN oportunidad o ON c.id = o.cliente_id
    WHERE o.etapa = 'GANADA'
      AND c.ciudad IS NOT NULL
    GROUP BY c.id, c.ciudad, c.nombre
),
RankingPorCiudad AS (
    SELECT 
        ciudad, 
        nombre_cliente, 
        total_ganado,
        RANK() OVER (PARTITION BY ciudad ORDER BY total_ganado DESC) as rnk
    FROM AcumuladoPorCliente
)
SELECT ciudad, nombre_cliente, total_ganado
FROM RankingPorCiudad
WHERE rnk = 1;


-- B5
CREATE INDEX idx_opt_etapa ON oportunidad(etapa);
CREATE INDEX idx_actividad_opt_fecha ON actividad(oportunidad_id, fecha);

/*
Justificación: 
`idx_opt_etapa` filtra velozmente solo las oportunidades abiertas antes del JOIN.
`idx_actividad_opt_fecha` al ser compuesto, permite al motor hacer un *Index Only Scan* 
para resolver rápidamente el MAX(fecha) y la agrupación por oportunidad sin leer toda la tabla.
*/