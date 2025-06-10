import streamlit as st
import tempfile
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def create_bar_chart(filename, title="Conversion par date", date_format="%d-%m-%Y"):
    with open(filename, 'r', encoding='utf-8') as f:
        data_json = json.load(f)
    
    if not data_json:
        raise ValueError("Le fichier JSON est vide ou ne contient pas de données valides")
    
    # Conversion des clés string en objets datetime et extraction des valeurs
    dates = []
    values = []
    total = 0    
    for date_str, value in data_json.items():
        try:
            # Convertir la chaîne de caractères en objet datetime
            date_obj = datetime.strptime(date_str, date_format)
            dates.append(date_obj)
            values.append(int(value))  # S'assurer que la valeur est un entier
            total+=int(value)
        except ValueError as e:
            continue
    
    # Vérification qu'il reste des données après le traitement
    if not dates:
        raise ValueError("Aucune date valide trouvée dans le fichier")
    
    # Trier les données par date
    sorted_data = sorted(zip(dates, values))
    dates, values = zip(*sorted_data)
    
    # Création du graphique
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Graphique en barres
    bars = ax.bar(dates, values, alpha=0.7, color='skyblue', edgecolor='navy', linewidth=1)
    
    # Personnalisation du graphique
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel('Date', fontsize=12)
    #ax.set_ylabel('Valeurs', fontsize=12)
    ax.set_facecolor('#f0f2f6')
    fig.patch.set_facecolor('#f0f2f6')  
    # Rotation des étiquettes de dates pour une meilleure lisibilité
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    
    # Grille pour améliorer la lisibilité
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=max(10, len(dates)//10)))
    
    # Rotation des étiquettes de dates pour une meilleure lisibilité
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')
    ax.grid(True, alpha=0.3, axis='y', linestyle='--')
    
    # Ajout des valeurs au-dessus des barres
    for bar, value in zip(bars, values):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(values)*0.01,
               f'{value}', ha='center', va='bottom', fontsize=10)
    
    # Ajustement automatique de la mise en page
    plt.tight_layout()
    
    return fig, total

