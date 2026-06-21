"""
TenderWin — Interface Web Streamlit.

Une interface élégante pour présenter le système multi-agents
de réponse automatique aux appels d'offres.

Lancement :
    streamlit run app.py
"""

import streamlit as st
import tempfile
import os
from main import process_rfp_files


# ──────────────────────────────────────────────────────────────
# Configuration de la page
# ──────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="TenderWin — Automatisateur RFP",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────────────────────
# Styles CSS personnalisés
# ──────────────────────────────────────────────────────────────

st.markdown("""
<style>
    /* ── Import Google Font ── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Base ── */
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    /* ── Masquer éléments par défaut de Streamlit ── */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* ── Fond principal ── */
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #1a1a3e 40%, #24243e 100%);
    }

    /* ── Titre hero ── */
    .hero-title {
        text-align: center;
        padding: 2rem 0 0.5rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: 3rem;
        font-weight: 900;
        letter-spacing: -1px;
        line-height: 1.1;
    }

    .hero-subtitle {
        text-align: center;
        color: #8b8fad;
        font-size: 1.15rem;
        font-weight: 400;
        margin-bottom: 2rem;
        letter-spacing: 0.3px;
    }

    /* ── Cartes glassmorphism ── */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.8rem;
        margin-bottom: 1.2rem;
        transition: all 0.3s ease;
    }
    .glass-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
        transform: translateY(-2px);
    }

    /* ── Agent cards ── */
    .agent-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 14px;
        padding: 1.4rem;
        text-align: center;
        transition: all 0.3s ease;
        height: 100%;
    }
    .agent-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    .agent-icon {
        font-size: 2.4rem;
        margin-bottom: 0.5rem;
    }
    .agent-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #e0e0ff;
        margin-bottom: 0.4rem;
    }
    .agent-role {
        font-size: 0.85rem;
        color: #7b7f9e;
        line-height: 1.5;
    }

    /* ── Badge de statut ── */
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .status-ready {
        background: rgba(102, 126, 234, 0.15);
        color: #667eea;
        border: 1px solid rgba(102, 126, 234, 0.3);
    }

    /* ── Séparateur ── */
    .divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102,126,234,0.3), transparent);
        margin: 2rem 0;
    }

    /* ── Résultat / Proposition ── */
    .result-header {
        font-size: 1.5rem;
        font-weight: 700;
        color: #e0e0ff;
        margin-bottom: 0.5rem;
    }

    /* ── Steps pipeline ── */
    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 10px;
        margin-bottom: 8px;
        font-size: 0.92rem;
    }
    .step-active {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.2);
        color: #c0c4f0;
    }
    .step-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.8rem;
        flex-shrink: 0;
    }

    /* ── Upload area ── */
    [data-testid="stFileUploader"] {
        background: rgba(255,255,255,0.02);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 14px;
        padding: 1rem;
        transition: all 0.3s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(102, 126, 234, 0.6);
        background: rgba(102, 126, 234, 0.04);
    }

    /* ── Bouton principal ── */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.8rem 2rem !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.3px !important;
        width: 100% !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5) !important;
    }
    .stButton > button:active {
        transform: translateY(0) !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00c9a7 0%, #00b4d8 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.7rem 1.5rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(0, 201, 167, 0.25) !important;
    }
    .stDownloadButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(0, 201, 167, 0.4) !important;
    }

    /* ── Tabs ── */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(255,255,255,0.03);
        border-radius: 12px;
        padding: 4px;
        gap: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 10px;
        color: #8b8fad;
        font-weight: 600;
        padding: 8px 20px;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
    }

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {
        background: rgba(15, 12, 41, 0.95);
        border-right: 1px solid rgba(255,255,255,0.06);
    }

    /* ── Spinner ── */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }

    /* ── Success / Warning / Error alerts ── */
    .stSuccess {
        background: rgba(0, 201, 167, 0.1) !important;
        border-color: rgba(0, 201, 167, 0.3) !important;
        border-radius: 12px !important;
    }
    .stWarning {
        background: rgba(255, 193, 7, 0.1) !important;
        border-color: rgba(255, 193, 7, 0.3) !important;
        border-radius: 12px !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# Sidebar — Infos projet
# ──────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1.5rem 0;">
        <div style="font-size: 3rem; margin-bottom: 0.5rem;">🏆</div>
        <div style="font-size: 1.3rem; font-weight: 800; color: #e0e0ff;
                    letter-spacing: -0.5px;">TenderWin</div>
        <div style="font-size: 0.8rem; color: #7b7f9e; margin-top: 4px;">
            Système Multi-Agents v1.0</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("#### 🔧 Architecture")
    st.markdown("""
    <div class="pipeline-step step-active">
        <div class="step-number">1</div>
        <div><strong>KnowledgeAgent</strong><br/>
        <span style="font-size:0.8rem; color:#7b7f9e;">Analyse & Collecte</span></div>
    </div>
    <div class="pipeline-step step-active">
        <div class="step-number">2</div>
        <div><strong>WriterAgent</strong><br/>
        <span style="font-size:0.8rem; color:#7b7f9e;">Rédaction Markdown</span></div>
    </div>
    <div class="pipeline-step step-active">
        <div class="step-number">3</div>
        <div><strong>AuditorAgent</strong><br/>
        <span style="font-size:0.8rem; color:#7b7f9e;">Vérification & Audit</span></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown("#### 📊 Technologies")
    st.markdown("""
    - 🤖 **LLM** : gemini-2.5-flash
    - 🧩 **Framework** : google-genai
    - 🐍 **Backend** : Python
    - 🎨 **Frontend** : Streamlit
    """)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)

    st.markdown(
        '<div style="text-align:center; color:#555; font-size:0.75rem; padding:1rem 0;">'
        "Projet PFE — 2026"
        "</div>",
        unsafe_allow_html=True,
    )


