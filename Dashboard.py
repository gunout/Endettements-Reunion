import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import warnings
import chardet
import io
import os
import re

warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Analyse Financière Communale - La Réunion",
    page_icon="🏝️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #264653;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .commune-header {
        font-size: 2rem;
        color: #2A9D8F;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .stAlert {
        border-radius: 10px;
    }
    .highlight-box {
        background-color: #e9f7ef;
        border-left: 5px solid #2A9D8F;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 5px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 15px 0;
    }
    .small-metric {
        font-size: 0.9rem;
    }
    .region-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

class ReunionFinancialDashboard:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', 
                      '#AB83A1', '#5CAB7D', '#2A9D8F', '#E76F51', '#264653',
                      '#E9C46A', '#2A9D8F', '#E63946', '#457B9D', '#1D3557',
                      '#A8DADC', '#F4A261', '#2A9D8F', '#E76F51', '#264653',
                      '#588157', '#3A5A40', '#A3B18A', '#DAD7CD']
        
        # Initialiser les données
        self.data = pd.DataFrame()
        self.communes_config = {}
        
    def _find_column(self, keywords):
        """Trouve une colonne dans le dataframe basée sur une liste de mots-clés"""
        if self.data.empty:
            return None
        for col in self.data.columns:
            col_lower = str(col).lower()
            for keyword in keywords:
                if keyword in col_lower:
                    return col
        return None

    def _clean_numeric_column(self, col_name):
        """Nettoie et convertit une colonne en numérique (gestion format français)"""
        if col_name and col_name in self.data.columns:
            # Remplacer les espaces (séparateur de milliers) et virgules (décimales)
            # On gère les cas où le séparateur de milliers est un espace ou rien, et la décimale est une virgule
            self.data[col_name] = self.data[col_name].astype(str).str.replace(' ', '', regex=False)
            self.data[col_name] = self.data[col_name].str.replace(',', '.', regex=False)
            self.data[col_name] = pd.to_numeric(self.data[col_name], errors='coerce')
            return True
        return False

    def _load_data(self):
        """Charge les données via fichier local ou upload"""
        st.sidebar.markdown("### 📁 Chargement des données")
        
        # Nom du fichier attendu dans le même dossier
        csv_filename = "ofgl-base-communes.csv"
        
        file_source = None
        
        # 1. Vérifier si le fichier existe localement
        if os.path.exists(csv_filename):
            try:
                file_source = open(csv_filename, 'rb')
                st.sidebar.success(f"✅ Fichier local '{csv_filename}' détecté !")
            except Exception as e:
                st.sidebar.error(f"Erreur lecture fichier local: {str(e)}")
        
        # 2. Option d'upload
        uploaded_file = st.sidebar.file_uploader(
            "Ou téléchargez un autre fichier CSV",
            type=['csv', 'txt'],
            help="Le fichier doit contenir les données financières des communes"
        )
        
        if uploaded_file is not None:
            file_source = uploaded_file
            st.sidebar.info("📄 Utilisation du fichier uploadé")
        
        # 3. Traitement des données
        if file_source is not None:
            try:
                raw_data = file_source.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                file_source.seek(0)
                
                data_loaded = False
                # Essai avec séparateurs courants et gestion des nombres français
                for sep in [';', ',', '\t', '|']:
                    try:
                        df = pd.read_csv(file_source, sep=sep, encoding=encoding, low_memory=False)
                        file_source.seek(0)
                        
                        if len(df.columns) >= 5:
                            self.data = df
                            # Nettoyage immédiat des noms de colonnes
                            self.data.columns = [str(col).strip() for col in self.data.columns]
                            data_loaded = True
                            st.sidebar.success(f"✅ Données chargées ({len(df)} lignes)")
                            break
                    except Exception:
                        file_source.seek(0)
                        continue
                
                if not data_loaded:
                    st.sidebar.error("Impossible de lire le fichier CSV. Vérifiez le format.")
                
                # Nettoyage post-chargement des colonnes numériques probables
                col_montant = self._find_column(['montant', 'solde', 'valeur'])
                if col_montant:
                    self._clean_numeric_column(col_montant)
                
                col_pop = self._find_column(['population'])
                if col_pop:
                    self._clean_numeric_column(col_pop)

                col_annee = self._find_column(['exercice', 'annee', 'année'])
                if col_annee:
                     self.data[col_annee] = pd.to_numeric(self.data[col_annee], errors='coerce')

                if not self.data.empty:
                    self.communes_config = self._extract_communes_config()
                    
                    with st.sidebar.expander("Aperçu des données"):
                        st.dataframe(self.data.head(3))

                if os.path.exists(csv_filename) and uploaded_file is None:
                    file_source.close()

            except Exception as e:
                st.sidebar.error(f"Erreur critique: {str(e)}")
                import traceback
                st.sidebar.text(traceback.format_exc())
        else:
            st.sidebar.info("📝 Mode démo. Fichier 'ofgl-base-communes.csv' introuvable.")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Crée des données d'exemple pour la démonstration"""
        st.info("Mode démonstration")
        sample_data = []
        communes = ['Saint-Denis', 'Saint-Paul', 'Saint-Pierre', 'Le Tampon', 'Saint-Louis']
        for i, commune in enumerate(communes):
            for year in [2017, 2018, 2019, 2020]:
                sample_data.append({
                    'Exercice': year,
                    'Nom 2024 Commune': commune,
                    'Agrégat': 'Recettes totales hors emprunts',
                    'Type de budget': 'Budget principal',
                    'Montant': np.random.uniform(10000000, 50000000),
                    'Population totale': np.random.randint(5000, 150000),
                    'Nom 2024 Région': 'La Réunion',
                    'Code Insee 2024 Département': '974',
                })
        self.data = pd.DataFrame(sample_data)
        
        # S'assurer que le montant est numérique pour la démo
        self._clean_numeric_column('Montant')
        self.communes_config = self._extract_communes_config()
    
    def _extract_communes_config(self):
        """Extrait la configuration des communes depuis les données"""
        if self.data.empty:
            return {}
        
        # Recherche dynamique des colonnes
        commune_col = self._find_column(['commune', 'nom', 'libellé'])
        region_col = self._find_column(['region', 'région'])
        pop_col = self._find_column(['population'])
        
        if not commune_col:
            st.error("Colonne 'Commune' introuvable. Vérifiez votre CSV.")
            return {}

        communes_list = self.data[commune_col].unique()
        communes_config = {}
        
        for commune in communes_list:
            if pd.isna(commune): continue
            
            commune_data = self.data[self.data[commune_col] == commune]
            if commune_data.empty: continue
            
            # Population
            population = 0
            if pop_col:
                population_series = commune_data[pop_col].dropna()
                population = population_series.mean() if not population_series.empty else 0
            
            # Région
            region = 'La Réunion'
            if region_col and not commune_data[region_col].empty:
                region = commune_data[region_col].iloc[0]

            communes_config[commune] = {
                "population_base": population,
                "budget_base": self._estimate_budget(commune_data),
                "type": self._determine_commune_type(commune),
                "specialites": self._determine_specialties(str(commune), commune_data),
                "endettement_base": 0,
                "fiscalite_base": 0.35,
                "couleur": self._get_commune_color(str(commune)),
                "region": region,
                "arrondissement": self._get_arrondissement(str(commune)),
                "intercommunalite": "Inconnue"
            }
        
        return communes_config

    def _determine_commune_type(self, commune_name):
        return "urbaine" # Simplifié pour la démo
    
    def _estimate_budget(self, commune_data):
        agregat_col = self._find_column(['agregat', 'agregat', 'nomenclature'])
        montant_col = self._find_column(['montant', 'solde'])
        
        if not agregat_col or not montant_col:
            # Si on ne trouve pas les colonnes, on prend la somme de tout pour estimer
            if montant_col:
                return commune_data[montant_col].sum() / 1000000
            return 0

        recettes_mask = commune_data[agregat_col].astype(str).str.contains('recettes totales', case=False, na=False)
        recettes_data = commune_data[recettes_mask]
        
        if not recettes_data.empty:
            return recettes_data[montant_col].sum() / 1000000
        return 0
    
    def _determine_specialties(self, commune_name, commune_data):
        # Logique simplifiée
        return ['services publics']

    def _get_commune_color(self, commune_name):
        return "#2A9D8F"
    
    def _get_arrondissement(self, commune_name):
        return "La Réunion"

    def get_years_available(self):
        year_col = self._find_column(['exercice', 'annee', 'année'])
        if year_col:
            years = sorted(self.data[year_col].dropna().unique())
            return [int(y) for y in years if y > 1900]
        return [2023] # Par défaut

    def prepare_commune_financial_data(self, commune_name):
        """Prépare les données financières d'une commune spécifique"""
        if self.data.empty:
            return pd.DataFrame(), {}
        
        commune_col = self._find_column(['commune', 'nom', 'libellé'])
        year_col = self._find_column(['exercice', 'annee', 'année'])
        agregat_col = self._find_column(['agregat', 'agrégat', 'nomenclature'])
        montant_col = self._find_column(['montant', 'solde'])
        pop_col = self._find_column(['population'])

        if not all([commune_col, year_col, agregat_col, montant_col]):
            st.warning(f"Données incomplètes pour analyser {commune_name}")
            return pd.DataFrame(), {}

        commune_data = self.data[self.data[commune_col] == commune_name].copy()
        
        if commune_data.empty:
            return pd.DataFrame(), {}
        
        financial_metrics = {}
        years_available = self.get_years_available()
        
        for year in years_available:
            year_data = commune_data[commune_data[year_col] == year]
            if year_data.empty: continue
            
            # Population
            pop_data = year_data[pop_col].mean() if pop_col and pop_col in year_data.columns else self.communes_config.get(commune_name, {}).get('population_base', 0)
            
            # Calculs basés sur les agrégats
            total_recettes = 0
            total_epargne = 0
            total_impots = 0
            financement = 0
            
            # On itère sur les lignes pour sommer par catégorie
            for _, row in year_data.iterrows():
                agr = str(row[agregat_col]).lower()
                mont = row[montant_col] if pd.notna(row[montant_col]) else 0
                
                if 'recette' in agr and 'total' in agr:
                    total_recettes += mont
                elif 'epargne' in agr and 'brute' in agr:
                    total_epargne += mont
                elif 'impot' in agr or 'taxe' in agr:
                    total_impots += mont
                elif 'capacite' in agr or 'financement' in agr:
                    financement += mont

            financial_metrics[year] = {
                'Annee': year,
                'Population': pop_data,
                'Recettes_Totales': total_recettes / 1000000,
                'Epargne_Brute': total_epargne / 1000000,
                'Capacite_Financement': financement / 1000000,
                'Impots_Locaux': total_impots / 1000000,
                'Dette_Totale': max(0, total_recettes * 0.8) / 1000000, # Estimation si pas de colonne dette
                'Depenses_Totales': max(0, total_recettes - total_epargne) / 1000000,
                'Taux_Endettement': 0.5, # Placeholder
                'Capacite_Remboursement': 1.5 if financement > 0 else 1.0
            }
        
        df = pd.DataFrame.from_dict(financial_metrics, orient='index')
        df = df.sort_values('Annee')
        config = self.communes_config.get(commune_name, {})
        return df, config
    
    def create_header(self):
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', unsafe_allow_html=True)
        if not self.data.empty:
            st.markdown(f"<div style='text-align:center'>Analyse basée sur {len(self.communes_config)} communes</div>", unsafe_allow_html=True)
    
    def create_sidebar(self):
        with st.sidebar:
            # Chargement
            self._load_data()
            
            if self.data.empty:
                st.warning("Aucune donnée chargée.")
                return None, None, False, [], []
            
            st.markdown("---")
            st.markdown("## 🔧 Paramètres")
            
            # Sélection Commune
            commune_options = sorted(list(self.communes_config.keys()))
            selected_commune = st.selectbox("Commune à analyser :", commune_options)
            
            # Période
            years = self.get_years_available()
            year_range = (min(years), max(years))
            
            # Options
            show_advanced = st.checkbox("Afficher les données brutes", value=False)
            compare_mode = st.checkbox("Mode Comparaison", value=False)
            
            compare_communes = []
            if compare_mode:
                compare_communes = st.multiselect(
                    "Communes à comparer :",
                    [c for c in commune_options if c != selected_commune],
                    max_selections=4
                )
            
            return selected_commune, year_range, show_advanced, compare_communes, []

    def create_commune_overview(self):
        st.markdown("### 🗺️ Vue d'ensemble des communes")
        if not self.communes_config:
            return
        
        overview_data = []
        for commune in self.communes_config:
            df, _ = self.prepare_commune_financial_data(commune)
            if not df.empty:
                last_row = df.iloc[-1]
                overview_data.append({
                    'Commune': commune,
                    'Population': int(last_row.get('Population', 0)),
                    'Recettes (M€)': round(last_row.get('Recettes_Totales', 0), 2),
                    'Épargne (M€)': round(last_row.get('Epargne_Brute', 0), 2)
                })
        
        if overview_data:
            df_overview = pd.DataFrame(overview_data)
            st.dataframe(df_overview, use_container_width=True)
            
            # Graphique simple
            fig = px.bar(df_overview.sort_values('Recettes (M€)', ascending=False).head(10), 
                         x='Recettes (M€)', y='Commune', orientation='h', color='Recettes (M€)',
                         title='Top 10 Recettes Totales')
            st.plotly_chart(fig, use_container_width=True)

    def create_summary_metrics(self, df, config, commune_name):
        st.markdown(f'<h2 class="commune-header">🏙️ {commune_name}</h2>', unsafe_allow_html=True)
        if df.empty:
            st.warning("Pas de données disponibles.")
            return

        last = df.iloc[-1]
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Population", f"{last['Population']:,.0f}")
            st.metric("Recettes (M€)", f"{last['Recettes_Totales']:.2f}")
        with c2:
            st.metric("Épargne (M€)", f"{last['Epargne_Brute']:.2f}")
            st.metric("Impôts (M€)", f"{last['Impots_Locaux']:.2f}")
        with c3:
            st.metric("Dette (M€)", f"{last['Dette_Totale']:.2f}")
            st.metric("Capacité Fin.", f"{last['Capacite_Financement']:.2f} M€")

        # Graphique évolution
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Annee'], y=df['Recettes_Totales'], mode='lines+markers', name='Recettes'))
        fig.add_trace(go.Scatter(x=df['Annee'], y=df['Depenses_Totales'], mode='lines+markers', name='Dépenses'))
        fig.update_layout(title="Évolution Recettes / Dépenses", xaxis_title="Année", yaxis_title="Millions d'Euros")
        st.plotly_chart(fig, use_container_width=True)

    def create_comparative_analysis(self, communes):
        st.markdown("### 📊 Comparaison inter-communes")
        if len(communes) < 2:
            st.info("Sélectionnez au moins 2 communes dans la sidebar pour comparer.")
            return
        
        comp_data = []
        for c in communes:
            df, _ = self.prepare_commune_financial_data(c)
            if not df.empty:
                l = df.iloc[-1]
                comp_data.append({
                    'Commune': c,
                    'Recettes/Hab': (l['Recettes_Totales'] * 1_000_000) / l['Population'] if l['Population'] > 0 else 0,
                    'Dette/Hab': (l['Dette_Totale'] * 1_000_000) / l['Population'] if l['Population'] > 0 else 0,
                    'Épargne (M€)': l['Epargne_Brute']
                })
        
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True)
        
        fig = px.bar(df_comp, x='Commune', y=['Recettes/Hab', 'Dette/Hab'], barmode='group',
                     title="Comparaison par habitant (€)")
        st.plotly_chart(fig, use_container_width=True)

    def create_data_explorer(self):
        st.markdown("### 🔍 Données Brutes")
        st.dataframe(self.data, use_container_width=True)

    def run_dashboard(self):
        self.create_header()
        
        params = self.create_sidebar()
        
        # Si pas de données, on arrête
        if not params or params[0] is None and self.data.empty:
            st.warning("Veuillez charger un fichier CSV nommé 'ofgl-base-communes.csv' dans le dossier.")
            return

        selected_commune, year_range, show_advanced, compare_communes, _ = params
        
        # Création des onglets
        tabs = st.tabs(["🏠 Vue d'ensemble", "🏙️ Analyse Détaillée", "🔄 Comparaisons", "🔍 Données Brutes"])
        
        with tabs[0]:
            self.create_commune_overview()
            
        with tabs[1]:
            if selected_commune:
                df, config = self.prepare_commune_financial_data(selected_commune)
                self.create_summary_metrics(df, config, selected_commune)
            else:
                st.info("Sélectionnez une commune dans la barre latérale.")
                
        with tabs[2]:
            self.create_comparative_analysis(compare_communes)
            
        with tabs[3]:
            if show_advanced:
                self.create_data_explorer()
            else:
                st.info("Cochez 'Afficher les données brutes' dans la sidebar pour voir cet onglet.")

# Point d'entrée
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