def incrementer(chemin_fichier):
    date_aujourd_hui = datetime.now().strftime("%d-%m-%Y")
    data = {}
    if os.path.exists(chemin_fichier):
        try:
            with open(chemin_fichier, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            # Erreur lors de la lecture du fichier {chemin_fichier}, création d'un nouveau dictionnaire
            data = {}
    
    # Ajouter +1 à la date du jour (ou initialiser à 1 si elle n'existe pas)
    if date_aujourd_hui in data:
        data[date_aujourd_hui] += 1
    else:
        data[date_aujourd_hui] = 1
    
    # Sauvegarder le fichier
    try:
        with open(chemin_fichier, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        pass
        
# Configuration de la page en mode wide pour utiliser toute la largeur
def convert_file(file_path, original_filename):
    """
    Fonction de conversion du fichier PDF
    """
    try:
        # Importer la fonction de conversion
        from convertitPV2 import convertit as convert_pdf_to_excel
        
        # Créer le nom du fichier de sortie basé sur le nom original
        original_name = Path(original_filename).stem
        output_path = str(Path(file_path).parent / f"{original_name}.xlsx")
        
        # Appeler la fonction de conversion
        df=convert_pdf_to_excel(file_path)
        
        # Vérifier si le fichier de sortie existe et le renommer si nécessaire
        default_output = str(Path(file_path).with_suffix('.xlsx'))
        if os.path.exists(default_output) and default_output != output_path:
            os.rename(default_output, output_path)
        
        return True, "Conversion réussie !", output_path, df
        
    except ImportError:
        return False, "Erreur : Le module 'convertitPV2' n'est pas disponible. Assurez-vous qu'il est dans le même répertoire.", None, None
    except Exception as e:
        error_msg = f"Erreur lors de la conversion : {str(e)}"
        # Ajouter plus de détails sur l'erreur si nécessaire
        if hasattr(e, '__traceback__'):
            error_msg += f"\nDétails : {traceback.format_exc()}"
        return False, error_msg, None, None

def check_credentials():
    """Vérifie les identifiants utilisateur"""
    # Dictionnaire des utilisateurs (à personnaliser selon vos besoins)
    users = {
        "fds": "UPPvb2026",
        "vincent": "LoveBB98*2"
    }
    
    def credentials_entered():
        if (st.session_state["username"] in users and 
            users[st.session_state["username"]] == st.session_state["password"]):
            st.session_state["authenticated"] = True
            st.session_state["current_user"] = st.session_state["username"]
            # Nettoyer les champs de connexion
            del st.session_state["username"]
            del st.session_state["password"]
        else:
            st.session_state["authenticated"] = False

    if "authenticated" not in st.session_state:
        # Première connexion
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2E86AB, #A23B72);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        ">
            <h1 style="margin: 0; font-size: 2.5rem;">Convertisseur de PV</h1>
            <h1 style="margin: 0; font-size: 2.5rem;">🔐 Connexion requise</h1>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            
            st.subheader("🚀 Accès à l'application")
            st.text_input("👤 Nom d'utilisateur", key="username", placeholder="Entrez votre nom d'utilisateur")
            st.text_input("🔑 Mot de passe", type="password", key="password", placeholder="Entrez votre mot de passe")
            st.button("🔓 Se connecter", on_click=credentials_entered, type="primary", use_container_width=True)
            
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Informations d'aide
            with st.expander("ℹ️ Informations de connexion"):
                st.info("""
                Contactez l'administrateur pour obtenir vos identifiants.

                *vincent.boudet@umontpellier.fr*
                """)
        
        return False
        
    elif not st.session_state["authenticated"]:
        # Identifiants incorrects
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #2E86AB, #A23B72);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 8px rgba(0,0,0,0.15);
        ">
            <h1 style="margin: 0; font-size: 2.5rem;">🔐 Connexion requise</h1>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Convertisseur PV - FDS</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            #st.markdown("""
            #<div style="
            #    background: white;
            #    padding: 2rem;
            #    border-radius: 15px;
            #    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            #    border: 1px solid #E1E8ED;
            #">
            #""", unsafe_allow_html=True)            
            st.subheader("🚀 Accès à l'application")
            st.text_input("👤 Nom d'utilisateur", key="username", placeholder="Entrez votre nom d'utilisateur")
            st.text_input("🔑 Mot de passe", type="password", key="password", placeholder="Entrez votre mot de passe")
            st.button("🔓 Se connecter", on_click=credentials_entered, type="primary", use_container_width=True)
            st.error("❌ Identifiants incorrects. Veuillez réessayer.")
            
            #st.markdown("</div>", unsafe_allow_html=True)
            
            # Informations d'aide
            with st.expander("ℹ️ Informations de connexion"):
                st.info("""
                Contactez l'administrateur pour obtenir vos identifiants.

                ***vincent.boudet@um-------ier.fr***
                                        """)
        
        return False
    else:
        # Utilisateur authentifié
        return True

st.set_page_config(
    page_title="Convertisseur PV - FDS",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé pour un thème professionnel
def apply_custom_theme():
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Variables CSS pour le thème */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --accent-color: #F18F01;
        --success-color: #C73E1D;
        --background-color: #F8F9FA;
        --surface-color: #FFFFFF;
        --text-primary: #2C3E50;
        --text-secondary: #7F8C8D;
        --border-color: #E1E8ED;
        --shadow: 0 2px 4px rgba(0,0,0,0.1);
        --shadow-hover: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    /* Style général de l'application */
    .main {
        padding: 0rem 0rem;
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: var(--surface-color);
        border-right: 2px solid var(--border-color);
    }

    /* Header personnalisé */
    .main-header {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        color: white;
        padding: 0rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow-hover);
        text-align: center;
    }
    
    .main-header h1 {
        margin: 0;
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        margin: 0.5rem 0 0 0;
        opacity: 0.9;
        font-size: 1.1rem;
    }
    
    /* Zone d'upload dans la sidebar */
    .upload-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        color: white;
        text-align: center;
    }
    
    .upload-section h3 {
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
        font-weight: 600;
    }
    
    .upload-section p {
        margin: 0;
        opacity: 0.8;
        font-size: 0.9rem;
    }
    
    /* Styling pour les boutons */
    .stButton > button {
        background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        padding: 0.75rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
        background: linear-gradient(135deg, var(--secondary-color), var(--primary-color));
    }
    
    /* Download button styling */
    .stDownloadButton > button {
        background: linear-gradient(135deg, var(--success-color), var(--accent-color));
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: var(--shadow);
    }
    
    .stDownloadButton > button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-hover);
    }
    
    /* Zone centrale pour le dataframe*/ 
    .dataframe-container {
        background: var(--surface-color);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        min-height: 70vh;
    }
    
    .dataframe-header {
        display: flex;
        align-items: center;
        margin-bottom: 1.5rem;
        padding-bottom: 1rem;
        border-bottom: 2px solid var(--border-color);
    }
    
    .dataframe-header h2 {
        margin: 0;
        color: var(--text-primary);
        font-family: 'Inter', sans-serif;
        font-weight: 600;
        font-size: 1.8rem;
    }
    
    /* Welcome message styling */
    .welcome-message {
        text-align: center;
        padding: 4rem 2rem;
        color: var(--text-secondary);
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 15px;
        border: 2px dashed var(--border-color);
    }
    
    .welcome-message h3 {
        color: var(--text-primary);
        margin-bottom: 1rem;
        font-size: 1.5rem;
    }
    
    .welcome-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        opacity: 0.6;
    }
    
    /* Dataframe styling */
    .stDataFrame {
        border-radius: 10px;
        box-shadow: var(--shadow);
    }
    
    /* Success/Error messages */
    .success-message {
        background: linear-gradient(135deg, #11998e, #38ef7d);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff416c, #ff4b2b);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: var(--text-secondary);
        border-top: 1px solid var(--border-color);
        margin-top: 2rem;
        font-style: italic;
    }
    
    /* Animation pour les éléments */
    .animate-fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        .dataframe-container {
            padding: 1rem;
        }
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    </style>
    """, unsafe_allow_html=True)

def main():
    # Vérifier l'authentification en premier
    if not check_credentials():
        return
    
    # Si on arrive ici, l'utilisateur est authentifié
    st.logo("logodpt.png", size="large")
    
    # Appliquer le thème personnalisé
    apply_custom_theme()
    
    # Header principal personnalisé avec info utilisateur
    current_user = st.session_state.get("current_user", "Utilisateur")
    st.markdown(f"""
    <div class="main-header animate-fade-in">
        <h1>📄 Convertisseur de PV pour la FDS</h1>
        <p>Connecté en tant que : <strong>{current_user}</strong></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar pour la sélection et téléchargement
    with st.sidebar:
        # Bouton de déconnexion en haut de la sidebar
        if st.button("🔓 Se déconnecter", type="secondary", use_container_width=True):
            # Réinitialiser l'état d'authentification
            st.session_state["authenticated"] = False
            if "current_user" in st.session_state:
                del st.session_state["current_user"]
            # Nettoyer les autres données de session
            for key in list(st.session_state.keys()):
                if key not in ["authenticated", "current_user"]:
                    del st.session_state[key]
            st.rerun()
        
        st.markdown("---")
        
        st.markdown("""
        <div class="upload-section">
            <h3>🚀 Zone de traitement</h3>
            <p>Déposez votre fichier PDF ici</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Zone de téléchargement de fichier
        uploaded_file = st.file_uploader(
            "Choisir un fichier PDF",
            type=['pdf'],
            help="Sélectionnez un fichier PDF à convertir",
            label_visibility="collapsed"
        )
        
        # Traitement du fichier téléchargé
        if uploaded_file is not None:
            # Afficher les informations du fichier
            #st.toast(f"""📁 **Fichier sélectionné**  
            #**{uploaded_file.name}**  
            #**Taille :** {uploaded_file.size / 1024:.1f} KB""")
            
            # Bouton de conversion
            if st.button("🚀 Convertir le fichier", type="primary", use_container_width=True):
                # Créer un fichier temporaire
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                try:
                    # Afficher le message de progression
                    with st.spinner("🔄 Conversion en cours... Veuillez patienter."):
                        # Appeler la fonction de conversion
                        success, message, output_path, df = convert_file(tmp_file_path, uploaded_file.name)
                    
                    if success and output_path and os.path.exists(output_path):
                        # Afficher le message de succès
                        st.balloons()
                        incrementer("metrics.json")
                        st.toast("✅ Conversion réussie !")
                        
                        # Stocker le dataframe pour l'affichage dans la zone principale
                        st.session_state['df_display'] = df.rename(columns={col: col.split()[0] for col in df.columns})
                        st.session_state['excel_data'] = None
                        st.session_state['download_filename'] = f"{Path(uploaded_file.name).stem}.xlsx"
                        
                        # Lire le fichier converti pour le téléchargement
                        with open(output_path, 'rb') as file:
                            excel_data = file.read()
                            st.session_state['excel_data'] = excel_data
                        
                        st.toast(f"📁 **Fichier prêt :** {st.session_state['download_filename']}")
                        
                        # Nettoyer le fichier de sortie
                        try:
                            os.unlink(output_path)
                        except:
                            pass
                            
                    elif success:
                        # Cas où la conversion réussit mais le fichier n'est pas trouvé
                        st.toast(f"""✅ Conversion terminée !""")
                    else:
                        # Afficher le message d'erreur
                        st.toast(f"""❌ Erreur de conversion""")
                        
                finally:
                    # Nettoyer le fichier temporaire
                    try:
                        os.unlink(tmp_file_path)
                    except:
                        pass
        
        # Bouton de téléchargement (affiché seulement si des données Excel sont disponibles)
        if 'excel_data' in st.session_state and st.session_state['excel_data'] is not None:
            st.markdown("---")
            st.download_button(
                label="📥 Télécharger le fichier Excel",
                data=st.session_state['excel_data'],
                file_name=st.session_state['download_filename'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                type="primary",
                use_container_width=True
            )
        
        # Footer dans la sidebar
        fig, total=create_bar_chart("metrics.json")
        
        st.markdown(f"""
        <div class="footer">
            <p>© Vincent Boudet</p>
            {total} PVs convertis
        </div>
        """, unsafe_allow_html=True)
        st.pyplot(fig)
    # Zone principale pour l'affichage du dataframe - prend toute la largeur
    if 'df_display' in st.session_state and st.session_state['df_display'] is not None:
        
        # Affichage du dataframe avec toute la largeur disponible
        st.dataframe(st.session_state['df_display'])
    else:
        # Message d'accueil dans la zone principale
        st.markdown("""
        <div class="dataframe-container">
            <div class="welcome-message animate-fade-in">
                <div class="welcome-icon">📊</div>
                <h3>👈 Sélectionnez un fichier PDF dans la barre latérale</h3>
                <p>Le tableau des données converties s'affichera ici après la conversion.</p>
                <br>
                <p><strong>Instructions :</strong></p>
                <p>1️⃣ Choisissez votre fichier PDF</p>
                <p>2️⃣ Cliquez sur "Convertir"</p>
                <p>3️⃣ Visualisez vos données</p>
                <p>4️⃣ Téléchargez le fichier Excel</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
