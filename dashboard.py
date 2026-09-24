#!/usr/bin/env python3
"""
Dashboard MEF 2026 — Benchmarking des portails de Ministères des Finances
4 pages claires · distinction eGov ONU / Score MEF · badge multi-sites
"""

import os, glob, re
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

st.set_page_config(page_title="MEF Benchmark 2026", page_icon="🏛️",
                   layout="wide", initial_sidebar_state="expanded")

_mef = go.layout.Template()
_mef.layout = go.Layout(
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="Inter, system-ui, sans-serif", size=11.5, color="#1A2B4A"),
    colorway=["#002D8A","#2874C8","#27AE60","#E8431A","#E67E22","#8E44AD","#117A65"],
    xaxis=dict(gridcolor="#E8EDF6", linecolor="#DEE4F0", zeroline=False,
               ticks="outside", tickcolor="#DEE4F0", tickfont=dict(size=11)),
    yaxis=dict(gridcolor="#E8EDF6", linecolor="#DEE4F0", zeroline=False,
               ticks="outside", tickcolor="#DEE4F0", tickfont=dict(size=11)),
    legend=dict(bgcolor="rgba(255,255,255,0.92)", bordercolor="#DEE4F0",
                borderwidth=1, font=dict(size=11)),
    hoverlabel=dict(bgcolor="white", bordercolor="#DEE4F0", font=dict(size=12, color="#1A2B4A")),
    margin=dict(l=55, r=35, t=35, b=55),
)
pio.templates["mef"] = _mef
pio.templates.default = "plotly+mef"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: 'Inter', system-ui, sans-serif !important; }
.main { background: #EEF2F9 !important; }
.stApp { background: #EEF2F9 !important; }
.main .block-container { padding-top: 0.5rem !important; padding-bottom: 2rem; }

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #001845 0%, #002A80 52%, #003AB2 100%) !important;
  box-shadow: 4px 0 28px rgba(0,24,69,0.30);
}
[data-testid="stSidebar"] > div { padding-top: 0 !important; }
[data-testid="stSidebar"] * { color: white !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.11) !important; }
[data-testid="stSidebar"] .stRadio > label {
  font-size: 0.58rem !important; font-weight: 700 !important;
  text-transform: uppercase !important; letter-spacing: 0.13em !important;
  color: rgba(255,255,255,0.36) !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"] {
  border-radius: 8px !important; padding: 5px 10px !important; margin-bottom: 2px !important;
}
[data-testid="stSidebar"] .stRadio [data-baseweb="radio"]:hover {
  background: rgba(255,255,255,0.10) !important;
}

.kpi { background: white; border-radius: 14px; padding: 18px 12px 15px; text-align: center;
  box-shadow: 0 1px 4px rgba(0,45,138,0.06), 0 4px 16px rgba(0,45,138,0.05);
  border: 1px solid rgba(0,45,138,0.07); position: relative; overflow: hidden; margin-bottom: 8px; }
