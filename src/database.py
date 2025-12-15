import streamlit as st
from sqlalchemy import create_engine, Engine

@st.cache_resource
def get_db_engine() -> Engine:
    """
    Crea y cachea el motor de conexión a PostgreSQL.
    Lee las credenciales desde .streamlit/secrets.toml
    """
    try:
        # Accedemos a la sección [postgres] de secrets.toml
        config = st.secrets["postgres"]
        
        # Construimos el connection string
        # Formato: postgresql+psycopg2://user:password@host:port/dbname
        db_url = f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['dbname']}"
        
        # Creamos el motor
        engine = create_engine(db_url)
        return engine
        
    except Exception as e:
        st.error(f"❌ Error crítico conectando a la base de datos: {e}")
        st.stop()