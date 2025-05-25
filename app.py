import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard BRVM", layout="wide")

# --- CONFIG ---
DATA_FILE = 'data/recommandations.xlsx'
FAVORIS = ["ORANGE COTE D'IVOIRE (ORAC)", "SAPH CI (SPHC)", "SONATEL SN (SNTS)"]

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df_main = pd.read_excel(DATA_FILE, sheet_name="Recommandations")
        df_ytd = pd.read_excel(DATA_FILE, sheet_name="Top_YTD")
        return df_main, df_ytd
    except Exception as e:
        st.error("❌ Erreur lors du chargement des données.")
        st.exception(e)
        return pd.DataFrame(), pd.DataFrame()

df, df_ytd = load_data()

# --- FAVORIS+ ---
if st.sidebar.checkbox("🎯 Activer mode Favoris+", value=True):
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

# --- EN-TÊTE ---
st.title("📊 Tableau de Bord BRVM – Portefeuille Intelligent")
st.markdown("Suivi automatique des opportunités sur la BRVM avec recommandations achat/vente/observer.")

# --- FILTRES ---
show_favoris = st.sidebar.checkbox("🎯 Afficher uniquement mes favoris", value=False)
if show_favoris:
    df = df[df['Titre'].isin(FAVORIS)]

if "Stratégie" in df.columns:
    strategie_selection = st.sidebar.selectbox("📌 Filtrer par stratégie", ["Toutes"] + df["Stratégie"].dropna().unique().tolist())
    if strategie_selection != "Toutes":
        df = df[df["Stratégie"] == strategie_selection]

# --- TABLEAU PRINCIPAL ---
st.subheader("🔍 Recommandations")
st.dataframe(df, use_container_width=True)

# --- GRAPHIQUE : Jours en Hausse / Baisse ---
if not df.empty and "Jours en Hausse" in df.columns and "Jours en Baisse" in df.columns:
    st.subheader("📈 Jours en Hausse vs Baisse")
    fig = px.bar(df, x="Titre", y=["Jours en Hausse", "Jours en Baisse"],
                 barmode="group", title="Comparaison par titre")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("⚠️ Données manquantes ou colonnes absentes : graphique non affiché.")

# --- GRAPHIQUE : Variations Totales ---
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

# --- TOP 10 YTD ---
if not df_ytd.empty:
    st.subheader("🚀 Top 10 Progressions depuis le début de l'année")
    st.dataframe(df_ytd, use_container_width=True)

    fig_ytd = px.bar(df_ytd.sort_values(by="Progression YTD (%)", ascending=True),
                     x="Progression YTD (%)", y="Titre", orientation='h',
                     title="Top Performers YTD")
    st.plotly_chart(fig_ytd, use_container_width=True)
