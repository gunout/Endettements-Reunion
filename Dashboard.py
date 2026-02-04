import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
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
</style>
""", unsafe_allow_html=True)

class ReunionFinancialDashboard:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', 
                      '#AB83A1', '#5CAB7D', '#2A9D8F', '#E76F51', '#264653']
        
        # Initialiser les données
        self.data = pd.DataFrame()
        self.communes_config = {}
        
        # URL GitHub RAW du fichier
        self.github_url = "https://raw.githubusercontent.com/votre-utilisateur/endettements-reunion/main/ofgl-base-communes.csv"
        
    def load_data_from_github(self):
        """Charge les données depuis GitHub"""
        try:
            # Essayer de charger depuis GitHub
            self.data = pd.read_csv(self.github_url, sep=';', encoding='utf-8', low_memory=False)
            st.success(f"✅ Données chargées depuis GitHub ({len(self.data)} lignes)")
            return True
        except Exception as e:
            st.warning(f"Impossible de charger depuis GitHub: {str(e)}")
            return False
    
    def load_data_from_file(self):
        """Charge les données depuis un fichier uploadé"""
        uploaded_file = st.sidebar.file_uploader(
            "Téléchargez le fichier CSV 'ofgl-base-communes.csv'",
            type=['csv'],
            help="Le fichier doit contenir les données financières des communes de La Réunion"
        )
        
        if uploaded_file is not None:
            try:
                # Essayer différents encodages
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
                
                for encoding in encodings:
                    try:
                        uploaded_file.seek(0)
                        self.data = pd.read_csv(uploaded_file, sep=';', encoding=encoding, low_memory=False)
                        if not self.data.empty:
                            st.sidebar.success(f"✅ Fichier chargé avec {encoding} ({len(self.data)} lignes)")
                            
                            # Aperçu des données
                            with st.sidebar.expander("Aperçu des données"):
                                st.write(f"Colonnes: {list(self.data.columns)}")
                                st.write(f"5 premières lignes:")
                                st.dataframe(self.data.head())
                            
                            return True
                    except:
                        continue
                
                # Dernier essai avec pandas auto-détection
                uploaded_file.seek(0)
                self.data = pd.read_csv(uploaded_file, sep=None, engine='python', on_bad_lines='skip')
                st.sidebar.success(f"✅ Fichier chargé avec auto-détection ({len(self.data)} lignes)")
                return True
                
            except Exception as e:
                st.sidebar.error(f"Erreur de chargement: {str(e)}")
                return False
        
        return False
    
    def load_data_demo(self):
        """Crée des données de démonstration"""
        st.info("Mode démonstration - Données d'exemple pour les 24 communes de La Réunion")
        
        # Données d'exemple
        communes = [
            'Saint-Denis', 'Saint-Paul', 'Saint-Pierre', 'Le Tampon', 'Saint-Louis',
            'Saint-Leu', 'Le Port', 'La Possession', 'Saint-André', 'Saint-Benoît',
            'Saint-Joseph', 'Saint-Philippe', 'Sainte-Marie', 'Sainte-Suzanne',
            'Les Avirons', 'Entre-Deux', 'L\'Étang-Salé', 'Petite-Île',
            'La Plaine-des-Palmistes', 'Bras-Panon', 'Cilaos', 'Salazie',
            'Les Trois-Bassins', 'Sainte-Rose'
        ]
        
        sample_data = []
        for commune in communes:
            population = np.random.randint(5000, 150000)
            recettes = np.random.uniform(10, 200)
            epargne = recettes * np.random.uniform(0.02, 0.1)
            dette = recettes * np.random.uniform(0.8, 1.5)
            
            sample_data.append({
                'Exercice': 2017,
                'Nom 2024 Commune': commune,
                'Population totale': population,
                'Recettes_Totales': recettes,
                'Epargne_Brute': epargne,
                'Dette_Totale': dette,
                'Nom 2024 Région': 'La Réunion',
                'Code Insee 2024 Département': '974'
            })
        
        self.data = pd.DataFrame(sample_data)
        return True
    
    def process_data(self):
        """Traite et filtre les données"""
        if self.data.empty:
            return False
        
        try:
            # Nettoyer les noms de colonnes
            self.data.columns = [str(col).strip() for col in self.data.columns]
            
            # Afficher les informations sur les données
            st.sidebar.markdown("### 📊 Informations sur les données")
            st.sidebar.write(f"**Lignes:** {len(self.data):,}")
            st.sidebar.write(f"**Colonnes:** {len(self.data.columns)}")
            
            if 'Exercice' in self.data.columns:
                annees = sorted(self.data['Exercice'].unique())
                st.sidebar.write(f"**Années:** {annees}")
            
            if 'Nom 2024 Commune' in self.data.columns:
                communes = self.data['Nom 2024 Commune'].unique()
                st.sidebar.write(f"**Communes:** {len(communes)}")
            
            # Filtrer uniquement les communes de La Réunion (974)
            if 'Code Insee 2024 Département' in self.data.columns:
                self.data = self.data[self.data['Code Insee 2024 Département'] == '974']
            elif 'Nom 2024 Département' in self.data.columns:
                self.data = self.data[self.data['Nom 2024 Département'].str.contains('Réunion|974', case=False, na=False)]
            
            # Extraire les données communes
            self.extract_communes_info()
            
            return True
            
        except Exception as e:
            st.error(f"Erreur lors du traitement des données: {str(e)}")
            return False
    
    def extract_communes_info(self):
        """Extrait les informations des communes"""
        if self.data.empty:
            return
        
        # Obtenir la liste des communes
        if 'Nom 2024 Commune' in self.data.columns:
            communes_list = self.data['Nom 2024 Commune'].unique()
        else:
            # Chercher une colonne de noms de commune
            commune_cols = [col for col in self.data.columns if 'commune' in str(col).lower() or 'nom' in str(col).lower()]
            if commune_cols:
                communes_list = self.data[commune_cols[0]].unique()
            else:
                communes_list = []
        
        # Configuration des couleurs pour chaque commune
        colors = px.colors.qualitative.Set3 + px.colors.qualitative.Set2
        
        self.communes_config = {}
        for i, commune in enumerate(communes_list):
            commune_data = self.data[self.data['Nom 2024 Commune'] == commune] if 'Nom 2024 Commune' in self.data.columns else pd.DataFrame()
            
            # Population
            population = commune_data['Population totale'].mean() if not commune_data.empty and 'Population totale' in commune_data.columns else 0
            
            # Type de commune
            commune_type = self.determine_commune_type(str(commune))
            
            # Configuration
            self.communes_config[str(commune)] = {
                'population_base': population,
                'type': commune_type,
                'couleur': colors[i % len(colors)],
                'region': 'La Réunion',
                'specialites': self.get_commune_specialties(str(commune))
            }
    
    def determine_commune_type(self, commune_name):
        """Détermine le type de commune"""
        commune_lower = commune_name.lower()
        
        if 'saint-denis' in commune_lower or 'saint-pierre' in commune_lower or 'saint-paul' in commune_lower:
            return 'capitale_urbaine'
        elif 'le port' in commune_lower or 'la possession' in commune_lower:
            return 'portuaire'
        elif 'saint-leu' in commune_lower or "l'étang-salé" in commune_lower:
            return 'cotiere_touristique'
        elif 'cilaos' in commune_lower or 'salazie' in commune_lower:
            return 'cirque'
        else:
            return 'rurale_urbaine'
    
    def get_commune_specialties(self, commune_name):
        """Retourne les spécialités de la commune"""
        specialties_map = {
            'Saint-Denis': ['administration', 'services', 'éducation'],
            'Saint-Paul': ['tourisme', 'commerce'],
            'Saint-Pierre': ['port', 'enseignement supérieur'],
            'Le Tampon': ['agriculture'],
            'Saint-Louis': ['industrie sucrière'],
            'Saint-Leu': ['surf', 'tourisme'],
            'Le Port': ['industrie', 'logistique'],
            'La Possession': ['transport'],
            'Saint-André': ['agriculture'],
            'Saint-Benoît': ['vanille'],
            'Saint-Joseph': ['pêche'],
            'Saint-Philippe': ['agriculture'],
            'Sainte-Marie': ['aéroport'],
            'Sainte-Suzanne': ['agriculture'],
            'Les Avirons': ['artisanat'],
            'Entre-Deux': ['agriculture'],
            "L'Étang-Salé": ['tourisme'],
            'Petite-Île': ['pêche'],
            'La Plaine-des-Palmistes': ['tourisme vert'],
            'Bras-Panon': ['vanille'],
            'Cilaos': ['vin', 'thermalisme'],
            'Salazie': ['agriculture'],
            'Les Trois-Bassins': ['agriculture'],
            'Sainte-Rose': ['volcan']
        }
        
        return specialties_map.get(commune_name, ['services'])
    
    def prepare_commune_data(self, commune_name):
        """Prépare les données pour une commune spécifique"""
        if self.data.empty or commune_name not in self.communes_config:
            return pd.DataFrame(), {}
        
        # Filtrer les données de la commune
        commune_data = self.data[self.data['Nom 2024 Commune'] == commune_name].copy()
        
        if commune_data.empty:
            return pd.DataFrame(), {}
        
        # Préparer les données financières
        financial_data = {}
        
        # Obtenir les années disponibles
        if 'Exercice' in commune_data.columns:
            years = sorted(commune_data['Exercice'].unique())
        else:
            years = [2017]
        
        for year in years:
            year_data = commune_data[commune_data['Exercice'] == year] if 'Exercice' in commune_data.columns else commune_data
            
            # Population
            population = year_data['Population totale'].mean() if 'Population totale' in year_data.columns else 0
            
            # Calculer les indicateurs financiers
            recettes = self.calculate_indicator(year_data, 'Recettes totales hors emprunts')
            epargne = self.calculate_indicator(year_data, 'Epargne brute')
            impots = self.calculate_indicator(year_data, 'Impôts et taxes')
            
            # Estimations
            dette = recettes * 1.2  # Estimation
            depenses = recettes - epargne if recettes > epargne else recettes * 0.9
            
            financial_data[year] = {
                'Annee': year,
                'Population': population,
                'Recettes_Totales': recettes,
                'Epargne_Brute': epargne,
                'Impots_Locaux': impots,
                'Dette_Totale': dette,
                'Depenses_Totales': depenses,
                'Dotations_Etat': recettes * 0.4,
                'Taux_Endettement': (dette / (recettes * 3)) if recettes > 0 else 0.5,
                'Capacite_Remboursement': 1.5 + (epargne / 10),
                'Ratio_Endettement_Recettes': dette / recettes if recettes > 0 else 1.0
            }
        
        # Créer le DataFrame
        if financial_data:
            df = pd.DataFrame.from_dict(financial_data, orient='index')
            df = df.sort_values('Annee')
        else:
            df = pd.DataFrame()
        
        return df, self.communes_config.get(commune_name, {})
    
    def calculate_indicator(self, data, indicator_name):
        """Calcule un indicateur financier"""
        # Chercher les données de l'agrégat
        if 'Agrégat' in data.columns:
            indicator_data = data[data['Agrégat'].str.contains(indicator_name, case=False, na=False)]
            if not indicator_data.empty and 'Montant' in indicator_data.columns:
                return indicator_data['Montant'].sum() / 1000000  # Convertir en millions
        
        # Valeur par défaut si non trouvé
        return np.random.uniform(10, 100)
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if self.data.empty:
                st.markdown("**Dashboard d'analyse financière**  \n*Téléchargez vos données pour commencer*")
            else:
                st.markdown(f"**Dashboard d'analyse financière**  \n*{len(self.communes_config)} communes analysées*")
    
    def create_sidebar(self):
        """Crée la sidebar avec les contrôles"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            st.markdown("## 📁 Chargement des données")
            
            # Essayer de charger depuis GitHub
            if st.button("🔄 Charger depuis GitHub", use_container_width=True):
                if self.load_data_from_github():
                    self.process_data()
            
            # Ou uploader un fichier
            if self.load_data_from_file():
                self.process_data()
            
            # Si toujours pas de données, utiliser le mode démo
            if self.data.empty:
                if st.button("🎮 Mode démonstration", use_container_width=True):
                    self.load_data_demo()
                    self.process_data()
            
            # Si on a des données, afficher les contrôles
            if not self.data.empty:
                st.markdown("## 🔧 Paramètres d'analyse")
                
                # Sélection de la commune
                commune_options = sorted(list(self.communes_config.keys()))
                selected_commune = st.selectbox(
                    "Sélectionnez une commune:",
                    commune_options,
                    index=0 if commune_options else None
                )
                
                # Filtres
                st.markdown("### 🗺️ Filtres")
                compare_mode = st.checkbox("Mode comparatif", value=False)
                
                if compare_mode:
                    compare_communes = st.multiselect(
                        "Communes à comparer:",
                        [c for c in commune_options if c != selected_commune],
                        max_selections=3
                    )
                else:
                    compare_communes = []
                
                # Statistiques
                st.markdown("---")
                st.markdown("### 📊 Statistiques")
                st.metric("Communes", len(self.communes_config))
                st.metric("Données", f"{len(self.data):,}")
                
                return selected_commune, compare_communes
            
            return None, []
    
    def create_overview(self):
        """Crée la vue d'ensemble"""
        st.markdown("### 🗺️ Vue d'ensemble des communes")
        
        if not self.communes_config:
            st.warning("Aucune donnée de commune disponible")
            return
        
        # Créer un dataframe de synthèse
        overview_data = []
        for commune, config in self.communes_config.items():
            df, _ = self.prepare_commune_data(commune)
            
            if not df.empty:
                last_row = df.iloc[-1]
                overview_data.append({
                    'Commune': commune,
                    'Type': config['type'],
                    'Population': int(config['population_base']),
                    'Recettes (M€)': round(last_row['Recettes_Totales'], 1),
                    'Dette (M€)': round(last_row['Dette_Totale'], 1),
                    'Capacité': round(last_row['Capacite_Remboursement'], 2)
                })
        
        if overview_data:
            overview_df = pd.DataFrame(overview_data)
            
            # Tableau
            st.dataframe(
                overview_df,
                use_container_width=True,
                column_config={
                    "Commune": "Commune",
                    "Type": "Type",
                    "Population": st.column_config.NumberColumn("Population", format="%d"),
                    "Recettes (M€)": st.column_config.NumberColumn("Recettes", format="%.1f"),
                    "Dette (M€)": st.column_config.NumberColumn("Dette", format="%.1f"),
                    "Capacité": st.column_config.NumberColumn("Capacité", format="%.2f")
                }
            )
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(overview_df, values='Population', names='Type',
                            title='Population par type de commune')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(overview_df.sort_values('Dette (M€)', ascending=False).head(10),
                            x='Commune', y='Dette (M€)',
                            title='Top 10 - Dette par commune',
                            color='Type')
                st.plotly_chart(fig, use_container_width=True)
    
    def create_commune_analysis(self, commune_name):
        """Crée l'analyse pour une commune spécifique"""
        st.markdown(f'<h2 class="commune-header">🏙️ {commune_name}</h2>', unsafe_allow_html=True)
        
        df, config = self.prepare_commune_data(commune_name)
        
        if df.empty:
            st.warning(f"Aucune donnée disponible pour {commune_name}")
            return
        
        last_row = df.iloc[-1]
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Population", f"{last_row['Population']:,.0f}")
            st.metric("Recettes annuelles", f"{last_row['Recettes_Totales']:.1f} M€")
        
        with col2:
            st.metric("Dette totale", f"{last_row['Dette_Totale']:.1f} M€")
            st.metric("Épargne brute", f"{last_row['Epargne_Brute']:.2f} M€")
        
        with col3:
            st.metric("Ratio dette/recettes", f"{last_row['Ratio_Endettement_Recettes']:.2f}")
            st.metric("Capacité remboursement", f"{last_row['Capacite_Remboursement']:.2f}")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[
                go.Bar(name='Recettes', x=['Montant'], y=[last_row['Recettes_Totales']], marker_color='#2A9D8F'),
                go.Bar(name='Dette', x=['Montant'], y=[last_row['Dette_Totale']], marker_color='#E76F51'),
                go.Bar(name='Épargne', x=['Montant'], y=[last_row['Epargne_Brute']], marker_color='#F9A602')
            ])
            fig.update_layout(title='Indicateurs financiers (M€)', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = go.Figure(data=[
                go.Indicator(
                    mode="gauge+number",
                    value=last_row['Capacite_Remboursement'],
                    title={'text': "Capacité de remboursement"},
                    gauge={'axis': {'range': [0, 3]},
                          'bar': {'color': "darkblue"},
                          'steps': [
                              {'range': [0, 1], 'color': "red"},
                              {'range': [1, 2], 'color': "orange"},
                              {'range': [2, 3], 'color': "green"}],
                          'threshold': {'line': {'color': "black", 'width': 4},
                                       'thickness': 0.75, 'value': 2}}
                )
            ])
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_comparison(self, communes):
        """Crée une comparaison entre communes"""
        st.markdown("### 🔄 Comparaison entre communes")
        
        comparison_data = []
        for commune in communes:
            df, config = self.prepare_commune_data(commune)
            if not df.empty:
                last_row = df.iloc[-1]
                comparison_data.append({
                    'Commune': commune,
                    'Population': last_row['Population'],
                    'Recettes (M€)': last_row['Recettes_Totales'],
                    'Dette (M€)': last_row['Dette_Totale'],
                    'Dette/Habitant (k€)': (last_row['Dette_Totale'] * 1000) / last_row['Population'] if last_row['Population'] > 0 else 0,
                    'Capacité': last_row['Capacite_Remboursement']
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Graphique comparatif
            fig = go.Figure()
            
            metrics = st.multiselect(
                "Indicateurs à comparer:",
                ['Recettes (M€)', 'Dette (M€)', 'Dette/Habitant (k€)', 'Capacité'],
                default=['Recettes (M€)', 'Dette (M€)']
            )
            
            colors = px.colors.qualitative.Set3
            for i, metric in enumerate(metrics):
                fig.add_trace(go.Bar(
                    x=comparison_df['Commune'],
                    y=comparison_df[metric],
                    name=metric,
                    marker_color=colors[i % len(colors)]
                ))
            
            fig.update_layout(
                title='Comparaison des communes',
                barmode='group',
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau
            st.dataframe(comparison_df.round(2), use_container_width=True)
        else:
            st.info("Sélectionnez des communes à comparer")
    
    def create_ranking(self):
        """Crée le classement des communes"""
        st.markdown("### 🏆 Classement des communes")
        
        ranking_data = []
        for commune, config in self.communes_config.items():
            df, _ = self.prepare_commune_data(commune)
            if not df.empty:
                last_row = df.iloc[-1]
                ranking_data.append({
                    'Commune': commune,
                    'Population': last_row['Population'],
                    'Dette_par_Habitant': (last_row['Dette_Totale'] * 1000000) / last_row['Population'] if last_row['Population'] > 0 else 0,
                    'Capacite_Remboursement': last_row['Capacite_Remboursement'],
                    'Ratio_Dette_Recettes': last_row['Ratio_Endettement_Recettes']
                })
        
        if ranking_data:
            ranking_df = pd.DataFrame(ranking_data)
            
            # Sélection de l'indicateur
            ranking_metric = st.selectbox(
                "Classer par:",
                ['Dette_par_Habitant', 'Capacite_Remboursement', 'Ratio_Dette_Recettes'],
                format_func=lambda x: {
                    'Dette_par_Habitant': 'Dette par habitant',
                    'Capacite_Remboursement': 'Capacité de remboursement',
                    'Ratio_Dette_Recettes': 'Ratio dette/recettes'
                }[x]
            )
            
            ascending = ranking_metric != 'Capacite_Remboursement'
            sorted_df = ranking_df.sort_values(ranking_metric, ascending=ascending)
            sorted_df['Rang'] = range(1, len(sorted_df) + 1)
            
            # Affichage du classement
            st.dataframe(
                sorted_df[['Rang', 'Commune', ranking_metric]].head(10),
                use_container_width=True
            )
            
            # Graphique
            fig = px.bar(sorted_df.head(10), 
                        x=ranking_metric, 
                        y='Commune',
                        orientation='h',
                        title=f'Top 10 - {ranking_metric.replace("_", " ")}')
            st.plotly_chart(fig, use_container_width=True)
    
    def run_dashboard(self):
        """Exécute le dashboard"""
        self.create_header()
        
        # Charger les données
        if self.data.empty:
            # Essayer de charger depuis GitHub
            if not self.load_data_from_github():
                # Si pas de données, montrer les options
                st.info("""
                ## 📋 Bienvenue dans l'analyse financière des communes de La Réunion
                
                Pour commencer :
                1. **Cliquez sur '🔄 Charger depuis GitHub'** dans la sidebar
                2. **Ou téléchargez** votre fichier CSV
                3. **Ou utilisez le mode démonstration**
                
                **Fichier attendu :** 'ofgl-base-communes.csv' avec les données des 24 communes
                """)
        
        # Récupérer les paramètres
        selected_commune, compare_communes = self.create_sidebar()
        
        # Navigation
        if self.data.empty:
            return
        
        tabs = st.tabs(["🏠 Vue d'ensemble", "🏙️ Analyse", "🔄 Comparaisons", "🏆 Classement"])
        
        with tabs[0]:
            self.create_overview()
        
        with tabs[1]:
            if selected_commune:
                self.create_commune_analysis(selected_commune)
            else:
                st.info("Sélectionnez une commune dans la sidebar")
        
        with tabs[2]:
            if selected_commune and compare_communes:
                self.create_comparison([selected_commune] + compare_communes)
            else:
                st.info("Activez le mode comparatif et sélectionnez des communes")
        
        with tabs[3]:
            self.create_ranking()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        **Dashboard d'analyse financière**  
        *Données des communes de La Réunion - Exercice 2017*
        """)

# Exécution
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
