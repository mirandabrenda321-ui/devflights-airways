# ✈️ DevFlights Airways | Business Intelligence Dashboard

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.40%2B-FF4B4B)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-336791)
![Status](https://img.shields.io/badge/Status-Completed-success)

> **Visualización interactiva de datos operativos, financieros y de mercado para una aerolínea comercial.**

---

## 📖 Descripción del Proyecto

Este proyecto representa la evolución del análisis de datos para **DevFlights Airways**. Se ha migrado de reportes estáticos a una **Aplicación Web Interactiva** que permite a los directivos explorar métricas clave (KPIs) en tiempo real.

La solución se construye sobre un **Data Warehouse con Esquema Estrella**, procesando grandes volúmenes de transacciones de vuelos, reservas y flota para ofrecer insights sobre rentabilidad, eficiencia operativa y comportamiento del cliente.

### 🎯 Objetivos

- **Centralizar la información:** Unificar datos de ventas, rutas y aviones.
- **Democratizar el acceso:** Permitir a usuarios no técnicos filtrar y explorar datos.
- **Responder preguntas de negocio:** Identificar rutas rentables, estacionalidad y perfiles de clientes.

---

## 🏗️ Arquitectura Técnica

El proyecto sigue una arquitectura desacoplada y modular:

1. **Base de Datos (Data Warehouse):** PostgreSQL. Los datos transaccionales fueron transformados a un modelo dimensional (Fact Tables y Dimensions) en un esquema `analytics`.
2. **Backend:** Python + SQLAlchemy para la conexión segura y Pandas para la manipulación vectorial de datos.
3. **Frontend:** Streamlit + Plotly para la renderización de gráficos interactivos y mapas geoespaciales.
4. **Gestión de Dependencias:** Utilización de `uv` para un entorno virtual rápido y reproducible.

### Estructura del Repositorio

```bash
devflights_analytics/
├── .streamlit/          # Configuración del tema (Branding DevFlights) y Secretos
├── assets/              # Recursos estáticos (Logos, imágenes)
├── src/
│   ├── database.py      # Gestión de conexión a DB (Engine & Caching)
│   └── queries.py       # Consultas SQL optimizadas (Business Logic)
├── app.py               # Orquestador de la UI (Frontend)
├── pyproject.toml       # Definición de dependencias (uv)
└── README.md            # Documentación
```

---

## 📊 Módulos y KPIs Analizados

El Dashboard está organizado en 5 pestañas estratégicas que responden a las necesidades del negocio:

### 1. 🌎 Análisis Geoespacial

- **Visualización de la red de conectividad global.**
- **Feature:** Mapa interactivo con proyección equirectangular.
- **Funcionalidad:** Filtro de densidad para visualizar desde las top 50 hasta 2000 rutas simultáneas.

### 2. 📊 Rentabilidad y Negocio

- **Análisis financiero de las operaciones.**
- **Rutas Estrella (Scatter Plot):** Correlación entre Volumen de Tickets vs. Ingresos Totales. Permite identificar rutas de alto valor ("Cash Cows") vs rutas de alto volumen.
- **Share de Mercado:** Composición de ingresos por Clase (Economía/Ejecutiva) o Categoría de Avión.

### 3. ✈️ Eficiencia de Flota

- **Evaluación del rendimiento de los activos.**
- **KPI:** Factor de ocupación y generación de ingresos por modelo de avión.
- **Insight:** Comparativa entre fabricantes (Boeing vs Airbus vs Embraer) para detectar subutilización de aeronaves grandes.

### 4. 👥 Clientes y Comportamiento (CRM)

- **Perfilado del pasajero.**
- **Histograma de Anticipación:** Análisis de días de antelación de compra (Lead Time), segmentado por clase. Revela patrones de compra corporativos vs turísticos.
- **Demografía:** Segmentación por rango etario y nacionalidad.

### 5. 📅 Tendencias Temporales

- **Análisis de series de tiempo.**
- **Evolución de Ventas:** Gráfico de área con agrupación dinámica (Diaria/Mensual/Trimestral) para detectar estacionalidad y picos de demanda.

---

## 🚀 Instalación y Despliegue

Este proyecto utiliza [uv](https://github.com/astral-sh/uv) para una gestión de dependencias ultrarrápida.

### Prerrequisitos

- Python 3.10 o superior.
- PostgreSQL (Local o en la nube) con el esquema `analytics` cargado.
- [uv](https://github.com/astral-sh/uv) instalado.

### Pasos

#### 1️⃣ Clonar el repositorio:

```bash
git clone https://github.com/tu-usuario/devflights-analytics.git
cd devflights-analytics
```

#### 2️⃣ Configurar Variables de Entorno

Crea un archivo `.streamlit/secrets.toml` con las credenciales de base de datos:

```toml
[postgres]
host = "localhost"
port = "5432"
dbname = "devflights_airways"
user = "tu_usuario"
password = "tu_password"
```

#### 3️⃣ Instalar dependencias y ejecutar:

```bash
uv sync
uv run streamlit run app.py
```

---

## 🛠️ Tecnologías Utilizadas

- **Lenguaje:** Python
- **Frontend:** Streamlit
- **Visualización:** Plotly Express & Graph Objects
- **Data Manipulation:** Pandas
- **Database ORM:** SQLAlchemy
- **Package Manager:** uv

---

## 👨‍💻 Créditos

Desarrollado como proyecto final de Data Analytics de DevFlights.

DevFlights Airways © 2025
