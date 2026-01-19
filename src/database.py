import streamlit as st
from sqlalchemy import create_engine

@st.cache_resource
def get_db_engine():
    db_config = st.secrets["postgres"]

    database_url = (
        f"postgresql+psycopg2://{db_config['user']}:{db_config['password']}"
        f"@{db_config['host']}:{db_config['port']}/{db_config['dbname']}"
    )

    # 👉 SI es localhost / docker → NO SSL
    # 👉 SI es Supabase / cloud → SSL
    if db_config["host"] in ["localhost", "127.0.0.1"]:
        connect_args = {"sslmode": "disable"}
    else:
        connect_args = {"sslmode": "require"}

    engine = create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
        pool_recycle=3600
    )

    return engine
