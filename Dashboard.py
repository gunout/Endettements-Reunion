import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
    .stDataFrame {
        max-height: 600px !important;
        overflow-y: auto !important;
    }
    .dataframe {
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

class ReunionFinancialDashboard:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', '#95E1D3', '#FCE38A', '#EAFFD0']
        
        # Initialiser les données
        self.data = pd.DataFrame()
        self.communes_config = {}
        self.annual_data = {}
        
        # Essayer de charger le fichier local
        self.load_local_file()
        
        # Liste des communes de La Réunion
        self.reunion_communes = [
            "Saint-Denis", "Saint-Paul", "Saint-Pierre", "Le Tampon", "Saint-Louis",
            "Saint-Leu", "Le Port", "La Possession", "Saint-André", "Saint-Benoît",
            "Saint-Joseph", "Sainte-Marie", "Sainte-Suzanne", "Saint-Philippe",
            "Les Avirons", "Entre-Deux", "L'Étang-Salé", "Petite-Île",
            "La Plaine-des-Palmistes", "Bras-Panon", "Cilaos", "Salazie",
            "Les Trois-Bassins", "Sainte-Rose"
        ]
    
    def load_local_file(self):
        """Charge le fichier CSV local depuis le dépôt GitHub"""
        try:
            # Chemin du fichier dans votre dépôt
            file_path = "ofgl-base-communes.csv"
            
            # Vérifier si le fichier existe
            if os.path.exists(file_path):
                st.info(f"📂 Chargement du fichier: {file_path}")
                
                # Essayer différents encodings
                encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252', 'utf-8-sig']
                
                for encoding in encodings:
                    try:
                        self.data = pd.read_csv(file_path, sep=';', encoding=encoding, low_memory=False)
                        if not self.data.empty:
                            st.success(f"✅ Fichier chargé avec succès! {len(self.data):,} lignes, {len(self.data.columns)} colonnes")
                            st.info(f"📅 Plage temporelle: {self.data['Exercice'].min() if 'Exercice' in self.data.columns else 'N/A'} - {self.data['Exercice'].max() if 'Exercice' in self.data.columns else 'N/A'}")
                            break
                    except UnicodeDecodeError:
                        continue
                    except Exception as e:
                        st.warning(f"⚠️ Erreur avec {encoding}: {str(e)}")
                        continue
                
                # Si toujours vide, essayer avec auto-détection
                if self.data.empty:
                    try:
                        self.data = pd.read_csv(file_path, sep=None, engine='python', on_bad_lines='skip')
                        st.success(f"✅ Fichier chargé avec auto-détection")
                    except Exception as e:
                        st.error(f"❌ Impossible de charger le fichier: {str(e)}")
            
            else:
                st.warning(f"⚠️ Fichier non trouvé: {file_path}")
                
        except Exception as e:
            st.error(f"❌ Erreur lors du chargement: {str(e)}")
    
    def analyze_data_structure(self):
        """Analyse la structure des données"""
        if self.data.empty:
            return
        
        with st.sidebar.expander("📊 Structure des données", expanded=False):
            st.write(f"**📈 Lignes totales:** {len(self.data):,}")
            st.write(f"**📊 Colonnes totales:** {len(self.data.columns)}")
            
            # Informations sur les années
            if 'Exercice' in self.data.columns:
                years = sorted(self.data['Exercice'].dropna().unique())
                st.write(f"**📅 Années disponibles:** {len(years)}")
                st.write(f"De {int(min(years))} à {int(max(years))}" if years else "N/A")
            
            # Aperçu des données
            st.write("**👁️ Aperçu des colonnes:**")
            cols_df = pd.DataFrame({
                'Colonne': self.data.columns,
                'Type': self.data.dtypes.astype(str),
                'Non-null': self.data.count().values,
                '% Rempli': (self.data.count().values / len(self.data) * 100).round(1)
            })
            st.dataframe(cols_df.head(15), height=300, use_container_width=True)
            
            if len(self.data.columns) > 15:
                st.write(f"... et {len(self.data.columns) - 15} autres colonnes")
    
    def prepare_financial_data(self):
        """Prépare les données financières pour analyse"""
        if self.data.empty:
            return
        
        # Identifier les colonnes importantes
        montant_col = None
        agregat_col = None
        commune_col = None
        exercice_col = None
        
        for col in self.data.columns:
            col_lower = str(col).lower()
            if 'montant' in col_lower and montant_col is None:
                montant_col = col
            elif ('agrégat' in col_lower or 'agregat' in col_lower) and agregat_col is None:
                agregat_col = col
            elif 'commune' in col_lower and commune_col is None:
                commune_col = col
            elif 'exercice' in col_lower and exercice_col is None:
                exercice_col = col
        
        # Si certaines colonnes ne sont pas trouvées, utiliser les premières correspondantes
        if not all([montant_col, agregat_col, commune_col, exercice_col]):
            st.warning("⚠️ Certaines colonnes clés n'ont pas été trouvées automatiquement")
            # Fallback: utiliser les premières colonnes de chaque type
            montant_col = montant_col or self.data.columns[2] if len(self.data.columns) > 2 else None
            agregat_col = agregat_col or self.data.columns[3] if len(self.data.columns) > 3 else None
            commune_col = commune_col or self.data.columns[0] if len(self.data.columns) > 0 else None
            exercice_col = exercice_col or self.data.columns[1] if len(self.data.columns) > 1 else None
        
        # Vérifier et préparer les données
        required_cols = [montant_col, agregat_col, commune_col, exercice_col]
        if all(required_cols):
            try:
                # Nettoyer les données
                financial_df = self.data[[commune_col, exercice_col, agregat_col, montant_col]].copy()
                financial_df.columns = ['Commune', 'Exercice', 'Agregat', 'Montant']
                
                # Convertir les types
                financial_df['Exercice'] = pd.to_numeric(financial_df['Exercice'], errors='coerce')
                financial_df['Montant'] = pd.to_numeric(financial_df['Montant'], errors='coerce')
                financial_df['Agregat'] = financial_df['Agregat'].astype(str)
                financial_df['Commune'] = financial_df['Commune'].astype(str)
                
                # Filtrer pour La Réunion
                financial_df = financial_df[financial_df['Commune'].str.contains('|'.join(self.reunion_communes), case=False, na=False)]
                
                # Créer des indicateurs financiers
                self.create_financial_indicators(financial_df)
                
            except Exception as e:
                st.error(f"❌ Erreur lors de la préparation des données: {str(e)}")
    
    def create_financial_indicators(self, df):
        """Crée les indicateurs financiers agrégés par commune et année"""
        try:
            # Pivoter les données pour avoir les agrégats en colonnes
            pivot_df = df.pivot_table(
                index=['Commune', 'Exercice'],
                columns='Agregat',
                values='Montant',
                aggfunc='sum'
            ).reset_index()
            
            # Remplacer les NaN par 0
            pivot_df = pivot_df.fillna(0)
            
            # Normaliser les noms des colonnes
            pivot_df.columns = [str(col).strip() for col in pivot_df.columns]
            
            # Stocker les données annuelles
            self.annual_data = pivot_df
            
            # Créer la configuration des communes
            self.create_communes_config(pivot_df)
            
            st.success(f"✅ Données financières préparées: {len(pivot_df)} enregistrements")
            
        except Exception as e:
            st.error(f"❌ Erreur dans create_financial_indicators: {str(e)}")
    
    def create_communes_config(self, df):
        """Crée la configuration des communes"""
        self.communes_config = {}
        
        for commune in df['Commune'].unique():
            if pd.isna(commune):
                continue
                
            commune_name = str(commune).strip()
            
            # Données de cette commune
            commune_data = df[df['Commune'] == commune_name]
            
            # Obtenir les années disponibles
            years = sorted(commune_data['Exercice'].unique())
            
            # Calculer les statistiques par année
            annual_stats = {}
            for year in years:
                year_data = commune_data[commune_data['Exercice'] == year]
                
                # Extraire les indicateurs clés (en supposant certaines colonnes)
                recettes = 0
                depenses = 0
                dette = 0
                
                for col in year_data.columns:
                    col_lower = str(col).lower()
                    if 'recette' in col_lower and 'total' in col_lower:
                        recettes = year_data[col].sum() / 1000000  # En millions
                    elif 'dépense' in col_lower and 'total' in col_lower:
                        depenses = year_data[col].sum() / 1000000  # En millions
                    elif 'dette' in col_lower:
                        dette = year_data[col].sum() / 1000000  # En millions
                
                annual_stats[year] = {
                    'recettes': recettes,
                    'depenses': depenses,
                    'dette': dette,
                    'epargne': recettes - depenses if recettes and depenses else 0,
                    'ratio_dette_recettes': dette / recettes if recettes > 0 else 0
                }
            
            # Configuration de la commune
            self.communes_config[commune_name] = {
                'nom': commune_name,
                'annees': years,
                'stats_annuelles': annual_stats,
                'derniere_annee': max(years) if years else None,
                'type': self.get_commune_type(commune_name),
                'couleur': self.get_commune_color(commune_name)
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
        elif any(commune in commune_lower for commune in ['saint-ben', 'saint-joseph', 'sainte-marie']):
            return '#F9A602'  # Jaune - petites villes
        else:
            colors = ['#6A0572', '#AB83A1', '#5CAB7D', '#45B7D1', '#95E1D3']
            return colors[hash(commune_name) % len(colors)]
    
    def create_header(self):
        """Crée l'en-tête"""
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        if not self.data.empty:
            st.markdown(f"""
            **📊 {len(self.communes_config)} communes analysées • 📅 Données historiques • 🔍 Analyse temporelle complète**
            """)
    
    def create_sidebar(self):
        """Crée la sidebar avec tous les contrôles"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            if self.data.empty:
                st.error("❌ Aucune donnée chargée")
                st.info("Vérifiez que le fichier 'ofgl-base-communes.csv' est dans votre dépôt")
                return None, None, []
            
            # Analyser la structure des données
            self.analyze_data_structure()
            
            # Préparer les données financières
            self.prepare_financial_data()
            
            if self.communes_config:
                st.markdown("## 🔧 Paramètres d'analyse")
                
                # Sélection des années
                st.markdown("### 📅 Sélection temporelle")
                all_years = []
                for commune in self.communes_config.values():
                    all_years.extend(commune['annees'])
                available_years = sorted(list(set(all_years)))
                
                if available_years:
                    year_range = st.slider(
                        "Période d'analyse",
                        min_value=int(min(available_years)),
                        max_value=int(max(available_years)),
                        value=(int(min(available_years)), int(max(available_years)))
                    )
                else:
                    year_range = (2017, 2023)
                    st.warning("Aucune année trouvée, utilisation des valeurs par défaut")
                
                # Sélection de la commune principale
                st.markdown("### 🏘️ Sélection des communes")
                commune_options = sorted(list(self.communes_config.keys()))
                
                selected_commune = st.selectbox(
                    "Commune principale:",
                    commune_options,
                    index=0 if 'Saint-Denis' in commune_options else 0
                )
                
                # Sélection des communes à comparer
                st.markdown("#### 🔄 Communes à comparer")
                compare_communes = st.multiselect(
                    "Sélectionnez jusqu'à 5 communes:",
                    [c for c in commune_options if c != selected_commune],
                    default=[],
                    max_selections=5
                )
                
                # Type d'analyse
                st.markdown("#### 📈 Type d'analyse")
                analysis_type = st.selectbox(
                    "Mode d'analyse:",
                    ["Analyse détaillée", "Comparaison multi-années", "Évolution temporelle", "Indicateurs clés"],
                    index=0
                )
                
                # Indicateurs à afficher
                st.markdown("#### 📊 Indicateurs")
                indicators = st.multiselect(
                    "Indicateurs financiers:",
                    ["Recettes", "Dépenses", "Dette", "Épargne", "Ratio Dette/Recettes"],
                    default=["Recettes", "Dette", "Épargne"]
                )
                
                return selected_commune, year_range, compare_communes, analysis_type, indicators
            
            return None, None, [], None, []
    
    def create_overview_tab(self):
        """Crée l'onglet Vue d'ensemble avec toutes les données"""
        st.markdown("### 📊 Vue d'ensemble complète des 24 communes")
        
        if not self.communes_config:
            st.warning("Aucune donnée de commune disponible")
            return
        
        # Tableau récapitulatif avec TOUTES les données
        overview_data = []
        
        for commune_name, config in self.communes_config.items():
            years = config['annees']
            stats = config['stats_annuelles']
            
            if years and stats:
                # Moyenne sur toutes les années
                avg_recettes = np.mean([stats[y]['recettes'] for y in years if y in stats])
                avg_dette = np.mean([stats[y]['dette'] for y in years if y in stats])
                avg_epargne = np.mean([stats[y]['epargne'] for y in years if y in stats])
                
                # Dernière année disponible
                last_year = max(years)
                last_stats = stats.get(last_year, {})
                
                overview_data.append({
                    'Commune': commune_name,
                    'Type': config['type'].replace('_', ' ').title(),
                    'Années': len(years),
                    'Dernière année': last_year,
                    'Recettes moy (M€)': round(avg_recettes, 1),
                    'Dette moy (M€)': round(avg_dette, 1),
                    'Épargne moy (M€)': round(avg_epargne, 1),
                    'Recettes dernière année (M€)': round(last_stats.get('recettes', 0), 1),
                    'Dette dernière année (M€)': round(last_stats.get('dette', 0), 1),
                    'Ratio D/R': round(last_stats.get('ratio_dette_recettes', 0), 2)
                })
        
        if overview_data:
            df_overview = pd.DataFrame(overview_data)
            
            # Afficher TOUTES les données sans limite
            st.markdown(f"#### 📋 Tableau complet ({len(df_overview)} communes)")
            st.dataframe(
                df_overview,
                use_container_width=True,
                height=600  # Hauteur fixe avec scroll
            )
            
            # Options d'export
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📥 Exporter en CSV"):
                    csv = df_overview.to_csv(index=False, sep=';')
                    st.download_button(
                        label="Télécharger CSV",
                        data=csv,
                        file_name="communes_reunion_complet.csv",
                        mime="text/csv"
                    )
            
            # Graphiques de synthèse
            st.markdown("#### 📈 Visualisations synthétiques")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top 10 par dette moyenne
                top_dette = df_overview.sort_values('Dette moy (M€)', ascending=False).head(10)
                fig = px.bar(top_dette,
                            x='Commune', y='Dette moy (M€)',
                            title='Top 10 - Dette moyenne (M€)',
                            color='Type',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Top 10 par épargne moyenne
                top_epargne = df_overview.sort_values('Épargne moy (M€)', ascending=False).head(10)
                fig = px.bar(top_epargne,
                            x='Commune', y='Épargne moy (M€)',
                            title='Top 10 - Épargne moyenne (M€)',
                            color='Type',
                            color_discrete_sequence=px.colors.qualitative.Set2)
                st.plotly_chart(fig, use_container_width=True)
            
            # Matrice de corrélation entre indicateurs
            st.markdown("#### 🔗 Relations entre indicateurs")
            
            numeric_cols = ['Recettes moy (M€)', 'Dette moy (M€)', 'Épargne moy (M€)', 'Ratio D/R']
            corr_df = df_overview[numeric_cols].corr()
            
            fig = px.imshow(corr_df,
                           text_auto='.2f',
                           aspect='auto',
                           title='Matrice de corrélation',
                           color_continuous_scale='RdBu_r')
            st.plotly_chart(fig, use_container_width=True)
    
    def create_analysis_tab(self, commune_name, year_range, indicators):
        """Crée l'onglet Analyse détaillée"""
        if not commune_name:
            st.info("Sélectionnez une commune dans la sidebar")
            return
        
        st.markdown(f'<h2 class="commune-header">🏙️ Analyse détaillée - {commune_name}</h2>', 
                   unsafe_allow_html=True)
        
        if commune_name not in self.communes_config:
            st.warning(f"Commune {commune_name} non trouvée dans les données")
            return
        
        config = self.communes_config[commune_name]
        years = [y for y in config['annees'] if year_range[0] <= y <= year_range[1]]
        
        if not years:
            st.warning(f"Aucune donnée pour {commune_name} dans la période {year_range[0]}-{year_range[1]}")
            return
        
        # Métriques principales
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("📅 Période analysée", f"{year_range[0]}-{year_range[1]}")
            st.metric("🏘️ Type", config['type'].replace('_', ' ').title())
        
        with col2:
            last_year = max(years)
            last_stats = config['stats_annuelles'].get(last_year, {})
            st.metric("💰 Recettes", f"{last_stats.get('recettes', 0):.1f} M€")
            st.metric("📈 Tendance", "▲ Croissante" if len(years) > 1 and 
                     config['stats_annuelles'][years[-1]].get('recettes', 0) > 
                     config['stats_annuelles'][years[-2]].get('recettes', 0) else "▼ Décroissante")
        
        with col3:
            st.metric("💸 Dette", f"{last_stats.get('dette', 0):.1f} M€")
            st.metric("📊 Ratio D/R", f"{last_stats.get('ratio_dette_recettes', 0):.2f}")
        
        with col4:
            st.metric("💎 Épargne", f"{last_stats.get('epargne', 0):.1f} M€")
            st.metric("📅 Années dispo", len(years))
        
        # Graphiques d'évolution temporelle
        st.markdown("#### 📈 Évolution temporelle")
        
        # Préparer les données pour les graphiques
        evolution_data = []
        for year in years:
            stats = config['stats_annuelles'].get(year, {})
            evolution_data.append({
                'Année': year,
                'Recettes (M€)': stats.get('recettes', 0),
                'Dépenses (M€)': stats.get('depenses', 0),
                'Dette (M€)': stats.get('dette', 0),
                'Épargne (M€)': stats.get('epargne', 0),
                'Ratio D/R': stats.get('ratio_dette_recettes', 0)
            })
        
        df_evolution = pd.DataFrame(evolution_data)
        
        # Graphique 1: Évolution des recettes et dépenses
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Recettes (M€)'],
                                 mode='lines+markers', name='Recettes', line=dict(color='#2A9D8F', width=3)))
        fig1.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Dépenses (M€)'],
                                 mode='lines+markers', name='Dépenses', line=dict(color='#E76F51', width=3)))
        fig1.update_layout(title='Évolution des recettes et dépenses',
                          xaxis_title='Année',
                          yaxis_title='Montant (M€)',
                          hovermode='x unified')
        st.plotly_chart(fig1, use_container_width=True)
        
        # Graphique 2: Évolution de la dette et du ratio
        fig2 = make_subplots(specs=[[{"secondary_y": True}]])
        fig2.add_trace(go.Bar(x=df_evolution['Année'], y=df_evolution['Dette (M€)'],
                             name='Dette (M€)', marker_color='#F9A602'),
                      secondary_y=False)
        fig2.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Ratio D/R'],
                                 mode='lines+markers', name='Ratio D/R', line=dict(color='#6A0572', width=3)),
                      secondary_y=True)
        fig2.update_layout(title='Évolution de la dette et du ratio dette/recettes',
                          xaxis_title='Année')
        fig2.update_yaxes(title_text="Dette (M€)", secondary_y=False)
        fig2.update_yaxes(title_text="Ratio D/R", secondary_y=True)
        st.plotly_chart(fig2, use_container_width=True)
        
        # Tableau détaillé par année
        st.markdown("#### 📋 Données annuelles détaillées")
        st.dataframe(df_evolution.round(2), use_container_width=True, height=400)
    
    def create_comparison_tab(self, communes, year_range, indicators):
        """Crée l'onglet Comparaison entre communes"""
        if len(communes) < 2:
            st.info("Sélectionnez au moins 2 communes à comparer dans la sidebar")
            return
        
        st.markdown(f"### 🔄 Comparaison entre {len(communes)} communes")
        
        comparison_data = []
        for commune in communes:
            if commune in self.communes_config:
                config = self.communes_config[commune]
                years = [y for y in config['annees'] if year_range[0] <= y <= year_range[1]]
                
                if years:
                    # Calculer les moyennes sur la période
                    stats_list = [config['stats_annuelles'][y] for y in years if y in config['stats_annuelles']]
                    
                    if stats_list:
                        avg_recettes = np.mean([s.get('recettes', 0) for s in stats_list])
                        avg_dette = np.mean([s.get('dette', 0) for s in stats_list])
                        avg_epargne = np.mean([s.get('epargne', 0) for s in stats_list])
                        avg_ratio = np.mean([s.get('ratio_dette_recettes', 0) for s in stats_list])
                        
                        comparison_data.append({
                            'Commune': commune,
                            'Type': config['type'].replace('_', ' ').title(),
                            'Années analysées': len(years),
                            'Recettes moy (M€)': round(avg_recettes, 1),
                            'Dette moy (M€)': round(avg_dette, 1),
                            'Épargne moy (M€)': round(avg_epargne, 1),
                            'Ratio D/R moy': round(avg_ratio, 2),
                            'Dette/Hab (k€)': round((avg_dette * 1000) / 50000, 1) if avg_dette else 0  # Estimation
                        })
        
        if comparison_data:
            df_comparison = pd.DataFrame(comparison_data)
            
            # Graphique de comparaison
            fig = px.bar(df_comparison,
                        x='Commune',
                        y=['Recettes moy (M€)', 'Dette moy (M€)', 'Épargne moy (M€)'],
                        title=f'Comparaison financière ({year_range[0]}-{year_range[1]})',
                        barmode='group',
                        color_discrete_sequence=['#2A9D8F', '#E76F51', '#F9A602'])
            st.plotly_chart(fig, use_container_width=True)
            
            # Graphique radar pour comparaison multi-dimensionnelle
            st.markdown("#### 📊 Comparaison multi-dimensionnelle (Radar)")
            
            # Normaliser les données pour le radar
            radar_data = []
            for idx, row in df_comparison.iterrows():
                radar_data.append({
                    'Commune': row['Commune'],
                    'Recettes': row['Recettes moy (M€)'] / df_comparison['Recettes moy (M€)'].max() * 100,
                    'Dette': row['Dette moy (M€)'] / df_comparison['Dette moy (M€)'].max() * 100 if df_comparison['Dette moy (M€)'].max() > 0 else 0,
                    'Épargne': row['Épargne moy (M€)'] / df_comparison['Épargne moy (M€)'].max() * 100 if df_comparison['Épargne moy (M€)'].max() > 0 else 0,
                    'Ratio': (1 - row['Ratio D/R moy'] / df_comparison['Ratio D/R moy'].max()) * 100 if df_comparison['Ratio D/R moy'].max() > 0 else 0
                })
            
            df_radar = pd.DataFrame(radar_data)
            
            fig_radar = go.Figure()
            for idx, row in df_radar.iterrows():
                fig_radar.add_trace(go.Scatterpolar(
                    r=[row['Recettes'], row['Dette'], row['Épargne'], row['Ratio'], row['Recettes']],
                    theta=['Recettes', 'Dette', 'Épargne', 'Ratio', 'Recettes'],
                    name=row['Commune'],
                    fill='toself'
                ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100]
                    )
                ),
                showlegend=True,
                title="Profil financier comparé (normalisé)"
            )
            st.plotly_chart(fig_radar, use_container_width=True)
            
            # Tableau de comparaison
            st.markdown("#### 📋 Tableau comparatif")
            st.dataframe(df_comparison, use_container_width=True, height=400)
            
            # Analyse des écarts
            st.markdown("#### 📈 Analyse des écarts")
            col1, col2 = st.columns(2)
            
            with col1:
                max_recettes = df_comparison.loc[df_comparison['Recettes moy (M€)'].idxmax()]
                st.info(f"**🏆 Meilleures recettes:** {max_recettes['Commune']} ({max_recettes['Recettes moy (M€)']} M€)")
            
            with col2:
                min_ratio = df_comparison.loc[df_comparison['Ratio D/R moy'].idxmin()]
                st.info(f"**✅ Meilleur ratio:** {min_ratio['Commune']} ({min_ratio['Ratio D/R moy']})")
    
    def create_temporal_analysis_tab(self, year_range):
        """Crée l'onglet Analyse temporelle globale"""
        st.markdown("### 📅 Analyse temporelle globale")
        
        if not self.communes_config:
            st.warning("Aucune donnée disponible")
            return
        
        # Agréger les données par année
        yearly_data = {}
        
        for commune, config in self.communes_config.items():
            for year, stats in config['stats_annuelles'].items():
                if year_range[0] <= year <= year_range[1]:
                    if year not in yearly_data:
                        yearly_data[year] = {
                            'recettes': [],
                            'dette': [],
                            'epargne': [],
                            'communes': []
                        }
                    
                    yearly_data[year]['recettes'].append(stats.get('recettes', 0))
                    yearly_data[year]['dette'].append(stats.get('dette', 0))
                    yearly_data[year]['epargne'].append(stats.get('epargne', 0))
                    yearly_data[year]['communes'].append(commune)
        
        # Préparer le DataFrame pour l'analyse
        temporal_data = []
        for year, data in sorted(yearly_data.items()):
            if data['recettes']:
                temporal_data.append({
                    'Année': year,
                    'Recettes moy (M€)': np.mean(data['recettes']),
                    'Dette moy (M€)': np.mean(data['dette']),
                    'Épargne moy (M€)': np.mean(data['epargne']),
                    'Nb communes': len(data['communes']),
                    'Recettes totales (M€)': np.sum(data['recettes']),
                    'Dette totale (M€)': np.sum(data['dette'])
                })
        
        if not temporal_data:
            st.warning("Aucune donnée dans la période sélectionnée")
            return
        
        df_temporal = pd.DataFrame(temporal_data)
        
        # Graphique d'évolution globale
        fig = make_subplots(rows=2, cols=2,
                           subplot_titles=('Évolution des recettes moyennes',
                                         'Évolution de la dette moyenne',
                                         'Évolution de l\'épargne moyenne',
                                         'Nombre de communes par année'))
        
        # Recettes moyennes
        fig.add_trace(go.Scatter(x=df_temporal['Année'], y=df_temporal['Recettes moy (M€)'],
                                mode='lines+markers', name='Recettes moy',
                                line=dict(color='#2A9D8F', width=3)),
                     row=1, col=1)
        
        # Dette moyenne
        fig.add_trace(go.Scatter(x=df_temporal['Année'], y=df_temporal['Dette moy (M€)'],
                                mode='lines+markers', name='Dette moy',
                                line=dict(color='#E76F51', width=3)),
                     row=1, col=2)
        
        # Épargne moyenne
        fig.add_trace(go.Scatter(x=df_temporal['Année'], y=df_temporal['Épargne moy (M€)'],
                                mode='lines+markers', name='Épargne moy',
                                line=dict(color='#F9A602', width=3)),
                     row=2, col=1)
        
        # Nombre de communes
        fig.add_trace(go.Bar(x=df_temporal['Année'], y=df_temporal['Nb communes'],
                            name='Nb communes', marker_color='#6A0572'),
                     row=2, col=2)
        
        fig.update_layout(height=600, showlegend=True, title_text="Évolution temporelle globale")
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des tendances
        st.markdown("#### 📋 Tendance annuelle")
        st.dataframe(df_temporal.round(2), use_container_width=True)
        
        # Calcul des taux de croissance
        if len(df_temporal) > 1:
            st.markdown("#### 📈 Taux de croissance annuels")
            
            growth_data = []
            for i in range(1, len(df_temporal)):
                prev = df_temporal.iloc[i-1]
                curr = df_temporal.iloc[i]
                
                growth_recettes = ((curr['Recettes moy (M€)'] - prev['Recettes moy (M€)']) / prev['Recettes moy (M€)']) * 100 if prev['Recettes moy (M€)'] > 0 else 0
                growth_dette = ((curr['Dette moy (M€)'] - prev['Dette moy (M€)']) / prev['Dette moy (M€)']) * 100 if prev['Dette moy (M€)'] > 0 else 0
                
                growth_data.append({
                    'Période': f"{int(prev['Année'])}-{int(curr['Année'])}",
                    'Δ Recettes (%)': round(growth_recettes, 1),
                    'Δ Dette (%)': round(growth_dette, 1),
                    'Recettes (M€)': round(curr['Recettes moy (M€)'], 1),
                    'Dette (M€)': round(curr['Dette moy (M€)'], 1)
                })
            
            if growth_data:
                df_growth = pd.DataFrame(growth_data)
                st.dataframe(df_growth, use_container_width=True)
    
    def create_data_explorer_tab(self):
        """Crée l'onglet Explorateur de données complet"""
        st.markdown("### 🔍 Explorateur de données complet")
        
        if self.data.empty:
            st.warning("Aucune donnée à explorer")
            return
        
        st.info(f"**Total des données:** {len(self.data):,} lignes × {len(self.data.columns)} colonnes")
        
        # Options de filtrage avancé
        st.markdown("#### 🎯 Filtres avancés")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Filtre par année
            if 'Exercice' in self.data.columns:
                years = sorted(self.data['Exercice'].dropna().unique())
                selected_years = st.multiselect(
                    "Filtrer par année:",
                    years,
                    default=years[:3] if len(years) > 3 else years
                )
            else:
                selected_years = []
        
        with col2:
            # Filtre par commune
            commune_col = None
            for col in self.data.columns:
                if 'commune' in str(col).lower():
                    commune_col = col
                    break
            
            if commune_col:
                communes = sorted(self.data[commune_col].dropna().unique())
                selected_communes = st.multiselect(
                    "Filtrer par commune:",
                    communes,
                    default=communes[:5] if len(communes) > 5 else communes
                )
            else:
                selected_communes = []
        
        with col3:
            # Filtre par colonnes
            all_columns = self.data.columns.tolist()
            selected_columns = st.multiselect(
                "Colonnes à afficher:",
                all_columns,
                default=all_columns[:15] if len(all_columns) > 15 else all_columns
            )
        
        # Appliquer les filtres
        filtered_data = self.data.copy()
        
        if selected_years and 'Exercice' in filtered_data.columns:
            filtered_data = filtered_data[filtered_data['Exercice'].isin(selected_years)]
        
        if selected_communes and commune_col:
            filtered_data = filtered_data[filtered_data[commune_col].isin(selected_communes)]
        
        if selected_columns:
            filtered_data = filtered_data[selected_columns]
        
        # Affichage des données filtrées
        st.markdown(f"#### 📄 Données filtrées ({len(filtered_data):,} lignes)")
        
        # Options d'affichage
        display_mode = st.radio(
            "Mode d'affichage:",
            ["Tableau complet", "Aperçu (1000 lignes)", "Statistiques"],
            horizontal=True
        )
        
        if display_mode == "Tableau complet":
            # Afficher TOUTES les données avec pagination virtuelle
            st.dataframe(
                filtered_data,
                use_container_width=True,
                height=600
            )
            
        elif display_mode == "Aperçu (1000 lignes)":
            st.dataframe(
                filtered_data.head(1000),
                use_container_width=True,
                height=600
            )
            
        else:  # Statistiques
            st.markdown("#### 📊 Statistiques descriptives")
            
            # Statistiques numériques
            numeric_cols = filtered_data.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                st.dataframe(
                    filtered_data[numeric_cols].describe().round(2),
                    use_container_width=True
                )
            
            # Informations sur les colonnes catégorielles
            cat_cols = filtered_data.select_dtypes(include=['object']).columns
            if len(cat_cols) > 0:
                st.markdown("#### 📝 Colonnes catégorielles")
                for col in cat_cols[:5]:  # Limiter à 5 colonnes
                    unique_vals = filtered_data[col].nunique()
                    st.write(f"**{col}:** {unique_vals} valeurs uniques")
                    if unique_vals < 20:
                        st.write(f"Valeurs: {', '.join(map(str, filtered_data[col].dropna().unique()[:10]))}")
                        if unique_vals > 10:
                            st.write("...")
        
        # Options d'export
        st.markdown("#### 📥 Export des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💾 Exporter les données filtrées (CSV)"):
                csv = filtered_data.to_csv(index=False, sep=';', encoding='utf-8-sig')
                st.download_button(
                    label="Télécharger CSV",
                    data=csv,
                    file_name=f"donnees_filtrees_{len(filtered_data)}_lignes.csv",
                    mime="text/csv"
                )
        
        with col2:
            if st.button("📊 Exporter résumé statistique"):
                if len(numeric_cols) > 0:
                    stats = filtered_data[numeric_cols].describe().round(2)
                    csv_stats = stats.to_csv(sep=';', encoding='utf-8-sig')
                    st.download_button(
                        label="Télécharger statistiques",
                        data=csv_stats,
                        file_name="statistiques_resume.csv",
                        mime="text/csv"
                    )
    
    def run_dashboard(self):
        """Exécute le dashboard complet"""
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
            - Colonnes: 'Exercice', 'Nom Commune', 'Montant', 'Agrégat'
            - Données des 24 communes de La Réunion
            """)
            return
        
        # Récupérer les paramètres de la sidebar
        selected_commune, year_range, compare_communes, analysis_type, indicators = self.create_sidebar()
        
        # Créer les onglets
        tab_titles = [
            "📊 Vue d'ensemble", 
            "🏙️ Analyse détaillée", 
            "🔄 Comparaisons", 
            "📅 Évolution temporelle", 
            "🔍 Explorateur de données"
        ]
        
        tabs = st.tabs(tab_titles)
        
        # Onglet 1: Vue d'ensemble (TOUTES les données)
        with tabs[0]:
            self.create_overview_tab()
        
        # Onglet 2: Analyse détaillée
        with tabs[1]:
            if selected_commune:
                self.create_analysis_tab(selected_commune, year_range, indicators)
            else:
                st.info("👈 Sélectionnez une commune dans la sidebar")
        
        # Onglet 3: Comparaisons
        with tabs[2]:
            if selected_commune:
                self.create_comparison_tab([selected_commune] + compare_communes, year_range, indicators)
            else:
                st.info("👈 Sélectionnez des communes à comparer dans la sidebar")
        
        # Onglet 4: Évolution temporelle
        with tabs[3]:
            self.create_temporal_analysis_tab(year_range)
        
        # Onglet 5: Explorateur de données
        with tabs[4]:
            self.create_data_explorer_tab()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        **📊 Dashboard d'analyse financière des communes de La Réunion**  
        *Données OFGL • Analyse temporelle complète • 24 communes analysées*
        
        *Fonctionnalités:*
        - ✅ **Affichage complet** de toutes les données
        - ✅ **Analyse temporelle** par exercice budgétaire
        - ✅ **Comparaison** des 24 communes
        - ✅ **Graphiques interactifs** et visualisations avancées
        - ✅ **Export des données** en CSV
        
        *Note: Les indicateurs sont calculés à partir des données disponibles.*
        """)

# Exécution principale
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
