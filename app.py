import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from src.database import get_db_engine
from src.queries import GET_SALES_MASTER_DATA

# -----------------------------------------------------------------------------
# 1. SETUP & BRANDING (DevFlights Theme)
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="DevFlights Airways - Dashboard",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS Personalizados (Violeta/Clean)
st.markdown("""
    <style>
        /* Títulos */
        h1, h2, h3 { color: #7D3C98 !important; }
        
        /* Métricas */
        div[data-testid="stMetricValue"] {
            font-size: 26px;
            color: #7D3C98;
            font-weight: 700;
        }
        
        /* Contenedores */
        .block-container { padding-top: 2rem; }
        
        /* Tabs Estilizados */
        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            background-color: #f9f9f9;
            border-radius: 4px 4px 0px 0px;
            padding: 10px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #7D3C98;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS
# -----------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def load_data():
    engine = get_db_engine()
    df = pd.read_sql(GET_SALES_MASTER_DATA, engine)
    
    # 1. Optimización de Texto -> Category (El mayor ahorro de RAM)
    # Pandas guarda el texto una sola vez y usa índices numéricos pequeños
    cat_cols = [
        'month', 'day_name', 'quarter', 'route_name', 
        'origin_city', 'origin_country', 'dest_city', 'dest_country', 
        'aircraft_model', 'manufacturer', 'size_category', 
        'service_class', 'age_group', 'passenger_nationality'
    ]
    
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].astype('category')

    # 2. Optimización Numérica (Downcasting)
    # Usar 32 bits en lugar de 64 bits (ahorra 50% en estas columnas)
    if 'revenue' in df.columns:
        df['revenue'] = pd.to_numeric(df['revenue'], downcast='float')
    
    if 'tickets_sold' in df.columns:
        df['tickets_sold'] = pd.to_numeric(df['tickets_sold'], downcast='integer')
        
    if 'lead_time' in df.columns:
        df['lead_time'] = pd.to_numeric(df['lead_time'], downcast='float')

    # 3. Fechas
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        
    # Validar integridad básica
    if 'year' in df.columns:
        df['year'] = df['year'].astype('int16') # Ahorra más que int32

    return df

try:
    with st.spinner('Cargando datos completos del proyecto...'):
        df_master = load_data()
except Exception as e:
    st.error(f"Error de conexión: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. SIDEBAR (FILTROS GLOBALES)
# -----------------------------------------------------------------------------
st.sidebar.image("assets/devflights_logo.jpg", use_container_width=True) 
st.sidebar.markdown("---")
st.sidebar.header("🔍 Panel de Control")

# Filtros Dinámicos
years = sorted(df_master['year'].unique())
sel_year = st.sidebar.selectbox("Año", years, index=len(years)-1, format_func=lambda x: f"{int(x)}")

manuf_opts = sorted(df_master['manufacturer'].unique())
sel_manuf = st.sidebar.multiselect("Fabricante", manuf_opts, default=manuf_opts)

class_opts = df_master['service_class'].unique()
sel_class = st.sidebar.multiselect("Clase", class_opts, default=class_opts)

# Filtro extra (Segmento)
seg_opts = sorted(df_master['age_group'].unique())
sel_seg = st.sidebar.multiselect("Segmento Etario", seg_opts, default=seg_opts)

# Aplicar Filtros
df = df_master[
    (df_master['year'] == int(sel_year)) &
    (df_master['manufacturer'].isin(sel_manuf)) &
    (df_master['service_class'].isin(sel_class)) &
    (df_master['age_group'].isin(sel_seg))
]

if df.empty:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. HEADER & KPIs MACRO
# -----------------------------------------------------------------------------
st.title("DevFlights Airways | Analytics")
st.markdown(f"**Tablero Ejecutivo - Periodo {int(sel_year)}**")

# KPIs Generales
total_rev = df['revenue'].sum()
total_tix = df['tickets_sold'].sum()
avg_ticket = total_rev / total_tix if total_tix > 0 else 0
avg_lead = df['lead_time'].mean()

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Ingresos Totales", f"${total_rev:,.0f}")
k2.metric("🎫 Pasajes Vendidos", f"{total_tix:,.0f}")
k3.metric("📈 Ticket Promedio", f"${avg_ticket:.2f}")
k4.metric("📅 Anticipación Media", f"{avg_lead:.1f} días")

st.markdown("---")

# -----------------------------------------------------------------------------
# 5. TABS (Respondiendo al Documento)
# -----------------------------------------------------------------------------
tab_geo, tab_biz, tab_fleet, tab_crm, tab_time = st.tabs([
    "🌎 Mapa de Rutas",           # Visualización Contextual
    "📊 Rentabilidad",     # Preguntas 1 y 2
    "✈️ Flota & Eficiencia",      # Pregunta 3
    "👥 Clientes",     # Pregunta 4
    "📅 Tendencias"      # Pregunta 5
])

# --- TAB 1: GEOESPACIAL (MAPA) ---
with tab_geo:
    c1, c2 = st.columns([1, 4])
    with c1:
        st.markdown("##### Configuración")
        st.caption("Filtra para ver las rutas más densas.")
        n_rutas = st.slider("Cant. Rutas", 50, 2000, 100)
        opacity = st.slider("Opacidad", 0.1, 1.0, 0.3)
    
    with c2:
        # Agrupación para mapa
        map_df = df.groupby(['route_name', 'origin_lat', 'origin_lon', 'dest_lat', 'dest_lon', 'origin_city'],
                            observed=True).agg(rev=('revenue', 'sum')).reset_index().sort_values('rev', ascending=False).head(n_rutas)
        
        fig_map = go.Figure()
        
        # Líneas optimizadas
        lons, lats = [], []
        for _, row in map_df.iterrows():
            lons.extend([row['origin_lon'], row['dest_lon'], None])
            lats.extend([row['origin_lat'], row['dest_lat'], None])
            
        fig_map.add_trace(go.Scattergeo(
            lon=lons, lat=lats,
            mode='lines',
            line=dict(width=1.5, color='#7D3C98'),
            opacity=opacity,
            name='Conexiones'
        ))
        
        # Puntos
        fig_map.add_trace(go.Scattergeo(
            lon=map_df['origin_lon'], lat=map_df['origin_lat'],
            mode='markers',
            marker=dict(size=4, color='#262730'),
            text=map_df['origin_city'], hoverinfo='text'
        ))
        
        fig_map.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            geo=dict(
                projection_type="equirectangular",
                showland=True, landcolor="#F5F5F5",
                countrycolor="#E0E0E0", coastlinecolor="#ffffff",
                bgcolor="rgba(0,0,0,0)"
            ),
            height=500
        )
        st.plotly_chart(fig_map, use_container_width=True)

# --- TAB 2: RENTABILIDAD (Preguntas 1 y 2 del Doc) ---
with tab_biz:
    col_l, col_r = st.columns([2, 1])
    
    with col_l:
        st.subheader("1. Rutas Estrella: Rentabilidad vs Volumen")
        st.caption("Responde: ¿Cuáles son las rutas más rentables? ")
        
        # Slider Local
        top_n_scatter = st.slider("Top Rutas a visualizar", 10, 500, 100)
        
        scatter_data = df.groupby('route_name').agg(
            rev=('revenue', 'sum'),
            vol=('tickets_sold', 'sum'),
            orig=('origin_city', 'first')
        ).reset_index().sort_values('rev', ascending=False).head(top_n_scatter)
        
        fig_scat = px.scatter(
            scatter_data, x="vol", y="rev",
            size="rev", color="rev",
            color_continuous_scale="Purples",
            hover_name="route_name",
            labels={"vol": "Tickets Vendidos", "rev": "Ingresos Totales ($)"},
            template="plotly_white"
        )
        st.plotly_chart(fig_scat, use_container_width=True)
        
    with col_r:
        st.subheader("2. Share de Ingresos")
        st.caption("Responde: ¿Qué peso tiene cada clase? ")
        
        pie_dim = st.selectbox("Dimensión", ["Clase", "Avión"])
        dim_col = "service_class" if "Clase" in pie_dim else "size_category"
        
        pie_data = df.groupby(dim_col)['revenue'].sum().reset_index()
        
        # Mapear size_category a nombres cortos si es necesario
        if dim_col == "size_category":
            size_mapping = {
                'Small': 'Pequeño',
                'small': 'Pequeño',
                'Medium': 'Mediano',
                'medium': 'Mediano',
                'Large': 'Grande',
                'large': 'Grande'
            }
            pie_data['label_short'] = pie_data[dim_col].map(size_mapping).fillna(pie_data[dim_col])
        else:
            pie_data['label_short'] = pie_data[dim_col]
        
        # Colores más diferenciados para mejor contraste en la leyenda
        custom_colors = ['#4A148C', '#7D3C98', '#9B59B6', '#BA68C8', '#CE93D8']
        
        fig_pie = px.pie(
            pie_data,
            values='revenue', names='label_short',
            hole=0.5,
            color_discrete_sequence=custom_colors[:len(pie_data)]
        )
        fig_pie.update_traces(
            texttemplate='%{percent}',
            textposition='inside',
            textfont=dict(size=16, color='white'),
            insidetextorientation='horizontal',
            textinfo='percent',
            hovertemplate='<b>%{label}</b><br>Ingresos: $%{value:,.0f}<br>Porcentaje: %{percent}<extra></extra>'
        )
        fig_pie.update_layout(
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.02,
                font=dict(size=15, color='#7D3C98', family='Arial'),
                bgcolor='rgba(255,255,255,0.8)',
                bordercolor='#7D3C98',
                borderwidth=1
            ),
            annotations=[dict(text='Share', x=0.5, y=0.5, font_size=18, showarrow=False)]
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# --- TAB 3: FLOTA (Pregunta 3 del Doc) ---
with tab_fleet:
    st.subheader("3. Factor de Ocupación y Eficiencia")
    st.caption("Responde: ¿Qué modelos transportan más pasajeros vs su capacidad? ")
    
    # Análisis de Eficiencia
    fleet_metrics = df.groupby('aircraft_model').agg(
        total_pax=('tickets_sold', 'sum'),
        total_rev=('revenue', 'sum'),
        # Capacidad promedio del modelo
        avg_cap=('aircraft_capacity', 'mean')
    ).reset_index()
    
    # Selector de métrica
    metric_fleet = st.radio("Comparar por:", ["Volumen de Pasajeros", "Ingresos Generados"], horizontal=True)
    y_col = "total_pax" if "Pasajeros" in metric_fleet else "total_rev"
    
    fig_bar = px.bar(
        fleet_metrics.sort_values(y_col, ascending=True),
        y='aircraft_model', x=y_col,
        orientation='h',
        color='avg_cap', # Coloreamos por capacidad para ver si los grandes llenan más
        color_continuous_scale="Purples",
        title=f"Ranking de Modelos por {metric_fleet}",
        labels={"avg_cap": "Capacidad Asientos", "aircraft_model": "Modelo"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    with st.expander("Ver Datos de Flota"):
        st.dataframe(fleet_metrics)

# --- TAB 4: CLIENTES (Pregunta 4 del Doc) ---
with tab_crm:
    c_crm1, c_crm2 = st.columns(2)
    
    with c_crm1:
        st.subheader("4. Comportamiento de Compra")
        st.caption("Responde: ¿Con cuánta anticipación compran? ")
        
        bins_slider = st.slider("Bins (Agrupación)", 10, 100, 30)
        
        # Histograma segmentado por Clase (Insight valioso)
        fig_hist = px.histogram(
            df, x="lead_time",
            nbins=bins_slider,
            color="service_class",
            color_discrete_sequence=["#4A148C", "#7D3C98", "#BA68C8"],
            opacity=0.85,
            labels={"lead_time": "Días de Anticipación", "count": "Transacciones"},
            title="Distribución de Anticipación por Clase"
        )
        fig_hist.update_layout(barmode='overlay')
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with c_crm2:
        st.subheader("Demografía")
        st.caption("Análisis por Segmento Etario y Nacionalidad")
        
        demo_dim = st.radio("Ver por:", ["Segmento Etario", "Nacionalidad (Top 10)"], horizontal=True)
        
        if "Etario" in demo_dim:
            demo_data = df.groupby('age_group')['tickets_sold'].sum().reset_index()
            x_ax = 'age_group'
        else:
            demo_data = df.groupby('passenger_nationality')['tickets_sold'].sum().reset_index().sort_values('tickets_sold', ascending=False).head(10)
            x_ax = 'passenger_nationality'
            
        fig_bar_demo = px.bar(
            demo_data, x=x_ax, y='tickets_sold',
            color='tickets_sold',
            color_continuous_scale=[[0, '#CE93D8'], [0.3, '#9B59B6'], [0.7, '#7D3C98'], [1, '#6A1B9A']],
            title=f"Pasajeros por {demo_dim}"
        )
        fig_bar_demo.update_traces(
            marker=dict(
                colorbar=dict(
                    title="Pasajeros",
                    thicknessmode="pixels",
                    thickness=15
                )
            )
        )
        st.plotly_chart(fig_bar_demo, use_container_width=True)

# --- TAB 5: TENDENCIAS (Pregunta 5 del Doc) ---
with tab_time:
    st.subheader("5. Tendencia de Ventas (Estacionalidad)")
    st.caption("Responde: ¿Cuál es la tendencia mensual/semanal? ")
    
    # Agrupación Dinámica
    time_agg = st.selectbox("Agrupación Temporal", ["Mensual", "Semanal", "Diaria"])
    
    # Lógica de resampleo
    if time_agg == "Mensual":
        rule = 'M'
    elif time_agg == "Semanal":
        rule = 'W'
    else:
        rule = 'D'
        
    trend_df = df.set_index('date').resample(rule)['revenue'].sum().reset_index()
    
    fig_line = px.area(
        trend_df, x='date', y='revenue',
        title=f"Evolución de Ingresos ({time_agg})",
        color_discrete_sequence=['#7D3C98']
    )
    st.plotly_chart(fig_line, use_container_width=True)