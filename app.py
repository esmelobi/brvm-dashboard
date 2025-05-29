
import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard BRVM", layout="wide")
DATA_FILE = 'data/recommandations.xlsx'
FAVORIS = ["ORANGE COTE D'IVOIRE (ORAC)", "BICI CI (BICC)", "TRACTAFRIC MOTORS CI (PRSC)"]

@st.cache_data
def load_data():
    try:
        return pd.read_excel(DATA_FILE, sheet_name='Recommandations')
    except:
        return pd.DataFrame()

@st.cache_data
def load_ytd():
    try:
        return pd.read_excel(DATA_FILE, sheet_name='Top_YTD')
    except:
        return pd.DataFrame()

df = load_data()
st.title("📊 Tableau de Bord BRVM – Portefeuille Intelligent")
st.markdown("Suivi automatique des opportunités sur la BRVM avec recommandations achat/vente/observer.")

if st.sidebar.checkbox("🎯 Activer mode Favoris+", value=True):
    st.subheader("🌟 Mes Titres Favoris")
    favoris_df = df[df["Titre"].isin(FAVORIS)]

    if favoris_df.empty:
        st.info("Aucun de vos favoris ne figure dans les données actuelles.")
    else:
        for _, row in favoris_df.iterrows():
            couleur = {"🟢 Achat": "green", "🔴 Vente": "red", "🟡 Observer": "orange"}.get(row["Recommandation"], "gray")
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
                         })
        st.plotly_chart(fig_fav, use_container_width=True)

show_favoris = st.sidebar.checkbox("🎯 Afficher uniquement mes favoris", value=False)
if show_favoris:
    df = df[df['Titre'].isin(FAVORIS)]

if "Stratégie" in df.columns:
    strategie_selection = st.sidebar.selectbox("📌 Filtrer par stratégie", ["Toutes"] + df["Stratégie"].dropna().unique().tolist())
    if strategie_selection != "Toutes":
        df = df[df["Stratégie"] == strategie_selection]

st.subheader("🔍 Recommandations")
st.dataframe(df, use_container_width=True)

if not df.empty and "Jours en Hausse" in df.columns and "Jours en Baisse" in df.columns:
    st.subheader("📈 Jours en Hausse vs Baisse")
    fig = px.bar(df, x="Titre", y=["Jours en Hausse", "Jours en Baisse"],
                 barmode="group", title="Comparaison par titre")
    st.plotly_chart(fig, use_container_width=True)

if "Variation Totale (%)" in df.columns and "Recommandation" in df.columns:
    st.subheader("📊 Variation Totale (%)")
    fig2 = px.bar(df.sort_values(by="Variation Totale (%)", ascending=False),
                  x="Titre", y="Variation Totale (%)", color="Recommandation",
                  color_discrete_map={
                      "🟢 Achat": "#27AE60",
                      "🔴 Vente": "#C0392B",
                      "🟡 Observer": "#F1C40F"
                  })
    st.plotly_chart(fig2, use_container_width=True)

# YTD View
ytd_df = load_ytd()
if not ytd_df.empty:
    st.subheader("🚀 Top 10 Progressions depuis le début de l'année")
    st.dataframe(ytd_df, use_container_width=True)
    fig_ytd = px.bar(ytd_df.sort_values(by="Progression YTD (%)", ascending=True),
                     x="Progression YTD (%)", y="Titre", orientation='h',
                     title="Top 10 YTD")
    st.plotly_chart(fig_ytd, use_container_width=True)
