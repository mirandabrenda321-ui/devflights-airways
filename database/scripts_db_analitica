-- Ver los Aeropuertos (Id, Códigos IATA, Ciudad, País)
SELECT * FROM Aeropuertos;

-- Ver la flota de Aviones (Modelos, Matrículas y Capacidades)
SELECT * FROM Aviones;

-- Ver los Vuelos programados (Relaciona IDs de Aeropuertos y Aviones con horarios)
SELECT * FROM Vuelos;

-- Ver el mapa de Asientos (Cada asiento físico de cada avión)
SELECT * FROM Asientos;

-- Ver la lista de Pasajeros registrados (Datos personales)
SELECT * FROM Pasajeros;

-- Ver las Reservas (La tabla que une Pasajero + Vuelo + Asiento + Precio)
SELECT * FROM Reservas;

-- 1.Crear el esquema exclusivo para análisis
CREATE SCHEMA IF NOT EXISTS analytics;

-- 2.Crear y poblar dim_avion
DROP TABLE IF EXISTS analytics.dim_avion;

CREATE TABLE analytics.dim_avion AS
SELECT
    id AS avion_id,
    modelo,
    fabricante,
    capacidad_total,
 
 -- Transformación: Categorizamos el avión según su capacidad
    CASE 
        WHEN capacidad_total < 150 THEN 'Pequeño (Regional)'
        WHEN capacidad_total BETWEEN 150 AND 250 THEN 'Mediano (Estándar)'
        ELSE 'Grande (Long Haul)'
    END AS categoria_tamanio
FROM public.aviones;

-- Verificamos que quedó bien
SELECT * FROM analytics.dim_avion;

-- 3.Crear y poblar dim_pasajero
DROP TABLE IF EXISTS analytics.dim_pasajero;

CREATE TABLE analytics.dim_pasajero AS
SELECT
    id AS pasajero_id,
	nombre, 
	apellido,
    nacionalidad,

 -- Transformación 1: Calcular la edad actual
    EXTRACT(YEAR FROM age(current_date, TO_DATE(fecha_nacimiento, 'YYYY-MM-DD'))) AS edad,
    
 -- Transformación 2: Segmentación de Marketing
    CASE 
        WHEN EXTRACT(YEAR FROM age(current_date, TO_DATE(fecha_nacimiento, 'YYYY-MM-DD'))) < 25 THEN 'Joven (Gen Z)'
        WHEN EXTRACT(YEAR FROM age(current_date, TO_DATE(fecha_nacimiento, 'YYYY-MM-DD'))) BETWEEN 25 AND 50 THEN 'Adulto (Laboral)'
        ELSE 'Senior (+50)'
    END AS segmento_etario
FROM public.pasajeros;

-- Verificamos
SELECT * FROM analytics.dim_pasajero;

-- 4.Crear y poblar dim_ruta
DROP TABLE IF EXISTS analytics.dim_ruta;

CREATE TABLE analytics.dim_ruta AS
SELECT
    -- Generamos un ID único para cada ruta encontrada
    ROW_NUMBER() OVER (ORDER BY v.aeropuerto_origen_id, v.aeropuerto_destino_id) AS ruta_id,
    
    -- IDs originales para referencia
    v.aeropuerto_origen_id,
    v.aeropuerto_destino_id,
    
    -- Nombres transformados
    ao.ciudad || ' (' || ao.codigo_iata || ') - ' || ad.ciudad || ' (' || ad.codigo_iata || ')' AS nombre_ruta,
    
    -- Datos Geográficos ORIGEN
    ao.ciudad AS origen_ciudad,
    ao.pais AS origen_pais,
    CAST(ao.latitud AS DECIMAL(10,6)) AS origen_latitud,
    CAST(ao.longitud AS DECIMAL(10,6)) AS origen_longitud,
    
    -- Datos Geográficos DESTINO
    ad.ciudad AS destino_ciudad,
    ad.pais AS destino_pais,
    CAST(ad.latitud AS DECIMAL(10,6)) AS destino_latitud,
    CAST(ad.longitud AS DECIMAL(10,6)) AS destino_longitud
FROM (SELECT DISTINCT aeropuerto_origen_id, aeropuerto_destino_id FROM public.vuelos) v
JOIN public.aeropuertos ao ON v.aeropuerto_origen_id = ao.id -- Join Izquierdo (Origen)
JOIN public.aeropuertos ad ON v.aeropuerto_destino_id = ad.id; -- Join Derecho (Destino)

-- Verificar
SELECT * FROM analytics.dim_ruta;

-- 5.Crear y poblar dim_tiempo
DROP TABLE IF EXISTS analytics.dim_tiempo;

CREATE TABLE analytics.dim_tiempo AS
SELECT DISTINCT
    TO_DATE(fecha_salida, 'YYYY-MM-DD') AS fecha_completa, -- Clave primaria (PK)
    EXTRACT(YEAR FROM TO_DATE(fecha_salida, 'YYYY-MM-DD')) AS anio,
    EXTRACT(MONTH FROM TO_DATE(fecha_salida, 'YYYY-MM-DD')) AS mes_numero,
    TO_CHAR(TO_DATE(fecha_salida, 'YYYY-MM-DD'), 'Month') AS mes_nombre,
    TO_CHAR(TO_DATE(fecha_salida, 'YYYY-MM-DD'), 'Day') AS dia_semana_nombre,
    EXTRACT(QUARTER FROM TO_DATE(fecha_salida, 'YYYY-MM-DD')) AS trimestre
FROM public.vuelos
ORDER BY 1;

-- Verificar
SELECT * FROM analytics.dim_tiempo;

-- 6.Crear la tabla de hechos Fact_Ventas
DROP TABLE IF EXISTS analytics.fact_ventas;

CREATE TABLE analytics.fact_ventas AS
SELECT
    r.id AS venta_id,
    
    -- Claves Foráneas (FK) hacia las dimensiones
    TO_DATE(v.fecha_salida, 'YYYY-MM-DD') AS fecha_fk, -- Une con dim_tiempo
    r.pasajero_id,                                     -- Une con dim_pasajero
    v.avion_id,                                        -- Une con dim_avion
    dr.ruta_id,                                        -- Une con dim_ruta
    
    -- Métricas de Negocio
    CAST(r.precio AS DECIMAL(10,2)) AS ingreso_ticket,
    1 AS cantidad_vendida, -- Para contar pasajes vendidos
    
    -- Métrica Calculada: Días de anticipación (Fecha Vuelo - Fecha Reserva)
    (TO_DATE(v.fecha_salida, 'YYYY-MM-DD') - TO_DATE(r.fecha_reserva, 'YYYY-MM-DD')) AS dias_anticipacion,
    
    -- Contexto útil para los hechos
    r.clase AS clase_servicio, -- Primera, Ejecutiva, Economica
    r.estado AS estado_venta   -- Confirmada, Completada
FROM public.reservas r
JOIN public.vuelos v ON r.vuelo_id = v.id

-- Buscamos el ID de la ruta basándonos en el origen/destino del vuelo
JOIN analytics.dim_ruta dr ON v.aeropuerto_origen_id = dr.aeropuerto_origen_id 
                           AND v.aeropuerto_destino_id = dr.aeropuerto_destino_id
	WHERE r.estado IN ('confirmada', 'completada', 'pendiente'); -- Descartamos reservas canceladas

-- Verificar
SELECT * FROM analytics.fact_ventas;