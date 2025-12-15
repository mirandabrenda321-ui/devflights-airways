# queries.py
GET_SALES_MASTER_DATA = """
SELECT 
    -- 1. Tiempo
    t.fecha_completa AS date,
    t.anio AS year,
    t.mes_nombre AS month,
    t.dia_semana_nombre AS day_name,
    t.trimestre AS quarter,
    
    -- 2. Ruta
    r.nombre_ruta AS route_name,
    r.origen_ciudad AS origin_city,
    r.origen_pais AS origin_country,
    r.origen_latitud AS origin_lat,
    r.origen_longitud AS origin_lon,
    r.destino_ciudad AS dest_city,
    r.destino_pais AS dest_country,
    r.destino_latitud AS dest_lat,
    r.destino_longitud AS dest_lon,
    
    -- 3. Avion
    a.modelo AS aircraft_model,
    a.fabricante AS manufacturer,
    a.categoria_tamanio AS size_category,
    a.capacidad_total AS aircraft_capacity,
    
    -- 4. Pasajero
    p.nacionalidad AS passenger_nationality,
    p.segmento_etario AS age_group,
    p.edad AS passenger_age,

    -- 5. Hechos (Ventas)
    f.clase_servicio AS service_class,
    f.ingreso_ticket AS revenue,
    f.cantidad_vendida AS tickets_sold,
    f.dias_anticipacion AS lead_time

FROM analytics.fact_ventas f
JOIN analytics.dim_tiempo t   ON f.fecha_fk = t.fecha_completa
JOIN analytics.dim_ruta r     ON f.ruta_id = r.ruta_id
JOIN analytics.dim_avion a    ON f.avion_id = a.avion_id
JOIN analytics.dim_pasajero p ON f.pasajero_id = p.pasajero_id

WHERE f.estado_venta IN ('confirmada', 'completada');
"""