import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# 1. Configurazione Pagina e Stile
st.set_page_config(page_title="SmartPest AI - Enterprise Dashboard", layout="wide", initial_sidebar_state="expanded")

st.title("📱 SmartPest AI - Dashboard IPM Professionale")
st.caption("Piattaforma Digitale di Autocontrollo Integrato - Scenario Fittizio: Pastificio Artigianale")
st.markdown("---")

# 2. Generazione del Database Fittizio Storico (1 Mese di Monitoraggi)
if 'df_catture' not in st.session_state:
    dates = pd.date_range(start="2026-04-26", end="2026-05-26", freq="D")
    np.random.seed(42)
    
    storico = []
    for d in dates:
        # Zona A - Silos (Punteruolo)
        storico.append({'Data': d, 'Area': 'Zona A: Silos Semola', 'Macchinario': 'Silos di Carico', 'Infestante': 'Sitophilus granarius', 'Catture': int(np.random.poisson(1.2)), 'Impatto': 3})
        # Zona B - Impasto (Blatte)
        cat_blatta = int(np.random.poisson(0.3)) if d.day != 15 else 4
        storico.append({'Data': d, 'Area': 'Zona B: Impasto', 'Macchinario': 'MAC-01 Trafile', 'Infestante': 'Blattella germanica', 'Catture': cat_blatta, 'Impatto': 4})
        # Zona C - Essiccazione (Tignole)
        cat_tignola = int(np.random.poisson(1.5 + (d.day / 10)))
        storico.append({'Data': d, 'Area': 'Zona C: Essiccazione', 'Macchinario': 'MAC-02 Celle', 'Infestante': 'Ephestia kueniella', 'Catture': cat_tignola, 'Impatto': 5})
        # Zona D - Logistica (Roditori)
        cat_topo = 1 if d.day == 24 else 0
        storico.append({'Data': d, 'Area': 'Zona D: Logistica', 'Macchinario': 'Magazzino Finito', 'Infestante': 'Mus musculus', 'Catture': cat_topo, 'Impatto': 5})

    st.session_state.df_catture = pd.DataFrame(storico)

# Funzione per calcolare rischi e alert secondo HACCP
def calcola_metriche(dataframe):
    df_res = dataframe.copy()
    df_res['Rischio_Ro'] = df_res['Catture'] * df_res['Impatto']
    def definisci_colore(r):
        if r['Rischio_Ro'] <= 4: return '🟢 VERDE (Normale)'
        elif r['Rischio_Ro'] <= 12: return '🟠 GIALLO (Attenzione)'
        else: return '🔴 ROSSO (Emergenza)'
    df_res['Stato_Alert'] = df_res.apply(definisci_colore, axis=1)
    return df_res

df_elaborato = calcola_metriche(st.session_state.df_catture)

# 3. BARRA LATERALE - Filtri e simulazione
st.sidebar.header("🔍 Filtri Avanzati Dashboard")
area_selezionata = st.sidebar.multiselect("Filtra per Area Fabbrica", options=df_elaborato['Area'].unique(), default=df_elaborato['Area'].unique())
infestante_selezionato = st.sidebar.multiselect("Filtra per Infestante Target", options=df_elaborato['Infestante'].unique(), default=df_elaborato['Infestante'].unique())

df_filtrato = df_elaborato[(df_elaborato['Area'].isin(area_selezionata)) & (df_elaborato['Infestante'].isin(infestante_selezionato))]

st.sidebar.markdown("---")
st.sidebar.subheader("📥 Inserimento Straordinario")
with st.sidebar.form("nuovo_dato"):
    st.write("Simula un'ispezione odierna:")
    f_area = st.selectbox("Area", ['Zona A: Silos Semola', 'Zona B: Impasto', 'Zona C: Essiccazione', 'Zona D: Logistica'])
    f_inf = st.selectbox("Specie", ['Ephestia kueniella', 'Sitophilus granarius', 'Blattella germanica', 'Mus musculus'])
    f_cat = st.number_input("Catture effettive", min_value=0, value=2)
    btn = st.form_submit_button("Inietta dato nel database")

if btn:
    m_dict = {'Zona A: Silos Semola':'Silos deaerato', 'Zona B: Impasto':'MAC-01 Trafile', 'Zona C: Essiccazione':'MAC-02 Celle', 'Zona D: Logistica':'Magazzino Finito'}
    i_dict = {'Ephestia kueniella':5, 'Sitophilus granarius':3, 'Blattella germanica':4, 'Mus musculus':5}
    nuovo_record = pd.DataFrame({'Data': [pd.to_datetime('2026-05-26')], 'Area': [f_area], 'Macchinario': [m_dict[f_area]], 'Infestante': [f_inf], 'Catture': [f_cat], 'Impatto': [i_dict[f_inf]]})
    st.session_state.df_catture = pd.concat([st.session_state.df_catture, nuovo_record], ignore_index=True)
    st.rerun()

