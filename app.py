import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIG ---
DATA_FILE = 'data/recommandations.xlsx'
FAVORIS = ["ORANGE COTE D'IVOIRE (ORAC)", "SAPH CI (SAPH)", "SONATEL SN (SNTS)"]

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(DATA_FILE)
        return df
    except Exception as e:
        st.error("❌ Erreur lors du chargement des données.")
        st.exception(e)
        return pd.DataFrame()

df = load_data()

if st.sidebar.checkbox("🎯 Activer mode Favoris+", value=True):
    # (code du bloc Favoris+ ici)

# --- SECTION FAVORIS BOOSTÉE ---
st.subheader("🌟 Mes Titres Favoris")

favoris_df = df[df["Titre"].isin(FAVORIS)]

if favoris_df.empty:
    st.info("Aucun de vos favoris ne figure dans les données actuelles.")
else:
    for _, row in favoris_df.iterrows():
        couleur = {
            "🟢 Achat": "green",
            "🔴 Vente": "red",
            "🟡 Observer": "orange"
        }.get(row["Recommandation"], "gray")

        st.markdown(
            f"<div style='padding:8px; border-radius:6px; background-color:{couleur}; color:white;'>"
            f"<b>{row['Titre']}</b><br>"
            f"📈 Variation Totale : <b>{row['Variation Totale (%)']}%</b><br>"
            f"📉 Dernière séance : <b>{row['Dernière Variation (%)']}%</b><br>"
            f"🧠 Recommandation : <b>{row['Recommandation']}</b>"
            f"</div><br>",
            unsafe_allow_html=True
        )

    # --- Graphique sur les favoris
    st.markdown("### 📊 Évolution globale de mes favoris")
    fig_fav = px.bar(favoris_df.sort_values(by="Variation Totale (%)", ascending=False),
                     x="Titre", y="Variation Totale (%)",
                     color="Recommandation",
                     color_discrete_map={
                         "🟢 Achat": "#27AE60",
                         "🔴 Vente": "#C0392B",
                         "🟡 Observer": "#F1C40F"
                     },
                     title="Performance de mes favoris")
    st.plotly_chart(fig_fav, use_container_width=True)

st.set_page_config(page_title="Dashboard BRVM", layout="wide")
st.title("📊 Tableau de Bord BRVM – Portefeuille Intelligent")
st.markdown("Suivi automatique des opportunités sur la BRVM avec recommandations achat/vente/observer.")

# --- DEBUG TEMPORAIRE ---
#st.write("🔍 Colonnes disponibles :", df.columns.tolist())
#st.write("🔍 Aperçu des données :", df.head())

# --- Filtre Favoris
show_favoris = st.sidebar.checkbox("🎯 Afficher uniquement mes favoris", value=False)
if show_favoris:
    df = df[df['Titre'].isin(FAVORIS)]

# --- Tableau principal
st.subheader("🔍 Recommandations")
st.dataframe(df, use_container_width=True)

# --- Graphique Jours en Hausse / Baisse (avec sécurité)
if not df.empty and "Jours en Hausse" in df.columns and "Jours en Baisse" in df.columns:
    st.subheader("📈 Jours en Hausse vs Baisse")
    fig = px.bar(df, x="Titre", y=["Jours en Hausse", "Jours en Baisse"],
                 barmode="group", title="Comparaison par titre")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Données manquantes ou colonnes absentes : graphique non affiché.")

# --- Graphique des variations
if "Variation Totale (%)" in df.columns and "Recommandation" in df.columns:
    st.subheader("📊 Variation Totale (%)")
    fig2 = px.bar(df.sort_values(by="Variation Totale (%)", ascending=False),
                  x="Titre", y="Variation Totale (%)", color="Recommandation",
                  color_discrete_map={
                      "🟢 Achat": "#27AE60",
                      "🔴 Vente": "#C0392B",
                      "🟡 Observer": "#F1C40F"
                  },
                  title="Classement par performance")
    st.plotly_chart(fig2, use_container_width=True)
else:
    st.warning("⚠️ Colonnes pour variation/recommandation manquantes.")
