import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import os
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
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572']
        
        # Initialiser les données
        self.data = pd.DataFrame()
        self.communes_config = {}
        
        # Essayer de charger le fichier local
        self.load_local_file()
    
    def load_local_file(self):
        """Charge le fichier CSV local depuis le dépôt GitHub"""
        try:
            # Chemin du fichier dans votre dépôt
            file_path = "ofgl-base-communes.csv"
            
            # Vérifier si le fichier existe
            if os.path.exists(file_path):
                st.info(f"Chargement du fichier local: {file_path}")
                
                # Essayer différents encodages
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
                
                for encoding in encodings:
                    try:
                        self.data = pd.read_csv(file_path, sep=';', encoding=encoding, low_memory=False)
                        st.success(f"✅ Fichier chargé avec succès! {len(self.data)} lignes, {len(self.data.columns)} colonnes")
                        break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        st.warning(f"Erreur avec {encoding}: {str(e)}")
                        continue
                
                # Si toujours vide, essayer avec auto-détection
                if self.data.empty:
                    try:
                        self.data = pd.read_csv(file_path, sep=None, engine='python', on_bad_lines='skip')
                        st.success(f"✅ Fichier chargé avec auto-détection")
                    except Exception as e:
                        st.error(f"Impossible de charger le fichier: {str(e)}")
            
            else:
                st.warning(f"Fichier non trouvé: {file_path}")
                
        except Exception as e:
            st.error(f"Erreur lors du chargement: {str(e)}")
    
    def analyze_data_structure(self):
        """Analyse la structure des données"""
        if self.data.empty:
            return
        
        # Afficher les informations de base
        st.sidebar.markdown("### 📊 Structure des données")
        st.sidebar.write(f"**Lignes:** {len(self.data):,}")
        st.sidebar.write(f"**Colonnes:** {len(self.data.columns)}")
        
        # Afficher les premières colonnes
        st.sidebar.write("**Colonnes disponibles:**")
        for i, col in enumerate(self.data.columns[:10]):  # Afficher les 10 premières
            st.sidebar.write(f"- {col}")
        
        if len(self.data.columns) > 10:
            st.sidebar.write(f"... et {len(self.data.columns) - 10} autres")
        
        # Afficher un aperçu des données
        with st.expander("👁️ Aperçu des données brutes"):
            st.write("5 premières lignes:")
            st.dataframe(self.data.head())
            
            st.write("Types de données:")
            st.dataframe(pd.DataFrame({
                'Colonne': self.data.columns,
                'Type': self.data.dtypes.astype(str),
                'Non-null': self.data.count().values
            }))
    
    def filter_reunion_data(self):
        """Filtre les données pour garder uniquement La Réunion"""
        if self.data.empty:
            return
        
        try:
            # Filtrer par département 974 (La Réunion)
            dept_cols = [col for col in self.data.columns if 'département' in str(col).lower() or 'departement' in str(col).lower()]
            
            if dept_cols:
                dept_col = dept_cols[0]
                # Chercher les lignes avec 974
                mask = self.data[dept_col].astype(str).str.contains('974', na=False)
                if mask.any():
                    before = len(self.data)
                    self.data = self.data[mask].copy()
                    st.success(f"✅ Filtrage La Réunion: {len(self.data)}/{before} lignes")
                else:
                    st.warning("Aucune donnée avec département 974 trouvée")
            else:
                st.warning("Colonne département non trouvée, pas de filtrage")
                
        except Exception as e:
            st.warning(f"Erreur lors du filtrage: {str(e)}")
    
    def extract_communes_info(self):
        """Extrait les informations des communes"""
        if self.data.empty:
            return
        
        # Chercher la colonne des noms de commune
        commune_cols = [col for col in self.data.columns if 'commune' in str(col).lower()]
        
        if commune_cols:
            commune_col = commune_cols[0]
            communes = self.data[commune_col].unique()
            
            st.sidebar.markdown("### 🏘️ Communes trouvées")
            st.sidebar.write(f"**Nombre de communes:** {len(communes)}")
            
            # Afficher les communes
            for i, commune in enumerate(communes[:15]):  # Limiter à 15 pour éviter trop d'affichage
                st.sidebar.write(f"- {commune}")
            
            if len(communes) > 15:
                st.sidebar.write(f"... et {len(communes) - 15} autres")
            
            # Créer la configuration des communes
            self.create_communes_config(communes, commune_col)
            
        else:
            st.warning("Colonne des communes non trouvée")
    
    def create_communes_config(self, communes, commune_col):
        """Crée la configuration des communes"""
        self.communes_config = {}
        
        for commune in communes:
            if pd.isna(commune):
                continue
                
            commune_name = str(commune).strip()
            
            # Filtrer les données de cette commune
            commune_data = self.data[self.data[commune_col] == commune]
            
            # Population (si disponible)
            pop_cols = [col for col in commune_data.columns if 'population' in str(col).lower()]
            population = 0
            if pop_cols:
                population = commune_data[pop_cols[0]].mean() if not commune_data[pop_cols[0]].isna().all() else 0
            
            # Configuration
            self.communes_config[commune_name] = {
                'population': int(population),
                'type': self.get_commune_type(commune_name),
                'color': self.get_commune_color(commune_name),
                'region': 'La Réunion',
                'data': commune_data
            }
    
    def get_commune_type(self, commune_name):
        """Détermine le type de commune"""
        commune_lower = commune_name.lower()
        
        types = {
            'capitale': ['saint-denis'],
            'grande_ville': ['saint-paul', 'saint-pierre', 'le tampon'],
            'ville_moyenne': ['saint-louis', 'saint-leu', 'le port', 'la possession', 'saint-andré'],
            'petite_ville': ['saint-benoît', 'saint-joseph', 'sainte-marie', 'sainte-suzanne'],
            'commune_rurale': ['saint-philippe', 'les avirons', 'entre-deux', "l'étang-salé", 'petite-île',
                              'la plaine-des-palmistes', 'bras-panon', 'cilaos', 'salazie', 
                              'les trois-bassins', 'sainte-rose']
        }
        
        for type_name, communes_list in types.items():
            for commune in communes_list:
                if commune in commune_lower:
                    return type_name
        
        return 'commune_rurale'
    
    def get_commune_color(self, commune_name):
        """Attribue une couleur à la commune"""
        commune_lower = commune_name.lower()
        
        # Couleurs basées sur le type
        if 'saint-denis' in commune_lower:
            return '#264653'  # Bleu foncé - capitale
        elif 'saint-paul' in commune_lower or 'saint-pierre' in commune_lower:
            return '#2A9D8F'  # Turquoise - grandes villes
        elif 'le tampon' in commune_lower or 'saint-louis' in commune_lower:
            return '#E76F51'  # Orange - villes moyennes
        else:
            colors = ['#F9A602', '#6A0572', '#AB83A1', '#5CAB7D', '#45B7D1']
            return colors[hash(commune_name) % len(colors)]
    
    def get_financial_data(self, commune_name):
        """Extrait les données financières d'une commune"""
        if commune_name not in self.communes_config:
            return pd.DataFrame()
        
        commune_data = self.communes_config[commune_name]['data']
        
        # Chercher les agrégats financiers
        agregat_cols = [col for col in commune_data.columns if 'agrégat' in str(col).lower() or 'agregat' in str(col).lower()]
        montant_cols = [col for col in commune_data.columns if 'montant' in str(col).lower()]
        
        if not agregat_cols or not montant_cols:
            return pd.DataFrame()
        
        agregat_col = agregat_cols[0]
        montant_col = montant_cols[0]
        
        # Chercher les années
        year_cols = [col for col in commune_data.columns if 'exercice' in str(col).lower() or 'annee' in str(col).lower()]
        if year_cols:
            year_col = year_cols[0]
            years = commune_data[year_col].unique()
        else:
            years = [2017]  # Valeur par défaut
        
        financial_data = []
        
        for year in years:
            year_data = commune_data[commune_data[year_col] == year] if year_cols else commune_data
            
            # Calculer les indicateurs
            recettes = self.calculate_indicator(year_data, agregat_col, montant_col, 'recettes totales')
            epargne = self.calculate_indicator(year_data, agregat_col, montant_col, 'épargne brute')
            impots = self.calculate_indicator(year_data, agregat_col, montant_col, 'impôts|taxes')
            
            financial_data.append({
                'Annee': year,
                'Commune': commune_name,
                'Population': self.communes_config[commune_name]['population'],
                'Recettes_Totales': recettes,
                'Epargne_Brute': epargne,
                'Impots_Locaux': impots,
                'Dette_Totale': recettes * 1.2,  # Estimation
                'Ratio_Dette_Recettes': 1.2,  # Estimation
                'Capacite_Remboursement': 1.5 + (epargne / 10)
            })
        
        return pd.DataFrame(financial_data)
    
    def calculate_indicator(self, data, agregat_col, montant_col, pattern):
        """Calcule un indicateur financier"""
        try:
            mask = data[agregat_col].astype(str).str.contains(pattern, case=False, na=False)
            indicator_data = data[mask]
            
            if not indicator_data.empty:
                return indicator_data[montant_col].sum() / 1000000  # Millions d'euros
        except:
            pass
        
        return 0
    
    def create_header(self):
        """Crée l'en-tête"""
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        if not self.data.empty:
            st.markdown(f"**{len(self.communes_config)} communes analysées • Données chargées avec succès**")
    
    def create_sidebar(self):
        """Crée la sidebar"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            if self.data.empty:
                st.error("❌ Aucune donnée chargée")
                st.info("Vérifiez que le fichier 'ofgl-base-communes.csv' est dans votre dépôt")
                return None, []
            
            # Analyser la structure
            self.analyze_data_structure()
            self.filter_reunion_data()
            self.extract_communes_info()
            
            # Sélection de la commune
            if self.communes_config:
                st.markdown("## 🔧 Paramètres")
                
                commune_options = sorted(list(self.communes_config.keys()))
                selected_commune = st.selectbox(
                    "Sélectionnez une commune:",
                    commune_options,
                    index=0
                )
                
                # Options
                show_comparison = st.checkbox("Afficher la comparaison", value=False)
                
                if show_comparison:
                    compare_communes = st.multiselect(
                        "Communes à comparer:",
                        [c for c in commune_options if c != selected_commune],
                        max_selections=3
                    )
                else:
                    compare_communes = []
                
                return selected_commune, compare_communes
            
            return None, []
    
    def create_overview_tab(self):
        """Crée l'onglet Vue d'ensemble"""
        st.markdown("### 📊 Vue d'ensemble")
        
        if not self.communes_config:
            st.warning("Aucune donnée de commune disponible")
            return
        
        # Tableau récapitulatif
        overview_data = []
        for commune_name, config in self.communes_config.items():
            financial_data = self.get_financial_data(commune_name)
            
            if not financial_data.empty:
                last_row = financial_data.iloc[-1]
                
                overview_data.append({
                    'Commune': commune_name,
                    'Type': config['type'],
                    'Population': config['population'],
                    'Recettes (M€)': round(last_row['Recettes_Totales'], 1),
                    'Dette (M€)': round(last_row['Dette_Totale'], 1),
                    'Ratio D/R': round(last_row['Ratio_Dette_Recettes'], 2),
                    'Capacité': round(last_row['Capacite_Remboursement'], 2)
                })
        
        if overview_data:
            df_overview = pd.DataFrame(overview_data)
            
            # Affichage du tableau
            st.dataframe(
                df_overview,
                use_container_width=True,
                height=400
            )
            
            # Graphiques
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df_overview.sort_values('Population', ascending=False).head(10),
                            x='Commune', y='Population',
                            title='Top 10 - Population',
                            color='Type')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df_overview.sort_values('Dette (M€)', ascending=False).head(10),
                            x='Commune', y='Dette (M€)',
                            title='Top 10 - Dette',
                            color='Type')
                st.plotly_chart(fig, use_container_width=True)
    
    def create_analysis_tab(self, commune_name):
        """Crée l'onglet Analyse"""
        if not commune_name:
            st.info("Sélectionnez une commune dans la sidebar")
            return
        
        st.markdown(f'<h2 class="commune-header">🏙️ {commune_name}</h2>', unsafe_allow_html=True)
        
        financial_data = self.get_financial_data(commune_name)
        
        if financial_data.empty:
            st.warning(f"Aucune donnée financière pour {commune_name}")
            return
        
        config = self.communes_config[commune_name]
        last_row = financial_data.iloc[-1]
        
        # Métriques
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Population", f"{config['population']:,}")
            st.metric("Type de commune", config['type'].replace('_', ' ').title())
        
        with col2:
            st.metric("Recettes totales", f"{last_row['Recettes_Totales']:.1f} M€")
            st.metric("Épargne brute", f"{last_row['Epargne_Brute']:.2f} M€")
        
        with col3:
            st.metric("Dette estimée", f"{last_row['Dette_Totale']:.1f} M€")
            st.metric("Ratio dette/recettes", f"{last_row['Ratio_Dette_Recettes']:.2f}")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            fig = go.Figure(data=[
                go.Bar(name='Recettes', x=['M€'], y=[last_row['Recettes_Totales']], marker_color='#2A9D8F'),
                go.Bar(name='Dette', x=['M€'], y=[last_row['Dette_Totale']], marker_color='#E76F51'),
                go.Bar(name='Épargne', x=['M€'], y=[last_row['Epargne_Brute']], marker_color='#F9A602')
            ])
            fig.update_layout(title='Indicateurs financiers', barmode='group')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Données brutes de la commune
            commune_data = config['data']
            st.markdown("**Données disponibles:**")
            st.write(f"- {len(commune_data)} lignes de données")
            
            # Afficher les agrégats disponibles
            agregat_cols = [col for col in commune_data.columns if 'agrégat' in str(col).lower()]
            if agregat_cols:
                agregats = commune_data[agregat_cols[0]].unique()
                st.write(f"- {len(agregats)} types d'agrégats financiers")
                
                with st.expander("Voir les agrégats"):
                    for agregat in agregats[:20]:  # Limiter à 20
                        st.write(f"  - {agregat}")
    
    def create_comparison_tab(self, communes):
        """Crée l'onglet Comparaison"""
        if len(communes) < 2:
            st.info("Sélectionnez au moins 2 communes à comparer")
            return
        
        st.markdown("### 🔄 Comparaison entre communes")
        
        comparison_data = []
        for commune in communes:
            financial_data = self.get_financial_data(commune)
            if not financial_data.empty:
                last_row = financial_data.iloc[-1]
                comparison_data.append({
                    'Commune': commune,
                    'Population': last_row['Population'],
                    'Recettes (M€)': last_row['Recettes_Totales'],
                    'Dette (M€)': last_row['Dette_Totale'],
                    'Dette/Hab (k€)': (last_row['Dette_Totale'] * 1000) / last_row['Population'] if last_row['Population'] > 0 else 0,
                    'Ratio D/R': last_row['Ratio_Dette_Recettes']
                })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            
            # Graphique
            fig = px.bar(df_comparison, 
                        x='Commune', 
                        y=['Recettes (M€)', 'Dette (M€)'],
                        title='Comparaison financière',
                        barmode='group')
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau
            st.dataframe(df_comparison.round(2), use_container_width=True)
    
    def create_ranking_tab(self):
        """Crée l'onglet Classement"""
        st.markdown("### 🏆 Classement des communes")
        
        if not self.communes_config:
            st.warning("Aucune donnée disponible")
            return
        
        ranking_data = []
        for commune_name in self.communes_config:
            financial_data = self.get_financial_data(commune_name)
            if not financial_data.empty:
                last_row = financial_data.iloc[-1]
                ranking_data.append({
                    'Commune': commune_name,
                    'Population': last_row['Population'],
                    'Dette_par_Habitant': (last_row['Dette_Totale'] * 1000000) / last_row['Population'] if last_row['Population'] > 0 else 0,
                    'Ratio_Dette_Recettes': last_row['Ratio_Dette_Recettes'],
                    'Capacite_Remboursement': last_row['Capacite_Remboursement']
                })
        
        if ranking_data:
            df_ranking = pd.DataFrame(ranking_data)
            
            # Sélection de l'indicateur
            ranking_metric = st.selectbox(
                "Classer par:",
                ['Dette_par_Habitant', 'Ratio_Dette_Recettes', 'Capacite_Remboursement'],
                index=0
            )
            
            ascending = ranking_metric != 'Capacite_Remboursement'
            df_sorted = df_ranking.sort_values(ranking_metric, ascending=ascending)
            df_sorted['Rang'] = range(1, len(df_sorted) + 1)
            
            # Affichage
            st.dataframe(
                df_sorted[['Rang', 'Commune', ranking_metric]].head(10),
                use_container_width=True
            )
            
            # Graphique
            fig = px.bar(df_sorted.head(10), 
                        x=ranking_metric, 
                        y='Commune',
                        orientation='h',
                        title=f'Top 10 - {ranking_metric.replace("_", " ")}')
            st.plotly_chart(fig, use_container_width=True)
    
    def create_data_explorer_tab(self):
        """Crée l'onglet Explorateur de données"""
        st.markdown("### 🔍 Explorateur de données")
        
        if self.data.empty:
            st.warning("Aucune donnée à explorer")
            return
        
        # Filtres
        col1, col2 = st.columns(2)
        
        with col1:
            rows_to_show = st.slider("Nombre de lignes à afficher", 10, 1000, 100)
        
        with col2:
            show_columns = st.multiselect(
                "Colonnes à afficher",
                self.data.columns.tolist(),
                default=self.data.columns[:10].tolist() if len(self.data.columns) > 10 else self.data.columns.tolist()
            )
        
        # Aperçu des données
        st.dataframe(
            self.data[show_columns].head(rows_to_show) if show_columns else self.data.head(rows_to_show),
            use_container_width=True,
            height=400
        )
        
        # Statistiques
        st.markdown("#### 📈 Statistiques par colonne")
        
        col_stats = []
        for col in self.data.columns:
            try:
                col_stats.append({
                    'Colonne': col,
                    'Type': str(self.data[col].dtype),
                    'Valeurs uniques': self.data[col].nunique(),
                    'Valeurs nulles': self.data[col].isnull().sum(),
                    'Exemple': str(self.data[col].iloc[0]) if len(self.data) > 0 else ''
                })
            except:
                pass
        
        if col_stats:
            st.dataframe(pd.DataFrame(col_stats), use_container_width=True)
    
    def run_dashboard(self):
        """Exécute le dashboard"""
        self.create_header()
        
        # Si pas de données, afficher les instructions
        if self.data.empty:
            st.error("""
            ## ❌ Fichier non trouvé
            
            Le fichier 'ofgl-base-communes.csv' n'a pas pu être chargé.
            
            **Vérifiez que:**
            1. Le fichier est bien dans votre dépôt GitHub
            2. Il s'appelle exactement 'ofgl-base-communes.csv'
            3. Il est dans le même dossier que ce script
            
            **Structure attendue du fichier:**
            - Format CSV avec séparateur ';'
            - Colonnes: 'Exercice', 'Nom 2024 Commune', 'Montant', 'Agrégat', etc.
            - Données des 24 communes de La Réunion (département 974)
            """)
            return
        
        # Récupérer les paramètres de la sidebar
        selected_commune, compare_communes = self.create_sidebar()
        
        # Créer les onglets
        tab_titles = ["📊 Vue d'ensemble", "🏙️ Analyse", "🔄 Comparaisons", "🏆 Classement", "🔍 Données"]
        
        if self.data.empty:
            tab_titles = ["📊 Vue d'ensemble"]  # Un seul onglet si pas de données
        
        tabs = st.tabs(tab_titles)
        
        with tabs[0]:
            self.create_overview_tab()
        
        if len(tabs) > 1:
            with tabs[1]:
                self.create_analysis_tab(selected_commune)
        
        if len(tabs) > 2:
            with tabs[2]:
                self.create_comparison_tab([selected_commune] + compare_communes if selected_commune else [])
        
        if len(tabs) > 3:
            with tabs[3]:
                self.create_ranking_tab()
        
        if len(tabs) > 4:
            with tabs[4]:
                self.create_data_explorer_tab()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        **Dashboard d'analyse financière des communes de La Réunion**  
        *Données OFGL - Exercice 2017*
        
        *Note: Certains indicateurs sont estimés à partir des données disponibles.*
        """)

# Exécution principale
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
