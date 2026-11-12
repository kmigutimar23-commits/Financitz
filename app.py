import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS GLOBALES
# ==========================================
st.set_page_config(page_title="Financitz | ITM 2026", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    .stApp {
        background: linear-gradient(rgba(14, 20, 31, 0.65), rgba(14, 20, 31, 0.85)), 
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070');
        background-size: cover; background-position: center; background-attachment: fixed;
    }
    
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6 0%, #1D4ED8 100%); 
        color: white; border-radius: 8px; border: none; font-weight: bold; width: 100%; padding: 12px; transition: transform 0.2s;
    }
    .stButton>button:hover { transform: scale(1.01); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5); }
    
    span[data-baseweb="tag"] { background-color: rgba(59, 130, 246, 0.25) !important; border: 1px solid #3B82F6 !important; color: #FFFFFF !important; }
    span[data-baseweb="tag"] svg { fill: #FFFFFF !important; }
    div[role="radiogroup"] > label > div:first-child { accent-color: #3B82F6 !important; }
    
    div[data-testid="metric-container"] {
        background-color: rgba(30, 33, 48, 0.85); backdrop-filter: blur(10px); border-left: 5px solid #3B82F6; padding: 15px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    .conclusion-box {
        background-color: rgba(29, 78, 216, 0.15); backdrop-filter: blur(10px); border-left: 5px solid #3B82F6; padding: 25px; border-radius: 8px; margin-top: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    .hero-banner { 
        background-color: rgba(14, 20, 31, 0.5); backdrop-filter: blur(8px); padding: 80px 40px; border-radius: 15px; text-align: center; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.1); 
    }
    
    h1, h2, h3, h4 { color: #E2E8F0; font-family: 'Helvetica Neue', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DICCIONARIOS DE ACTIVOS Y PERFILES EN ESPAÑOL
# ==========================================
activos_dict = {
    "Apple (AAPL) - Tecnología": "AAPL", "Microsoft (MSFT) - Tecnología": "MSFT", "Nvidia (NVDA) - Tecnología": "NVDA", "Alphabet (GOOGL) - Tecnología": "GOOGL", "Meta Platforms (META) - Tecnología": "META",
    "JPMorgan Chase (JPM) - Finanzas": "JPM", "Visa (V) - Finanzas": "V", "Mastercard (MA) - Finanzas": "MA", "Bank of America (BAC) - Finanzas": "BAC", "Goldman Sachs (GS) - Finanzas": "GS",
    "Johnson & Johnson (JNJ) - Salud": "JNJ", "UnitedHealth (UNH) - Salud": "UNH", "Eli Lilly (LLY) - Salud": "LLY", "Pfizer (PFE) - Salud": "PFE", "AbbVie (ABBV) - Salud": "ABBV",
    "Amazon (AMZN) - Consumo Discrecional": "AMZN", "Tesla (TSLA) - Consumo Discrecional": "TSLA", "Walmart (WMT) - Consumo Básico": "WMT", "Coca-Cola (KO) - Consumo Básico": "KO", "PepsiCo (PEP) - Consumo Básico": "PEP",
    "Exxon Mobil (XOM) - Energía": "XOM", "Chevron (CVX) - Energía": "CVX", "Caterpillar (CAT) - Industrial": "CAT", "General Electric (GE) - Industrial": "GE", "Lockheed Martin (LMT) - Industrial": "LMT",
    "Walt Disney (DIS) - Entretenimiento": "DIS", "Netflix (NFLX) - Entretenimiento": "NFLX", "Comcast (CMCSA) - Telecom": "CMCSA", "AT&T (T) - Telecom": "T", "Verizon (VZ) - Telecom": "VZ",
    "S&P 500 (SPY) - Mercado EE.UU.": "SPY", "SPDR Gold (GLD) - ETF Oro": "GLD", "Bonos del Tesoro (TLT) - Refugio": "TLT", "Bitcoin (BTC-USD) - Criptomoneda": "BTC-USD", "Ethereum (ETH-USD) - Criptomoneda": "ETH-USD"
}
nombres_activos = list(activos_dict.keys())

# Base de datos local para que la presentación cargue de forma instantánea y en perfecto español
perfiles_es = {
    "AAPL": {"sector": "Tecnología", "industria": "Electrónica de Consumo", "resumen": "Diseña, fabrica y comercializa dispositivos móviles, computadoras y wearables a nivel mundial, destacando por su ecosistema iOS y servicios digitales."},
    "MSFT": {"sector": "Tecnología", "industria": "Software / Nube", "resumen": "Líder global en software, servicios en la nube (Azure) y hardware. Domina el mercado de sistemas operativos y herramientas de productividad empresarial."},
    "NVDA": {"sector": "Tecnología", "industria": "Semiconductores", "resumen": "Pionera en unidades de procesamiento gráfico (GPU) e inteligencia artificial. Sus chips son fundamentales para el desarrollo de IA, gaming y centros de datos."},
    "GOOGL": {"sector": "Tecnología", "industria": "Servicios de Internet", "resumen": "Motor de búsqueda líder mundial, domina la publicidad digital, el ecosistema Android, computación en la nube y desarrollo avanzado de Inteligencia Artificial."},
    "META": {"sector": "Tecnología", "industria": "Redes Sociales", "resumen": "Opera las plataformas de redes sociales más grandes del mundo (Facebook, Instagram, WhatsApp) y lidera el desarrollo de tecnologías de realidad virtual y metaverso."},
    "JPM": {"sector": "Finanzas", "industria": "Banca Diversificada", "resumen": "Una de las instituciones financieras más grandes del mundo, ofreciendo servicios de banca de inversión, servicios financieros para consumidores y gestión de activos."},
    "V": {"sector": "Finanzas", "industria": "Servicios de Crédito", "resumen": "Red global de pagos digitales que conecta a consumidores, comerciantes, instituciones financieras y gobiernos en más de 200 países y territorios."},
    "MA": {"sector": "Finanzas", "industria": "Servicios de Crédito", "resumen": "Empresa tecnológica multinacional en la industria global de pagos, facilitando el procesamiento de transacciones electrónicas en todo el mundo."},
    "BAC": {"sector": "Finanzas", "industria": "Banca Diversificada", "resumen": "Institución financiera multinacional que ofrece una amplia gama de servicios bancarios, de inversión y de gestión de patrimonio para individuos y empresas."},
    "GS": {"sector": "Finanzas", "industria": "Mercados de Capitales", "resumen": "Firma global líder en banca de inversión, valores y gestión de inversiones que atiende a corporaciones, instituciones financieras y gobiernos."},
    "JNJ": {"sector": "Salud", "industria": "Farmacéutica", "resumen": "Gigante diversificado del sector salud que investiga, desarrolla y comercializa productos farmacéuticos, dispositivos médicos y bienes de consumo masivo."},
    "UNH": {"sector": "Salud", "industria": "Planes de Salud", "resumen": "Empresa de seguros de salud y servicios médicos diversificados, proporcionando beneficios y cobertura a millones de personas a nivel mundial."},
    "LLY": {"sector": "Salud", "industria": "Farmacéutica", "resumen": "Compañía farmacéutica global enfocada en el descubrimiento y desarrollo de medicamentos innovadores para la diabetes, oncología y neurociencias."},
    "PFE": {"sector": "Salud", "industria": "Farmacéutica", "resumen": "Una de las mayores empresas biofarmacéuticas del mundo, famosa por descubrir y desarrollar medicamentos y vacunas para diversas áreas terapéuticas."},
    "ABBV": {"sector": "Salud", "industria": "Biotecnología", "resumen": "Compañía biofarmacéutica basada en la investigación, enfocada en desarrollar terapias avanzadas en inmunología, oncología, virología y neurociencia."},
    "AMZN": {"sector": "Consumo", "industria": "Comercio Electrónico / Nube", "resumen": "Gigante del comercio electrónico minorista y proveedor líder de infraestructura de computación en la nube (AWS) a nivel mundial."},
    "TSLA": {"sector": "Consumo", "industria": "Fabricación de Automóviles", "resumen": "Diseña, desarrolla y fabrica vehículos eléctricos de alto rendimiento, así como sistemas de generación y almacenamiento de energía limpia y paneles solares."},
    "WMT": {"sector": "Consumo Básico", "industria": "Supermercados", "resumen": "La corporación minorista más grande del mundo, operando una cadena global de hipermercados, tiendas de descuento y supermercados."},
    "KO": {"sector": "Consumo Básico", "industria": "Bebidas no alcohólicas", "resumen": "La empresa líder de bebidas a nivel global, propietaria y comercializadora de algunas de las marcas de refrescos, jugos y aguas más reconocidas."},
    "PEP": {"sector": "Consumo Básico", "industria": "Bebidas y Snacks", "resumen": "Compañía multinacional de alimentos, aperitivos y bebidas, con un portafolio que incluye marcas populares globalmente como Frito-Lay y Gatorade."},
    "XOM": {"sector": "Energía", "industria": "Petróleo y Gas", "resumen": "Una de las mayores compañías petroleras y petroquímicas del mundo que cotizan en bolsa, explorando y produciendo energía a nivel global."},
    "CVX": {"sector": "Energía", "industria": "Petróleo y Gas", "resumen": "Corporación energética multinacional que participa en todos los aspectos de las industrias del petróleo, gas natural y fuentes de energía alternativas."},
    "CAT": {"sector": "Industrial", "industria": "Maquinaria Pesada", "resumen": "Fabricante líder mundial de equipos de construcción y minería, motores diésel y de gas natural, turbinas industriales y locomotoras."},
    "GE": {"sector": "Industrial", "industria": "Conglomerado", "resumen": "Compañía industrial y tecnológica multinacional con un fuerte enfoque actual en la aviación, sistemas de energía y energías renovables."},
    "LMT": {"sector": "Industrial", "industria": "Aeroespacial y Defensa", "resumen": "Compañía global de seguridad y aeroespacial dedicada a la investigación, diseño y fabricación de sistemas de tecnología avanzada militar y civil."},
    "DIS": {"sector": "Entretenimiento", "industria": "Medios y Parques", "resumen": "Conglomerado multinacional de medios y entretenimiento, operando redes de televisión, parques temáticos, estudios de producción y streaming."},
    "NFLX": {"sector": "Entretenimiento", "industria": "Streaming de Video", "resumen": "El servicio líder de entretenimiento por streaming en el mundo, ofreciendo una amplia variedad de series, documentales y largometrajes originales."},
    "CMCSA": {"sector": "Telecomunicaciones", "industria": "TV por Cable / Internet", "resumen": "Conglomerado global de telecomunicaciones y medios, uno de los mayores proveedores de servicios de radiodifusión, cable y conectividad a internet."},
    "T": {"sector": "Telecomunicaciones", "industria": "Servicios de Comunicación", "resumen": "Holding que provee servicios de telecomunicaciones, medios y tecnología a nivel mundial, incluyendo redes móviles e internet de banda ancha."},
    "VZ": {"sector": "Telecomunicaciones", "industria": "Servicios de Comunicación", "resumen": "Proveedor líder de servicios de comunicaciones, tecnología, información y entretenimiento móvil para consumidores y empresas a nivel mundial."},
    "SPY": {"sector": "Refugio / ETF", "industria": "Índice de Mercado", "resumen": "Fondo cotizado (ETF) que busca replicar el rendimiento del índice S&P 500, permitiendo invertir simultáneamente en las 500 empresas más grandes de EE. UU."},
    "GLD": {"sector": "Refugio / ETF", "industria": "Materias Primas", "resumen": "Fondo de inversión (ETF) diseñado para rastrear el precio del oro físico, ofreciendo a los inversores un activo de refugio seguro en tiempos de incertidumbre."},
    "TLT": {"sector": "Refugio / ETF", "industria": "Bonos Gubernamentales", "resumen": "Fondo (ETF) que busca replicar los resultados de un índice compuesto por bonos del Tesoro de EE. UU. con vencimientos superiores a 20 años (deuda segura)."},
    "BTC-USD": {"sector": "Criptomoneda", "industria": "Activo Digital", "resumen": "La primera y más grande criptomoneda descentralizada del mundo, basada en tecnología blockchain y utilizada como activo digital y reserva de valor."},
    "ETH-USD": {"sector": "Criptomoneda", "industria": "Contratos Inteligentes", "resumen": "Plataforma de software descentralizada basada en blockchain, famosa por su criptomoneda (Ether) y por ser la red principal para ejecutar contratos inteligentes."}
}

# ==========================================
# 3. BANNER PRINCIPAL
# ==========================================
st.markdown("""
<div class="hero-banner">
<h3 style="color: #FF4B4B; letter-spacing: 3px; text-transform: uppercase; font-weight: 800;">⚡ Financitz</h3>
<h1 style="color: #FFFFFF; font-size: 3.2em; font-style: italic; margin-top: 15px; margin-bottom: 10px; line-height: 1.2; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">"El retorno de la inversión es importante,<br>pero también lo es el grado de incertidumbre que lo rodea."</h1>
<h3 style="color: #3B82F6; font-weight: 400; margin-bottom: 25px;">- Harry Markowitz, Premio Nobel de Economía</h3>
<p style="color: #CBD5E1; font-size: 1.15em; max-width: 700px; margin: 0 auto; line-height: 1.5; border-top: 1px solid rgba(59, 130, 246, 0.3); padding-top: 20px;">Defina su horizonte de inversión para evaluar el mercado y deje que nuestro motor algorítmico construya la estrategia que mejor equilibre su riesgo y rentabilidad.</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. SELECCIÓN DE HISTÓRICO DE DATOS
# ==========================================
st.markdown("<h3 style='text-align: center;'>Selección de Histórico de Datos</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0AEC0;'>Defina el período de tiempo sobre el cual se calcularán las varianzas, covarianzas y Betas.</p>", unsafe_allow_html=True)

col_esp1, col_f1, col_f2, col_esp2 = st.columns([1, 1.5, 1.5, 1])
fecha_inicio_str = col_f1.text_input("Desde (AAAA-MM-DD):", "2020-01-01")
fecha_fin_str = col_f2.text_input("Hasta (AAAA-MM-DD):", "2024-01-01")
st.divider()

fechas_validas = False
try:
    fecha_inicio = datetime.datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
    fecha_fin = datetime.datetime.strptime(fecha_fin_str, "%Y-%m-%d").date()
    if fecha_inicio < fecha_fin:
        fechas_validas = True
    else:
        st.error("La fecha de inicio debe ser estrictamente anterior a la fecha de fin.")
except ValueError:
    st.error("Formato de fecha incorrecto. Utilice el estándar AAAA-MM-DD.")

if fechas_validas:
    # ==========================================
    # SECCIÓN 1: COMPARADOR CON INFORMACIÓN EMPRESARIAL
    # ==========================================
    st.markdown("<h2 style='text-align: center;'>Fase I: Análisis de Activos Individuales</h2>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 4, 1])
    with col_c2:
        activos_comparar = st.multiselect("Seleccione los activos a evaluar:", nombres_activos, default=["S&P 500 (SPY) - Mercado EE.UU.", "Apple (AAPL) - Tecnología"])
        btn_comparar = st.button("Ejecutar Análisis Comparativo")

    if btn_comparar:
        if len(activos_comparar) > 0:
            tcks_comp = [activos_dict[ac] for ac in activos_comparar]
            with st.spinner("Procesando series de tiempo..."):
                
                st.markdown("<h4 style='text-align: center; margin-top: 20px; color: #3B82F6;'>Perfil Corporativo de los Activos Seleccionados</h4>", unsafe_allow_html=True)
                cols_info = st.columns(len(tcks_comp))
                
                # Renderizado de perfiles en español de forma instantánea
                for idx, ticker in enumerate(tcks_comp):
                    with cols_info[idx]:
                        if ticker in perfiles_es:
                            sector = perfiles_es[ticker]["sector"]
                            industria = perfiles_es[ticker]["industria"]
                            resumen = perfiles_es[ticker]["resumen"]
                        else:
                            sector, industria, resumen = "Desconocido", "Desconocido", "Datos corporativos no disponibles en la base."
                        
                        st.markdown(f"**{ticker}**<br>🛡️ Sector: {sector}<br>⚙️ Industria: {industria}<br>_{resumen}_", unsafe_allow_html=True)
                
                data_comp = yf.download(tcks_comp, start=fecha_inicio, end=fecha_fin)['Close']
                fig_comp = go.Figure()
                if len(tcks_comp) == 1:
                    data_norm = (data_comp / data_comp.iloc[0]) * 100
                    data_norm = pd.DataFrame(data_norm, columns=tcks_comp)
                else:
                    data_norm = (data_comp / data_comp.iloc[0]) * 100
                
                for ticker in tcks_comp:
                    fig_comp.add_trace(go.Scatter(x=data_norm.index, y=data_norm[ticker], mode='lines', name=ticker, line=dict(width=3)))
                
                fig_comp.update_layout(title="Proyección de Crecimiento (Base $100 USD)", template="plotly_dark", hovermode="x unified", height=450, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_comp, use_container_width=True)

                if len(tcks_comp) > 1:
                    st.markdown(f"""
                    <div class="conclusion-box">
                        <h3 style="margin-top: 0; color: #3B82F6;">Interpretación de Dinámica de Mercado</h3>
                        <p>Observe cómo el <b>S&P 500 (SPY)</b> actúa como el termómetro general de la economía. Las acciones individuales que superan la línea del SPY generan mayores retornos, pero generalmente exponen su capital a caídas mucho más agresivas durante períodos de crisis. Conocer el negocio detrás de la acción (ver perfiles arriba) es el primer paso antes de optimizar matemáticamente.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
    st.divider()

    # ==========================================
    # SECCIÓN 2: OPTIMIZACIÓN Y FRONTERA EFICIENTE
    # ==========================================
    st.markdown("<h2 style='text-align: center;'>Fase II: Frontera Eficiente (Modelo Markowitz)</h2>", unsafe_allow_html=True)
    
    col_o1, col_o2, col_o3 = st.columns([1, 4, 1])
    with col_o2:
        modo = st.radio("Estrategia de Estructuración:", ["Asistente de Diversificación Inteligente", "Selección Manual de Activos"], horizontal=True)
        
        if modo == "Selección Manual de Activos":
            opciones_portafolio = st.multiselect("Defina el universo de activos a optimizar:", nombres_activos, default=["Apple (AAPL) - Tecnología", "Johnson & Johnson (JNJ) - Salud", "Exxon Mobil (XOM) - Energía"])
        else:
            favorita = st.selectbox("Seleccione un activo núcleo (Core Asset):", nombres_activos)
            
            sectores_algoritmo = {
                "Tecnología": ["Apple (AAPL) - Tecnología", "Microsoft (MSFT) - Tecnología", "Nvidia (NVDA) - Tecnología", "Alphabet (GOOGL) - Tecnología", "Meta Platforms (META) - Tecnología"],
                "Finanzas": ["JPMorgan Chase (JPM) - Finanzas", "Visa (V) - Finanzas", "Mastercard (MA) - Finanzas", "Bank of America (BAC) - Finanzas", "Goldman Sachs (GS) - Finanzas"],
                "Salud": ["Johnson & Johnson (JNJ) - Salud", "UnitedHealth (UNH) - Salud", "Eli Lilly (LLY) - Salud", "Pfizer (PFE) - Salud", "AbbVie (ABBV) - Salud"],
                "Consumo": ["Amazon (AMZN) - Consumo Discrecional", "Tesla (TSLA) - Consumo Discrecional", "Walmart (WMT) - Consumo Básico", "Coca-Cola (KO) - Consumo Básico", "PepsiCo (PEP) - Consumo Básico"],
                "Energía/Industrial": ["Exxon Mobil (XOM) - Energía", "Chevron (CVX) - Energía", "Caterpillar (CAT) - Industrial", "General Electric (GE) - Industrial", "Lockheed Martin (LMT) - Industrial"],
                "Telecom/Entretenimiento": ["Walt Disney (DIS) - Entretenimiento", "Netflix (NFLX) - Entretenimiento", "Comcast (CMCSA) - Telecom", "AT&T (T) - Telecom", "Verizon (VZ) - Telecom"],
                "Refugios/Cripto": ["S&P 500 (SPY) - Mercado EE.UU.", "SPDR Gold (GLD) - ETF Oro", "Bonos del Tesoro (TLT) - Refugio", "Bitcoin (BTC-USD) - Criptomoneda", "Ethereum (ETH-USD) - Criptomoneda"]
            }
            
            recomendacion = [favorita]
            categoria_fav = None
            
            for sector, lista_activos in sectores_algoritmo.items():
                if favorita in lista_activos:
                    categoria_fav = sector
                    break
            
            for sector, lista_activos in sectores_algoritmo.items():
                if sector != categoria_fav:
                    recomendacion.append(lista_activos[0])
            
            opciones_portafolio = st.multiselect("Portafolio blindado sugerido por el algoritmo (7 Sectores):", nombres_activos, default=recomendacion)
        
        opciones_portafolio = list(dict.fromkeys(opciones_portafolio))
        st.write("")
        simular_port_btn = st.button("Construir Frontera Eficiente")

    if simular_port_btn:
        if len(opciones_portafolio) < 2:
            st.error("El motor de cálculo requiere al menos 2 activos.")
        else:
            tcks_port = [activos_dict[op] for op in opciones_portafolio]
            tcks_download = list(set(tcks_port + ['SPY'])) 
            
            with st.spinner("Modelando 3,000 portafolios y calculando riesgo Beta..."):
                data_all = yf.download(tcks_download, start=fecha_inicio, end=fecha_fin)['Close'].pct_change().dropna()
                retornos = data_all[tcks_port]
                retornos_mercado = data_all['SPY'] 
                
                np.random.seed(42)
                num_port = 3000
                resultados = np.zeros((3, num_port))
                betas_portafolios = np.zeros(num_port)
                pesos_guardados = []
                
                matriz_cov = retornos.cov() * 252
                retornos_anuales = retornos.mean() * 252
                
                cov_con_mercado = [np.cov(retornos[ticker], retornos_mercado)[0,1] for ticker in tcks_port]
                var_mercado = np.var(retornos_mercado)
                betas_individuales = np.array(cov_con_mercado) / var_mercado
                
                for i in range(num_port):
                    pesos = np.random.random(len(tcks_port))
                    pesos /= np.sum(pesos)
                    pesos_guardados.append(pesos)
                    
                    r_port = np.sum(retornos_anuales * pesos)
                    vol_port = np.sqrt(np.dot(pesos.T, np.dot(matriz_cov, pesos)))
                    beta_port = np.dot(pesos, betas_individuales)
                    
                    resultados[0,i] = r_port       
                    resultados[1,i] = vol_port     
                    resultados[2,i] = r_port / vol_port 
                    betas_portafolios[i] = beta_port

                idx_optimo = np.argmax(resultados[2])
                idx_conservador = np.argmin(resultados[1])
                idx_agresivo = np.argmax(resultados[0]) 
                
                st.write("")
                st.markdown("<h3 style='text-align: center;'>Métricas de los Portafolios Recomendados</h3>", unsafe_allow_html=True)
                
                col_met1, col_met2, col_met3 = st.columns(3)
                
                with col_met1:
                    st.markdown("<div style='background-color:rgba(255, 75, 75, 0.1); padding:10px; border-radius:10px; border:1px solid #FF4B4B;'>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color:#FF4B4B; text-align:center;'>Perfil Óptimo</h4>", unsafe_allow_html=True)
                    m1, m2 = st.columns(2)
                    m1.metric("Retorno Esperado", f"{resultados[0, idx_optimo]:.2%}")
                    m2.metric("Coeficiente Beta", f"{betas_portafolios[idx_optimo]:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with col_met2:
                    st.markdown("<div style='background-color:rgba(0, 191, 255, 0.1); padding:10px; border-radius:10px; border:1px solid #00BFFF;'>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color:#00BFFF; text-align:center;'>Perfil Conservador</h4>", unsafe_allow_html=True)
                    m3, m4 = st.columns(2)
                    m3.metric("Retorno Esperado", f"{resultados[0, idx_conservador]:.2%}")
                    m4.metric("Coeficiente Beta", f"{betas_portafolios[idx_conservador]:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                with col_met3:
                    st.markdown("<div style='background-color:rgba(139, 92, 246, 0.1); padding:10px; border-radius:10px; border:1px solid #8B5CF6;'>", unsafe_allow_html=True)
                    st.markdown(f"<h4 style='color:#8B5CF6; text-align:center;'>Perfil Agresivo</h4>", unsafe_allow_html=True)
                    m5, m6 = st.columns(2)
                    m5.metric("Retorno Esperado", f"{resultados[0, idx_agresivo]:.2%}")
                    m6.metric("Coeficiente Beta", f"{betas_portafolios[idx_agresivo]:.2f}")
                    st.markdown("</div>", unsafe_allow_html=True)

                fig_scatter = go.Figure()
                
                fig_scatter.add_trace(go.Scatter(
                    x=resultados[1,:], y=resultados[0,:], mode='markers',
                    marker=dict(color=resultados[2,:], colorscale='Viridis', size=6, opacity=0.7, colorbar=dict(title="Ratio Sharpe")),
                    name='Portafolios Simulados', hovertext=[f"Beta: {b:.2f}" for b in betas_portafolios]
                ))
                
                fig_scatter.add_trace(go.Scatter(
                    x=[resultados[1, idx_optimo]], y=[resultados[0, idx_optimo]], mode='markers+text',
                    marker=dict(color='#FF4B4B', size=16, symbol='star', line=dict(width=2, color='white')),
                    name='Máximo Sharpe', text=['Óptimo'], textposition='top left', textfont=dict(color='#FF4B4B', size=15)
                ))
                
                fig_scatter.add_trace(go.Scatter(
                    x=[resultados[1, idx_conservador]], y=[resultados[0, idx_conservador]], mode='markers+text',
                    marker=dict(color='#00BFFF', size=16, symbol='star', line=dict(width=2, color='white')),
                    name='Mínima Varianza', text=['Conservador'], textposition='bottom right', textfont=dict(color='#00BFFF', size=15)
                ))

                fig_scatter.add_trace(go.Scatter(
                    x=[resultados[1, idx_agresivo]], y=[resultados[0, idx_agresivo]], mode='markers+text',
                    marker=dict(color='#8B5CF6', size=16, symbol='star', line=dict(width=2, color='white')),
                    name='Máximo Retorno', text=['Agresivo'], textposition='top right', textfont=dict(color='#8B5CF6', size=15)
                ))
                
                fig_scatter.update_layout(title="Frontera Eficiente de Markowitz (Riesgo vs. Retorno)", xaxis_title="Riesgo (Volatilidad Anualizada)", yaxis_title="Retorno Esperado Anualizado", template="plotly_dark", height=600, paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_scatter, use_container_width=True)
                
                st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Estructura Porcentual Recomendada</h3>", unsafe_allow_html=True)
                cp1, cp2, cp3 = st.columns(3)
                
                with cp1:
                    f_opt = px.pie(values=pesos_guardados[idx_optimo], names=opciones_portafolio, hole=0.5, color_discrete_sequence=px.colors.sequential.Reds_r)
                    f_opt.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    f_opt.update_layout(title=dict(text="Perfil Óptimo", x=0.5, font=dict(color="#FF4B4B", size=18)), template="plotly_dark", showlegend=False, height=450, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=50, l=10, r=10))
                    st.plotly_chart(f_opt, use_container_width=True)
                    
                with cp2:
                    f_cons = px.pie(values=pesos_guardados[idx_conservador], names=opciones_portafolio, hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
                    f_cons.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    f_cons.update_layout(title=dict(text="Perfil Conservador", x=0.5, font=dict(color="#00BFFF", size=18)), template="plotly_dark", showlegend=False, height=450, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=50, l=10, r=10))
                    st.plotly_chart(f_cons, use_container_width=True)

                with cp3:
                    f_agr = px.pie(values=pesos_guardados[idx_agresivo], names=opciones_portafolio, hole=0.5, color_discrete_sequence=px.colors.sequential.Purples_r)
                    f_agr.update_traces(textposition='inside', textinfo='percent+label', textfont_size=12)
                    f_agr.update_layout(title=dict(text="Perfil Agresivo", x=0.5, font=dict(color="#8B5CF6", size=18)), template="plotly_dark", showlegend=False, height=450, paper_bgcolor='rgba(0,0,0,0)', margin=dict(t=50, b=50, l=10, r=10))
                    st.plotly_chart(f_agr, use_container_width=True)

                activo_fuerte_optimo = opciones_portafolio[np.argmax(pesos_guardados[idx_optimo])]
                activo_fuerte_cons = opciones_portafolio[np.argmax(pesos_guardados[idx_conservador])]
                activo_fuerte_agr = opciones_portafolio[np.argmax(pesos_guardados[idx_agresivo])]
                
                st.markdown(f"""
                <div class="conclusion-box">
                    <h3 style="margin-top: 0; color: #3B82F6;">Síntesis Estratégica de Asignación de Capital</h3>
                    <p>La <b>Frontera Eficiente</b> (Gráfico de dispersión) representa 3,000 combinaciones posibles. Seleccione su estructura ideal basándose en el <b>Coeficiente Beta</b> (Sensibilidad al mercado) y su tolerancia al riesgo:</p>
                    <ul>
                        <li><span style="color:#FF4B4B; font-weight:bold;">Perfil Óptimo (Beta: {betas_portafolios[idx_optimo]:.2f}):</span> Matemáticamente es el punto con mejor equilibrio (Máximo Ratio de Sharpe). Liderado por <b>{activo_fuerte_optimo}</b>, este portafolio compensa inteligentemente cada punto de riesgo asumido con un nivel de rentabilidad justificado.</li>
                        <li><span style="color:#00BFFF; font-weight:bold;">Perfil Conservador (Beta: {betas_portafolios[idx_conservador]:.2f}):</span> Se ubica en el extremo izquierdo de la frontera. Concentra su peso en <b>{activo_fuerte_cons}</b>, buscando minimizar la volatilidad a toda costa. Actúa como un amortiguador cuando los mercados financieros colapsan.</li>
                        <li><span style="color:#8B5CF6; font-weight:bold;">Perfil Agresivo (Beta: {betas_portafolios[idx_agresivo]:.2f}):</span> Se encuentra en la punta superior derecha. Concentra la mayor parte del capital en <b>{activo_fuerte_agr}</b> para extraer el retorno absoluto más alto posible, ignorando por completo la estabilidad. Recomendado exclusivamente para capital de alto riesgo.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