.kpi::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #002D8A, #2874C8); border-radius: 14px 14px 0 0; }
.kpi-v { font-size: 1.75rem; font-weight: 800; color: #002D8A; line-height: 1.1; }
.kpi-l { font-size: 0.63rem; color: #6B7A99; margin-top: 5px; font-weight: 600;
          text-transform: uppercase; letter-spacing: 0.07em; }
.kpi-ma::before  { background: linear-gradient(90deg, #B0300F, #E8431A, #F39C12); }
.kpi-ma .kpi-v   { color: #B0300F; }
.kpi-ok::before  { background: linear-gradient(90deg, #0C6630, #27AE60); }
.kpi-ok .kpi-v   { color: #0C6630; }
.kpi-warn::before { background: linear-gradient(90deg, #A86908, #D4AC0D); }
.kpi-warn .kpi-v  { color: #A86908; }

.page-header { background: linear-gradient(130deg, #001845 0%, #002D8A 42%, #0041C8 100%);
  border-radius: 16px; padding: 22px 28px 18px; margin-bottom: 16px; position: relative;
  overflow: hidden; box-shadow: 0 4px 24px rgba(0,24,69,0.18); }
.ph-badge { display: inline-flex; align-items: center; gap: 5px;
  background: rgba(255,255,255,0.11); border: 1px solid rgba(255,255,255,0.17);
  padding: 2px 11px; border-radius: 20px; font-size: 0.67rem;
  color: rgba(255,255,255,0.78); font-weight: 500; margin-bottom: 8px; }
.ph-title { font-size: 1.6rem; font-weight: 800; color: white; line-height: 1.15; }
.ph-subtitle { font-size: 0.83rem; color: rgba(255,255,255,0.58); margin-top: 4px; }

/* Source distinction banner */
.src-banner { display: flex; gap: 12px; margin: 14px 0 20px; }
.src-box { flex: 1; border-radius: 12px; padding: 14px 18px; font-size: 0.85rem; line-height: 1.6; }
.src-egov { background: linear-gradient(135deg, #EBF3FB, #D4E9F7); border-left: 4px solid #1C6EA4; }
.src-mef  { background: linear-gradient(135deg, #FEF9E7, #FDEAA5); border-left: 4px solid #C28011; }
.src-title { font-weight: 700; font-size: 0.9rem; margin-bottom: 4px; }

.warn-box { background: linear-gradient(135deg, #FEF9E7, #FDEAA5); border-left: 4px solid #C28011;
  border-radius: 0 12px 12px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.86rem; line-height: 1.55; }
.ok-box   { background: linear-gradient(135deg, #EAFAF1, #C8EFD7); border-left: 4px solid #0C6630;
  border-radius: 0 12px 12px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.86rem; line-height: 1.55; }
.info-box { background: linear-gradient(135deg, #EBF3FB, #D4E9F7); border-left: 4px solid #1C6EA4;
  border-radius: 0 12px 12px 0; padding: 12px 16px; margin: 8px 0; font-size: 0.86rem; line-height: 1.55; }

h2, .css-10trblm { color: #002D8A !important; font-weight: 700 !important; }
h3 { color: #1A2B4A !important; font-weight: 600 !important; }
hr { border: none !important; border-top: 1px solid #DEE4F0 !important; margin: 14px 0 !important; }

.stTabs [data-baseweb="tab-list"] { gap: 2px !important; border-bottom: 2px solid #DEE4F0 !important; }
.stTabs [data-baseweb="tab"] { padding: 7px 16px !important; font-size: 0.84rem !important;
  font-weight: 500 !important; color: #6B7A99 !important; border-radius: 8px 8px 0 0 !important;
  background: rgba(0,45,138,0.025) !important; border: none !important; }
.stTabs [data-baseweb="tab"]:hover { background: rgba(0,45,138,0.07) !important; color: #002D8A !important; }
.stTabs [aria-selected="true"] { color: #002D8A !important; font-weight: 700 !important;
  background: white !important; box-shadow: 0 -2px 0 #002D8A inset !important; }
.stTabs [data-baseweb="tab-panel"] { background: white; border-radius: 0 12px 12px 12px;
  padding: 20px 16px; border: 1px solid #DEE4F0; border-top: none; }

.stDataFrame, [data-testid="stDataFrame"] { border-radius: 12px !important;
  border: 1px solid #DEE4F0 !important; box-shadow: 0 1px 6px rgba(0,45,138,0.05) !important; }
[data-baseweb="tag"] { background: #002D8A !important; border-radius: 6px !important; }
[data-testid="stExpander"] { border-radius: 12px !important; border: 1px solid #DEE4F0 !important; }
details > summary { font-weight: 600 !important; color: #002D8A !important; }
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-thumb { background: #BCC8E0; border-radius: 3px; }
</style>
""", unsafe_allow_html=True)

# ─── Constantes ───────────────────────────────────────────────────────────────
COUNTRY_META = {
    "Afghanistan":("AFG","Asie"), "Afrique du Sud":("ZAF","Afrique"),
    "Albanie":("ALB","Europe"), "Algérie":("DZA","Afrique"),
    "Allemagne":("DEU","Europe"), "Angola":("AGO","Afrique"),
    "Arabie Saoudite":("SAU","Asie"), "Argentine":("ARG","Amériques"),
    "Arménie":("ARM","Asie"), "Australie":("AUS","Océanie"),
    "Autriche":("AUT","Europe"), "Azerbaïdjan":("AZE","Asie"),
    "Bahamas":("BHS","Amériques"), "Bahreïn":("BHR","Asie"),
    "Bangladesh":("BGD","Asie"), "Belgique":("BEL","Europe"),
    "Bolivie":("BOL","Amériques"), "Bosnie-Herzégovine":("BIH","Europe"),
    "Botswana":("BWA","Afrique"), "Brésil":("BRA","Amériques"),
    "Bulgarie":("BGR","Europe"), "Burkina Faso":("BFA","Afrique"),
    "Burundi":("BDI","Afrique"), "Bénin":("BEN","Afrique"),
    "Cambodge":("KHM","Asie"), "Cameroun":("CMR","Afrique"),
    "Canada":("CAN","Amériques"), "Cap-Vert":("CPV","Afrique"),
    "Chili":("CHL","Amériques"), "Chine":("CHN","Asie"),
    "Chypre":("CYP","Asie"), "Colombie":("COL","Amériques"),
    "Comores":("COM","Afrique"), "Congo (Brazza.)":("COG","Afrique"),
    "Corée du Nord":("PRK","Asie"), "Corée du Sud":("KOR","Asie"),
    "Costa Rica":("CRI","Amériques"), "Croatie":("HRV","Europe"),
    "Cuba":("CUB","Amériques"), "Côte d'Ivoire":("CIV","Afrique"),
    "Danemark":("DNK","Europe"), "Djibouti":("DJI","Afrique"),
    "El Salvador":("SLV","Amériques"), "Espagne":("ESP","Europe"),
    "Estonie":("EST","Europe"), "Eswatini":("SWZ","Afrique"),
    "Fidji":("FJI","Océanie"), "Finlande":("FIN","Europe"),
    "France":("FRA","Europe"), "Gabon":("GAB","Afrique"),
    "Gambie":("GMB","Afrique"), "Ghana":("GHA","Afrique"),
    "Grèce":("GRC","Europe"), "Guatemala":("GTM","Amériques"),
    "Guinée":("GIN","Afrique"), "Guinée équatoriale":("GNQ","Afrique"),
    "Guinée-Bissau":("GNB","Afrique"), "Guyana":("GUY","Amériques"),
    "Géorgie":("GEO","Asie"), "Haïti":("HTI","Amériques"),
    "Honduras":("HND","Amériques"), "Hongrie":("HUN","Europe"),
    "Iles Marshall":("MHL","Océanie"), "Iles Salomon":("SLB","Océanie"),
    "Inde":("IND","Asie"), "Indonésie":("IDN","Asie"),
    "Irak":("IRQ","Asie"), "Iran":("IRN","Asie"),
    "Irlande":("IRL","Europe"), "Islande":("ISL","Europe"),
    "Israël":("ISR","Asie"), "Italie":("ITA","Europe"),
    "Jamaïque":("JAM","Amériques"), "Japon":("JPN","Asie"),
    "Jordanie":("JOR","Asie"), "Kazakhstan":("KAZ","Asie"),
    "Kenya":("KEN","Afrique"), "Kirghizstan":("KGZ","Asie"),
    "Koweït":("KWT","Asie"), "Laos":("LAO","Asie"),
    "Lesotho":("LSO","Afrique"), "Lettonie":("LVA","Europe"),
    "Liban":("LBN","Asie"), "Libye":("LBY","Afrique"),
    "Libéria":("LBR","Afrique"), "Lituanie":("LTU","Europe"),
    "Luxembourg":("LUX","Europe"), "Macédoine du Nord":("MKD","Europe"),
    "Madagascar":("MDG","Afrique"), "Malaisie":("MYS","Asie"),
    "Malawi":("MWI","Afrique"), "Mali":("MLI","Afrique"),
    "Malte":("MLT","Europe"), "Maroc":("MAR","Afrique"),
    "Maurice":("MUS","Afrique"), "Mauritanie":("MRT","Afrique"),
    "Mexique":("MEX","Amériques"), "Moldavie":("MDA","Europe"),
    "Mongolie":("MNG","Asie"), "Monténégro":("MNE","Europe"),
    "Mozambique":("MOZ","Afrique"), "Myanmar":("MMR","Asie"),
    "Namibie":("NAM","Afrique"), "Nicaragua":("NIC","Amériques"),
    "Niger":("NER","Afrique"), "Nigéria":("NGA","Afrique"),
    "Norvège":("NOR","Europe"), "Nouvelle-Zélande":("NZL","Océanie"),
    "Népal":("NPL","Asie"), "Oman":("OMN","Asie"),
    "Ouganda":("UGA","Afrique"), "Ouzbékistan":("UZB","Asie"),
    "Pakistan":("PAK","Asie"), "Panama":("PAN","Amériques"),
    "Papouasie-NG":("PNG","Océanie"), "Paraguay":("PRY","Amériques"),
    "Pays-Bas":("NLD","Europe"), "Philippines":("PHL","Asie"),
    "Pologne":("POL","Europe"), "Portugal":("PRT","Europe"),
    "Pérou":("PER","Amériques"), "Qatar":("QAT","Asie"),
    "RCA":("CAF","Afrique"), "RD Congo":("COD","Afrique"),
    "Roumanie":("ROU","Europe"), "Royaume-Uni":("GBR","Europe"),
    "Russie":("RUS","Europe"), "Rwanda":("RWA","Afrique"),
    "Rép. Dominicaine":("DOM","Amériques"), "Saint-Marin":("SMR","Europe"),
    "Samoa":("WSM","Océanie"), "Serbie":("SRB","Europe"),
    "Seychelles":("SYC","Afrique"), "Sierra Leone":("SLE","Afrique"),
    "Singapour":("SGP","Asie"), "Slovaquie":("SVK","Europe"),
    "Slovénie":("SVN","Europe"), "Somalie":("SOM","Afrique"),
    "Soudan":("SDN","Afrique"), "Soudan du Sud":("SSD","Afrique"),
    "Sri Lanka":("LKA","Asie"), "Suisse":("CHE","Europe"),
    "Suède":("SWE","Europe"), "Syrie":("SYR","Asie"),
    "São Tomé":("STP","Afrique"), "Sénégal":("SEN","Afrique"),
    "Tadjikistan":("TJK","Asie"), "Tanzanie":("TZA","Afrique"),
    "Tchad":("TCD","Afrique"), "Tchéquie":("CZE","Europe"),
    "Thaïlande":("THA","Asie"), "Timor-Leste":("TLS","Asie"),
    "Togo":("TGO","Afrique"), "Tonga":("TON","Océanie"),
    "Trinidad & Tobago":("TTO","Amériques"), "Tunisie":("TUN","Afrique"),
    "Türkiye":("TUR","Asie"), "Ukraine":("UKR","Europe"),
    "Uruguay":("URY","Amériques"), "Venezuela":("VEN","Amériques"),
    "Viêt Nam":("VNM","Asie"), "Yémen":("YEM","Asie"),
    "Zambie":("ZMB","Afrique"), "Zimbabwe":("ZWE","Afrique"),
    "Égypte":("EGY","Afrique"), "Émirats":("ARE","Asie"),
    "Équateur":("ECU","Amériques"), "États-Unis":("USA","Amériques"),
    "Éthiopie":("ETH","Afrique"),
}

MENA_PAYS = ["Arabie Saoudite","Émirats","Bahreïn","Oman","Qatar","Koweït",
             "Jordanie","Liban","Irak","Yémen","Syrie","Tunisie","Algérie",
             "Libye","Égypte","Mauritanie"]

BOOL_COLS = [
    "HTTPS","Responsive","Sitemap.xml","Moteur de recherche","Bandeau cookies",
    "Formulaires en ligne","Chatbot","Documents PDF","Section actualités",
    "Section marchés publics","Facebook","Twitter/X","LinkedIn","YouTube",
    "Espace citoyen","Politique confidentialité","Mention API publique",
    "Déclaration accessibilité","Facturation électronique","Tableau de bord temps réel",
    "Mécanisme de réclamations","Liberté d'accès à l'info","Abonnement newsletter",
    "Données téléchargeables","API avec documentation","Données budgétaires structurées",
    "Mention budget","Mention loi de finances","Mention rapport annuel",
    "Mention open data","Mention transparence",
]

_BOOL_MAP = {"O": True, "N": False, "True": True, "False": False,
             "oui": True, "non": False, "nan": None, "None": None, "": None}

# ─── Chargement ───────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    clean = sorted(glob.glob(os.path.join(base, "code/output/grille_comparative_*_clean.csv")))
    raw   = sorted([f for f in glob.glob(os.path.join(base, "code/output/grille_comparative_*.csv"))
                    if "_clean" not in f])
    csvs = clean if clean else raw
    if not csvs:
        st.error("Aucun fichier de données trouvé dans code/output/"); st.stop()
    csv_path = csvs[-1]
    df = pd.read_csv(csv_path, encoding="utf-8-sig")
    df.columns = [c.strip("﻿").strip() for c in df.columns]
    for col in BOOL_COLS:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().map(_BOOL_MAP)
    num_cols = ["Rang EGOV 2024","Indice EGOV","Indice E-Participation",
                "Indice Services en ligne","Indice Capital humain","Indice Télécom",
                "Score Maturité (%)","Couverture (%)","Temps réponse (ms)","Nb Langues"]
    for col in num_cols:
        if col in df.columns: df[col] = pd.to_numeric(df[col], errors="coerce")
    df["ISO3"] = df["Pays"].map(lambda x: COUNTRY_META.get(x,("?","?"))[0])
    if "Région" not in df.columns or df["Région"].isna().all():
        df["Région"] = df["Pays"].map(lambda x: COUNTRY_META.get(x,("?","?"))[1])
    if "Catégorie" not in df.columns:
        df["Catégorie"] = df["Rang EGOV 2024"].apply(
            lambda r: "meilleure pratique" if r<=20 else ("aspirationnel" if r<=80
                       else ("pair" if r<=130 else "en développement")) if pd.notna(r) else "en développement")
        df.loc[df["Pays"]=="Maroc","Catégorie"] = "référence"
    df["Catégorie"] = df["Catégorie"].replace("observation","en développement")

    # ── Badge multi-sites ──────────────────────────────────────────────────────
    def _site_type(statut):
        if not isinstance(statut, str): return "centralisé"
        m = re.search(r'\+(\d+)sat', statut)
        if m: return f"multi-sites ({m.group(1)} portails)"
        if "multi" in statut.lower(): return "multi-sites"
        return "centralisé"
    if "Statut" in df.columns:
        df["Type portail"] = df["Statut"].apply(_site_type)
    else:
        df["Type portail"] = "centralisé"

    # ── Source collecte ───────────────────────────────────────────────────────
    if "Source" in df.columns:
        df["Collecte"] = df["Source"].apply(
            lambda s: "⚠️ Wayback" if str(s)=="wayback" else
                      ("🤖 Playwright" if str(s)=="playwright" else
                       ("✅ Direct" if str(s)=="direct" else
                        ("🔗 Multi-sites" if "multi" in str(s).lower() else str(s)))))
    elif "Statut" in df.columns:
        df["Collecte"] = df["Statut"].apply(
            lambda s: "✅ Direct" if "✓" in str(s) else "❌ Échec")

    return df, csv_path

df, _csv_src = load_data()
maroc = df[df["Pays"] == "Maroc"].iloc[0]

# ─── Helpers ──────────────────────────────────────────────────────────────────
def kpi(label, value, style="", tooltip=""):
    cls = f"kpi{' kpi-'+style if style else ''}"
    tip = f' title="{tooltip}"' if tooltip else ""
    return (f'<div class="{cls}"{tip}>'
            f'<div class="kpi-v">{value}</div>'
            f'<div class="kpi-l">{label}</div></div>')

def page_header(title, subtitle="", badge=""):
    badge_html = f'<div class="ph-badge">{badge}</div>' if badge else ""
    sub_html   = f'<div class="ph-subtitle">{subtitle}</div>' if subtitle else ""
    st.markdown(f'<div class="page-header">{badge_html}<div class="ph-title">{title}</div>{sub_html}</div>',
                unsafe_allow_html=True)

def source_banner():
    """Banner bilingue expliquant les 2 sources de données."""
    st.markdown("""
<div class="src-banner">
  <div class="src-box src-egov">
    <div class="src-title">🏛️ Indice eGov ONU 2024</div>
    <b>Périmètre :</b> gouvernement numérique <b>entier</b> (santé, éducation, finances, justice…)<br>
    <b>Source :</b> enquête officielle Nations Unies · données 2024<br>
    <b>Usage ici :</b> référence internationale de validation du classement MEF
  </div>
  <div class="src-box src-mef">
    <div class="src-title">🔍 Score MEF 2026 (scraper)</div>
    <b>Périmètre :</b> portail du <b>Ministère des Finances uniquement</b> · 38 critères techniques<br>
    <b>Source :</b> collecte automatique sur 193 sites · données juillet 2026<br>
    <b>Usage ici :</b> classement spécifique MoF · identification des axes d'amélioration
  </div>
</div>
""", unsafe_allow_html=True)

def adopt_pct(sub, col):
    if col not in sub.columns: return 0
    s = sub[col]
    if s.dtype == object: s = s.astype(str).str.strip().map(_BOOL_MAP)
    nn = int(s.notna().sum())
    return round(float(s.sum()) / nn * 100, 1) if nn > 0 else 0

def bar_chart(gdf, title_col="Score Maturité (%)"):
    d = gdf[gdf[title_col].notna()].sort_values(title_col, ascending=True).copy()
    colors = ["#E8431A" if p == "Maroc" else "#2874C8" for p in d["Pays"]]
    fig = go.Figure(go.Bar(
        x=d[title_col], y=d["Pays"], orientation="h",
        marker_color=colors,
        text=d[title_col].apply(lambda v: f"{v:.0f}"),
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Score : %{x:.0f}/100<extra></extra>",
    ))
    med = float(d[title_col].median())
    fig.add_vline(x=med, line_dash="dash", line_color="#27AE60",
                  annotation_text=f"Médiane {med:.0f}", annotation_position="top left",
                  annotation_font_color="#27AE60", annotation_font_size=10)
    ma_val = d[d["Pays"]=="Maroc"][title_col]
    if len(ma_val):
        fig.add_vline(x=float(ma_val.iloc[0]), line_dash="dot", line_color="#E8431A",
                      annotation_text="🇲🇦", annotation_position="top right",
                      annotation_font_color="#E8431A")
    fig.update_layout(
        height=max(300, len(d)*26+60), xaxis_range=[0, 115],
        xaxis_title="Score MEF (/100)",
        yaxis=dict(autorange="reversed", tickfont=dict(size=10)),
        yaxis_title="", margin=dict(l=140, r=80, t=20, b=40),
        showlegend=False, plot_bgcolor="white", paper_bgcolor="white",
    )
    return fig

# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center;padding:24px 12px 16px;">
      <div style="display:inline-flex;align-items:center;justify-content:center;
           width:52px;height:52px;background:rgba(255,255,255,0.10);border-radius:14px;
           font-size:1.5rem;border:1px solid rgba(255,255,255,0.15);margin-bottom:10px;">🏛️</div>
      <div style="font-weight:800;font-size:1.02rem;color:white;line-height:1.2;">MEF Benchmarking</div>
      <div style="font-size:0.65rem;color:rgba(255,255,255,0.40);margin-top:4px;">
        Ministère de l'Économie · 2026</div>
    </div>""", unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.10);margin:0 -1rem 14px;"></div>',
                unsafe_allow_html=True)

    page = st.radio("Navigation", [
        "🌍  Vue d'ensemble",
        "🇲🇦  Positionnement Maroc",
        "🏆  Classement mondial MoF",
        "🎯  Axes d'amélioration",
        "🧩  Typologies de portails",
        "🔬  Méthodologie & biais",
    ], label_visibility="collapsed")

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.10);margin:10px -1rem 14px;"></div>',
                unsafe_allow_html=True)

    _n_scored  = int(df["Score Maturité (%)"].notna().sum())
    _n_multi   = int((df["Type portail"] != "centralisé").sum())
    _csv_name  = os.path.basename(_csv_src)
    _ts_match  = re.search(r'(\d{8}_\d{4})', _csv_name)
    _ts_fmt    = ""
    if _ts_match:
        t = _ts_match.group(1)
        _ts_fmt = f"{t[6:8]}/{t[4:6]}/{t[:4]} {t[9:11]}h{t[11:13]}"

    st.markdown(f"""
    <div style="padding:0 2px;">
      <div style="background:rgba(255,255,255,0.07);border-radius:11px;padding:12px 13px;
                  border:1px solid rgba(255,255,255,0.09);">
        <p style="font-size:0.57rem;color:rgba(255,255,255,0.36);text-transform:uppercase;
                  letter-spacing:0.12em;font-weight:700;margin:0 0 9px;">Données</p>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="font-size:0.70rem;color:rgba(255,255,255,0.62);">🌍 Pays ONU</span>
          <span style="font-weight:800;font-size:0.92rem;color:rgba(255,255,255,0.88);">193</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="font-size:0.70rem;color:rgba(255,255,255,0.62);">✅ Pays scorés</span>
          <span style="font-weight:800;font-size:0.92rem;color:#FACC15;">{_n_scored}</span>
        </div>
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
          <span style="font-size:0.70rem;color:rgba(255,255,255,0.62);">🔗 Multi-sites</span>
          <span style="font-weight:800;font-size:0.92rem;color:#FACC15;">{_n_multi}</span>
        </div>
        <div style="font-size:0.58rem;color:rgba(255,255,255,0.25);margin-top:8px;">
          {_ts_fmt or _csv_name[:16]}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div style="height:1px;background:rgba(255,255,255,0.10);margin:10px -1rem 14px;"></div>',
                unsafe_allow_html=True)

    with st.expander("📖 Glossaire"):
        st.markdown("""
**Score MEF** — Score 0–100 calculé sur 38 critères techniques du portail MoF (HTTPS, formulaires, open data…). Calculé uniquement sur les critères effectivement mesurés.

**eGov ONU** — Indice 0–1 publié par les Nations Unies tous les 2 ans. Mesure la maturité du gouvernement numérique *entier* d'un pays (pas uniquement le MoF).

**ρ = 0.8068** — Corrélation de Spearman entre le classement MEF et le classement eGov ONU. Valeur significative (seuil 0.52), ce qui valide la cohérence du Score MEF.

**Multi-sites** — Pays où les fonctions du MEF marocain sont réparties sur plusieurs portails (ex : UK = HM Treasury + HMRC + GOV.UK). Le scraper fusionne jusqu'à 4 portails par pays.

**Wayback** — Site scrappé via la Wayback Machine (archive). Données moins fiables (JS non rendu, contenu dynamique manquant).

**Catégories** — *meilleure pratique* (eGov top 20), *aspirationnel* (rang 21–80), *pair* (rang 81–130), *en développement* (rang 131+), *référence* (Maroc).
        """)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — VUE D'ENSEMBLE
# ══════════════════════════════════════════════════════════════════════════════
if page.startswith("🌍"):
    page_header("🌍 Vue d'ensemble",
                "193 ministères des Finances analysés · 2 sources de données complémentaires",
                badge="MEF 2026 · 193 pays ONU")

    source_banner()

    # KPIs
    ma_score = float(maroc["Score Maturité (%)"]) if pd.notna(maroc.get("Score Maturité (%)")) else None
    ma_egov  = int(maroc["Rang EGOV 2024"]) if pd.notna(maroc.get("Rang EGOV 2024")) else None
    df_sc    = df[df["Score Maturité (%)"].notna() & df["Rang EGOV 2024"].notna()]
    # Exclure les pays géoblocqués (data_quality_flag="blocked") du calcul de ρ
    df_rho   = df_sc[df_sc.get("data_quality_flag", pd.Series("", index=df_sc.index)) != "blocked"] \
               if "data_quality_flag" in df_sc.columns else df_sc
    ma_rank  = int((df_sc["Score Maturité (%)"] > (ma_score or 0)).sum()) + 1 if ma_score else "—"
    n_scored = len(df[df["Score Maturité (%)"].notna()])
    from scipy.stats import spearmanr as _spearmanr
    _rho_val, _ = _spearmanr(df_rho["Score Maturité (%)"], -df_rho["Rang EGOV 2024"])
    rho = round(float(_rho_val), 4)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.markdown(kpi("Pays scorés (MoF 2026)", f"{n_scored}/193", "ok"), unsafe_allow_html=True)
    c2.markdown(kpi("Rang MEF Maroc", f"#{ma_rank}/{n_scored}", "ma",
        tooltip="Classement du Maroc selon le Score MEF (scraper MoF 2026)"), unsafe_allow_html=True)
    c3.markdown(kpi("Score MEF Maroc", f"{ma_score:.0f}/100" if ma_score else "—", "ma",
        tooltip="Score composite sur 38 critères techniques du portail finances.gov.ma"), unsafe_allow_html=True)
    c4.markdown(kpi("Rang eGov ONU Maroc", f"#{ma_egov}/193" if ma_egov else "—", "warn",
        tooltip="Rang du Maroc dans l'indice eGov ONU 2024 (gouvernement entier, pas uniquement MoF)"), unsafe_allow_html=True)
    c5.markdown(kpi("Corrélation MEF ↔ eGov ONU", f"ρ = {rho}", "ok",
        tooltip="Corrélation de Spearman entre le classement MEF et le classement eGov ONU. Seuil de significativité : 0.52. ρ=0.8068 confirme la cohérence du Score MEF."), unsafe_allow_html=True)

    st.markdown("---")

    # ── Comparaison directe des deux classements ──────────────────────────────
    st.subheader("📊 Comparaison — Rang MEF 2026 vs Rang eGov ONU 2024")
    st.markdown("""<div class="info-box" style="margin-bottom:14px;">
    Les pays sont <b>classés par rang eGov ONU</b> (référence internationale). Le graphique de droite montre leur rang sur le <b>Score MEF</b> — les écarts illustrent où le portail MoF surperforme ou sous-performe.
    🇲🇦 <b>Maroc : #90 eGov ONU → #35 MEF</b> : son portail MoF est bien plus avancé que sa gouvernance globale.
    </div>""", unsafe_allow_html=True)

    # Tous les pays scorés + rang eGov — avec contrôle du nombre affiché
    df_comp = df[df["Score Maturité (%)"].notna() & df["Rang EGOV 2024"].notna()].copy()
    df_comp_all = df[df["Rang EGOV 2024"].notna()].copy()  # inclut non-scorés
    df_comp = df_comp.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
    df_comp["Rang MEF"] = range(1, len(df_comp)+1)

    # Fusionner pays non-scorés (wayback/failed) avec rang MEF = "—"
    df_comp_all = df_comp_all.merge(
        df_comp[["Pays","Rang MEF"]], on="Pays", how="left"
    )
    df_comp_all["Rang MEF"] = df_comp_all["Rang MEF"].fillna(0).astype(int)
    df_comp_all = df_comp_all.sort_values("Rang EGOV 2024")

    n_mef_total = len(df_comp)
    n_total_egov = len(df_comp_all)

    _col_ctrl, _ = st.columns([1, 3])
    with _col_ctrl:
        n_show = st.slider("Nombre de pays affichés", min_value=20, max_value=n_total_egov,
                           value=min(50, n_total_egov), step=10,
                           help="Défilez pour voir plus de pays, triés par rang eGov ONU")
    top25 = df_comp_all.head(n_show).copy()
    top25 = top25.sort_values("Rang EGOV 2024", ascending=False)  # inversé pour bar horiz

    pays_list  = top25["Pays"].tolist()
    rang_mef   = top25["Rang MEF"].tolist()
    rang_egov  = top25["Rang EGOV 2024"].tolist()
    scores_mef = top25["Score Maturité (%)"].fillna(0).tolist()

    def _color(p, base, highlight="#E8431A"):
        return [highlight if x == "Maroc" else base for x in p]

    # Graphique papillon : eGov gauche ← | → MEF droite
    fig_butterfly = go.Figure()

    txt_color = ["#E8431A" if p == "Maroc" else "#1A2B4A" for p in pays_list]

    # Barres eGov (vers la gauche = valeurs négatives)
    fig_butterfly.add_trace(go.Bar(
        name="🏛️ Rang eGov ONU 2024",
        y=pays_list,
        x=[-v for v in top25["Indice EGOV"].fillna(0).tolist()],
        orientation="h",
        marker=dict(color=_color(pays_list, "#1A5276"), line=dict(color="white", width=0.4)),
        text=[f"#{int(r)}/193" for r in rang_egov],
        textposition="inside",
        insidetextanchor="start",
        textfont=dict(size=10, color="white"),
        hovertemplate="<b>%{y}</b><br>Rang eGov : #%{customdata}/193<extra></extra>",
        customdata=[int(r) for r in rang_egov],
    ))

    # Barres MEF (vers la droite)
    fig_butterfly.add_trace(go.Bar(
        name="🔍 Score MEF 2026",
        y=pays_list,
        x=[s / 100 for s in scores_mef],
        orientation="h",
        marker=dict(color=_color(pays_list, "#2874C8"), line=dict(color="white", width=0.4)),
        text=[f"#{r}/{n_mef_total}" if r > 0 else "non scoré" for r in rang_mef],
        textposition="outside",
        textfont=dict(size=10, color=txt_color),
        hovertemplate="<b>%{y}</b><br>Rang MEF : #%{customdata}/{n}<br>Score : %{customdata2:.0f}/100<extra></extra>".replace("{n}", str(n_mef_total)),
        customdata=list(zip(rang_mef, scores_mef)),
    ))

    # Annotations des noms de pays au centre
    fig_butterfly.update_layout(
        barmode="overlay",
        height=max(460, len(top25) * 22 + 80),
        xaxis=dict(
            range=[-1.18, 1.18],
            tickvals=[-1, -0.75, -0.5, -0.25, 0, 0.25, 0.5, 0.75, 1],
            ticktext=["Indice 1.0", "0.75", "0.50", "0.25", "", "25/100", "50/100", "75/100", "100/100"],
            zeroline=True, zerolinecolor="#1A2B4A", zerolinewidth=2,
            gridcolor="#F0F3F9", tickfont=dict(size=9.5),
        ),
        yaxis=dict(tickfont=dict(size=11), side="left"),
        legend=dict(orientation="h", y=1.04, x=0.5, xanchor="center",
                    font=dict(size=11), bgcolor="rgba(255,255,255,0.9)",
                    bordercolor="#DEE4F0", borderwidth=1),
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=140, r=80, t=45, b=50),
        annotations=[
            dict(x=-0.58, y=1.06, xref="paper", yref="paper", showarrow=False,
                 text="← 🏛️ eGov ONU 2024 (gouvernement entier)",
                 font=dict(size=11, color="#1A5276", weight=700)),
            dict(x=0.98, y=1.06, xref="paper", yref="paper", showarrow=False,
                 text="🔍 Score MEF 2026 (portail MoF) →",
                 font=dict(size=11, color="#2874C8", weight=700)),
        ],
    )

    # Ligne horizontale Maroc
    if "Maroc" in pays_list:
        ma_idx = pays_list.index("Maroc")
        fig_butterfly.add_hrect(
            y0=ma_idx - 0.45, y1=ma_idx + 0.45,
            fillcolor="rgba(232,67,26,0.07)", line_width=0,
        )

    st.plotly_chart(fig_butterfly, use_container_width=True)

    st.markdown("""<div class="ok-box">
    ✅ <b>Lecture</b> : barres <b>bleues foncées à gauche</b> = indice eGov ONU (plus long = meilleur gouvernement numérique global).
    Barres <b>bleues claires à droite</b> = Score MEF (plus long = meilleur portail MoF).
    La zone <b>rouge 🇲🇦</b> montre le Maroc : portail MoF <b>#64/135</b> · rang eGov global <b>#90/193</b>.
    </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Portails multi-sites vs centralisés ──────────────────────────────────
    st.subheader("🔗 Portails multi-sites vs centralisés")

    n_multi_tot = int((df["Type portail"] != "centralisé").sum())
    n_centr_tot = int((df["Type portail"] == "centralisé").sum())

    # Compteurs visuels
    cc1, cc2, cc3 = st.columns(3)
    cc1.markdown(kpi("Pays centralisés (1 portail)", str(n_centr_tot), "ok",
        tooltip="Un seul portail MoF officiel scrappé"), unsafe_allow_html=True)
    cc2.markdown(kpi("Pays multi-sites détectés", str(n_multi_tot), "warn",
        tooltip="Fonctions MoF réparties sur plusieurs portails"), unsafe_allow_html=True)
    cc3.markdown(kpi("Règle de fusion", "Meilleur score", "",
        tooltip="Pour chaque indicateur, on retient la valeur la plus favorable parmi tous les portails du pays"), unsafe_allow_html=True)

    st.markdown("<div style='margin:12px 0 6px;font-size:0.88rem;color:#6B7A99;'>Dans ces pays, les fonctions du ministère des finances sont <b>réparties sur plusieurs sites</b>. Le scraper les fusionne automatiquement.</div>", unsafe_allow_html=True)

    EXEMPLES_MULTI = {
        "Royaume-Uni":  ("🇬🇧", "HM Treasury · HMRC · GOV.UK · Companies House", 4),
        "France":       ("🇫🇷", "economie.gouv.fr · budget.gouv.fr · impots.gouv.fr · data.gouv.fr", 4),
        "Australie":    ("🇦🇺", "treasury.gov.au · ATO · data.gov.au", 3),
        "États-Unis":   ("🇺🇸", "treasury.gov · IRS · usaspending.gov", 3),
        "Allemagne":    ("🇩🇪", "bundesfinanzministerium.de · destatis.de · bundeshaushalt.de", 3),
        "Inde":         ("🇮🇳", "finmin.gov.in · incometax.gov.in · data.gov.in · cbic.gov.in", 4),
    }

    # Grille 3 colonnes
    keys = list(EXEMPLES_MULTI.keys())
    for row_i in range(0, len(keys), 3):
        cols = st.columns(3)
        for ci, pays in enumerate(keys[row_i:row_i+3]):
            flag, portails, nb = EXEMPLES_MULTI[pays]
            row_data = df[df["Pays"]==pays]
            score_str = f"{float(row_data.iloc[0]['Score Maturité (%)']):.0f}/100" if len(row_data) and pd.notna(row_data.iloc[0].get("Score Maturité (%)")) else "—"
            with cols[ci]:
                st.markdown(f"""
<div style="background:white;border-radius:12px;padding:16px 18px;
     border:1px solid #DEE4F0;box-shadow:0 2px 8px rgba(0,45,138,0.05);
     border-top:3px solid #2874C8;height:100%;">
  <div style="font-size:1.4rem;margin-bottom:4px;">{flag}</div>
  <div style="font-weight:700;font-size:0.95rem;color:#002D8A;">{pays}</div>
  <div style="margin:6px 0;">
    <span style="background:#EBF3FB;color:#1C6EA4;font-size:0.72rem;font-weight:600;
          padding:2px 8px;border-radius:20px;">🔗 {nb} portails</span>
    <span style="background:#FEF9E7;color:#A86908;font-size:0.72rem;font-weight:600;
          padding:2px 8px;border-radius:20px;margin-left:4px;">Score : {score_str}</span>
  </div>
  <div style="font-size:0.78rem;color:#6B7A99;line-height:1.6;margin-top:6px;">{portails}</div>
</div>""", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:10px'></div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Adoption globale des indicateurs ─────────────────────────────────────
    st.subheader("📊 Ce que les portails MoF ont dans le monde")

    feat_data = []
    for col in [c for c in BOOL_COLS if c in df.columns]:
        s = df[col]
        if s.dtype == object: s = s.astype(str).str.strip().map(_BOOL_MAP)
        nn = int(s.notna().sum())
        if nn == 0: continue
        pct = round(float(s.sum()) / nn * 100, 1)
        ma_v = maroc.get(col)
        ma_has = ma_v is True
        feat_data.append({"Indicateur": col, "Adoption (%)": pct, "Maroc": ma_has})
    feat_df = pd.DataFrame(feat_data).sort_values("Adoption (%)", ascending=True)

    # Séparer présent / absent au Maroc
    ma_present = feat_df[feat_df["Maroc"] == True]
    ma_absent  = feat_df[feat_df["Maroc"] == False]

    col_p, col_a = st.columns(2)

    with col_p:
        st.markdown("""<div style="background:#EAFAF1;border-left:4px solid #27AE60;border-radius:0 10px 10px 0;
            padding:10px 14px;margin-bottom:10px;font-weight:700;color:#0C6630;">
            ✅ Présent sur finances.gov.ma</div>""", unsafe_allow_html=True)
        fig_p = go.Figure(go.Bar(
            x=ma_present["Adoption (%)"], y=ma_present["Indicateur"],
            orientation="h",
            marker=dict(
                color=ma_present["Adoption (%)"],
                colorscale=[[0,"#A9DFBF"],[1,"#1A6B3C"]],
                showscale=False,
            ),
            text=ma_present["Adoption (%)"].apply(lambda v: f"{v:.0f}%"),
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>%{x:.0f}% des portails mondiaux<extra></extra>",
        ))
        fig_p.update_layout(
            height=max(300, len(ma_present)*26+40),
            xaxis=dict(range=[0,125], title="% portails mondiaux", tickfont=dict(size=9), gridcolor="#F0F3F9"),
            yaxis=dict(tickfont=dict(size=10)),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=160, r=55, t=10, b=40), showlegend=False,
        )
        st.plotly_chart(fig_p, use_container_width=True)

    with col_a:
        st.markdown("""<div style="background:#FDECEA;border-left:4px solid #E74C3C;border-radius:0 10px 10px 0;
            padding:10px 14px;margin-bottom:10px;font-weight:700;color:#922B21;">
            ❌ Absent de finances.gov.ma — à améliorer</div>""", unsafe_allow_html=True)
        fig_a = go.Figure(go.Bar(
            x=ma_absent["Adoption (%)"], y=ma_absent["Indicateur"],
            orientation="h",
            marker=dict(
                color=ma_absent["Adoption (%)"],
                colorscale=[[0,"#F1948A"],[1,"#922B21"]],
                showscale=False,
            ),
            text=ma_absent["Adoption (%)"].apply(lambda v: f"{v:.0f}%"),
            textposition="outside", textfont=dict(size=10),
            hovertemplate="<b>%{y}</b><br>%{x:.0f}% des portails mondiaux l'ont<extra></extra>",
        ))
        fig_a.update_layout(
            height=max(300, len(ma_absent)*26+40),
            xaxis=dict(range=[0,125], title="% portails mondiaux", tickfont=dict(size=9), gridcolor="#F0F3F9"),
            yaxis=dict(tickfont=dict(size=10)),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=200, r=55, t=10, b=40), showlegend=False,
        )
        st.plotly_chart(fig_a, use_container_width=True)

    st.caption("Les barres plus longues à droite = fonctionnalités très répandues mondialement → priorités d'amélioration pour le Maroc.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — POSITIONNEMENT MAROC
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("🇲🇦"):
    page_header("🇲🇦 Positionnement du Maroc",
                "finances.gov.ma — Score MEF vs eGov ONU · monde · Afrique · MENA",
                badge="finances.gov.ma")

    source_banner()

    ma_score = float(maroc["Score Maturité (%)"]) if pd.notna(maroc.get("Score Maturité (%)")) else None
    ma_egov  = int(maroc["Rang EGOV 2024"]) if pd.notna(maroc.get("Rang EGOV 2024")) else None
    ma_egov_score = float(maroc["Indice EGOV"]) if pd.notna(maroc.get("Indice EGOV")) else None
    df_sc    = df[df["Score Maturité (%)"].notna()].copy()

    # Rangs MEF
    def rank_in(gdf, pays="Maroc", col="Score Maturité (%)"):
        s = gdf[gdf[col].notna()].sort_values(col, ascending=False).reset_index(drop=True)
        if pays not in s["Pays"].values: return "—", len(s)
        return int(s[s["Pays"]==pays].index[0]) + 1, len(s)

    r_monde,  n_monde  = rank_in(df_sc)
    r_afr,    n_afr    = rank_in(df_sc[df_sc["Région"]=="Afrique"])
    r_mena,   n_mena   = rank_in(df_sc[df_sc["Pays"].isin(MENA_PAYS + ["Maroc"])])

    # Rangs eGov
    df_eg = df[df["Rang EGOV 2024"].notna()].copy()
    def egov_rank_in(gdf):
        s = gdf.sort_values("Rang EGOV 2024").reset_index(drop=True)
        if "Maroc" not in s["Pays"].values: return "—", len(s)
        return int(s[s["Pays"]=="Maroc"].index[0]) + 1, len(s)
    re_monde, ne_monde = egov_rank_in(df_eg)
    re_afr,   ne_afr   = egov_rank_in(df_eg[df_eg["Région"]=="Afrique"])
    re_mena,  ne_mena  = egov_rank_in(df_eg[df_eg["Pays"].isin(MENA_PAYS + ["Maroc"])])

    # ── Tableau comparatif des rangs ──────────────────────────────────────────
    st.subheader("📍 Rangs du Maroc")

    comp_data = {
        "Périmètre": ["🌍 Mondial", "🌍 Afrique", "🌙 MENA"],
        "Score MEF 2026": [f"#{r_monde}/{n_monde}", f"#{r_afr}/{n_afr}", f"#{r_mena}/{n_mena}"],
    }
    comp_df = pd.DataFrame(comp_data).set_index("Périmètre")
    st.dataframe(comp_df, use_container_width=True)

    st.markdown("---")

    tab_monde, tab_afr, tab_mena, tab_peers, tab_inspi = st.tabs([
        "🌍 Position mondiale", "🌍 Leadership africain", "🌙 Comparaison MENA",
        "🎯 Pairs eGov", "🌟 Inspirations"
    ])

    # ── Tab Monde ─────────────────────────────────────────────────────────────
    with tab_monde:
        gdf = df_sc.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
        top20 = gdf.head(20).copy()
        if "Maroc" not in top20["Pays"].values:
            top20 = pd.concat([top20, gdf[gdf["Pays"]=="Maroc"]]).reset_index(drop=True)
        med = float(gdf["Score Maturité (%)"].median())
        n_above = int((gdf["Score Maturité (%)"] > (ma_score or 0)).sum())
        n_below = len(gdf) - n_above - 1

        col_g, col_txt = st.columns([3, 2])
        with col_g:
            st.markdown("**Top 20 Score MEF + Maroc**")
            st.plotly_chart(bar_chart(top20), use_container_width=True)
        with col_txt:
            st.markdown("**Ce que dit ce classement**")
            pct_top = round(r_monde / n_monde * 100)
            st.markdown(f"""
- finances.gov.ma **#{r_monde}/{n_monde}** mondial · top **{pct_top}%**
- Score : **{ma_score:.0f}/100** · médiane mondiale : **{med:.0f}/100**
- **+{ma_score-med:.0f} pts** au-dessus de la médiane
- Devance **{n_below}** portails sur {n_monde}
            """)
            st.markdown("**🏆 Podium mondial (Score MEF)**")
            for i in range(min(5, len(gdf))):
                p = gdf.iloc[i]["Pays"]; s = gdf.iloc[i]["Score Maturité (%)"]
                ico = ["🥇","🥈","🥉","4️⃣","5️⃣"][i]
                b = "color:#E8431A;font-weight:700;" if p=="Maroc" else ""
                st.markdown(f'<p style="margin:3px 0;{b}">{ico} {p} — {s:.0f}/100</p>', unsafe_allow_html=True)

    # ── Tab Afrique ────────────────────────────────────────────────────────────
    with tab_afr:
        gdf_afr = df_sc[df_sc["Région"]=="Afrique"].sort_values("Score Maturité (%)", ascending=False).copy()
        if "Maroc" not in gdf_afr["Pays"].values:
            gdf_afr = pd.concat([gdf_afr, df_sc[df_sc["Pays"]=="Maroc"]]).reset_index(drop=True)
        med_afr = float(gdf_afr["Score Maturité (%)"].median())
        n_above_afr = int((gdf_afr["Score Maturité (%)"] > (ma_score or 0)).sum())

        col_g, col_txt = st.columns([3, 2])
        with col_g:
            st.markdown("**Score MEF — portails africains**")
            st.plotly_chart(bar_chart(gdf_afr), use_container_width=True)
        with col_txt:
            st.markdown("**Position du Maroc en Afrique**")
            if r_afr == 1:
                st.markdown(f"""<div class="ok-box">
                🥇 Le Maroc est le <b>leader africain</b> selon le Score MEF.<br>
                Score : <b>{ma_score:.0f}/100</b> · médiane Afrique : <b>{med_afr:.0f}/100</b>
                </div>""", unsafe_allow_html=True)
            else:
                above_ls = gdf_afr[gdf_afr["Score Maturité (%)"] > (ma_score or 0)]["Pays"].tolist()
                st.markdown(f"""
- **#{r_afr}/{n_afr}** en Afrique selon le Score MEF
- Devancé par : **{', '.join(above_ls)}**
- Médiane africaine : **{med_afr:.0f}/100** · Maroc : **{ma_score:.0f}/100**
- **+{ma_score-med_afr:.0f} pts** au-dessus de la médiane africaine
                """)

    # ── Tab MENA ──────────────────────────────────────────────────────────────
    with tab_mena:
        gdf_mena = df_sc[df_sc["Pays"].isin(MENA_PAYS + ["Maroc"])].sort_values(
            "Score Maturité (%)", ascending=False).copy()
        med_mena = float(gdf_mena["Score Maturité (%)"].median())
        above_mena = gdf_mena[gdf_mena["Score Maturité (%)"] > (ma_score or 0)]["Pays"].tolist()

        col_g, col_r = st.columns([3, 2])
        with col_g:
            st.markdown("**Score MEF — région MENA**")
            st.plotly_chart(bar_chart(gdf_mena), use_container_width=True)
        with col_r:
            st.markdown("**Position MENA**")
            st.markdown(f"""
- **#{r_mena}/{n_mena}** dans la région MENA
- {"Devancé par : **" + ', '.join(above_mena) + "**" if above_mena else "**Leader MENA** selon le Score MEF"}
- Médiane MENA : **{med_mena:.0f}/100**
            """)
            st.markdown("---")
            st.markdown("**eGov ONU MENA (pour comparaison)**")
            df_mena_eg = df_eg[df_eg["Pays"].isin(MENA_PAYS + ["Maroc"])].sort_values("Rang EGOV 2024")
            mena_eg_tbl = df_mena_eg[["Pays","Rang EGOV 2024","Indice EGOV"]].copy()
            mena_eg_tbl["Rang EGOV 2024"] = mena_eg_tbl["Rang EGOV 2024"].astype("Int64")
            def _hl(row): return ["background-color:#FEF3E8;font-weight:bold"]*len(row) if row["Pays"]=="Maroc" else [""]*len(row)
            st.dataframe(mena_eg_tbl.style.apply(_hl, axis=1), hide_index=True, use_container_width=True)
            st.caption("eGov ONU = gouvernement entier, pas uniquement MoF")

        st.markdown("---")
        # Heatmap MENA
        st.subheader("🔥 Heatmap indicateurs — Maroc vs MENA")
        MENA_HM = ["Arabie Saoudite","Émirats","Bahreïn","Égypte","Jordanie","Tunisie","Algérie","Maroc","Oman","Qatar","Mauritanie"]
        hm_cols = ["HTTPS","Responsive","Sitemap.xml","Moteur de recherche","Bandeau cookies",
                   "Formulaires en ligne","Section actualités","Section marchés publics",
                   "Facebook","YouTube","Mention open data","Mention rapport annuel",
                   "Politique confidentialité","Déclaration accessibilité","Données téléchargeables"]
        hm_df = df[df["Pays"].isin(MENA_HM)].set_index("Pays")[[c for c in hm_cols if c in df.columns]].copy()
        _applymap = getattr(hm_df, "map", None) or hm_df.applymap
        hm_num = _applymap(lambda x: 1 if x is True else (0 if x is False else None))
        hm_num["_s"] = hm_num.sum(axis=1)
        hm_num = hm_num.sort_values("_s", ascending=False).drop("_s", axis=1)
        hm_num = hm_num.reindex(["Maroc"] + [p for p in hm_num.index if p != "Maroc"])
        _applymap2 = getattr(hm_num, "map", None) or hm_num.applymap
        hm_txt = _applymap2(lambda v: "✓" if v==1 else ("✗" if v==0 else "—"))
        fig_hm = px.imshow(hm_num, color_continuous_scale=[[0,"#FDECEA"],[0.5,"#F5EEF8"],[1,"#1A5276"]],
            aspect="auto", zmin=0, zmax=1)
        fig_hm.update_traces(text=hm_txt.values, texttemplate="%{text}", textfont=dict(size=12))
        fig_hm.update_layout(height=400, coloraxis_showscale=False, xaxis_tickangle=-35,
            margin=dict(l=130, r=20, t=20, b=80))
        st.plotly_chart(fig_hm, use_container_width=True)

    # ── Tab Pairs eGov ────────────────────────────────────────────────────────
    with tab_peers:
        WINDOW = 6  # ±6 rangs autour du rang eGov du Maroc
        if ma_egov:
            peers_df = df_sc[
                df_sc["Rang EGOV 2024"].notna() &
                (df_sc["Rang EGOV 2024"] >= ma_egov - WINDOW) &
                (df_sc["Rang EGOV 2024"] <= ma_egov + WINDOW)
            ].copy()
            # Toujours inclure le Maroc
            if "Maroc" not in peers_df["Pays"].values:
                peers_df = pd.concat([peers_df, df_sc[df_sc["Pays"]=="Maroc"]]).reset_index(drop=True)
            peers_df = peers_df.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
            peers_df["Rang MEF (peers)"] = range(1, len(peers_df)+1)
            r_peers = int(peers_df[peers_df["Pays"]=="Maroc"].index[0]) + 1
            n_peers = len(peers_df)
            med_peers = float(peers_df["Score Maturité (%)"].median())
            above_peers = peers_df[peers_df["Score Maturité (%)"] > (ma_score or 0)]["Pays"].tolist()

            col_g, col_r = st.columns([3, 2])
            with col_g:
                st.markdown(f"**Score MEF — pays avec eGov rank #{ma_egov-WINDOW}–#{ma_egov+WINDOW}** (pairs eGov du Maroc)")
                st.plotly_chart(bar_chart(peers_df), use_container_width=True)
            with col_r:
                st.markdown("**Ce que révèle ce comparatif**")
                if r_peers <= 3:
                    st.markdown(f"""<div class="ok-box">
                    🏅 Le Maroc est <b>#{r_peers}/{n_peers}</b> parmi ses pairs eGov.<br>
                    Score MEF : <b>{ma_score:.0f}/100</b> · médiane peers : <b>{med_peers:.0f}/100</b><br>
                    Le portail <b>finances.gov.ma dépasse largement</b> son niveau de maturité numérique globale (eGov #{ma_egov}).
                    </div>""", unsafe_allow_html=True)
                else:
                    st.markdown(f"""
- **#{r_peers}/{n_peers}** parmi les pays eGov #{ma_egov-WINDOW}–#{ma_egov+WINDOW}
- Score MEF : **{ma_score:.0f}/100** · médiane peers : **{med_peers:.0f}/100**
- {"Devancé par : **" + ', '.join(above_peers[:5]) + ("...**" if len(above_peers)>5 else "**") if above_peers else "**Leader de ses pairs eGov**"}
                    """)
                st.markdown("---")
                st.markdown("""**💡 Lecture**
Les *pairs eGov* sont les pays avec un rang ONU similaire à celui du Maroc.
Comparer les scores MEF dans ce groupe montre si le portail MoF marocain
est **sur- ou sous-performant** par rapport à son niveau de gouvernance globale.""")
        else:
            st.info("Rang eGov non disponible pour le Maroc.")

    # ── Tab Inspirations ──────────────────────────────────────────────────────
    with tab_inspi:
        st.markdown("**🌟 Références mondiales & sources d'inspiration pour finances.gov.ma**")
        st.markdown("""Ces portails se distinguent par leurs pratiques exemplaires dans des domaines
        que le Maroc peut cibler à court ou moyen terme.""")

        # Sélection dynamique : top 5 mondial hors Maroc + top 3 par région cible
        top_global = df_sc[df_sc["Pays"] != "Maroc"].nlargest(5, "Score Maturité (%)").copy()

        # Indicateurs clés pour comparaison
        inspi_cols = ["Mention open data", "Données téléchargeables", "Formulaires en ligne",
                      "Déclaration accessibilité", "Bandeau cookies", "Mention transparence",
                      "Politique confidentialité", "Abonnement newsletter", "Mention rapport annuel"]
        inspi_cols = [c for c in inspi_cols if c in df.columns]

        maroc_row_inspi = df[df["Pays"]=="Maroc"].iloc[0]

        def _has(series, col):
            v = series.get(col, False)
            if isinstance(v, bool): return v
            return str(v).strip().upper() == "O"

        st.markdown("#### 🏆 Top 5 mondial — ce qui les distingue")
        for _, row in top_global.iterrows():
            p = row["Pays"]; s = row["Score Maturité (%)"]
            egov_r = int(row["Rang EGOV 2024"]) if pd.notna(row.get("Rang EGOV 2024")) else "—"
            gaps = [c for c in inspi_cols if _has(row, c) and not _has(maroc_row_inspi, c)]
            with st.expander(f"**{p}** — Score MEF {s:.0f}/100 · eGov #{egov_r}"):
                if gaps:
                    st.markdown("**Indicateurs que le Maroc pourrait adopter :**")
                    for g in gaps:
                        st.markdown(f"  ✅ {g}")
                else:
                    st.markdown("_Le Maroc dispose déjà de tous les indicateurs de ce pays._")

        st.markdown("---")
        st.markdown("#### 🌍 Références régionales — MENA & Afrique")
        ref_pays = ["Émirats","Arabie Saoudite","Afrique du Sud","Sénégal"]
        ref_df = df_sc[df_sc["Pays"].isin(ref_pays)].sort_values("Score Maturité (%)", ascending=False)
        for _, row in ref_df.iterrows():
            p = row["Pays"]; s = row["Score Maturité (%)"]
            gaps = [c for c in inspi_cols if _has(row, c) and not _has(maroc_row_inspi, c)]
            with st.expander(f"**{p}** — Score MEF {s:.0f}/100"):
                if gaps:
                    st.markdown("**Pratiques à observer :**")
                    for g in gaps: st.markdown(f"  ✅ {g}")
                else:
                    st.markdown("_Le Maroc dépasse déjà ce pays sur tous les indicateurs listés._")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — CLASSEMENT MONDIAL MoF
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("🏆"):
    page_header("🏆 Classement mondial des portails MoF",
                "193 ministères des Finances · Score MEF 2026 · 38 critères techniques",
                badge="Score MEF · données scrapées 2026")

    source_banner()

    df_sc = df[df["Score Maturité (%)"].notna()].sort_values(
        "Score Maturité (%)", ascending=False).reset_index(drop=True).copy()
    df_sc["Rang MEF"] = range(1, len(df_sc)+1)

    st.markdown("""<div class="warn-box">
    ⚠️ <b>Limites de ce classement</b> : (1) Les sites nordiques/européens en SPA (React/Angular) sont
    <b>sous-scorés</b> car le JavaScript dynamique n'est pas rendu lors du scraping.
    (2) Les pays avec <b>multi-sites fusionnés</b> peuvent avoir un avantage structurel.
    (3) Les scores <b>⚠️ Wayback</b> sont moins fiables (snapshots d'archive).
    Ce classement est à lire comme un <b>inventaire de fonctionnalités</b>, pas un rang absolu de maturité.
    </div>""", unsafe_allow_html=True)

    # ── Filtres ───────────────────────────────────────────────────────────────
    col_f1, col_f2, col_f3, col_f4 = st.columns(4)
    with col_f1:
        reg_filter = st.multiselect("Région", options=sorted(df_sc["Région"].dropna().unique()),
                                     default=[], placeholder="Toutes")
    with col_f2:
        cat_filter = st.multiselect("Catégorie", options=["meilleure pratique","aspirationnel","pair","référence","en développement"],
                                     default=[], placeholder="Toutes")
    with col_f3:
        portail_filter = st.radio("Type portail", ["Tous","Multi-sites","Centralisé"], horizontal=True)
    with col_f4:
        live_only = st.toggle("🔬 Live uniquement", value=False,
                              help="Exclut les scores issus de la Wayback Machine (archives) — données directes uniquement, plus fiables (ρ = 0.566)")

    df_filt = df_sc.copy()
    has_quality_col = "data_quality_flag" in df_filt.columns
    if live_only and has_quality_col:
        df_filt = df_filt[df_filt["data_quality_flag"].isin(["live", "satellite"])].copy()
        df_filt["Rang MEF"] = range(1, len(df_filt) + 1)
    if reg_filter: df_filt = df_filt[df_filt["Région"].isin(reg_filter)]
    if cat_filter: df_filt = df_filt[df_filt["Catégorie"].isin(cat_filter)]
    if portail_filter == "Multi-sites": df_filt = df_filt[df_filt["Type portail"] != "centralisé"]
    if portail_filter == "Centralisé":  df_filt = df_filt[df_filt["Type portail"] == "centralisé"]

    n_live = int(df_sc["data_quality_flag"].isin(["live","satellite"]).sum()) if has_quality_col else "?"
    n_archive = (len(df_sc) - n_live) if isinstance(n_live, int) else "?"
    if live_only:
        st.caption(f"**{len(df_filt)} pays** — collecte directe uniquement (archives Wayback exclues) · ρ = 0.566")
    else:
        st.caption(f"{len(df_filt)} pays affichés · {n_live} collecte directe · {n_archive} archives Wayback")

    # ── Tableau ───────────────────────────────────────────────────────────────
    disp_cols = ["Rang MEF","Pays","Catégorie","Région","Score Maturité (%)","Rang EGOV 2024",
                 "Type portail","Collecte","Couverture (%)"]
    disp = df_filt[[c for c in disp_cols if c in df_filt.columns]].copy()
    disp["Score Maturité (%)"] = disp["Score Maturité (%)"].apply(lambda v: f"{v:.0f}/100" if pd.notna(v) else "—")
    if "Rang EGOV 2024" in disp.columns:
        disp["Rang EGOV 2024"] = disp["Rang EGOV 2024"].apply(lambda v: f"#{int(v)}" if pd.notna(v) else "—")
    if "Couverture (%)" in disp.columns:
        disp["Couverture (%)"] = disp["Couverture (%)"].apply(lambda v: f"{v:.0f}%" if pd.notna(v) else "—")
    if "Collecte" in disp.columns:
        disp["Collecte"] = disp["Collecte"].apply(lambda v:
            "⚠️ Archive (score sous-estimé)" if "Wayback" in str(v) else v)

    def hl_maroc(row):
        return ["background-color:#FEF3E8;font-weight:bold"]*len(row) if row.get("Pays")=="Maroc" else [""]*len(row)

    st.dataframe(disp.style.apply(hl_maroc, axis=1), hide_index=True, use_container_width=True, height=520)

    st.markdown("---")

    # ── Scatter : Rang MEF vs Rang eGov ONU ──────────────────────────────────
    rho_label = "0.566" if live_only else "0.8068"
    n_corr_label = "94" if live_only else "132"
    st.subheader(f"📈 Rang MEF 2026 vs Rang eGov ONU 2024 — corrélation ρ = {rho_label}")
    st.caption("Chaque point = un pays. 🇲🇦 = Maroc. Plus un pays est en haut à gauche, plus il est bien classé sur les deux systèmes.")

    _corr_base = df_filt if live_only else df
    df_corr = _corr_base[_corr_base["Score Maturité (%)"].notna() & _corr_base["Rang EGOV 2024"].notna()].copy()
    df_corr["Score Maturité (%)"] = pd.to_numeric(df_corr["Score Maturité (%)"], errors="coerce")
    df_corr = df_corr.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
    df_corr["Rang MEF"] = range(1, len(df_corr) + 1)

    # Rang eGov re-calculé sur les 132 pays communs (même périmètre que MEF)
    n_commun = len(df_corr)
    df_corr = df_corr.sort_values("Rang EGOV 2024").reset_index(drop=True)
    df_corr["Rang eGov commun"] = range(1, n_commun + 1)
    df_corr = df_corr.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
    df_corr["Rang MEF"] = range(1, n_commun + 1)
    # Percentiles sur le même périmètre — directement comparables
    df_corr["Percentile MEF"]  = df_corr["Rang MEF"]        / n_commun * 100
    df_corr["Percentile eGov"] = df_corr["Rang eGov commun"] / n_commun * 100

    CAT_COL = {"meilleure pratique":"#1A5276","aspirationnel":"#2E86C1",
               "pair":"#85C1E9","référence":"#E8431A","en développement":"#BFC9CA"}

    fig_sc = px.scatter(df_corr, x="Rang eGov commun", y="Rang MEF",
        color="Catégorie", color_discrete_map=CAT_COL,
        hover_name="Pays", opacity=0.75,
        custom_data=["Rang eGov commun", "Rang MEF"],
        labels={"Rang eGov commun": f"Rang eGov ONU sur {n_commun} pays communs (1=meilleur →)",
                "Rang MEF":         f"Rang MEF sur {n_commun} pays communs (1=meilleur ↑)"},
        size_max=8)
    fig_sc.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Rang eGov: #%{customdata[0]}/%{customdata[1]|}<extra></extra>"
    )
    fig_sc.update_traces(
        hovertemplate="<b>%{hovertext}</b><br>Rang eGov: #%{customdata[0]}<br>Rang MEF: #%{customdata[1]}<extra></extra>"
    )

    maroc_row = df_corr[df_corr["Pays"] == "Maroc"]
    if len(maroc_row):
        fig_sc.add_scatter(
            x=maroc_row["Rang eGov commun"], y=maroc_row["Rang MEF"],
            mode="markers+text", text=["🇲🇦"], textposition="top right",
            marker=dict(color="#E8431A", size=18, symbol="star"),
            name="Maroc", showlegend=False)

    # Diagonale — même échelle, même périmètre
    fig_sc.add_scatter(x=[1, n_commun], y=[1, n_commun],
        mode="lines", line=dict(dash="dot", color="#BCC8E0", width=1.5),
        name="Alignement parfait", showlegend=True)

    fig_sc.update_xaxes(autorange="reversed")
    fig_sc.update_yaxes(autorange="reversed")
    fig_sc.update_layout(height=470, legend=dict(orientation="h", y=-0.18))
    st.plotly_chart(fig_sc, use_container_width=True)

    st.markdown("""<div class="ok-box">
    ✅ <b>Lecture</b> : les deux axes sont calculés sur les <b>132 pays présents dans les deux classements</b>,
    ce qui les rend directement comparables. Les pays <b>au-dessus</b> de la diagonale ont un portail MoF
    <b>meilleur</b> que leur gouvernance globale (ex : 🇲🇦 Maroc — #71 MEF vs #82 eGov sur 132 pays communs).
    La corrélation <b>ρ = 0.8068</b> confirme que les deux classements sont cohérents sans être identiques.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — AXES D'AMÉLIORATION
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("🎯"):
    page_header("🎯 Axes d'amélioration — finances.gov.ma",
                "Fonctionnalités manquantes · comparaison avec les leaders · plan d'action",
                badge="finances.gov.ma · recommandations")

    st.markdown("""<div class="info-box">
    🎯 Cette page identifie les fonctionnalités <b>présentes chez les meilleurs portails MoF mondiaux
    mais absentes de finances.gov.ma</b>. Chaque recommandation est classée par priorité selon
    son taux d'adoption chez les pays leaders.
    </div>""", unsafe_allow_html=True)

    ma_score = float(maroc["Score Maturité (%)"]) if pd.notna(maroc.get("Score Maturité (%)")) else None
    best_df  = df[df["Catégorie"]=="meilleure pratique"]
    aspir_df = df[df["Catégorie"]=="aspirationnel"]

    # ── KPIs Maroc ────────────────────────────────────────────────────────────
    feat_present = sum(1 for c in BOOL_COLS if c in df.columns and maroc.get(c) is True)
    feat_missing = sum(1 for c in BOOL_COLS if c in df.columns and maroc.get(c) is False)
    crit_missing = sum(1 for c in BOOL_COLS if c in df.columns
                       and maroc.get(c) is False and adopt_pct(best_df, c) >= 70)

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Score MEF Maroc", f"{ma_score:.0f}/100" if ma_score else "—","ma"), unsafe_allow_html=True)
    c2.markdown(kpi("Indicateurs présents", f"{feat_present}/{len([c for c in BOOL_COLS if c in df.columns])}","ok"), unsafe_allow_html=True)
    c3.markdown(kpi("Indicateurs manquants", str(feat_missing), "warn"), unsafe_allow_html=True)
    c4.markdown(kpi("Critiques manquants (≥70% leaders)", str(crit_missing), "ma",
        tooltip="Fonctionnalités présentes chez ≥70% des meilleurs portails MoF et absentes de finances.gov.ma"), unsafe_allow_html=True)

    st.markdown("---")

    # ── Radar Maroc vs leaders ────────────────────────────────────────────────
    st.subheader("🕸️ Radar — Maroc vs top portails")
    RADAR_DIMS = {
        "Fondamentaux":  ["HTTPS","Responsive","Moteur de recherche","Sitemap.xml"],
        "Transparence":  ["Mention rapport annuel","Mention open data","Documents PDF","Mention loi de finances"],
        "Services":      ["Formulaires en ligne","Espace citoyen","Chatbot","Facturation électronique"],
        "Données ouv.":  ["Données téléchargeables","API avec documentation","Données budgétaires structurées"],
        "Conformité":    ["Bandeau cookies","Déclaration accessibilité","Politique confidentialité"],
        "Réseaux soc.":  ["Facebook","YouTube","Twitter/X","Abonnement newsletter"],
    }
    RADAR_PAYS = ["Maroc","Émirats","Royaume-Uni","Singapour","Arabie Saoudite"]
    RADAR_COL  = {"Maroc":"#E8431A","Émirats":"#1A5276","Royaume-Uni":"#117A65",
                  "Singapour":"#8E44AD","Arabie Saoudite":"#C28011"}

    fig_r = go.Figure()
    dims  = list(RADAR_DIMS.keys())
    for pays in RADAR_PAYS:
        row = df[df["Pays"]==pays]
        if len(row) == 0: continue
        row = row.iloc[0]
        scores = []
        for dcols in RADAR_DIMS.values():
            avail = [c for c in dcols if c in df.columns]
            if not avail: scores.append(0); continue
            n_true = sum(1 for c in avail if row.get(c) is True)
            scores.append(round(n_true / len(avail) * 100, 0))
        scores.append(scores[0])
        fig_r.add_trace(go.Scatterpolar(
            r=scores, theta=dims + [dims[0]], name=pays,
            line=dict(color=RADAR_COL.get(pays,"#888"), width=3 if pays=="Maroc" else 1.5),
            fill="toself" if pays=="Maroc" else "none",
            fillcolor="rgba(232,67,26,0.10)" if pays=="Maroc" else None,
        ))
    fig_r.update_layout(
        polar=dict(radialaxis=dict(range=[0,100], tickvals=[0,25,50,75,100])),
        height=420, legend=dict(orientation="h", y=-0.12), showlegend=True,
    )
    st.plotly_chart(fig_r, use_container_width=True)

    st.markdown("---")

    # ── Tableau des quick wins ────────────────────────────────────────────────
    st.subheader("📋 Plan d'action — fonctionnalités manquantes sur finances.gov.ma")

    EFFORT = {
        "Bandeau cookies":"Faible","Politique confidentialité":"Faible",
        "Déclaration accessibilité":"Faible","Abonnement newsletter":"Faible",
        "Données téléchargeables":"Moyen","Mention open data":"Moyen",
        "API avec documentation":"Moyen","Formulaires en ligne":"Moyen",
        "Chatbot":"Élevé","Facturation électronique":"Élevé",
        "Tableau de bord temps réel":"Élevé","Données budgétaires structurées":"Élevé",
    }

    qw_rows = []
    for col in [c for c in BOOL_COLS if c in df.columns]:
        if maroc.get(col) is False:
            pct_best  = adopt_pct(best_df, col)
            pct_aspir = adopt_pct(aspir_df, col)
            effort    = EFFORT.get(col, "Moyen")
            phase     = ("⚡ Court terme" if pct_best >= 60 and effort == "Faible"
                         else "🎯 Moyen terme" if pct_best >= 40 else "🔭 Long terme")
            prio      = ("🔴 Critique" if pct_best >= 70 else "🟡 Important" if pct_best >= 40 else "🟢 Optionnel")
            qw_rows.append({
                "Indicateur": col, "Priorité": prio,
                "Leaders (%)": round(pct_best), "Aspir. (%)": round(pct_aspir),
                "Effort": effort, "Phase": phase,
            })
    qw_df = pd.DataFrame(qw_rows).sort_values(["Leaders (%)"], ascending=False)

    ph_ct, ph_mt, ph_lt = st.tabs(["⚡ Court terme","🎯 Moyen terme","🔭 Long terme"])
    for tab, label in [(ph_ct,"⚡ Court terme"),(ph_mt,"🎯 Moyen terme"),(ph_lt,"🔭 Long terme")]:
        with tab:
            sub = qw_df[qw_df["Phase"]==label].drop(columns=["Phase"])
            if sub.empty:
                st.success("✅ Aucune fonctionnalité manquante dans cette phase.")
            else:
                st.dataframe(sub, hide_index=True, use_container_width=True)

    st.markdown("---")

    # ── Ce que les leaders MENA ont et que le Maroc n'a pas ──────────────────
    st.subheader("🌙 Ce que les Émirats & Arabie Saoudite ont — et que le Maroc peut adopter")
    gulf = ["Émirats","Arabie Saoudite"]
    gaps, leads = [], []
    for col in [c for c in BOOL_COLS if c in df.columns]:
        ma_has = maroc.get(col) is True
        gulf_with = [p for p in gulf if len(df[df["Pays"]==p]) > 0 and df[df["Pays"]==p].iloc[0].get(col) is True]
        if not ma_has and gulf_with:
            gaps.append((col, gulf_with))
        elif ma_has and not gulf_with:
            leads.append(col)

    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("**❌ À adopter — présent chez les leaders MENA, absent au Maroc**")
        for feat, who in gaps:
            st.markdown(f"""
<div style="padding:8px 14px;margin:4px 0;background:white;border-radius:8px;
     border-left:3px solid #E74C3C;font-size:0.88rem;box-shadow:0 1px 3px rgba(0,0,0,.06);">
  ❌ <b>{feat}</b> <span style="color:#888;">({' & '.join(who)})</span>
</div>""", unsafe_allow_html=True)
    with col_l:
        st.markdown("**✅ Avances du Maroc — présent au Maroc, absent chez ces leaders**")
        if leads:
            for feat in leads:
                st.markdown(f"""
<div style="padding:8px 14px;margin:4px 0;background:white;border-radius:8px;
     border-left:3px solid #27AE60;font-size:0.88rem;box-shadow:0 1px 3px rgba(0,0,0,.06);">
  ✅ <b>{feat}</b>
</div>""", unsafe_allow_html=True)
        else:
            st.info("Aucune fonctionnalité uniquement présente au Maroc dans ce groupe.")

    st.markdown("---")

    # ── Exemples de pays par indicateur manquant ──────────────────────────────
    st.subheader("🌍 Qui l'a déjà fait ? — Exemples concrets par fonctionnalité")
    st.markdown("""<div class="info-box">
    Pour chaque fonctionnalité manquante sur finances.gov.ma, voici des pays comparables
    qui l'ont déjà mise en œuvre — avec leur Score MEF et leur région, pour montrer que c'est faisable.
    </div>""", unsafe_allow_html=True)

    EXEMPLES_PAYS = {
        "Mention open data": [
            ("Jordanie", "Asie", "lancement data.gov.jo en 2022 — portail open data gouvernemental"),
            ("Sénégal",  "Afrique", "portail opendata.sec.gouv.sn — données budgétaires libres"),
            ("Tunisie",  "Afrique", "données.gov.tn — contexte culturel proche du Maroc"),
        ],
        "Bandeau cookies": [
            ("Algérie",  "Afrique", "mf.gov.dz — ajout du bandeau RGPD en 2023"),
            ("Tunisie",  "Afrique", "ajout rapide, effort estimé < 1 semaine"),
            ("Maroc (CNDP)", "Afrique", "la CNDP recommande l'adoption — base légale existe déjà"),
        ],
        "Mention rapport annuel": [
            ("Ghana",    "Afrique", "mofep.gov.gh — rapport annuel MoF publié chaque année"),
            ("Ouganda",  "Afrique", "finance.go.ug — rapport de performance budgétaire"),
            ("Rwanda",   "Afrique", "minecofin.gov.rw — leader africain en transparence"),
        ],
        "Déclaration accessibilité": [
            ("Portugal", "Europe", "dgo.pt — déclaration WCAG 2.1 AA publiée"),
            ("Espagne",  "Europe", "hacienda.gob.es — modèle de déclaration réutilisable"),
            ("Tunisie",  "Afrique", "démarche en cours — momentum régional"),
        ],
        "Données téléchargeables": [
            ("Kenya",    "Afrique", "opendata.go.ke — fichiers CSV/XLSX budget exécution"),
            ("Rwanda",   "Afrique", "minecofin.gov.rw — données BOOST Banque Mondiale"),
            ("Émirats",  "Asie",    "mof.gov.ae — Excel téléchargeables sur budget fédéral"),
        ],
        "Abonnement newsletter": [
            ("Côte d'Ivoire", "Afrique", "budget.gouv.ci — newsletter actualités fiscales"),
            ("Arabie Saoudite", "Asie", "mof.gov.sa — alertes email sur circulaires"),
            ("Jordanie",  "Asie",   "mof.gov.jo — abonnement aux communiqués"),
        ],
        "Mécanisme de réclamations": [
            ("Ghana",    "Afrique", "formulaire plainte en ligne sur mofep.gov.gh"),
            ("Kenya",    "Afrique", "kra.go.ke — signalement corruption intégré"),
            ("Singapour","Asie",    "mof.gov.sg — feedback form avec suivi"),
        ],
        "Liberté d'accès à l'info": [
            ("Afrique du Sud", "Afrique", "loi PAIA — formulaire de demande en ligne"),
            ("Ghana",    "Afrique", "Right to Information Act 2019 — portail dédié"),
            ("Tunisie",  "Afrique", "décret 2011-41 — mécanisme similaire applicable"),
        ],
    }

    missing_indicators = [c for c in BOOL_COLS if c in df.columns and maroc.get(c) is False]
    for indic in missing_indicators:
        if indic not in EXEMPLES_PAYS:
            continue
        exemples = EXEMPLES_PAYS[indic]
        # Récupérer le score MEF de chaque pays exemple
        with st.expander(f"**{indic}** — {len(exemples)} exemples de pays"):
            cols_ex = st.columns(len(exemples))
            for i, (pays_ex, region_ex, desc_ex) in enumerate(exemples):
                row_ex = df[df["Pays"] == pays_ex]
                score_ex = f"{row_ex.iloc[0]['Score Maturité (%)']:.0f}/100" if len(row_ex) > 0 and pd.notna(row_ex.iloc[0].get("Score Maturité (%)")) else "—"
                with cols_ex[i]:
                    st.markdown(f"""
<div style="background:white;border-radius:10px;padding:12px;border:1px solid #DEE4F0;
     box-shadow:0 1px 4px rgba(0,45,138,0.06);height:100%;">
  <div style="font-weight:700;color:#002D8A;font-size:0.92rem;">🌍 {pays_ex}</div>
  <div style="font-size:0.75rem;color:#6B7A99;margin:2px 0 6px;">{region_ex} · Score MEF {score_ex}</div>
  <div style="font-size:0.82rem;color:#444;line-height:1.5;">{desc_ex}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Simulateur de score ───────────────────────────────────────────────────
    st.subheader("🎛️ Simulateur de score — Et si finances.gov.ma ajoutait ces fonctionnalités ?")
    st.markdown("""<div class="info-box">
    Sélectionne les fonctionnalités que le Maroc pourrait ajouter et vois en temps réel
    l'impact sur le Score de Maturité et le rang mondial.
    </div>""", unsafe_allow_html=True)

    # Dimensions pour recalcul simplifié (poids proportionnels)
    DIMS_SIM = {
        "Fondamentaux web": {
            "poids": 35,
            "indicateurs": {
                "HTTPS":2,"Responsive":3,"Moteur de recherche":4,"Sitemap.xml":2,
                "Politique confidentialité":3,"Déclaration accessibilité":5,"Bandeau cookies":3,
            }
        },
        "Transparence": {
            "poids": 15,
            "indicateurs": {
                "Mention rapport annuel":5,"Section actualités":2,"Section marchés publics":2,
                "Documents PDF":2,"Mention transparence":2,
            }
        },
        "Services": {
            "poids": 20,
            "indicateurs": {
                "Espace citoyen":7,"Formulaires en ligne":5,"Mécanisme de réclamations":4,
                "Facturation électronique":3,"Chatbot":2,
            }
        },
        "Données ouvertes": {
            "poids": 25,
            "indicateurs": {
                "Mention open data":8,"Données téléchargeables":8,"Mention API publique":6,
                "Tableau de bord temps réel":2,
            }
        },
        "Ouverture institutionnelle": {
            "poids": 5,
            "indicateurs": {
                "Liberté d'accès à l'info":4,"Abonnement newsletter":2,
                "Facebook":1,"YouTube":2,"Twitter/X":1,
            }
        },
    }

    def compute_sim_score(indic_values):
        total_w, total_p = 0.0, 0.0
        for dim_data in DIMS_SIM.values():
            dp = dim_data["poids"]
            inds = dim_data["indicateurs"]
            avail = {k: v for k, v in inds.items() if k in indic_values}
            if not avail:
                continue
            max_pts = sum(inds.values())
            got_pts = sum(v for k, v in inds.items() if indic_values.get(k) is True)
            avail_pts = sum(avail.values())
            ds = got_pts / max_pts * 100 if max_pts > 0 else 0
            total_w += ds * dp
            total_p += dp
        return round(total_w / total_p, 1) if total_p > 0 else 0

    # Valeurs actuelles Maroc
    maroc_vals = {c: maroc.get(c) for c in BOOL_COLS if c in df.columns}
    score_actuel = float(maroc.get("Score Maturité (%)") or 0)

    # Indicateurs manquants cochables
    missing_sim = [c for c in BOOL_COLS if c in df.columns and maroc.get(c) is False
                   and any(c in d["indicateurs"] for d in DIMS_SIM.values())]

    col_sim_left, col_sim_right = st.columns([2, 3])

    with col_sim_left:
        st.markdown("**Cocher les fonctionnalités à ajouter :**")
        selected_adds = []
        for indic in missing_sim:
            if st.checkbox(indic, key=f"sim_{indic}"):
                selected_adds.append(indic)

    with col_sim_right:
        # Recalcul avec les indicateurs ajoutés
        sim_vals = dict(maroc_vals)
        for indic in selected_adds:
            sim_vals[indic] = True

        score_sim = compute_sim_score(sim_vals)
        gain = score_sim - score_actuel

        # Rang estimé
        df_sc_sim = df[df["Score Maturité (%)"].notna()].copy()
        rang_actuel = int((df_sc_sim["Score Maturité (%)"] > score_actuel).sum()) + 1
        rang_sim = int((df_sc_sim["Score Maturité (%)"] > score_sim).sum()) + 1
        gain_rang = rang_actuel - rang_sim

        # Affichage
        col_a1, col_a2, col_a3 = st.columns(3)
        col_a1.markdown(f"""<div class="kpi kpi-ma">
            <div class="kpi-v">{score_actuel:.0f}/100</div>
            <div class="kpi-l">Score actuel</div></div>""", unsafe_allow_html=True)
        color_gain = "kpi-ok" if gain > 0 else "kpi-warn"
        col_a2.markdown(f"""<div class="kpi {color_gain}">
            <div class="kpi-v">{score_sim:.0f}/100</div>
            <div class="kpi-l">Score simulé (+{gain:.1f} pts)</div></div>""", unsafe_allow_html=True)
        col_a3.markdown(f"""<div class="kpi {'kpi-ok' if gain_rang > 0 else ''}">
            <div class="kpi-v">#{rang_sim}/{len(df_sc_sim)}</div>
            <div class="kpi-l">Rang simulé ({"+" if gain_rang>0 else ""}{gain_rang} places)</div></div>""", unsafe_allow_html=True)

        if selected_adds:
            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            # Barre de progression
            fig_sim = go.Figure()
            fig_sim.add_trace(go.Bar(
                x=[score_actuel], y=["Score actuel"], orientation="h",
                marker_color="#E8431A", name="Actuel",
                text=[f"{score_actuel:.0f}/100"], textposition="outside",
            ))
            fig_sim.add_trace(go.Bar(
                x=[score_sim], y=["Score simulé"], orientation="h",
                marker_color="#27AE60", name="Simulé",
                text=[f"{score_sim:.0f}/100"], textposition="outside",
            ))
            fig_sim.update_layout(
                height=140, xaxis=dict(range=[0, 105], title="Score MEF (%)"),
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=110, r=60, t=10, b=40),
                showlegend=False, barmode="group",
            )
            st.plotly_chart(fig_sim, use_container_width=True)

            st.markdown(f"""<div class="ok-box">
            ✅ En ajoutant <b>{len(selected_adds)} fonctionnalité(s)</b> :
            <b>{', '.join(selected_adds[:3])}{'...' if len(selected_adds)>3 else ''}</b><br>
            Le Maroc passerait de <b>{score_actuel:.0f} → {score_sim:.0f} pts</b>
            et gagnerait <b>{gain_rang} place(s)</b> dans le classement mondial.
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class="warn-box">
            ← Cocher des fonctionnalités à gauche pour simuler l'impact sur le score.
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — MÉTHODOLOGIE & BIAIS
# ══════════════════════════════════════════════════════════════════════════════
elif page.startswith("🧩"):
    page_header("🧩 Typologies de portails MoF",
                "Clustering k-means · 5 profils · 135 pays · 37 indicateurs binaires",
                badge="Analyse non supervisée · Stage MEF 2026")

    df_sc = df[df["Score Maturité (%)"].notna()].copy()

    PROFIL_COLORS = {
        "Profil A — Portail Numérique Mature":    "#1F3864",
        "Profil B — Portail Transactionnel":       "#2E74B5",
        "Profil C — Portail Communicant":          "#5B9BD5",
        "Profil D — Portail Émergent":             "#ED7D31",
        "Profil E — Portail Minimal":              "#C00000",
    }
    PROFIL_DESC = {
        "Profil A — Portail Numérique Mature":    "Sites complets, services en ligne opérationnels. Principalement Europe OCDE.",
        "Profil B — Portail Transactionnel":       "Formulaires + réseaux sociaux. Lacunes sur open data & API. Amériques / Afrique.",
        "Profil C — Portail Communicant":          "Forte présence web, peu de redevabilité (réclamations, signalement). Asie dominante.",
        "Profil D — Portail Émergent":             "Techniquement fonctionnel, contenu limité. Groupe hétérogène en transition.",
        "Profil E — Portail Minimal":              "Présence basique. Pas de services ni données ouvertes. Pays à faible indice eGov.",
    }

    df_cl = df_sc[df_sc["Profil Numérique"].notna() & (df_sc["Profil Numérique"] != "")].copy() \
        if "Profil Numérique" in df_sc.columns else pd.DataFrame()

    if df_cl.empty:
        st.warning("Colonne 'Profil Numérique' absente du CSV — relancer fix_data.py avec le clustering.")
    else:
        # KPIs par profil
        profils = [p for p in PROFIL_COLORS if p in df_cl["Profil Numérique"].values]
        cols = st.columns(len(profils))
        for col, profil in zip(cols, profils):
            sub = df_cl[df_cl["Profil Numérique"] == profil]
            color = PROFIL_COLORS[profil]
            col.markdown(f"""
<div style="background:{color};border-radius:12px;padding:14px 12px;text-align:center;color:white;">
<div style="font-size:0.75rem;opacity:0.85;margin-bottom:4px;">{profil.split('—')[0].strip()}</div>
<div style="font-size:1.5rem;font-weight:700;">{len(sub)}</div>
<div style="font-size:0.72rem;opacity:0.85;">pays</div>
<div style="font-size:1.1rem;font-weight:600;margin-top:6px;">{sub['Score Maturité (%)'].mean():.1f}%</div>
<div style="font-size:0.7rem;opacity:0.80;">score moyen</div>
</div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

        # Scatter score MEF vs rang EGOV coloré par profil
        st.subheader("📊 Positionnement des profils — Score MEF vs Rang eGov ONU")
        fig_cl = px.scatter(
            df_cl, x="Rang EGOV 2024", y="Score Maturité (%)",
            color="Profil Numérique",
            color_discrete_map=PROFIL_COLORS,
            hover_name="Pays",
            hover_data={"Rang EGOV 2024": True, "Score Maturité (%)": True, "Profil Numérique": False},
            labels={"Rang EGOV 2024": "Rang eGov ONU 2024 (1=meilleur)", "Score Maturité (%)": "Score MEF (%)"},
            height=480,
        )
        # Annoter Maroc
        ma_row = df_cl[df_cl["Pays"] == "Maroc"]
        if not ma_row.empty:
            r = ma_row.iloc[0]
            fig_cl.add_annotation(x=r["Rang EGOV 2024"], y=r["Score Maturité (%)"],
                text="🇲🇦 Maroc", showarrow=True, arrowhead=2,
                arrowcolor="#E8431A", font=dict(color="#E8431A", size=11), ax=35, ay=-25)
        fig_cl.update_layout(
            margin=dict(l=20, r=20, t=20, b=40),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(title="Profil", orientation="v", x=1.01, y=1),
        )
        fig_cl.update_xaxes(showgrid=True, gridcolor="#F0F4FA")
        fig_cl.update_yaxes(showgrid=True, gridcolor="#F0F4FA")
        st.plotly_chart(fig_cl, use_container_width=True)

        # Tableau détaillé par profil sélectionné
        st.subheader("🔍 Explorer un profil")
        profil_sel = st.selectbox("Sélectionner un profil", profils, format_func=lambda x: x)
        st.caption(PROFIL_DESC[profil_sel])

        sub_sel = df_cl[df_cl["Profil Numérique"] == profil_sel].sort_values("Score Maturité (%)", ascending=False)
        cols_show = ["Pays", "Région", "Score Maturité (%)", "Rang EGOV 2024", "data_quality_flag"]
        cols_show = [c for c in cols_show if c in sub_sel.columns]
        st.dataframe(
            sub_sel[cols_show].reset_index(drop=True),
            use_container_width=True, height=min(400, 40 + len(sub_sel) * 35),
        )

        # Cohérence interne
        st.markdown("---")
        st.subheader("⚠️ Audit de cohérence interne")
        st.markdown("""
<div style="background:#FFF8E1;border-radius:12px;padding:16px 20px;border-left:4px solid #ED7D31;">
<b>57 incohérences logiques détectées sur 135 pays</b><br>
<span style="font-size:0.88rem;">Règles vérifiées : si A=O alors B devrait être O. Une violation signale soit un faux positif du scraper, soit un écart réel entre discours et contenu du site.</span>
</div>""", unsafe_allow_html=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        coherence_data = {
            "Règle logique": [
                "Mention open data → Données téléchargeables",
                "SSO citoyen → Espace citoyen",
                "Chatbot → Espace citoyen",
                "API avec documentation → Mention API publique",
                "Espace citoyen → HTTPS",
                "Formulaires en ligne → HTTPS",
                "Facturation électronique → Formulaires en ligne",
            ],
            "Violations": [28, 17, 3, 1, 1, 1, 1],
            "Interprétation": [
                "Biais marketing — mention sans preuve de dataset",
                "Portails SSO nationaux hors périmètre MoF",
                "Chatbots autonomes sans espace citoyen rattaché",
                "Rare — cohérence généralement respectée",
                "Risque sécurité critique (Tunisie)",
                "Risque sécurité critique (Tunisie)",
                "Incohérence isolée (Burundi)",
            ],
        }
        df_coh = pd.DataFrame(coherence_data)
        st.dataframe(df_coh, use_container_width=True, hide_index=True)

elif page.startswith("🔬"):
    page_header("🔬 Méthodologie & travail sur les biais",
                "Architecture du scraper · itérations · validation statistique",
                badge="Démarche scientifique · Stage MEF 2026")

    # ── Architecture ──────────────────────────────────────────────────────────
    st.subheader("⚙️ Architecture du scraper")

    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("""
<div style="background:white;border-radius:14px;padding:20px 24px;border:1px solid #DEE4F0;
     box-shadow:0 2px 8px rgba(0,45,138,0.06);">

<div style="font-weight:700;color:#002D8A;font-size:1rem;margin-bottom:14px;">Pipeline de collecte</div>

<div style="display:flex;flex-direction:column;gap:10px;">

<div style="background:#EBF3FB;border-radius:10px;padding:12px 16px;border-left:4px solid #1C6EA4;">
  <b>1. Source de données</b><br>
  <span style="font-size:0.84rem;color:#444;">Liste ONU EGOV 2024 · 193 pays · URL MoF vérifiées manuellement</span>
</div>

<div style="text-align:center;font-size:1.2rem;color:#BCC8E0;">↓</div>

<div style="background:#EBF3FB;border-radius:10px;padding:12px 16px;border-left:4px solid #1C6EA4;">
  <b>2. Collecte multi-stratégie (par priorité)</b><br>
  <span style="font-size:0.84rem;color:#444;">
    ① Direct HTTP · ② Playwright (SPA/JS) · ③ Wayback Machine (archive)<br>
    + Portails satellites fusionnés (jusqu'à 4 par pays)
  </span>
</div>

<div style="text-align:center;font-size:1.2rem;color:#BCC8E0;">↓</div>

<div style="background:#EBF3FB;border-radius:10px;padding:12px 16px;border-left:4px solid #1C6EA4;">
  <b>3. Extraction des 38 indicateurs</b><br>
  <span style="font-size:0.84rem;color:#444;">
    Parsing HTML/CSS/JS · détection par sélecteurs CSS + regex + heuristiques<br>
    Cache PostgreSQL (30 jours) · parallélisation 8 threads
  </span>
</div>

<div style="text-align:center;font-size:1.2rem;color:#BCC8E0;">↓</div>

<div style="background:#EBF3FB;border-radius:10px;padding:12px 16px;border-left:4px solid #1C6EA4;">
  <b>4. Scoring DIMENSIONS_V8</b><br>
  <span style="font-size:0.84rem;color:#444;">
    5 dimensions · poids calibrés · score normalisé 0–100<br>
    Validation : corrélation de Spearman avec indice eGov ONU 2024
  </span>
</div>

</div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div style="background:white;border-radius:14px;padding:20px 24px;border:1px solid #DEE4F0;
     box-shadow:0 2px 8px rgba(0,45,138,0.06);">
<div style="font-weight:700;color:#002D8A;font-size:1rem;margin-bottom:14px;">Chiffres clés</div>
""", unsafe_allow_html=True)

        stats = [
            ("193", "pays ONU analysés"),
            ("38", "indicateurs mesurés"),
            ("5", "dimensions de scoring"),
            ("8", "threads parallèles"),
            ("~6h", "durée d'un run complet"),
            ("30j", "cache PostgreSQL"),
            ("ρ = 0.8068", "corrélation eGov ONU"),
        ]
        for val, label in stats:
            color = "#E8431A" if "ρ" in val else "#002D8A"
            st.markdown(f"""
<div style="display:flex;justify-content:space-between;align-items:center;
     padding:9px 0;border-bottom:1px solid #F0F3F9;">
  <span style="color:#6B7A99;font-size:0.84rem;">{label}</span>
  <span style="font-weight:800;font-size:1.05rem;color:{color};">{val}</span>
</div>""", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("---")

    # ── Biais identifiés et corrections ───────────────────────────────────────
    st.subheader("🔍 Biais identifiés et corrections apportées")

    BIAIS = [
        {
            "ico": "⚡",
            "titre": "Biais SPA / JavaScript dynamique",
            "symptome": "Les sites en React, Angular ou Vue.js renvoyaient une page HTML vide au scraper HTTP standard. Résultat : tous leurs indicateurs détectés comme absents (faux négatifs).",
            "impact": "Sous-évaluation systématique des pays nordiques et anglophones (UK, Danemark, Finlande…) qui utilisent massivement les frameworks JS modernes.",
            "correction": "Ajout d'un fallback automatique vers Playwright (navigateur headless) quand le contenu HTML < seuil minimal. Le navigateur exécute le JS et expose le DOM complet.",
            "couleur": "#1C6EA4",
        },
        {
            "ico": "📦",
            "titre": "Biais Wayback Machine (sites archivés)",
            "symptome": "Pour les sites inaccessibles (down, bloqués, restructurés), le scraper bascule sur la Wayback Machine. Mais les snapshots d'archive ne rendent pas le JS, et le contenu peut dater de plusieurs mois.",
            "impact": "Scores potentiellement sous-estimés sur des critères dynamiques (chatbot, formulaires, tableaux de bord temps réel) pour les pays concernés.",
            "correction": "Badge ⚠️ Wayback affiché explicitement dans le dashboard. Ces pays sont exclus des comparaisons de performance et signalés dans le classement.",
            "couleur": "#C28011",
        },
        {
            "ico": "🔗",
            "titre": "Biais de périmètre (multi-sites)",
            "symptome": "Dans certains pays (UK, France, Inde…), les fonctions du MoF sont réparties sur plusieurs portails distincts. Scraper un seul site sous-évaluait fortement ces pays.",
            "impact": "Le Royaume-Uni scrappé sur HM Treasury seul = score ~45. Avec HMRC + GOV.UK + Companies House fusionnés = score réel ~78.",
            "correction": "Détection automatique des portails satellites. Fusion des indicateurs par règle 'meilleur score observé' sur l'ensemble des portails du pays. Badge 🔗 Multi-sites dans le classement.",
            "couleur": "#117A65",
        },
        {
            "ico": "⚖️",
            "titre": "Biais de pondération (DIMENSIONS v1→v8)",
            "symptome": "Les premières versions du scoring pondéraient également tous les indicateurs, ce qui favorisait les critères faciles à détecter (HTTPS, réseaux sociaux) et pénalisait les critères de valeur (open data, API, transparence budgétaire).",
            "impact": "Corrélation eGov ONU v1 ≈ 0.30 — le classement MEF ne corrélait pas avec la réalité de la gouvernance numérique mondiale.",
            "correction": "Calibration itérative sur 10 versions : regroupement en 5 dimensions thématiques, ajustement des poids par optimisation de ρ. V9.1 atteint ρ = 0.8068 (seuil de significativité : 0.52).",
            "couleur": "#8E44AD",
        },
        {
            "ico": "🌐",
            "titre": "Biais de langue / encodage",
            "symptome": "Les détecteurs de mots-clés (open data, transparence, loi de finances…) étaient initialement en français uniquement. Les sites arabes, anglais, espagnols étaient systématiquement sous-scorés.",
            "impact": "Les pays arabophones (Arabie Saoudite, Qatar) et hispanophones (Mexique, Argentine) avaient des scores artificiellement bas.",
            "correction": "Extension des dictionnaires à l'arabe, l'anglais, l'espagnol, le portugais pour chaque indicateur textuel. Détection multilingue simultanée.",
            "couleur": "#B0300F",
        },
    ]

    for b in BIAIS:
        with st.expander(f"{b['ico']}  {b['titre']}", expanded=False):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"""<div style="background:#FDECEA;border-radius:10px;padding:14px 16px;">
<div style="font-weight:700;color:#922B21;margin-bottom:6px;font-size:0.85rem;">🔴 Symptôme détecté</div>
<div style="font-size:0.84rem;line-height:1.6;color:#444;">{b['symptome']}</div>
</div>""", unsafe_allow_html=True)
            with c2:
                st.markdown(f"""<div style="background:#FEF9E7;border-radius:10px;padding:14px 16px;">
<div style="font-weight:700;color:#A86908;margin-bottom:6px;font-size:0.85rem;">🟡 Impact sur le classement</div>
<div style="font-size:0.84rem;line-height:1.6;color:#444;">{b['impact']}</div>
</div>""", unsafe_allow_html=True)
            with c3:
                st.markdown(f"""<div style="background:#EAFAF1;border-radius:10px;padding:14px 16px;">
<div style="font-weight:700;color:#0C6630;margin-bottom:6px;font-size:0.85rem;">✅ Correction apportée</div>
<div style="font-size:0.84rem;line-height:1.6;color:#444;">{b['correction']}</div>
</div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Évolution de la corrélation ───────────────────────────────────────────
    st.subheader("📈 Évolution de la corrélation MEF ↔ eGov ONU au fil des versions")

    versions = ["V1\n(base)", "V2\n(multilingue)", "V3\n(SPA)", "V4\n(multi-sites)",
                "V5\n(wayback)", "V6\n(poids)", "V7\n(nordique)", "V8\n(final)", "V9\n(poids opt.)", "V9.1\n(IS natif)", "V9.2\n(corrections)"]
    rho_vals = [0.30, 0.35, 0.40, 0.46, 0.48, 0.52, 0.545, 0.662, 0.718, 0.7213, 0.8068]
    seuil    = 0.52

    fig_rho = go.Figure()
    fig_rho.add_hline(y=seuil, line_dash="dash", line_color="#C28011", line_width=2,
                      annotation_text="Seuil de significativité (0.52)",
                      annotation_position="bottom right",
                      annotation_font_color="#C28011", annotation_font_size=11)
    fig_rho.add_trace(go.Scatter(
        x=versions, y=rho_vals, mode="lines+markers+text",
        text=[f"{v:.3f}" for v in rho_vals],
        textposition=["bottom center"]*7 + ["top center"],
        textfont=dict(size=11, color=["#1A5276"]*6 + ["#E8431A","#E8431A"]),
        line=dict(color="#2874C8", width=3),
        marker=dict(
            size=[10]*6 + [12, 18],
            color=["#2874C8"]*6 + ["#E8431A","#E8431A"],
            line=dict(color="white", width=2),
        ),
        hovertemplate="<b>%{x}</b><br>ρ = %{y:.3f}<extra></extra>",
    ))
    fig_rho.add_annotation(x=versions[-1], y=rho_vals[-1],
        text="✅ DIMENSIONS_V8<br>ρ = 0.8068",
        showarrow=True, arrowhead=2, arrowcolor="#E8431A",
        ax=40, ay=-50, bgcolor="white", bordercolor="#E8431A",
        font=dict(color="#E8431A", size=12, weight=700))
    fig_rho.update_layout(
        height=360, yaxis=dict(range=[0.20, 0.80], title="Corrélation de Spearman (ρ)"),
        xaxis_title="Version du modèle de scoring",
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=60, r=60, t=30, b=50),
    )
    st.plotly_chart(fig_rho, use_container_width=True)

    col_i, col_ii = st.columns(2)
    with col_i:
        st.markdown("""<div class="ok-box">
        ✅ <b>Interprétation</b> : ρ = 0.8068 dépasse le seuil de significativité statistique (0.52),
        ce qui confirme que le Score MEF est <b>cohérent avec la réalité de la gouvernance numérique mondiale</b>
        mesurée par les Nations Unies — sans être redondant (il mesure autre chose : le portail MoF uniquement).
        </div>""", unsafe_allow_html=True)
    with col_ii:
        st.markdown("""<div class="info-box">
        🎯 <b>Objectif pour la suite</b> : atteindre ρ ≥ 0.60 en améliorant la détection JS dynamique
        (Playwright sur plus de sites), en affinant les pondérations par région, et en intégrant
        des données de performance (temps de réponse, disponibilité) comme dimension additionnelle.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Analyse des résidus — décalage structurel eGov vs Score MEF ───────────
    st.subheader("🔍 Analyse des résidus — décalage structurel eGov vs Score MEF")
    st.markdown("""<div class="info-box">
    ℹ️ <b>Limite inhérente à la méthode</b> : l'eGov ONU mesure la maturité numérique de <i>l'ensemble du gouvernement</i>
    d'un pays, tandis que le Score MEF mesure <i>uniquement le portail du ministère des Finances</i>.
    Ces deux périmètres diffèrent structurellement, ce qui crée des "résidus" (écarts) même avec un modèle parfait.
    Cette section identifie et explique les principaux cas.
    </div>""", unsafe_allow_html=True)

    df_resid = df[df["Score Maturité (%)"].notna() & df["Rang EGOV 2024"].notna()].copy()
    n_tot = len(df_resid)
    # Rang MEF calculé
    df_resid = df_resid.sort_values("Score Maturité (%)", ascending=False).reset_index(drop=True)
    df_resid["Rang MEF"] = range(1, len(df_resid)+1)
    df_resid["Rang EGOV 2024"] = df_resid["Rang EGOV 2024"].astype(int)
    # Résidu = rang MEF - rang eGov (positif = sur-performe en MEF vs eGov)
    df_resid["Résidu"] = df_resid["Rang EGOV 2024"] - df_resid["Rang MEF"]

    # Catégories
    seuil_fort = 30
    df_resid["Catégorie"] = "✅ Bien aligné"
    df_resid.loc[df_resid["Résidu"] >  seuil_fort, "Catégorie"] = "🟢 Sur-performance MEF"
    df_resid.loc[df_resid["Résidu"] < -seuil_fort, "Catégorie"] = "🔴 Sous-performance MEF"

    n_over  = (df_resid["Catégorie"]=="🟢 Sur-performance MEF").sum()
    n_under = (df_resid["Catégorie"]=="🔴 Sous-performance MEF").sum()
    n_align = (df_resid["Catégorie"]=="✅ Bien aligné").sum()

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)
    col_kpi1.markdown(kpi("✅ Bien alignés", f"{n_align} pays", "ok",
        tooltip=f"Résidu |rang eGov − rang MEF| ≤ {seuil_fort}"), unsafe_allow_html=True)
    col_kpi2.markdown(kpi("🟢 Sur-performers MEF", f"{n_over} pays", "",
        tooltip="Portail MoF bien meilleur que la maturité numérique globale du pays"), unsafe_allow_html=True)
    col_kpi3.markdown(kpi("🔴 Sous-performers MEF", f"{n_under} pays", "warn",
        tooltip="Portail MoF en retard sur la maturité numérique globale du pays"), unsafe_allow_html=True)

    # Scatter résidu
    color_map = {
        "🟢 Sur-performance MEF": "#27AE60",
        "✅ Bien aligné":          "#2874C8",
        "🔴 Sous-performance MEF": "#E8431A",
    }
    fig_res = px.scatter(
        df_resid, x="Rang EGOV 2024", y="Score Maturité (%)",
        color="Catégorie", color_discrete_map=color_map,
        hover_name="Pays",
        hover_data={"Rang MEF": True, "Rang EGOV 2024": True, "Résidu": True, "Catégorie": False},
        labels={"Rang EGOV 2024": "Rang eGov ONU 2024 (1=meilleur)", "Score Maturité (%)": "Score MEF (0–100)"},
        height=420,
    )
    # Ligne de tendance manuelle (régression de Spearman → approx linéaire)
    import numpy as _np2
    _x = df_resid["Rang EGOV 2024"].values
    _y = df_resid["Score Maturité (%)"].values
    _z = _np2.polyfit(_x, _y, 1)
    _xr = _np2.linspace(_x.min(), _x.max(), 100)
    fig_res.add_trace(go.Scatter(x=_xr, y=_np2.polyval(_z, _xr),
        mode="lines", line=dict(color="#BCC8E0", dash="dot", width=1.5),
        name="Tendance", showlegend=False))
    # Annoter Maroc
    ma_res = df_resid[df_resid["Pays"]=="Maroc"].iloc[0]
    fig_res.add_annotation(x=ma_res["Rang EGOV 2024"], y=ma_res["Score Maturité (%)"],
        text="🇲🇦 Maroc", showarrow=True, arrowhead=2, arrowcolor="#E8431A",
        font=dict(color="#E8431A", size=11), ax=30, ay=-25)
    fig_res.update_layout(margin=dict(l=20, r=20, t=20, b=40),
        legend=dict(orientation="h", y=-0.18))
    st.plotly_chart(fig_res, use_container_width=True)

    col_ov, col_un = st.columns(2)
    with col_ov:
        st.markdown("**🟢 Principaux sur-performers MEF** (portail MoF > maturité globale)")
        top_over = df_resid[df_resid["Catégorie"]=="🟢 Sur-performance MEF"].nlargest(8, "Résidu")[
            ["Pays","Rang EGOV 2024","Rang MEF","Résidu"]].copy()
        top_over.columns = ["Pays","Rang eGov","Rang MEF","Écart"]
        def _hl_ma(row): return ["background-color:#FEF3E8;font-weight:bold"]*len(row) if row["Pays"]=="Maroc" else [""]*len(row)
        st.dataframe(top_over.style.apply(_hl_ma, axis=1), hide_index=True, use_container_width=True)
        st.caption("Écart = Rang eGov − Rang MEF · positif = MEF mieux classé que eGov")

    with col_un:
        st.markdown("**🔴 Principaux sous-performers MEF** (portail MoF < maturité globale)")
        top_under = df_resid[df_resid["Catégorie"]=="🔴 Sous-performance MEF"].nsmallest(8, "Résidu")[
            ["Pays","Rang EGOV 2024","Rang MEF","Résidu"]].copy()
        top_under.columns = ["Pays","Rang eGov","Rang MEF","Écart"]
        st.dataframe(top_under, hide_index=True, use_container_width=True)
        st.caption("Causes : site SPA/JS, WAF, portail satellite non fusionné, MoF délégué")

    st.markdown("""<div class="warn-box" style="margin-top:12px;">
    <b>💡 Pourquoi ces résidus sont attendus — et non des erreurs :</b><br>
    <b>Sur-performance MEF</b> (🟢) : certains pays investissent spécifiquement dans leur portail MoF
    (transparence budgétaire, dette publique, open data fiscal) sans avoir une maturité numérique globale élevée.
    C'est le cas du Maroc, du Qatar, du Chili, du Kazakhstan.<br><br>
    <b>Sous-performance MEF</b> (🔴) : certains pays ont un bon score eGov parce que leurs <i>autres</i>
    ministères ou services en ligne sont excellents, mais le MoF reste en retard — ou bien son site
    est une SPA React non scrappable (Thaïlande, Malaisie exclus du scoring).<br><br>
    Ces deux catégories représentent <b>{pct:.0f}%</b> du dataset et sont documentées dans la méthodologie.
    Elles n'affectent pas la validité de ρ = 0.787 (corrélation globale significative).
    </div>""".format(pct=(n_over+n_under)/n_tot*100), unsafe_allow_html=True)

    st.markdown("---")

    # ── Analyses statistiques avancées ────────────────────────────────────────
    st.subheader("📐 Analyses statistiques avancées")

    tab_reg, tab_anova, tab_sens = st.tabs(["📊 Régression — importance des indicateurs",
                                             "🌍 ANOVA — écarts entre régions",
                                             "⚖️ Sensibilité des poids"])

    df_stat = df[df["Score Maturité (%)"].notna()].copy()
    score_actuel = float(maroc.get("Score Maturité (%)") or 0)
    for col in BOOL_COLS:
        if col in df_stat.columns:
            df_stat[col] = df_stat[col].map({True: 1, False: 0, None: 0})

    # ── TAB 1 : Régression ────────────────────────────────────────────────────
    with tab_reg:
        st.markdown("""**Quels indicateurs prédisent le mieux un Score MEF élevé ?**
        Régression linéaire — coefficient de chaque indicateur sur le Score de Maturité.""")
        import numpy as _np_s
        from scipy import stats as _scipy_stats

        X_cols = [c for c in BOOL_COLS if c in df_stat.columns]
        X = df_stat[X_cols].fillna(0).values
        y = df_stat["Score Maturité (%)"].values

        # Régression simple indicateur par indicateur (corrélation partielle)
        coefs = []
        for i, col in enumerate(X_cols):
            xi = X[:, i]
            if xi.std() == 0:
                continue
            slope, intercept, r, p, se = _scipy_stats.linregress(xi, y)
            coefs.append({"Indicateur": col, "Coefficient": round(slope, 2),
                          "r²": round(r**2, 3), "p-value": round(p, 4)})

        coef_df = pd.DataFrame(coefs).sort_values("Coefficient", ascending=True)
        coef_df_top = coef_df.nlargest(15, "Coefficient").sort_values("Coefficient")

        fig_reg = go.Figure(go.Bar(
            x=coef_df_top["Coefficient"], y=coef_df_top["Indicateur"],
            orientation="h",
            marker=dict(
                color=coef_df_top["Coefficient"],
                colorscale=[[0,"#AED6F1"],[1,"#002D8A"]],
                showscale=False,
            ),
            text=coef_df_top["Coefficient"].apply(lambda v: f"+{v:.1f} pts"),
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>+%{x:.1f} pts de score en moyenne<extra></extra>",
        ))
        fig_reg.update_layout(
            height=420, plot_bgcolor="white", paper_bgcolor="white",
            xaxis=dict(title="Impact moyen sur le Score MEF (pts)", range=[0, coef_df_top["Coefficient"].max()*1.3]),
            margin=dict(l=200, r=80, t=20, b=40),
        )
        st.plotly_chart(fig_reg, use_container_width=True)
        st.markdown("""<div class="info-box">
        📖 <b>Lecture</b> : un coefficient de +15 signifie que les pays ayant cet indicateur ont en moyenne
        15 points de plus que ceux qui ne l'ont pas. Ce n'est pas une causalité — c'est une corrélation
        partielle qui reflète la co-occurrence des fonctionnalités avancées.
        </div>""", unsafe_allow_html=True)

        # Top 5 tableau
        st.markdown("**Top 5 indicateurs les plus discriminants :**")
        top5 = coef_df.nlargest(5, "Coefficient")[["Indicateur","Coefficient","r²","p-value"]]
        top5.columns = ["Indicateur","Impact moyen (pts)","R² partiel","p-value"]
        st.dataframe(top5, hide_index=True, use_container_width=True)

    # ── TAB 2 : ANOVA ─────────────────────────────────────────────────────────
    with tab_anova:
        st.markdown("""**Les écarts de score entre régions sont-ils statistiquement significatifs ?**
        Test de Kruskal-Wallis (non-paramétrique, robuste aux outliers).""")
        from scipy.stats import kruskal as _kruskal

        regions = df_stat["Région"].dropna().unique()
        region_scores = {r: df_stat[df_stat["Région"]==r]["Score Maturité (%)"].dropna().values
                         for r in regions}
        region_scores = {r: v for r, v in region_scores.items() if len(v) >= 3}

        # Stats par région
        reg_stats = []
        for r, vals in region_scores.items():
            reg_stats.append({
                "Région": r, "N pays": len(vals),
                "Score médian": round(float(_np_s.median(vals)), 1),
                "Score moyen": round(float(_np_s.mean(vals)), 1),
                "Min": round(float(vals.min()), 1),
                "Max": round(float(vals.max()), 1),
            })
        reg_df = pd.DataFrame(reg_stats).sort_values("Score médian", ascending=False)

        # Test Kruskal-Wallis
        stat_kw, p_kw = _kruskal(*region_scores.values())

        col_kw1, col_kw2 = st.columns([3, 2])
        with col_kw1:
            fig_box = go.Figure()
            colors_reg = {"Europe":"#002D8A","Asie":"#E8431A","Amériques":"#27AE60",
                          "Afrique":"#E67E22","Océanie":"#8E44AD","MENA":"#117A65"}
            for r in reg_df["Région"]:
                vals = region_scores.get(r, [])
                fig_box.add_trace(go.Box(
                    y=vals, name=r,
                    marker_color=colors_reg.get(r, "#BCC8E0"),
                    boxmean=True,
                ))
            fig_box.update_layout(
                height=380, yaxis_title="Score MEF (%)",
                plot_bgcolor="white", paper_bgcolor="white",
                margin=dict(l=40, r=20, t=20, b=60),
                showlegend=False,
            )
            st.plotly_chart(fig_box, use_container_width=True)

        with col_kw2:
            st.dataframe(reg_df[["Région","N pays","Score médian","Score moyen"]],
                         hide_index=True, use_container_width=True)
            sig = p_kw < 0.05
            st.markdown(f"""<div class="{'ok-box' if sig else 'warn-box'}">
            <b>Kruskal-Wallis H = {stat_kw:.1f}</b><br>
            p-value = {p_kw:.2e}<br><br>
            {'✅ <b>Résultat significatif</b> (p < 0.05) : les écarts entre régions ne sont pas dus au hasard. Les pays européens ont structurellement de meilleurs portails MoF.' if sig else '⚠️ Résultat non significatif.'}
            </div>""", unsafe_allow_html=True)

    # ── TAB 3 : Sensibilité ───────────────────────────────────────────────────
    with tab_sens:
        st.markdown("""**Si on modifie les poids des dimensions de ±10%, le rang du Maroc change-t-il ?**
        Analyse de robustesse du modèle de scoring.""")

        DIMS_BASE = {"Fondamentaux web": 35, "Transparence": 15,
                     "Services": 20, "Données ouvertes": 25, "Ouverture institutionnelle": 5}

        DIMS_INDICS = {
            "Fondamentaux web": ["HTTPS","Responsive","Moteur de recherche","Sitemap.xml",
                                  "Politique confidentialité","Déclaration accessibilité","Bandeau cookies"],
            "Transparence": ["Mention rapport annuel","Section actualités","Section marchés publics",
                              "Documents PDF","Mention transparence"],
            "Services": ["Espace citoyen","Formulaires en ligne","Mécanisme de réclamations",
                         "Facturation électronique","Chatbot"],
            "Données ouvertes": ["Mention open data","Données téléchargeables","Mention API publique",
                                  "Tableau de bord temps réel"],
            "Ouverture institutionnelle": ["Liberté d'accès à l'info","Abonnement newsletter",
                                            "Facebook","YouTube","Twitter/X"],
        }

        def score_with_weights(row, weights):
            total_w, total_p = 0.0, 0.0
            for dim, dp in weights.items():
                inds = DIMS_INDICS.get(dim, [])
                inds_ok = [c for c in inds if c in row.index]
                if not inds_ok: continue
                pts = sum(1 for c in inds_ok if row.get(c) == 1)
                ds = pts / len(inds_ok) * 100 if inds_ok else 0
                total_w += ds * dp; total_p += dp
            return total_w / total_p if total_p else 0

        # Calcul du rang Maroc avec variations de ±10% sur chaque dimension
        df_w = df_stat.copy()
        maroc_w = df_w[df_w["Pays"] == "Maroc"].iloc[0]

        sens_rows = []
        for dim_var in DIMS_BASE:
            for delta in [-10, -5, 0, +5, +10]:
                new_w = dict(DIMS_BASE)
                new_w[dim_var] = max(1, new_w[dim_var] + delta)
                scores = df_w.apply(lambda r: score_with_weights(r, new_w), axis=1)
                rang_ma = int((scores > score_with_weights(maroc_w, new_w)).sum()) + 1
                sens_rows.append({"Dimension": dim_var, "Δ poids": delta,
                                   "Rang Maroc": rang_ma,
                                   "Poids": new_w[dim_var]})

        sens_df = pd.DataFrame(sens_rows)

        fig_sens = go.Figure()
        colors_dims = ["#002D8A","#27AE60","#E8431A","#E67E22","#8E44AD"]
        for i, dim in enumerate(DIMS_BASE):
            sub = sens_df[sens_df["Dimension"] == dim]
            fig_sens.add_trace(go.Scatter(
                x=sub["Δ poids"], y=sub["Rang Maroc"],
                mode="lines+markers", name=dim,
                line=dict(color=colors_dims[i], width=2),
                marker=dict(size=7),
                hovertemplate=f"<b>{dim}</b><br>Δ poids: %{{x}}<br>Rang Maroc: #%{{y}}<extra></extra>",
            ))
        # Rang actuel
        rang_actuel_ma = int((df_stat["Score Maturité (%)"] > score_actuel).sum()) + 1
        fig_sens.add_hline(y=rang_actuel_ma, line_dash="dot", line_color="#BCC8E0",
                           annotation_text=f"Rang actuel #{rang_actuel_ma}",
                           annotation_position="right")
        fig_sens.update_layout(
            height=400, yaxis=dict(title="Rang Maroc (plus bas = meilleur)", autorange="reversed"),
            xaxis=dict(title="Variation du poids de la dimension (pts)"),
            plot_bgcolor="white", paper_bgcolor="white",
            margin=dict(l=60, r=100, t=20, b=60),
            legend=dict(orientation="h", y=-0.25, font=dict(size=10)),
        )
        st.plotly_chart(fig_sens, use_container_width=True)
        st.markdown("""<div class="ok-box">
        ✅ <b>Interprétation</b> : si les lignes restent proches quelle que soit la variation de poids,
        le modèle est <b>robuste</b> — le rang du Maroc ne dépend pas d'un choix de pondération arbitraire.
        Une ligne très pentue signale une dimension sensible à surveiller.
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # ── Démo live ─────────────────────────────────────────────────────────────
    st.subheader("🚀 Démo — lancer le scraper sur un pays")
    st.markdown("""<div class="warn-box">
    ⚠️ <b>Mode démo uniquement</b> : scrape 1 seul pays, résultat affiché en direct dans le terminal.
    Durée estimée : 30–90 secondes selon le site.
    </div>""", unsafe_allow_html=True)

    DEMO_PAYS = {
        "🇹🇳 Tunisie — finances.gov.tn":       "Tunisie",
        "🇩🇿 Algérie — mf.gov.dz":             "Algérie",
        "🇸🇳 Sénégal — finances.gouv.sn":      "Sénégal",
        "🇲🇦 Maroc — finances.gov.ma":         "Maroc",
        "🇦🇪 Émirats — mof.gov.ae":            "Émirats",
    }
    choix = st.selectbox("Choisir un pays à scraper en live", list(DEMO_PAYS.keys()))
    pays_demo = DEMO_PAYS[choix]

    if st.button(f"▶️ Lancer le scraper sur {pays_demo}", type="primary"):
        import subprocess
        base_dir     = "/Users/ghita/Downloads/Stage benchmarking"
        scraper_path = os.path.join(base_dir, "code/scraper.py")
        py_bin       = "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/bin/python3"
        with st.spinner(f"Scraping de {pays_demo} en cours… (30–90 sec)"):
            try:
                result = subprocess.run(
                    [py_bin, scraper_path, "--demo-pays", pays_demo],
                    capture_output=True, text=True, timeout=120,
                    cwd=base_dir
                )
                output = (result.stdout + result.stderr).strip()
                if output:
                    st.code(output[-3000:], language="text")
                else:
                    st.info("Le scraper ne supporte pas encore --demo-pays. Voir le terminal pour les logs du run en cours.")
            except subprocess.TimeoutExpired:
                st.error("Timeout (120s) — site lent. Essayer un autre pays.")
            except Exception as e:
                st.error(f"Erreur : {e}")
