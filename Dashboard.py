import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
import chardet
import os

warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière - La Réunion (26k Lignes)",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS
st.markdown("""
<style>
    .main-header { font-size: 2.2rem; color: #264653; text-align: center; margin-bottom: 1rem; font-weight: bold; }
    .commune-header { font-size: 1.8rem; color: #2A9D8F; margin-bottom: 1rem; }
    .metric-box { background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center; }
</style>
""", unsafe_allow_html=True)

class ReunionFinancialDashboard:
    def __init__(self):
        self.data = pd.DataFrame()
        self.communes_config = {}
        
    def _find_column(self, keywords):
        """Trouve une colonne par mots-clés"""
        if self.data.empty: return None
        for col in self.data.columns:
            if any(k in str(col).lower() for k in keywords):
                return col
        return None

    def _clean_french_numbers(self, col_name):
        """Convertit les formats français (1 000,00) en float Python"""
        if col_name and col_name in self.data.columns:
            # Remplacer les espaces (milliers) et virgules (décimales)
            self.data[col_name] = (
                self.data[col_name]
                .astype(str)
                .str.replace(' ', '', regex=False)
                .str.replace(',', '.', regex=False)
            )
            self.data[col_name] = pd.to_numeric(self.data[col_name], errors='coerce')
            return True
        return False

    def _load_data(self):
        """Charge le fichier CSV local"""
        st.sidebar.markdown("### 📁 Chargement des données")
        csv_filename = "ofgl-base-communes.csv"
        file_source = None

        # 1. Tentative de lecture du fichier local
        if os.path.exists(csv_filename):
            try:
                file_source = open(csv_filename, 'rb')
                st.sidebar.success(f"✅ Fichier '{csv_filename}' détecté")
            except Exception as e:
                st.sidebar.error(f"Erreur lecture: {e}")
        
        # 2. Upload alternatif
        uploaded_file = st.sidebar.file_uploader("Ou charger un fichier CSV", type=['csv'])
        if uploaded_file is not None:
            file_source = uploaded_file
            st.sidebar.info("📄 Fichier uploadé utilisé")

        # 3. Traitement
        if file_source is not None:
            try:
                raw_data = file_source.read()
                encoding = chardet.detect(raw_data)['encoding']
                file_source.seek(0)
                
                loaded = False
                for sep in [';', ',', '\t']:
                    try:
                        df = pd.read_csv(file_source, sep=sep, encoding=encoding, low_memory=False)
                        if len(df.columns) > 3:
                            self.data = df
                            self.data.columns = [str(c).strip() for c in self.data.columns]
                            loaded = True
                            st.sidebar.success(f"✅ {len(self.data)} lignes chargées")
                            break
                    except: 
                        file_source.seek(0)
                        continue
                
                if not loaded:
                    st.sidebar.error("Format CSV non reconnu.")
                
                # Nettoyage des colonnes numériques automatique
                montant_col = self._find_column(['montant', 'solde', 'valeur'])
                if montant_col: self._clean_french_numbers(montant_col)
                
                pop_col = self._find_column(['population'])
                if pop_col: self._clean_french_numbers(pop_col)

                if not self.data.empty:
                    self.communes_config = self._extract_communes_config()
                
                # Fermeture fichier local si ouvert
                if os.path.exists(csv_filename) and uploaded_file is None:
                    file_source.close()

            except Exception as e:
                st.sidebar.error(f"Erreur: {e}")
        else:
            st.sidebar.warning("Fichier introuvable. Mode démo.")
            self._create_sample_data()

    def _create_sample_data(self):
        """Données factices si pas de fichier"""
        data = []
        for c in ['Saint-Denis', 'Saint-Pierre', 'Saint-Paul']:
            for y in range(2018, 2024):
                data.append({'Exercice': y, 'Nom Commune': c, 'Montant': np.random.randint(1000, 50000)})
        self.data = pd.DataFrame(data)
        self.communes_config = {c: {} for c in ['Saint-Denis', 'Saint-Pierre', 'Saint-Paul']}

    def _extract_communes_config(self):
        """Extrait la liste des communes uniques"""
        if self.data.empty: return {}
        col = self._find_column(['commune', 'nom', 'libellé'])
        if col:
            # Retourne un dictionnaire simple pour l'instant
            return {c: {"population": 10000} for c in self.data[col].dropna().unique()}
        return {}

    def get_years(self):
        c = self._find_column(['exercice', 'annee'])
        if c:
            return sorted(self.data[c].dropna().unique())
        return [2023]

    def prepare_commune_data(self, commune_name):
        """Prépare les données pour une commune spécifique"""
        col_com = self._find_column(['commune', 'nom'])
        col_year = self._find_column(['exercice', 'annee'])
        col_mont = self._find_column(['montant'])
        col_agr = self._find_column(['agregat', 'nomenclature', 'libellé'])

        if not all([col_com, col_year, col_mont]): return pd.DataFrame(), {}
        
        df = self.data[self.data[col_com] == commune_name].copy()
        
        # Si pas de colonne agrégat, on fait simple
        if not col_agr:
            return df, {}
            
        # Analyse basique si colonne agrégat existe
        summary = df.groupby(col_year)[col_mont].sum().reset_index()
        summary.columns = ['Annee', 'Total_Montant']
        return summary, {}

    def create_overview(self):
        """Vue d'ensemble : Affiche TOUTES les lignes (26k)"""
        st.markdown("### 🗺️ Vue d'ensemble du Dataset")
        
        if self.data.empty:
            st.warning("Données non chargées.")
            return

        # 1. Métriques rapides en haut
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Lignes", f"{len(self.data):,}")
        c2.metric("Colonnes", len(self.data.columns))
        
        col_com = self._find_column(['commune', 'nom'])
        if col_com:
            c3.metric("Communes Uniques", self.data[col_com].nunique())

        st.markdown("---")
        
        # 2. AFFICHAGE COMPLET DES DONNÉES (Demande utilisateur)
        st.markdown("### 📋 Données Brutes Complètes (Fichier Source)")
        st.info("💡 **Tableau interactif** : Vous pouvez utiliser la barre de recherche ci-dessus pour filtrer par commune, année ou montant.")
        
        # Utilisation de st.dataframe pour gérer les grandes quantités de données
        st.dataframe(
            self.data,
            use_container_width=True,
            height=800  # Ajustez la hauteur selon vos besoins
        )
        
        # 3. Optionnel : Un petit graphique sur la répartition si possible
        st.markdown("### 📊 Aperçu rapide")
        col_mont = self._find_column(['montant'])
        col_com = self._find_column(['commune', 'nom'])
        
        if col_mont and col_com:
            # Top 10 des sommes par commune
            top_com = self.data.groupby(col_com)[col_mont].sum().sort_values(ascending=False).head(10).reset_index()
            fig = px.bar(top_com, x=col_mont, y=col_com, orientation='h', 
                         title=f"Top 10 des communes par volume financier ({col_mont})")
            st.plotly_chart(fig, use_container_width=True)

    def create_commune_analysis(self, commune_name):
        st.markdown(f'<h2 class="commune-header">🏙️ {commune_name}</h2>', unsafe_allow_html=True)
        
        df, _ = self.prepare_commune_data(commune_name)
        
        if df.empty:
            st.warning("Pas assez de données détaillées pour cette commune.")
            # Afficher quand même les lignes brutes filtrées pour cette commune
            col_com = self._find_column(['commune', 'nom'])
            if col_com:
                st.write("Données brutes pour cette commune :")
                st.dataframe(self.data[self.data[col_com] == commune_name])
            return

        st.metric("Années disponibles", f"{df['Annee'].min()} - {df['Annee'].max()}")
        
        fig = px.line(df, x='Annee', y='Total_Montant', markers=True, title="Évolution financière")
        st.plotly_chart(fig, use_container_width=True)

    def run(self):
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière Communale</h1>', unsafe_allow_html=True)
        
        # Sidebar
        self._load_data()
        
        if not self.data.empty:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### ⚙️ Options")
            
            communes = sorted(list(self.communes_config.keys()))
            selected_commune = st.sidebar.selectbox("Analyser une commune :", [""] + communes)
            
            tabs = st.tabs(["📊 Vue d'ensemble (Données)", "🏙️ Analyse Commune"])
            
            with tabs[0]:
                self.create_overview()
            
            with tabs[1]:
                if selected_commune:
                    self.create_commune_analysis(selected_commune)
                else:
                    st.info("Sélectionnez une commune dans la barre latérale.")

# Lancement
if __name__ == "__main__":
    app = ReunionFinancialDashboard()
    app.run()