# 4. KPI CARDS PRINCIPALI
c1, c2, c3, c4 = st.columns(4)
c1.metric("Catture Totali (30 gg)", int(df_filtrato['Catture'].sum()))
c2.metric("Indice di Rischio Medio", f"{df_filtrato['Rischio_Ro'].mean():.2f} / 25")
aree_rosse = len(df_elaborato[df_elaborato['Stato_Alert'] == '🔴 ROSSO (Emergenza)']['Area'].unique())
c3.metric("Aree in Allarme Critico", aree_rosse, delta="- Azione Richiesta" if aree_rosse > 0 else "OK")
c4.metric("Conformità Normativa BRC/IFS", "84%" if aree_rosse > 0 else "100%", delta="Sotto Soglia" if aree_rosse > 0 else "Ottimale")

st.markdown("### 📊 Analisi Grafica e Trend degli Infestanti")

# GRAFICI
col_g1, col_g2 = st.columns(2)

with col_g1:
    st.markdown("#### Linea di Tendenza delle Catture Giornaliere")
    fig_trend = px.line(df_filtrato, x='Data', y='Catture', color='Infestante', line_shape="spline", markers=True,
                        color_discrete_map={'Ephestia kueniella':'#ef4444', 'Sitophilus granarius':'#3b82f6', 'Blattella germanica':'#f59e0b', 'Mus musculus':'#8b5cf6'})
    st.plotly_chart(fig_trend, use_container_width=True)

with col_g2:
    st.markdown("#### Distribuzione delle Specie sul Totale delle Catture")
    fig_pie = px.pie(df_filtrato, values='Catture', names='Infestante', hole=0.4,
                     color_discrete_map={'Ephestia kueniella':'#ef4444', 'Sitophilus granarius':'#3b82f6', 'Blattella germanica':'#f59e0b', 'Mus musculus':'#8b5cf6'})
    st.plotly_chart(fig_pie, use_container_width=True)

# MAPPA TERMICA
st.markdown("### 🗺️ Mappa Termica Aziendale del Rischio Spaziale (Heatmap)")
mappa_data = df_elaborato.groupby(['Area', 'Infestante'])['Rischio_Ro'].max().unstack().fillna(0)

fig_heat = go.Figure(data=go.Heatmap(
    z=mappa_data.values,
    x=mappa_data.columns,
    y=mappa_data.index,
    colorscale='YlOrRd',
    hoverongaps=False))
fig_heat.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
st.plotly_chart(fig_heat, use_container_width=True)

# 5. MATRICE OPERATIVA HACCP CON LOGICA AUTOMATICA
st.markdown("### 📋 Registro Generale delle Ispezioni e Azioni Correttive Automatiche")

def colore_righe(val):
    if '🟢' in val: return 'background-color: #dcfce7; color: #166534; font-weight: bold;'
    elif '🟠' in val: return 'background-color: #ffedd5; color: #9a3412; font-weight: bold;'
    return 'background-color: #fee2e2; color: #991b1b; font-weight: bold;'

def genera_prescrizione(row):
    if row['Stato_Alert'] == '🟢 VERDE (Normale)':
        return "Conforme. Proseguire con piano di sanificazione giornaliera e monitoraggio standard."
    elif row['Stato_Alert'] == '🟠 GIALLO (Attenzione)':
        return f"Soglia Tolleranza superata su {row['Macchinario']}. Pulizia straordinaria sfridi e controllo zanzariere entro 48 ore."
    else:
        if row['Infestante'] == 'Mus musculus':
            return "🚨 CRITICITÀ ISO 22000: Attivare 'Piano straordinario di derattizzazione'. Controllo dei dispensatori meccanici tassativo ogni 3 giorni."
        elif row['Infestante'] == 'Ephestia kueniella':
            return f"🚨 BLOCCO SANITARIO: Sospensione flusso semola su {row['Macchinario']}. Eseguire pulizia criogenica delle guide ed eradicazione bave sericee entro 12 ore."
        else:
            return f"🚨 EMERGENZA: Applicazione gel insetticida specifico nel carter motore di {row['Macchinario']}. Sigillatura crepe strutturali."

df_filtrato['Prescrizione Obbligatoria (HACCP / Linee Guida)'] = df_filtrato.apply(genera_prescrizione, axis=1)

st.dataframe(
    df_filtrato[['Data', 'Area', 'Macchinario', 'Infestante', 'Catture', 'Rischio_Ro', 'Stato_Alert', 'Prescrizione Obbligatoria (HACCP / Linee Guida)']]
    .sort_values(by='Data', ascending=False)
    .style.map(colore_righe, subset=['Stato_Alert']),
    use_container_width=True,
    hide_index=True
)
