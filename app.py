import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import datetime

# ==========================================
# 1. CONFIGURACIÓN Y ESTILOS
# ==========================================
st.set_page_config(page_title="Financitz | ITM 2026", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Fondo global iluminado para destacar la imagen de los edificios */
    .stApp {
        background: linear-gradient(rgba(14, 20, 31, 0.65), rgba(14, 20, 31, 0.85)), 
                    url('https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=2070');
        background-size: cover;
        background-position: center;
        background-attachment: fixed;
    }
    
    /* Botones con gradiente Azul Ejecutivo */
    .stButton>button {
        background: linear-gradient(90deg, #3B82F6 0%, #1D4ED8 100%); 
        color: white; border-radius: 8px; border: none; font-weight: bold; width: 100%; padding: 12px; transition: transform 0.2s;
    }
    .stButton>button:hover { transform: scale(1.01); box-shadow: 0 4px 15px rgba(59, 130, 246, 0.5); }
    
    /* Alinear los radio buttons al rojo de Streamlit */
    div[role="radiogroup"] > label > div:first-child {
        accent-color: #FF4B4B !important;
    }
    
    /* Cajas de métricas con borde rojo */
    div[data-testid="metric-container"] {
        background-color: rgba(30, 33, 48, 0.85);
        backdrop-filter: blur(10px);
        border-left: 5px solid #FF4B4B; padding: 15px; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.4);
    }
    
    .hero-banner {
        background-color: rgba(14, 20, 31, 0.5);
        backdrop-filter: blur(8px);
        padding: 80px 40px; border-radius: 15px; text-align: center; margin-bottom: 40px; border: 1px solid rgba(255,255,255,0.1);
    }
    
    .conclusion-box {
        background-color: rgba(29, 78, 216, 0.15); backdrop-filter: blur(10px); border-left: 5px solid #3B82F6; padding: 25px; border-radius: 8px; margin-top: 30px; box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    
    h1, h2, h3, h4 { color: #E2E8F0; font-family: 'Helvetica Neue', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. DICCIONARIO DE ACTIVOS
# ==========================================
activos_dict = {
    "Apple (AAPL) - Tecnología": "AAPL", "Microsoft (MSFT) - Software": "MSFT", "Nvidia (NVDA) - Semiconductores": "NVDA", "Amazon (AMZN) - E-commerce / Cloud": "AMZN",
    "Tesla (TSLA) - Automotriz": "TSLA", "Coca-Cola (KO) - Consumo Básico": "KO", "Johnson & Johnson (JNJ) - Salud": "JNJ", "JPMorgan Chase (JPM) - Finanzas": "JPM",
    "Delta Airlines (DAL) - Transporte": "DAL", "Exxon Mobil (XOM) - Energía": "XOM", "SPDR Gold (GLD) - ETF Oro": "GLD", "Bonos del Tesoro (TLT) - Refugio": "TLT",
    "Bitcoin (BTC-USD) - Criptomoneda": "BTC-USD", "S&P 500 (SPY) - Mercado EE.UU.": "SPY"
}
nombres_activos = list(activos_dict.keys())

# ==========================================
# 3. BANNER PRINCIPAL (FRASE MAXIMIZADA)
# ==========================================
st.markdown("""
<div class="hero-banner">
    <h3 style="color: #FF4B4B; letter-spacing: 3px; text-transform: uppercase; font-weight: 800;">⚡ Financitz</h3>
    <h1 style="color: #FFFFFF; font-size: 3.2em; font-style: italic; margin-top: 15px; margin-bottom: 20px; line-height: 1.2; text-shadow: 2px 2px 4px rgba(0,0,0,0.5);">"El retorno de la inversión es importante,<br>pero también lo es el grado de incertidumbre que lo rodea."</h1>
    <h3 style="color: #CBD5E1; font-weight: 300;">- Harry Markowitz, Premio Nobel de Economía</h3>
</div>
""", unsafe_allow_html=True)

# ==========================================
# 4. CONFIGURACIÓN GLOBAL DE TIEMPO (CENTRADA)
# ==========================================
st.markdown("<h3 style='text-align: center;'>Horizonte de Inversión Global</h3>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #A0AEC0;'>Defina el período histórico base para la ejecución de los modelos cuantitativos.</p>", unsafe_allow_html=True)

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
    # SECCIÓN 1: COMPARADOR (PANTALLA COMPLETA)
    # ==========================================
    st.markdown("<h2 style='text-align: center;'>Fase I: Análisis de Activos Individuales</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Evaluación del comportamiento aislado de cada instrumento financiero frente a la volatilidad del mercado.</p>", unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns([1, 4, 1])
    with col_c2:
        activos_comparar = st.multiselect("Seleccione los activos a evaluar:", nombres_activos, default=["Apple (AAPL) - Tecnología", "Bonos del Tesoro (TLT) - Refugio"])
        btn_comparar = st.button("Ejecutar Análisis Comparativo")

    if btn_comparar:
        if len(activos_comparar) > 0:
            tcks_comp = [activos_dict[ac] for ac in activos_comparar]
            with st.spinner("Procesando series de tiempo..."):
                data_comp = yf.download(tcks_comp, start=fecha_inicio, end=fecha_fin)['Close']
                
                fig_comp = go.Figure()
                if len(tcks_comp) == 1:
                    data_norm = (data_comp / data_comp.iloc[0]) * 100
                    data_norm = pd.DataFrame(data_norm, columns=tcks_comp)
                else:
                    data_norm = (data_comp / data_comp.iloc[0]) * 100
                
                for ticker in tcks_comp:
                    fig_comp.add_trace(go.Scatter(x=data_norm.index, y=data_norm[ticker], mode='lines', name=ticker, line=dict(width=3)))
                
                fig_comp.update_layout(title="Proyección de Crecimiento (Base $100 USD)", template="plotly_dark", hovermode="x unified", height=500, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_comp, use_container_width=True)

                if len(tcks_comp) > 1:
                    retornos_diarios = data_comp.pct_change().dropna()
                    retorno_total = (data_norm.iloc[-1] / 100) - 1
                    volatilidad_anual = retornos_diarios.std() * np.sqrt(252)
                    
                    mejor_ganador_idx = retorno_total.idxmax()
                    mas_seguro_idx = volatilidad_anual.idxmin()
                    mas_volatil_idx = volatilidad_anual.idxmax()
                    
                    nombre_ganador = [k for k, v in activos_dict.items() if v == mejor_ganador_idx][0]
                    nombre_seguro = [k for k, v in activos_dict.items() if v == mas_seguro_idx][0]
                    nombre_volatil = [k for k, v in activos_dict.items() if v == mas_volatil_idx][0]

                    st.markdown(f"""
                    <div class="conclusion-box">
                        <h3 style="margin-top: 0; color: #3B82F6;">Interpretación de Dinámica de Mercado</h3>
                        <p>Los datos históricos revelan patrones fundamentales en el binomio riesgo-rentabilidad:</p>
                        <ul>
                            <li><b>Líder de Rendimiento:</b> <b>{nombre_ganador}</b> maximizó la rentabilidad acumulada ({retorno_total[mejor_ganador_idx]:.1%}). Este potencial de crecimiento suele requerir tolerar caídas abruptas.</li>
                            <li><b>Pico de Volatilidad:</b> <b>{nombre_volatil}</b> registró las fluctuaciones más amplias (Desviación anual: {volatilidad_anual[mas_volatil_idx]:.1%}), representando el activo con mayor exposición al riesgo de mercado.</li>
                            <li><b>Ancla de Estabilidad:</b> <b>{nombre_seguro}</b> operó como el instrumento más conservador (Desviación anual: {volatilidad_anual[mas_seguro_idx]:.1%}), siendo óptimo para mitigar pérdidas durante ciclos bajistas.</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                
    st.divider()

    # ==========================================
    # SECCIÓN 2: OPTIMIZACIÓN (PANTALLA COMPLETA)
    # ==========================================
    st.markdown("<h2 style='text-align: center;'>Fase II: Construcción y Optimización (Modelo Markowitz)</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>Asignación matemática de pesos para maximizar el Ratio de Sharpe y estructurar la frontera eficiente.</p>", unsafe_allow_html=True)
    
    col_o1, col_o2, col_o3 = st.columns([1, 4, 1])
    with col_o2:
        modo = st.radio("Estrategia de Estructuración:", ["Selección Manual de Activos", "Asistente de Diversificación Inteligente"], horizontal=True)
        
        if modo == "Selección Manual de Activos":
            opciones_portafolio = st.multiselect("Defina el universo de activos a optimizar (Mínimo 3):", nombres_activos, default=["Apple (AAPL) - Tecnología", "SPDR Gold (GLD) - ETF Oro", "Johnson & Johnson (JNJ) - Salud"])
        else:
            favorita = st.selectbox("Seleccione un activo núcleo (Core Asset):", nombres_activos)
            if "Tecnología" in favorita or "Criptomoneda" in favorita:
                recomendacion = [favorita, "SPDR Gold (GLD) - ETF Oro", "Johnson & Johnson (JNJ) - Salud", "Coca-Cola (KO) - Consumo Básico"]
            else:
                recomendacion = [favorita, "Apple (AAPL) - Tecnología", "Bonos del Tesoro (TLT) - Refugio", "S&P 500 (SPY) - Mercado EE.UU."]
            opciones_portafolio = st.multiselect("Estructura sugerida por correlación inversa:", nombres_activos, default=recomendacion)
            opciones_portafolio = list(dict.fromkeys(opciones_portafolio))
        
        st.write("")
        simular_port_btn = st.button("Procesar Simulaciones de Monte Carlo")

    if simular_port_btn:
        if len(opciones_portafolio) < 2:
            st.error("El motor de cálculo requiere al menos 2 activos.")
        else:
            tcks_port = [activos_dict[op] for op in opciones_portafolio]
            with st.spinner("Modelando 3,000 escenarios probabilísticos..."):
                retornos = yf.download(tcks_port, start=fecha_inicio, end=fecha_fin)['Close'].pct_change().dropna()
                
                np.random.seed(42)
                num_port = 3000
                resultados = np.zeros((3, num_port))
                pesos_guardados = []
                matriz_cov = retornos.cov() * 252
                retornos_anuales = retornos.mean() * 252
                
                for i in range(num_port):
                    pesos = np.random.random(len(tcks_port))
                    pesos /= np.sum(pesos)
                    pesos_guardados.append(pesos)
                    r_port = np.sum(retornos_anuales * pesos)
                    vol_port = np.sqrt(np.dot(pesos.T, np.dot(matriz_cov, pesos)))
                    resultados[0,i] = r_port
                    resultados[1,i] = vol_port
                    resultados[2,i] = r_port / vol_port
                    
                idx_optimo = np.argmax(resultados[2])
                idx_conservador = np.argmin(resultados[1])
                
                trayectoria_opt = (1 + retornos.dot(pesos_guardados[idx_optimo])).cumprod() * 10000
                trayectoria_cons = (1 + retornos.dot(pesos_guardados[idx_conservador])).cumprod() * 10000

                st.write("")
                m1, m2 = st.columns(2)
                m1.metric("Retorno Esperado (Portafolio Óptimo)", f"{resultados[0, idx_optimo]:.2%}")
                m2.metric("Nivel de Riesgo (Portafolio Conservador)", f"{resultados[1, idx_conservador]:.2%}")

                # Gráfica a pantalla completa
                fig_port = go.Figure()
                fig_port.add_trace(go.Scatter(x=trayectoria_opt.index, y=trayectoria_opt, name='Frontera Óptima (Max Sharpe)', line=dict(color='#FF4B4B', width=3)))
                fig_port.add_trace(go.Scatter(x=trayectoria_cons.index, y=trayectoria_cons, name='Mínima Varianza (Protección)', line=dict(color='#00BFFF', width=3)))
                fig_port.update_layout(title="Simulación de Capital ($10,000 USD Base)", template="plotly_dark", hovermode="x unified", height=500, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor='rgba(0,0,0,0.5)', plot_bgcolor='rgba(0,0,0,0)')
                st.plotly_chart(fig_port, use_container_width=True)
                
                # Tortas centradas y expansivas (Rojos para óptimo, Azules para conservador)
                st.markdown("<h3 style='text-align: center; margin-top: 20px;'>Estructura Porcentual Recomendada</h3>", unsafe_allow_html=True)
                cp1, cp2 = st.columns(2)
                
                with cp1:
                    f_opt = px.pie(values=pesos_guardados[idx_optimo], names=opciones_portafolio, hole=0.5, color_discrete_sequence=['#D32F2F', '#FF6D00', '#FFD600', '#FF1744', '#E65100', '#FF9100', '#B71C1C'])          
                    f_opt.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
                    f_opt.update_layout(title=dict(text="Portafolio Óptimo", x=0.5, font=dict(size=20)), template="plotly_dark", showlegend=False, height=500, margin=dict(t=60, b=60, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(f_opt, use_container_width=True)
                with cp2:
                    f_cons = px.pie(values=pesos_guardados[idx_conservador], names=opciones_portafolio, hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
                    f_cons.update_traces(textposition='outside', textinfo='percent+label', textfont_size=15)
                    f_cons.update_layout(title=dict(text="Portafolio Conservador", x=0.5, font=dict(size=20)), template="plotly_dark", showlegend=False, height=500, margin=dict(t=60, b=60, l=40, r=40), paper_bgcolor='rgba(0,0,0,0)')
                    st.plotly_chart(f_cons, use_container_width=True)

                activo_fuerte_optimo = opciones_portafolio[np.argmax(pesos_guardados[idx_optimo])]
                activo_fuerte_cons = opciones_portafolio[np.argmax(pesos_guardados[idx_conservador])]
                
                st.markdown(f"""
                <div class="conclusion-box">
                    <h3 style="margin-top: 0; color: #3B82F6;">Síntesis Estratégica de Asignación de Capital</h3>
                    <p>Las métricas generadas por el modelo cuantitativo respaldan las siguientes directrices de inversión:</p>
                    <ul>
                        <li><b>Estrategia de Crecimiento (Perfil Óptimo):</b> Al sobreponderar sistemáticamente en <b>{activo_fuerte_optimo}</b> y estructurar una correlación defensiva con el resto del universo, el modelo alcanza el Ratio de Sharpe máximo. Esta arquitectura es idónea para horizontes de inversión donde la premisa es la acumulación agresiva de capital bajo riesgo matemático calibrado.</li>
                        <li><b>Estrategia de Preservación (Perfil Conservador):</b> Para blindar el patrimonio frente a la volatilidad sistemática, el motor estadístico transfiere el peso direccional hacia <b>{activo_fuerte_cons}</b>. Esta ponderación minimiza la varianza total del portafolio, constituyendo la táctica recomendada para perfiles con baja tolerancia al riesgo o necesidades de liquidez a corto plazo.</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)