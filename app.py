import streamlit as st
import pandas as pd
import plotly.express as px

# Chargement des données
DATA_FILE = 'data/recommandations.xlsx'
FAVORIS = ["ORANGE COTE D'IVOIRE (ORAC)", "SAPH CI (SAPH)", "SONATEL SN (SNTS)"]

@st.cache_data
def load_data():
    try:
        df = pd.read_excel(DATA_FILE, sheet_name="Recommandations")
        return df
    except Exception as e:
        st.error("Erreur lors du chargement du fichier Excel.")
        return pd.DataFrame()

df = load_data()

st.title("📊 Tableau de Bord BRVM – Portefeuille Intelligent")
st.markdown("Suivi automatique des opportunités sur la BRVM avec recommandations achat/vente/observer.")

# --- Filtre Favoris
show_favoris = st.sidebar.checkbox("🎯 Afficher uniquement mes favoris", value=False)
if show_favoris:
    df = df[df['Titre'].isin(FAVORIS)]

# --- Tableau principal
st.subheader("🔍 Recommandations")
st.dataframe(df, use_container_width=True)

# --- Graphiques
st.subheader("📈 Jours en Hausse vs Baisse")
fig = px.bar(df, x="Titre", y=["Jours en Hausse", "Jours en Baisse"],
             barmode="group", title="Comparaison par titre",
             color_discrete_sequence=["#2ECC71", "#E74C3C"])
st.plotly_chart(fig, use_container_width=True)

st.subheader("📊 Variation Totale (%)")
fig2 = px.bar(df.sort_values(by="Variation Totale (%)", ascending=False),
              x="Titre", y="Variation Totale (%)", color="Recommandation",
              color_discrete_map={"🟢 Achat": "#27AE60", "🔴 Vente": "#C0392B", "🟡 Observer": "#F1C40F"},
              title="Classement par performance")
st.plotly_chart(fig2, use_container_width=True)