# ──────────────────────────────────────────────────────────────
# Header principal
# ──────────────────────────────────────────────────────────────

st.markdown('<h1 class="hero-title">🏆 TenderWin</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-subtitle">'
    "Automatisateur Intelligent de Réponses aux Appels d'Offres — "
    "Propulsé par un Système Multi-Agents"
    "</p>",
    unsafe_allow_html=True,
)

# ── Présentation des 3 agents ──
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">📋</div>
        <div class="agent-name">KnowledgeAgent</div>
        <div class="agent-role">Analyse le RFP et collecte les données internes
        (profil entreprise, catalogue tarifaire)</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">✍️</div>
        <div class="agent-name">WriterAgent</div>
        <div class="agent-role">Rédige une proposition commerciale professionnelle
        et structurée en Markdown</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="agent-card">
        <div class="agent-icon">🔍</div>
        <div class="agent-name">AuditorAgent</div>
        <div class="agent-role">Audite la conformité : vérifie les prix,
        certifications et structure</div>
    </div>
    """, unsafe_allow_html=True)


st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# Zone d'upload et lancement
# ──────────────────────────────────────────────────────────────

st.markdown(
    '<div class="result-header">📄 Importez votre Appel d\'Offres</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<p style="color:#7b7f9e; margin-bottom:1rem;">'
    "Glissez-déposez ou sélectionnez le fichier texte (.txt) de l'appel d'offres "
    "que vous souhaitez traiter."
    "</p>",
    unsafe_allow_html=True,
)

uploaded_files = st.file_uploader(
    "Sélectionnez les fichiers RFP",
    type=["txt", "pdf", "docx"],
    accept_multiple_files=True,
    help="Formats acceptés : fichiers texte (.txt), PDF (.pdf), Word (.docx).",
    label_visibility="collapsed",
)

# Prévisualisation des fichiers uploadés
if uploaded_files:
    # On n'affiche un aperçu complet que pour le premier fichier s'il est au format texte
    first_file = uploaded_files[0]
    is_text = first_file.name.endswith(".txt")
    
    if is_text:
        try:
            rfp_content = first_file.getvalue().decode("utf-8")
            with st.expander(f"👁️ Aperçu de {first_file.name}", expanded=False):
                st.markdown(
                    f'<div class="glass-card" style="max-height:300px; overflow-y:auto;">'
                    f"<pre style='color:#c0c4f0; white-space:pre-wrap; font-size:0.88rem;'>"
                    f"{rfp_content}"
                    f"</pre></div>",
                    unsafe_allow_html=True,
                )
        except Exception:
            pass

    st.markdown(
        f'<div style="display:flex; justify-content:space-between; margin:0.5rem 0 1.5rem 0;">'
        f'<span class="status-badge status-ready">📎 {len(uploaded_files)} fichier(s) sélectionné(s)</span>'
        f'<span class="status-badge status-ready">📏 Taille totale : {sum(f.size for f in uploaded_files) / 1024:.1f} KB</span>'
        f"</div>",
        unsafe_allow_html=True,
    )

# ── Bouton de lancement ──
st.markdown("")  # Spacing
generate_clicked = st.button("🚀 Générer la Proposition Commerciale", use_container_width=True)


# ──────────────────────────────────────────────────────────────
# Exécution du pipeline
# ──────────────────────────────────────────────────────────────

if generate_clicked:
    if not uploaded_files:
        st.warning(
            "⚠️ **Aucun fichier importé.** "
            "Veuillez d'abord sélectionner un ou plusieurs fichiers (TXT, PDF, DOCX) ci-dessus.",
            icon="⚠️",
        )
    else:
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # Création des fichiers temporaires
        temp_dir = tempfile.mkdtemp()
        temp_paths = []
        try:
            for uf in uploaded_files:
                path = os.path.join(temp_dir, uf.name)
                with open(path, "wb") as f:
                    f.write(uf.getvalue())
                temp_paths.append(path)

            with st.spinner("🤖 Les agents analysent les documents... Cela peut prendre quelques minutes."):
                try:
                    results = process_rfp_files(temp_paths)
                except Exception as e:
                    st.error(f"❌ **Erreur lors du traitement :** {e}", icon="🚨")
                    st.stop()
        finally:
            # Nettoyage des fichiers temporaires locaux
            for p in temp_paths:
                if os.path.exists(p):
                    os.remove(p)
            if os.path.exists(temp_dir):
                os.rmdir(temp_dir)

        # ── Succès ──
        st.success("✅ **Proposition générée avec succès !**", icon="🎉")

        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        # ── Affichage des résultats dans des onglets ──
        st.markdown(
            '<div class="result-header">📑 Résultats</div>',
            unsafe_allow_html=True,
        )

        tab_proposition, tab_audit, tab_analyse = st.tabs([
            "📝 Proposition Commerciale",
            "🔍 Rapport d'Audit",
            "📋 Rapport d'Analyse",
        ])

        proposition_md = str(results["proposition"])
        audit_md = str(results["audit"])
        analyse_md = str(results["analyse"])

        with tab_proposition:
            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True,
            )
            st.markdown(proposition_md)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_audit:
            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True,
            )
            st.markdown(audit_md)
            st.markdown("</div>", unsafe_allow_html=True)

        with tab_analyse:
            st.markdown(
                '<div class="glass-card">',
                unsafe_allow_html=True,
            )
            st.markdown(analyse_md)
            st.markdown("</div>", unsafe_allow_html=True)

        # ── Boutons de téléchargement ──
        st.markdown('<hr class="divider">', unsafe_allow_html=True)

        st.markdown(
            '<div class="result-header">💾 Télécharger les Fichiers</div>',
            unsafe_allow_html=True,
        )

        dl_col1, dl_col2, dl_col3 = st.columns(3)

        with dl_col1:
            st.download_button(
                label="📝 Proposition Finale",
                data=proposition_md,
                file_name="proposition_finale.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with dl_col2:
            st.download_button(
                label="🔍 Rapport d'Audit",
                data=audit_md,
                file_name="rapport_audit.md",
                mime="text/markdown",
                use_container_width=True,
            )

        with dl_col3:
            st.download_button(
                label="📋 Rapport d'Analyse",
                data=analyse_md,
                file_name="rapport_analyse.md",
                mime="text/markdown",
                use_container_width=True,
            )
