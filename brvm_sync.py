import os
import io
import json
import re
import fitz
import pandas as pd
from collections import defaultdict
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
FOLDER_ID = '1w2W-SI19l3qgpJKOEGCIiKS2fOIwx3OY'  # 🔁 Mets ici l'ID de ton dossier Drive
BULLETIN_DIR = 'bulletins'
DATA_FILE = 'data/recommandations.xlsx'

# 🔐 Authentification sans interaction
def authenticate_drive():
    with open("credentials.json") as f:
        creds_info = json.load(f)
    with open("token.json") as f:
        token_info = json.load(f)

    creds = Credentials.from_authorized_user_info(token_info, SCOPES)
    return build('drive', 'v3', credentials=creds)

# 📥 Téléchargement
def download_bulletins():
    os.makedirs(BULLETIN_DIR, exist_ok=True)
    service = authenticate_drive()
    query = f"'{FOLDER_ID}' in parents and mimeType='application/pdf'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    for file in results.get('files', []):
        name = file['name']
        path = os.path.join(BULLETIN_DIR, name)
        if not os.path.exists(path):
            request = service.files().get_media(fileId=file['id'])
            with open(path, 'wb') as f:
                downloader = MediaIoBaseDownload(f, request)
                done = False
                while not done:
                    _, done = downloader.next_chunk()
            print(f"⬇️ Téléchargé : {name}")

# 🧠 Extraction verticale des tops hausses/baisses
def extract_top_movers_from_pdf(path, date_str):
    with fitz.open(path) as doc:
        text = "\n".join(page.get_text() for page in doc)

    data = []
    i = 0
    lines = text.splitlines()
    section = None
    while i < len(lines):
        line = lines[i].strip()
        if "PLUS FORTES HAUSSES" in line:
            section = "hausse"
            i += 4
        elif "PLUS FORTES BAISSES" in line:
            section = "baisse"
            i += 4
        elif section and line:
            titre = lines[i].strip()
            if re.match(r'^\d[\d\s]*$', titre) or "%" in titre or len(titre) < 4:
                i += 1
                continue
            try:
                cours = int(lines[i+1].replace(" ", "").replace("FCFA", ""))
                var_jour = float(lines[i+2].replace("%", "").replace(",", "."))
                var_annuelle = float(lines[i+3].replace("%", "").replace(",", "."))
                data.append({
                    'date': date_str,
                    'titre': titre,
                    'cours': cours,
                    'variation_jour': var_jour,
                    'variation_annuelle': var_annuelle,
                    'type': section
                })
                i += 4
            except:
                i += 1
        else:
            i += 1
    return data

# 📊 Mise à jour du portefeuille
def update_portfolio():
    all_data = []
    os.makedirs('data', exist_ok=True)

    for file in sorted(os.listdir(BULLETIN_DIR)):
        if file.endswith(".pdf"):
            date_match = re.search(r'\d{4}-\d{2}-\d{2}', file)
            if not date_match:
                continue
            date_str = date_match.group(0)
            path = os.path.join(BULLETIN_DIR, file)
            all_data.extend(extract_top_movers_from_pdf(path, date_str))

    df = pd.DataFrame(all_data)
# --- AJOUT STRATÉGIE PAR TITRE ---

# Filtrer sur les 7 derniers jours
df['date'] = pd.to_datetime(df['date'])
last_days = df['date'].max() - pd.Timedelta(days=7)
recent_df = df[df['date'] >= last_days]

# Dictionnaire pour stocker la stratégie
strategies = {}

# Regrouper par titre
for titre, group in recent_df.groupby('titre'):
    nb_hausses = group[group['type'] == 'hausse'].shape[0]
    nb_baisses = group[group['type'] == 'baisse'].shape[0]
    variation_totale = group['variation_jour'].sum()

    if nb_hausses >= 3 and variation_totale > 5:
        strategie = "✅ Renforcer"
    elif nb_baisses >= 3 and variation_totale < -5:
        strategie = "⚠️ Risque de décrochage"
    elif nb_hausses >= 1 and nb_baisses >= 1:
        strategie = "👀 À surveiller"
    else:
        strategie = "➖ Neutre"

    strategies[titre] = strategie

    # Calcul des recommandations
    stats = defaultdict(lambda: {'hausses': 0, 'baisses': 0, 'total_var': 0.0, 'last_var': 0.0, 'last_date': ''})
    for _, row in df.iterrows():
        t = row['titre']
        if row['type'] == 'hausse':
            stats[t]['hausses'] += 1
        else:
            stats[t]['baisses'] += 1
        stats[t]['total_var'] += row['variation_jour']
        if row['date'] > stats[t]['last_date']:
            stats[t]['last_var'] = row['variation_jour']
            stats[t]['last_date'] = row['date']

    portfolio = []
    for titre, st in stats.items():
        if st['hausses'] >= 3 and st['total_var'] > 5:
            reco = '🟢 Achat'
        elif st['baisses'] >= 3 and st['total_var'] < -5:
            reco = '🔴 Vente'
        else:
            reco = '🟡 Observer'
        portfolio.append({
            'Titre': titre,
            'Jours en Hausse': st['hausses'],
            'Jours en Baisse': st['baisses'],
            'Variation Totale (%)': round(st['total_var'], 2),
            'Dernière Variation (%)': round(st['last_var'], 2),
            'Recommandation': reco,
            'Stratégie': strategies.get(titre, "Non évalué")
        })


    df_final = pd.DataFrame(portfolio)
    df_final = df_final.sort_values(by='Variation Totale (%)', ascending=False)
    df_final.to_excel(DATA_FILE, index=False)
    print("✅ Recommandations mises à jour dans :", DATA_FILE)

# 🚀 Exécution
if __name__ == "__main__":
    download_bulletins()
    update_portfolio()
