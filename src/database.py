import streamlit as st
from sqlalchemy import create_engine

# Cacheamos la conexión para no abrir una nueva cada vez que alguien toca un botón
@st.cache_resource
def get_db_engine():
    # Leemos los secretos que configuraste en Streamlit Cloud
    db_config = st.secrets["postgres"]
    
    # Construimos la URL de conexión (Connection String)
    # Formato: postgresql+psycopg2://user:password@host:port/dbname
    database_url = f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    
    # CREAMOS EL MOTOR CON SSL REQUERIDO
    # Esto es lo critico: connect_args={"sslmode": "require"}
    engine = create_engine(
        database_url,
        connect_args={"sslmode": "require"}, # Obligatorio para Supabase
        pool_pre_ping=True, # Verifica que la conexión esté viva antes de usarla
        pool_recycle=3600   # Recicla conexiones cada hora para evitar cortes
    )
    
    return engine