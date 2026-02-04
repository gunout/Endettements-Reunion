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
                            
                            # Afficher toutes les colonnes pour debugging
                            with st.expander("🔍 Voir toutes les colonnes disponibles", expanded=True):
                                for i, col in enumerate(self.data.columns):
                                    st.write(f"{i+1}. **{col}** - Type: {self.data[col].dtype}, Exemple: {str(self.data[col].iloc[0])[:50] if len(self.data) > 0 else 'N/A'}")
                            
                            # Vérifier les années
                            if 'Exercice' in self.data.columns:
                                years = sorted(self.data['Exercice'].dropna().unique())
                                st.info(f"📅 Plage temporelle: {int(min(years))} - {int(max(years))} ({len(years)} années)")
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
        
        with st.sidebar.expander("📊 Structure des données", expanded=True):
            st.write(f"**📈 Lignes totales:** {len(self.data):,}")
            st.write(f"**📊 Colonnes totales:** {len(self.data.columns)}")
            
            # Identifier automatiquement les colonnes clés
            st.markdown("### 🔑 Colonnes identifiées:")
            
            # Colonne commune
            commune_cols = [col for col in self.data.columns if any(x in str(col).lower() for x in ['commune', 'nom', 'libellé', 'libelle'])]
            if commune_cols:
                st.write(f"**🏘️ Colonne commune:** {commune_cols[0]}")
                sample_communes = self.data[commune_cols[0]].dropna().unique()[:5]
                st.write(f"Exemples: {', '.join(map(str, sample_communes))}")
            
            # Colonne année/exercice
            year_cols = [col for col in self.data.columns if any(x in str(col).lower() for x in ['exercice', 'annee', 'année', 'year'])]
            if year_cols:
                st.write(f"**📅 Colonne année:** {year_cols[0]}")
                years = sorted(self.data[year_cols[0]].dropna().unique())
                st.write(f"Années: {', '.join(map(str, years[:5]))}{'...' if len(years) > 5 else ''}")
            
            # Colonne montant
            montant_cols = [col for col in self.data.columns if any(x in str(col).lower() for x in ['montant', 'valeur', 'euros', '€'])]
            if montant_cols:
                st.write(f"**💰 Colonne montant:** {montant_cols[0]}")
            
            # Colonne agrégat/catégorie
            agregat_cols = [col for col in self.data.columns if any(x in str(col).lower() for x in ['agrégat', 'agregat', 'categorie', 'catégorie', 'rubrique', 'compte'])]
            if agregat_cols:
                st.write(f"**📋 Colonne agrégat:** {agregat_cols[0]}")
                sample_agregats = self.data[agregat_cols[0]].dropna().unique()[:5]
                st.write(f"Exemples: {', '.join(map(str, sample_agregats))}")
            
            # Colonne code INSEE
            code_cols = [col for col in self.data.columns if 'insee' in str(col).lower() or 'code' in str(col).lower()]
            if code_cols:
                st.write(f"**🔢 Colonne code:** {code_cols[0]}")
    
    def prepare_financial_data(self):
        """Prépare les données financières pour analyse"""
        if self.data.empty:
            return
        
        # Interface pour sélectionner manuellement les colonnes
        st.sidebar.markdown("## 🔧 Configuration des colonnes")
        
        # Sélection manuelle des colonnes
        all_columns = self.data.columns.tolist()
        
        commune_col = st.sidebar.selectbox(
            "Sélectionnez la colonne des communes:",
            all_columns,
            index=next((i for i, col in enumerate(all_columns) if 'nom' in str(col).lower() and 'commune' in str(col).lower()), 0)
        )
        
        exercice_col = st.sidebar.selectbox(
            "Sélectionnez la colonne de l'exercice:",
            all_columns,
            index=next((i for i, col in enumerate(all_columns) if 'exercice' in str(col).lower()), 0)
        )
        
        agregat_col = st.sidebar.selectbox(
            "Sélectionnez la colonne de l'agrégat:",
            all_columns,
            index=next((i for i, col in enumerate(all_columns) if 'agrégat' in str(col).lower() or 'agregat' in str(col).lower()), 0)
        )
        
        montant_col = st.sidebar.selectbox(
            "Sélectionnez la colonne du montant:",
            all_columns,
            index=next((i for i, col in enumerate(all_columns) if 'montant' in str(col).lower()), 0)
        )
        
        if st.sidebar.button("🚀 Préparer les données avec ces colonnes"):
            try:
                # Nettoyer et préparer les données
                financial_df = self.data[[commune_col, exercice_col, agregat_col, montant_col]].copy()
                financial_df.columns = ['Commune', 'Exercice', 'Agregat', 'Montant']
                
                # Convertir les types
                financial_df['Exercice'] = pd.to_numeric(financial_df['Exercice'], errors='coerce')
                financial_df['Montant'] = pd.to_numeric(financial_df['Montant'], errors='coerce')
                financial_df['Agregat'] = financial_df['Agregat'].astype(str)
                financial_df['Commune'] = financial_df['Commune'].astype(str)
                
                # Filtrer pour La Réunion
                reunion_mask = financial_df['Commune'].str.contains('|'.join(self.reunion_communes), case=False, na=False)
                financial_df = financial_df[reunion_mask].copy()
                
                if len(financial_df) > 0:
                    # Nettoyer les noms de communes
                    financial_df['Commune'] = financial_df['Commune'].apply(self.clean_commune_name)
                    
                    # Créer les indicateurs financiers
                    self.create_financial_indicators(financial_df)
                    
                    st.sidebar.success(f"✅ Données préparées: {len(financial_df)} lignes")
                    st.sidebar.info(f"🏘️ Communes trouvées: {len(financial_df['Commune'].unique())}")
                    st.sidebar.info(f"📅 Années: {len(financial_df['Exercice'].unique())}")
                    
                    # Aperçu des données préparées
                    with st.sidebar.expander("👁️ Aperçu des données préparées"):
                        st.dataframe(financial_df.head(10))
                else:
                    st.sidebar.error("❌ Aucune donnée trouvée pour La Réunion")
                    
            except Exception as e:
                st.sidebar.error(f"❌ Erreur: {str(e)}")
    
    def clean_commune_name(self, name):
        """Nettoie le nom de la commune"""
        if pd.isna(name):
            return name
        
        name_str = str(name).strip()
        
        # Retirer les codes ou numéros
        name_str = name_str.split(' - ')[-1]
        name_str = name_str.split('(')[0].strip()
        
        # Standardiser les noms
        for commune in self.reunion_communes:
            if commune.lower() in name_str.lower():
                return commune
        
        return name_str
    
    def create_financial_indicators(self, df):
        """Crée les indicateurs financiers agrégés par commune et année"""
        try:
            # Vérifier les colonnes nécessaires
            required_cols = ['Commune', 'Exercice', 'Agregat', 'Montant']
            if not all(col in df.columns for col in required_cols):
                st.error("❌ Colonnes manquantes dans les données")
                return
            
            # Grouper par commune, année et agrégat
            grouped = df.groupby(['Commune', 'Exercice', 'Agregat'])['Montant'].sum().reset_index()
            
            # Pivoter pour avoir les agrégats en colonnes
            pivot_df = grouped.pivot_table(
                index=['Commune', 'Exercice'],
                columns='Agregat',
                values='Montant',
                aggfunc='sum'
            ).reset_index()
            
            # Remplir les valeurs manquantes avec 0
            pivot_df = pivot_df.fillna(0)
            
            # Réinitialiser les noms de colonnes
            pivot_df.columns.name = None
            
            # Stocker les données annuelles
            self.annual_data = pivot_df
            
            # Créer la configuration des communes
            self.create_communes_config(pivot_df)
            
            st.success(f"✅ Données financières préparées: {len(pivot_df)} enregistrements")
            
            # Afficher un aperçu
            with st.expander("📋 Aperçu des données agrégées"):
                st.dataframe(pivot_df.head(20))
            
        except Exception as e:
            st.error(f"❌ Erreur dans create_financial_indicators: {str(e)}")
            import traceback
            st.error(traceback.format_exc())
    
    def create_communes_config(self, df):
        """Crée la configuration des communes"""
        self.communes_config = {}
        
        # Identifier les communes de La Réunion dans les données
        communes_in_data = []
        for commune in df['Commune'].unique():
            if pd.isna(commune):
                continue
                
            commune_name = str(commune).strip()
            
            # Vérifier si c'est une commune de La Réunion
            for reunion_commune in self.reunion_communes:
                if reunion_commune.lower() in commune_name.lower():
                    communes_in_data.append(reunion_commune)
                    break
        
        # Si pas de communes identifiées, utiliser toutes les communes uniques
        if not communes_in_data:
            communes_in_data = [str(c).strip() for c in df['Commune'].unique() if not pd.isna(c)]
        
        st.info(f"🏘️ {len(communes_in_data)} communes identifiées pour analyse")
        
        for commune in communes_in_data[:24]:  # Limiter aux 24 communes principales
            # Filtrer les données de cette commune
            commune_mask = df['Commune'].astype(str).str.contains(commune, case=False, na=False)
            commune_data = df[commune_mask].copy()
            
            if len(commune_data) == 0:
                continue
                
            # Obtenir les années disponibles
            years = sorted(commune_data['Exercice'].unique())
            
            # Calculer les statistiques par année
            annual_stats = {}
            for year in years:
                year_data = commune_data[commune_data['Exercice'] == year]
                
                # Analyser les colonnes disponibles pour extraire les indicateurs
                recettes = 0
                depenses = 0
                dette = 0
                
                # Chercher les colonnes qui pourraient contenir ces indicateurs
                for col in year_data.columns:
                    col_str = str(col).lower()
                    
                    # Recettes
                    if any(term in col_str for term in ['recette', 'revenu', 'produit']):
                        if 'total' in col_str or 'ensemble' in col_str:
                            recettes = year_data[col].sum() / 1000000  # En millions
                    
                    # Dépenses
                    elif any(term in col_str for term in ['depense', 'charge', 'fonte']):
                        if 'total' in col_str or 'ensemble' in col_str:
                            depenses = year_data[col].sum() / 1000000  # En millions
                    
                    # Dette
                    elif any(term in col_str for term in ['dette', 'emprunt', 'endettement']):
                        dette = year_data[col].sum() / 1000000  # En millions
                
                annual_stats[year] = {
                    'recettes': recettes,
                    'depenses': depenses,
                    'dette': dette,
                    'epargne': recettes - depenses if recettes and depenses else 0,
                    'ratio_dette_recettes': dette / recettes if recettes > 0 else 0
                }
            
            # Configuration de la commune
            self.communes_config[commune] = {
                'nom': commune,
                'annees': years,
                'stats_annuelles': annual_stats,
                'derniere_annee': max(years) if years else None,
                'type': self.get_commune_type(commune),
                'couleur': self.get_commune_color(commune),
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
            **📊 {len(self.communes_config)} communes analysées • 📅 {len(self.data['Exercice'].unique()) if 'Exercice' in self.data.columns else 'N/A'} années • 🔍 {len(self.data):,} lignes de données**
            """)
    
    def create_overview_tab(self):
        """Crée l'onglet Vue d'ensemble"""
        st.markdown("### 📊 Vue d'ensemble des données")
        
        if not self.data.empty:
            # Afficher les premières lignes pour inspection
            st.markdown("#### 🔍 Aperçu des données brutes")
            st.dataframe(self.data.head(100), use_container_width=True, height=400)
            
            # Statistiques de base
            st.markdown("#### 📈 Statistiques descriptives")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Lignes totales", f"{len(self.data):,}")
                numeric_cols = self.data.select_dtypes(include=[np.number]).columns
                st.metric("Colonnes numériques", len(numeric_cols))
            
            with col2:
                if 'Exercice' in self.data.columns:
                    years = self.data['Exercice'].dropna().unique()
                    st.metric("Années disponibles", len(years))
                    st.metric("Plage temporelle", f"{int(min(years))}-{int(max(years))}")
            
            with col3:
                # Compter les valeurs uniques pour les colonnes textuelles
                text_cols = self.data.select_dtypes(include=['object']).columns
                unique_counts = {}
                for col in text_cols[:3]:  # Premières 3 colonnes textuelles
                    unique_counts[col] = self.data[col].nunique()
                
                if unique_counts:
                    st.metric("Valeurs uniques (premières colonnes)", "")
                    for col, count in list(unique_counts.items())[:2]:
                        st.write(f"  • {col[:20]}...: {count}")
    
    def create_analysis_tab(self):
        """Crée l'onglet Analyse avec exploration des données"""
        st.markdown("### 🔍 Exploration et analyse des données")
        
        if self.data.empty:
            st.warning("Aucune donnée disponible")
            return
        
        # Explorer les agrégats financiers disponibles
        st.markdown("#### 📋 Agrégats financiers disponibles")
        
        # Trouver la colonne des agrégats
        agregat_cols = [col for col in self.data.columns if any(x in str(col).lower() for x in ['agrégat', 'agregat', 'categorie', 'catégorie'])]
        
        if agregat_cols:
            agregat_col = agregat_cols[0]
            agregats = self.data[agregat_col].dropna().unique()
            
            st.write(f"**{len(agregats)} types d'agrégats trouvés:**")
            
            # Afficher les agrégats par catégorie
            agregats_df = pd.DataFrame({'Agrégat': agregats})
            agregats_df['Catégorie'] = agregats_df['Agrégat'].apply(self.categorize_aggregat)
            
            # Compter par catégorie
            category_counts = agregats_df['Catégorie'].value_counts()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(x=category_counts.index, y=category_counts.values,
                            title="Répartition des agrégats par catégorie",
                            labels={'x': 'Catégorie', 'y': 'Nombre'})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Afficher les agrégats par catégorie
                for category in category_counts.index:
                    with st.expander(f"{category} ({category_counts[category]})"):
                        category_agregats = agregats_df[agregats_df['Catégorie'] == category]['Agrégat'].tolist()
                        for agregat in category_agregats[:20]:  # Limiter à 20 par catégorie
                            st.write(f"• {agregat}")
                        if len(category_agregats) > 20:
                            st.write(f"... et {len(category_agregats) - 20} autres")
        
        # Analyser les montants par année
        st.markdown("#### 📅 Évolution des montants par année")
        
        if 'Exercice' in self.data.columns and 'Montant' in self.data.columns:
            # Agréger par année
            yearly_totals = self.data.groupby('Exercice')['Montant'].agg(['sum', 'mean', 'count']).reset_index()
            yearly_totals.columns = ['Année', 'Total (€)', 'Moyenne (€)', 'Nombre de lignes']
            
            # Convertir en millions
            yearly_totals['Total (M€)'] = yearly_totals['Total (€)'] / 1000000
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(yearly_totals, x='Année', y='Total (M€)',
                             title="Total des montants par année (M€)",
                             markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(yearly_totals, x='Année', y='Nombre de lignes',
                            title="Nombre de lignes par année")
                st.plotly_chart(fig, use_container_width=True)
            
            # Afficher le tableau
            st.dataframe(yearly_totals.round(2), use_container_width=True)
    
    def categorize_aggregat(self, agregat):
        """Catégorise un agrégat financier"""
        if pd.isna(agregat):
            return "Non catégorisé"
        
        agregat_str = str(agregat).lower()
        
        categories = {
            'recettes': ['recette', 'revenu', 'produit', 'fiscal', 'taxe', 'impôt'],
            'dépenses': ['depense', 'charge', 'fonctionnement', 'investissement', 'personnel'],
            'dette': ['dette', 'emprunt', 'endettement', 'remboursement'],
            'épargne': ['epargne', 'capacité', 'autofinancement'],
            'fiscalité': ['fiscal', 'taxe', 'impôt', 'cotisation'],
            'investissement': ['investissement', 'équipement', 'immobilisation']
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in agregat_str:
                    return category
        
        return "Autre"
    
    def create_commune_analysis_tab(self):
        """Crée l'onglet d'analyse par commune"""
        if not self.communes_config:
            st.info("👈 Configurez d'abord les données dans la sidebar")
            return
        
        st.markdown("### 🏙️ Analyse par commune")
        
        # Sélection de la commune
        commune_options = list(self.communes_config.keys())
        selected_commune = st.selectbox("Sélectionnez une commune:", commune_options)
        
        if selected_commune in self.communes_config:
            config = self.communes_config[selected_commune]
            
            st.markdown(f"#### 📊 Analyse de {selected_commune}")
            
            # Métriques de base
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Type", config['type'].replace('_', ' ').title())
                st.metric("Années disponibles", len(config['annees']))
            
            with col2:
                if config['derniere_annee']:
                    last_stats = config['stats_annuelles'].get(config['derniere_annee'], {})
                    st.metric("Dernière année", config['derniere_annee'])
                    st.metric("Recettes (M€)", f"{last_stats.get('recettes', 0):.1f}")
            
            with col3:
                if config['derniere_annee']:
                    last_stats = config['stats_annuelles'].get(config['derniere_annee'], {})
                    st.metric("Dette (M€)", f"{last_stats.get('dette', 0):.1f}")
                    st.metric("Ratio D/R", f"{last_stats.get('ratio_dette_recettes', 0):.2f}")
            
            # Graphique d'évolution
            if config['annees']:
                evolution_data = []
                for year in sorted(config['annees']):
                    stats = config['stats_annuelles'].get(year, {})
                    evolution_data.append({
                        'Année': year,
                        'Recettes (M€)': stats.get('recettes', 0),
                        'Dépenses (M€)': stats.get('depenses', 0),
                        'Dette (M€)': stats.get('dette', 0),
                        'Épargne (M€)': stats.get('epargne', 0)
                    })
                
                df_evolution = pd.DataFrame(evolution_data)
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Recettes (M€)'],
                                        mode='lines+markers', name='Recettes', line=dict(color='#2A9D8F')))
                fig.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Dépenses (M€)'],
                                        mode='lines+markers', name='Dépenses', line=dict(color='#E76F51')))
                fig.add_trace(go.Scatter(x=df_evolution['Année'], y=df_evolution['Dette (M€)'],
                                        mode='lines+markers', name='Dette', line=dict(color='#F9A602')))
                
                fig.update_layout(title=f'Évolution financière - {selected_commune}',
                                xaxis_title='Année',
                                yaxis_title='Montant (M€)',
                                hovermode='x unified')
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Afficher les données
                st.dataframe(df_evolution.round(2), use_container_width=True)
    
    def create_comparison_tab(self):
        """Crée l'onglet de comparaison"""
        if not self.communes_config:
            st.info("👈 Configurez d'abord les données dans la sidebar")
            return
        
        st.markdown("### 🔄 Comparaison entre communes")
        
        # Sélection des communes à comparer
        commune_options = list(self.communes_config.keys())
        selected_communes = st.multiselect(
            "Sélectionnez les communes à comparer (2-5):",
            commune_options,
            default=commune_options[:3] if len(commune_options) >= 3 else commune_options
        )
        
        if len(selected_communes) >= 2:
            # Préparer les données de comparaison
            comparison_data = []
            
            for commune in selected_communes:
                if commune in self.communes_config:
                    config = self.communes_config[commune]
                    
                    # Calculer les moyennes sur toutes les années
                    stats_list = list(config['stats_annuelles'].values())
                    if stats_list:
                        avg_recettes = np.mean([s.get('recettes', 0) for s in stats_list])
                        avg_dette = np.mean([s.get('dette', 0) for s in stats_list])
                        avg_epargne = np.mean([s.get('epargne', 0) for s in stats_list])
                        avg_ratio = np.mean([s.get('ratio_dette_recettes', 0) for s in stats_list])
                        
                        comparison_data.append({
                            'Commune': commune,
                            'Type': config['type'].replace('_', ' ').title(),
                            'Années': len(config['annees']),
                            'Recettes moy (M€)': round(avg_recettes, 1),
                            'Dette moy (M€)': round(avg_dette, 1),
                            'Épargne moy (M€)': round(avg_epargne, 1),
                            'Ratio D/R moy': round(avg_ratio, 2)
                        })
            
            if comparison_data:
                df_comparison = pd.DataFrame(comparison_data)
                
                # Graphique de comparaison
                fig = px.bar(df_comparison,
                            x='Commune',
                            y=['Recettes moy (M€)', 'Dette moy (M€)', 'Épargne moy (M€)'],
                            title='Comparaison financière',
                            barmode='group',
                            color_discrete_sequence=['#2A9D8F', '#E76F51', '#F9A602'])
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Tableau de comparaison
                st.dataframe(df_comparison, use_container_width=True)
                
                # Analyse des performances
                st.markdown("#### 🏆 Analyse comparative")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    best_recettes = df_comparison.loc[df_comparison['Recettes moy (M€)'].idxmax()]
                    st.info(f"**💰 Meilleures recettes:** {best_recettes['Commune']} ({best_recettes['Recettes moy (M€)']} M€)")
                
                with col2:
                    best_epargne = df_comparison.loc[df_comparison['Épargne moy (M€)'].idxmax()]
                    st.success(f"**💎 Meilleure épargne:** {best_epargne['Commune']} ({best_epargne['Épargne moy (M€)']} M€)")
                
                with col3:
                    best_ratio = df_comparison.loc[df_comparison['Ratio D/R moy'].idxmin()]
                    st.warning(f"**⚖️ Meilleur ratio:** {best_ratio['Commune']} ({best_ratio['Ratio D/R moy']})")
    
    def create_data_explorer_tab(self):
        """Crée l'onglet Explorateur de données"""
        st.markdown("### 🔍 Explorateur de données complet")
        
        if self.data.empty:
            st.warning("Aucune donnée à explorer")
            return
        
        st.info(f"**Total des données:** {len(self.data):,} lignes × {len(self.data.columns)} colonnes")
        
        # Filtres interactifs
        st.markdown("#### 🎯 Filtrage des données")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Filtre par colonne de texte
            text_cols = self.data.select_dtypes(include=['object']).columns.tolist()
            if text_cols:
                filter_col = st.selectbox("Filtrer par colonne:", text_cols)
                if filter_col:
                    unique_values = self.data[filter_col].dropna().unique()
                    selected_values = st.multiselect(f"Valeurs pour {filter_col}:", unique_values)
        
        with col2:
            # Filtre par valeur numérique
            numeric_cols = self.data.select_dtypes(include=[np.number]).columns.tolist()
            if numeric_cols:
                num_filter_col = st.selectbox("Filtrer par valeur numérique:", numeric_cols)
                if num_filter_col:
                    min_val = float(self.data[num_filter_col].min())
                    max_val = float(self.data[num_filter_col].max())
                    value_range = st.slider(f"Plage pour {num_filter_col}:", min_val, max_val, (min_val, max_val))
        
        # Appliquer les filtres
        filtered_data = self.data.copy()
        
        if 'selected_values' in locals() and selected_values and filter_col:
            filtered_data = filtered_data[filtered_data[filter_col].isin(selected_values)]
        
        if 'value_range' in locals() and num_filter_col:
            filtered_data = filtered_data[
                (filtered_data[num_filter_col] >= value_range[0]) & 
                (filtered_data[num_filter_col] <= value_range[1])
            ]
        
        # Affichage des données filtrées
        st.markdown(f"#### 📄 Données filtrées ({len(filtered_data):,} lignes)")
        
        # Options d'affichage
        display_rows = st.slider("Nombre de lignes à afficher:", 10, 10000, 1000, 100)
        
        # Sélection des colonnes
        all_columns = filtered_data.columns.tolist()
        selected_columns = st.multiselect(
            "Sélectionnez les colonnes à afficher:",
            all_columns,
            default=all_columns[:10] if len(all_columns) > 10 else all_columns
        )
        
        if selected_columns:
            display_data = filtered_data[selected_columns]
        else:
            display_data = filtered_data
        
        # Afficher les données
        st.dataframe(
            display_data.head(display_rows),
            use_container_width=True,
            height=600
        )
        
        # Statistiques
        st.markdown("#### 📊 Statistiques")
        
        if len(numeric_cols) > 0:
            st.dataframe(
                filtered_data[numeric_cols].describe().round(2),
                use_container_width=True
            )
    
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
            """)
            return
        
        # Analyser la structure des données
        self.analyze_data_structure()
        
        # Préparer les données financières
        self.prepare_financial_data()
        
        # Créer les onglets
        tab_titles = ["📊 Vue d'ensemble", "🔍 Exploration", "🏙️ Analyse commune", "🔄 Comparaisons", "📁 Données brutes"]
        
        tabs = st.tabs(tab_titles)
        
        with tabs[0]:
            self.create_overview_tab()
        
        with tabs[1]:
            self.create_analysis_tab()
        
        with tabs[2]:
            self.create_commune_analysis_tab()
        
        with tabs[3]:
            self.create_comparison_tab()
        
        with tabs[4]:
            self.create_data_explorer_tab()
        
        # Footer
        st.markdown("---")
        st.markdown("""
        **📊 Dashboard d'analyse financière des communes de La Réunion**  
        *Données OFGL • Exploration interactive • Analyse complète*
        
        *Fonctionnalités:*
        - ✅ **Exploration complète** des 25,690 lignes de données
        - ✅ **Identification automatique** des colonnes importantes
        - ✅ **Analyse par commune** et comparaisons
        - ✅ **Visualisations interactives** avec Plotly
        - ✅ **Filtrage avancé** des données
        
        *Instructions:*
        1. Consultez la sidebar pour voir la structure des données
        2. Identifiez les colonnes clés (commune, exercice, agrégat, montant)
        3. Configurez les colonnes dans la section "Configuration des colonnes"
        4. Lancez la préparation des données
        5. Explorez les différentes analyses dans les onglets
        """)

# Exécution principale
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
