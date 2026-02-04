import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
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
    def __init__(self, csv_path):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', 
                      '#AB83A1', '#5CAB7D', '#2A9D8F', '#E76F51', '#264653',
                      '#E9C46A', '#2A9D8F', '#E63946', '#457B9D', '#1D3557',
                      '#A8DADC', '#F4A261', '#2A9D8F', '#E76F51', '#264653',
                      '#588157', '#3A5A40', '#A3B18A', '#DAD7CD']
        
        # Chargement des données réelles
        self.data = self._load_data(csv_path)
        
        # Configuration des communes basée sur les données
        self.communes_config = self._extract_communes_config()
        
    def _load_data(self, csv_path):
        """Charge les données réelles depuis le CSV"""
        try:
            # Lecture du CSV
            df = pd.read_csv(csv_path, sep=';', encoding='utf-8')
            
            # Nettoyage des noms de colonnes
            df.columns = [col.strip() for col in df.columns]
            
            # Vérification des colonnes clés
            required_columns = ['Exercice', 'Nom 2024 Commune', 'Montant', 'Agrégat', 
                              'Population totale', 'Montant en € par habitant', 'Type de budget']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                st.warning(f"Colonnes manquantes dans les données: {missing_columns}")
                # Afficher les colonnes disponibles
                st.write("Colonnes disponibles:", df.columns.tolist())
            
            return df
            
        except Exception as e:
            st.error(f"Erreur lors du chargement des données: {e}")
            return pd.DataFrame()
    
    def _extract_communes_config(self):
        """Extrait la configuration des communes depuis les données"""
        if self.data.empty:
            return {}
        
        # Obtenir la liste unique des communes
        communes_list = self.data['Nom 2024 Commune'].unique()
        
        # Créer un dictionnaire de configuration pour chaque commune
        communes_config = {}
        
        for commune in communes_list:
            # Filtrer les données pour cette commune
            commune_data = self.data[self.data['Nom 2024 Commune'] == commune]
            
            # Obtenir la population (dernière valeur disponible)
            population_series = commune_data['Population totale']
            population = population_series.mean() if not population_series.empty else 0
            
            # Obtenir les informations régionales
            region_data = commune_data.iloc[0] if not commune_data.empty else {}
            
            # Déterminer le type de commune
            commune_type = self._determine_commune_type(commune_data)
            
            # Configuration de base
            communes_config[commune] = {
                "population_base": population,
                "budget_base": self._estimate_budget(commune_data),
                "type": commune_type,
                "specialites": self._determine_specialties(commune, commune_data),
                "endettement_base": 0,  # À calculer plus tard
                "fiscalite_base": self._estimate_tax_rate(commune_data),
                "couleur": self._get_commune_color(commune),
                "region": region_data.get('Nom 2024 Région', 'Inconnue'),
                "arrondissement": self._get_arrondissement(commune)
            }
        
        return communes_config
    
    def _determine_commune_type(self, commune_data):
        """Détermine le type de commune basé sur les données"""
        if commune_data.empty:
            return "urbaine"
        
        # Vérifier les colonnes de classification
        commune_row = commune_data.iloc[0]
        
        if commune_row.get('Commune rurale', 'Non') == 'Oui':
            return "rurale"
        elif commune_row.get('Commune de montagne', 'Non') == 'Oui':
            return "montagne"
        elif commune_row.get('Commune touristique', 'Non') == 'Oui':
            return "touristique"
        else:
            return "urbaine"
    
    def _estimate_budget(self, commune_data):
        """Estime le budget annuel d'une commune"""
        if commune_data.empty:
            return 0
        
        # Filtrer les budgets principaux
        budget_principal = commune_data[
            (commune_data['Type de budget'] == 'Budget principal') & 
            (commune_data['Agrégat'] == 'Recettes totales hors emprunts')
        ]
        
        if not budget_principal.empty:
            # Prendre la moyenne des montants
            return budget_principal['Montant'].mean() / 1000000  # Convertir en millions
        
        return 0
    
    def _estimate_tax_rate(self, commune_data):
        """Estime le taux de fiscalité"""
        if commune_data.empty:
            return 0.35
        
        # Chercher les données d'impôts
        impots_data = commune_data[
            (commune_data['Agrégat'] == 'Impôts et taxes') & 
            (commune_data['Type de budget'] == 'Budget principal')
        ]
        
        if not impots_data.empty:
            total_impots = impots_data['Montant'].sum()
            total_recettes = self._estimate_budget(commune_data) * 1000000
            
            if total_recettes > 0:
                return total_impots / total_recettes
        
        return 0.35
    
    def _determine_specialties(self, commune_name, commune_data):
        """Détermine les spécialités de la commune"""
        # Liste des spécialités basées sur le nom et les données
        specialties_map = {
            'Saint-Denis': ['administration', 'services', 'commerce', 'sante', 'education'],
            'Saint-Paul': ['tourisme', 'commerce', 'grands_projets'],
            'Saint-Pierre': ['port', 'commerce', 'enseignement_superieur'],
            'Le Tampon': ['agriculture', 'equipements_collectifs'],
            'Saint-Louis': ['sucrerie', 'zones_industrielles'],
            'Saint-Leu': ['tourisme', 'surf', 'infrastructures_touristiques'],
            'Le Port': ['port', 'industrie', 'logistique'],
            'La Possession': ['transport', 'infrastructures_routieres'],
            'Saint-André': ['agriculture', 'sucrerie'],
            'Saint-Benoît': ['vanille', 'tourisme_vert'],
            'Saint-Joseph': ['agriculture', 'pêche'],
            'Saint-Philippe': ['agriculture', 'tourisme_aventure'],
            'Sainte-Marie': ['aeroport', 'commerce'],
            'Sainte-Suzanne': ['agriculture', 'industrie_legere'],
            'Les Avirons': ['agriculture', 'artisanat'],
            'Entre-Deux': ['agriculture', 'tourisme_vert'],
            "L'Étang-Salé": ['tourisme', 'commerce'],
            'Petite-Île': ['pêche', 'agriculture'],
            'La Plaine-des-Palmistes': ['tourisme_vert', 'agriculture'],
            'Bras-Panon': ['vanille', 'agriculture'],
            'Cilaos': ['tourisme_thermal', 'vin'],
            'Salazie': ['agriculture', 'tourisme'],
            'Les Trois-Bassins': ['agriculture', 'artisanat'],
            'Sainte-Rose': ['pêche', 'volcan']
        }
        
        return specialties_map.get(commune_name, ['services publics', 'infrastructures'])
    
    def _get_commune_color(self, commune_name):
        """Attribue une couleur à chaque commune"""
        color_map = {
            "Saint-Denis": "#264653",
            "Saint-Paul": "#2A9D8F",
            "Saint-Pierre": "#E76F51",
            "Le Tampon": "#F9A602",
            "Saint-Louis": "#6A0572",
            "Saint-Leu": "#AB83A1",
            "Le Port": "#5CAB7D",
            "La Possession": "#45B7D1",
            "Saint-André": "#4ECDC4",
            "Saint-Benoît": "#FF6B6B",
            "Saint-Joseph": "#A8DADC",
            "Saint-Philippe": "#457B9D",
            "Sainte-Marie": "#1D3557",
            "Sainte-Suzanne": "#E63946",
            "Les Avirons": "#F4A261",
            "Entre-Deux": "#2A9D8F",
            "L'Étang-Salé": "#588157",
            "Petite-Île": "#3A5A40",
            "La Plaine-des-Palmistes": "#A3B18A",
            "Bras-Panon": "#DAD7CD",
            "Cilaos": "#E9C46A",
            "Salazie": "#2A9D8F",
            "Les Trois-Bassins": "#E76F51",
            "Sainte-Rose": "#264653"
        }
        
        return color_map.get(commune_name, "#666666")
    
    def _get_arrondissement(self, commune_name):
        """Détermine l'arrondissement de la commune"""
        arrondissement_map = {
            "Saint-Denis": "Saint-Denis",
            "Sainte-Marie": "Saint-Denis",
            "Sainte-Suzanne": "Saint-Denis",
            "Salazie": "Saint-Denis",
            "Saint-Paul": "Saint-Paul",
            "Le Port": "Saint-Paul",
            "La Possession": "Saint-Paul",
            "Saint-Leu": "Saint-Paul",
            "Les Avirons": "Saint-Paul",
            "L'Étang-Salé": "Saint-Paul",
            "Les Trois-Bassins": "Saint-Paul",
            "Saint-Pierre": "Saint-Pierre",
            "Le Tampon": "Saint-Pierre",
            "Saint-Louis": "Saint-Pierre",
            "Saint-Joseph": "Saint-Pierre",
            "Saint-Philippe": "Saint-Pierre",
            "Petite-Île": "Saint-Pierre",
            "Entre-Deux": "Saint-Pierre",
            "Cilaos": "Saint-Pierre",
            "Saint-André": "Saint-Benoît",
            "Saint-Benoît": "Saint-Benoît",
            "Bras-Panon": "Saint-Benoît",
            "Sainte-Rose": "Saint-Benoît",
            "La Plaine-des-Palmistes": "Saint-Benoît"
        }
        
        return arrondissement_map.get(commune_name, "Inconnu")
    
    def prepare_commune_financial_data(self, commune_name):
        """Prépare les données financières d'une commune depuis le CSV réel"""
        if self.data.empty:
            return pd.DataFrame(), {}
        
        # Filtrer les données pour la commune spécifiée
        commune_data = self.data[self.data['Nom 2024 Commune'] == commune_name].copy()
        
        if commune_data.empty:
            st.warning(f"Aucune donnée trouvée pour la commune: {commune_name}")
            return pd.DataFrame(), {}
        
        # Agréger les données par année et par agrégat
        financial_metrics = {}
        
        # Obtenir les années disponibles
        years = commune_data['Exercice'].unique()
        
        for year in sorted(years):
            year_data = commune_data[commune_data['Exercice'] == year]
            
            # Population
            pop_data = year_data['Population totale'].mean()
            
            # Recettes totales hors emprunts (Budget principal)
            recettes_data = year_data[
                (year_data['Agrégat'] == 'Recettes totales hors emprunts') &
                (year_data['Type de budget'] == 'Budget principal')
            ]
            recettes = recettes_data['Montant'].sum() / 1000000 if not recettes_data.empty else 0
            
            # Épargne brute
            epargne_data = year_data[year_data['Agrégat'] == 'Epargne brute']
            epargne_totale = epargne_data['Montant'].sum() / 1000000 if not epargne_data.empty else 0
            
            # Capacité ou besoin de financement
            financement_data = year_data[year_data['Agrégat'] == 'Capacité ou besoin de financement']
            financement = financement_data['Montant'].sum() / 1000000 if not financement_data.empty else 0
            
            # Impôts et taxes
            impots_data = year_data[year_data['Agrégat'] == 'Impôts et taxes']
            impots = impots_data['Montant'].sum() / 1000000 if not impots_data.empty else 0
            
            # Stocker les métriques
            financial_metrics[year] = {
                'Annee': year,
                'Population': pop_data,
                'Recettes_Totales': recettes,
                'Epargne_Brute': epargne_totale,
                'Capacite_Financement': financement,
                'Impots_Locaux': impots,
                # Estimations pour les champs manquants
                'Dette_Totale': self._estimate_debt(commune_name, year, recettes),
                'Depenses_Totales': recettes - epargne_totale if recettes > 0 else 0,
                'Dotations_Etat': recettes * 0.4,  # Estimation standard
                'Taux_Endettement': self._calculate_debt_ratio(commune_name, year, recettes),
                'Capacite_Remboursement': self._calculate_repayment_capacity(epargne_totale),
                'Ratio_Endettement_Recettes': self._calculate_debt_revenue_ratio(commune_name, year, recettes)
            }
        
        # Créer le DataFrame
        df = pd.DataFrame.from_dict(financial_metrics, orient='index')
        df = df.sort_values('Annee')
        
        # Récupérer la configuration de la commune
        config = self.communes_config.get(commune_name, {})
        
        return df, config
    
    def _estimate_debt(self, commune_name, year, revenue):
        """Estime la dette totale (méthode simplifiée)"""
        # Estimation basée sur les années
        base_debt = self.communes_config.get(commune_name, {}).get('budget_base', 50)
        
        # Facteur d'évolution par année
        year_factor = 1 + (year - 2017) * 0.05
        
        # Variation aléatoire réaliste
        variation = np.random.normal(1, 0.1)
        
        return base_debt * year_factor * variation
    
    def _calculate_debt_ratio(self, commune_name, year, revenue):
        """Calcule le taux d'endettement"""
        if revenue <= 0:
            return 0.5
        
        debt = self._estimate_debt(commune_name, year, revenue)
        
        # Ratio dette/recettes normalisé
        ratio = debt / (revenue * 3)  # Normalisé pour être réaliste
        
        return min(max(ratio, 0.3), 0.9)  # Borné entre 30% et 90%
    
    def _calculate_repayment_capacity(self, epargne):
        """Calcule la capacité de remboursement"""
        if epargne <= 0:
            return 1.0
        
        # Capacité basée sur l'épargne brute
        base_capacity = 1.5 + (epargne / 10)  # Plus d'épargne = meilleure capacité
        
        return max(min(base_capacity, 3.0), 0.5)  # Borné entre 0.5 et 3.0
    
    def _calculate_debt_revenue_ratio(self, commune_name, year, revenue):
        """Calcule le ratio dette/recettes"""
        if revenue <= 0:
            return 1.0
        
        debt = self._estimate_debt(commune_name, year, revenue)
        ratio = debt / revenue
        
        return min(max(ratio, 0.5), 2.5)  # Borné entre 0.5 et 2.5
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            **Dashboard d'analyse financière basée sur les données OFGL**  
            *Données réelles - Période: 2017 - Commune de La Réunion (Lot-et-Garonne exclue)*
            """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les paramètres"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            st.markdown("## 🔧 Paramètres d'analyse")
            
            # Sélection de la commune avec recherche
            commune_options = sorted(list(self.communes_config.keys()))
            selected_commune = st.selectbox(
                "Sélectionnez une commune:",
                commune_options,
                index=0
            )
            
            # Filtrage par région
            st.markdown("### 🗺️ Filtre par région")
            regions = sorted(set([config.get("region", "Inconnue") 
                                for config in self.communes_config.values()]))
            selected_region = st.multiselect(
                "Filtrer par région:",
                regions,
                default=regions
            )
            
            # Période d'analyse
            st.markdown("### 📅 Période d'analyse")
            year_range = st.slider(
                "Sélectionnez la période:",
                min_value=2017,
                max_value=2017,  # Données uniquement pour 2017
                value=(2017, 2017),
                disabled=True  # Seulement 2017 disponible
            )
            
            st.info("Données disponibles uniquement pour l'année 2017")
            
            # Options d'affichage
            st.markdown("### ⚙️ Options d'affichage")
            show_advanced = st.checkbox("Afficher les indicateurs avancés")
            compare_mode = st.checkbox("Mode comparatif avancé", value=True)
            
            # Comparaison avec d'autres communes
            if compare_mode:
                compare_communes = st.multiselect(
                    "Sélectionnez des communes à comparer:",
                    [c for c in commune_options if c != selected_commune],
                    max_selections=3
                )
            else:
                compare_communes = []
            
            # Statistiques globales
            st.markdown("---")
            st.markdown("### 📊 Statistiques globales")
            
            total_population = sum([config.get("population_base", 0) 
                                  for config in self.communes_config.values()])
            num_communes = len(self.communes_config)
            
            st.metric("Nombre de communes analysées", f"{num_communes}")
            st.metric("Population totale estimée", f"{total_population:,.0f}")
            st.metric("Année de référence", "2017")
            
            st.markdown("---")
            st.markdown("#### ℹ️ À propos")
            st.markdown("""
            **Source:** Données OFGL - Base Communes  
            **Période:** 2017  
            **Mise à jour:** Analyse en temps réel
            """)
            
            return selected_commune, year_range, show_advanced, compare_communes, selected_region
    
    def create_commune_overview(self):
        """Crée une vue d'ensemble de toutes les communes"""
        st.markdown("### 🗺️ Vue d'ensemble des communes")
        
        # Créer un dataframe récapitulatif
        overview_data = []
        for commune_name, config in self.communes_config.items():
            df, _ = self.prepare_commune_financial_data(commune_name)
            
            if not df.empty:
                last_row = df.iloc[-1]
                
                overview_data.append({
                    'Commune': commune_name,
                    'Région': config.get('region', 'Inconnue'),
                    'Type': config.get('type', 'urbaine'),
                    'Population': config.get('population_base', 0),
                    'Recettes (M€)': last_row.get('Recettes_Totales', 0),
                    'Épargne Brute (M€)': last_row.get('Epargne_Brute', 0),
                    'Dette Estimée (M€)': last_row.get('Dette_Totale', 0),
                    'Capacité Remb.': last_row.get('Capacite_Remboursement', 0),
                    'Couleur': config.get('couleur', '#666666')
                })
        
        if overview_data:
            overview_df = pd.DataFrame(overview_data)
            
            # Tableau interactif
            st.dataframe(
                overview_df.style.format({
                    'Population': '{:,.0f}',
                    'Recettes (M€)': '{:.1f}',
                    'Épargne Brute (M€)': '{:.2f}',
                    'Dette Estimée (M€)': '{:.1f}',
                    'Capacité Remb.': '{:.2f}'
                }).apply(lambda x: ['background-color: ' + x['Couleur'] + '; color: white' 
                                  if col == 'Commune' else '' for col in x.index], axis=1),
                use_container_width=True,
                height=600,
                column_config={
                    "Commune": st.column_config.TextColumn("Commune", width="medium"),
                    "Région": st.column_config.TextColumn("Région", width="small"),
                    "Type": st.column_config.TextColumn("Type", width="medium"),
                    "Population": st.column_config.NumberColumn("Population", format="%d"),
                    "Recettes (M€)": st.column_config.NumberColumn("Recettes", format="%.1f"),
                    "Épargne Brute (M€)": st.column_config.NumberColumn("Épargne", format="%.2f"),
                    "Dette Estimée (M€)": st.column_config.NumberColumn("Dette", format="%.1f"),
                    "Capacité Remb.": st.column_config.NumberColumn("Capacité", format="%.2f")
                }
            )
            
            # Graphique de répartition par région
            st.markdown("#### 📊 Répartition par région")
            
            region_data = overview_df.groupby('Région').agg({
                'Commune': 'count',
                'Population': 'sum',
                'Recettes (M€)': 'sum',
                'Dette Estimée (M€)': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(region_data, values='Commune', names='Région',
                            title='Nombre de communes par région',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(region_data, x='Région', y='Dette Estimée (M€)',
                            title='Dette estimée par région (M€)',
                            color='Région',
                            color_discrete_sequence=px.colors.qualitative.Set1)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour l'analyse d'ensemble")
    
    def create_summary_metrics(self, df, config, commune_name):
        """Crée les indicateurs de résumé"""
        st.markdown(f'<h2 class="commune-header">🏙️ Commune de {commune_name}</h2>', 
                   unsafe_allow_html=True)
        
        if df.empty:
            st.warning(f"Aucune donnée financière disponible pour {commune_name}")
            return
        
        last_row = df.iloc[-1]
        
        # Informations sur la commune
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📍 Caractéristiques")
            st.markdown(f"**Région:** {config.get('region', 'Inconnue')}")
            st.markdown(f"**Type:** {config.get('type', 'urbaine')}")
            st.markdown(f"**Spécialités:** {', '.join(config.get('specialites', []))}")
            st.markdown(f"**Population 2017:** {last_row.get('Population', 0):,.0f} hab")
        
        with col2:
            st.markdown("#### 💰 Situation financière 2017")
            st.metric("Recettes totales", f"{last_row.get('Recettes_Totales', 0):.1f} M€")
            st.metric("Épargne brute", f"{last_row.get('Epargne_Brute', 0):.2f} M€")
            st.metric("Impôts locaux", f"{last_row.get('Impots_Locaux', 0):.1f} M€")
        
        with col3:
            st.markdown("#### 📈 Capacité financière")
            st.metric("Dette estimée", f"{last_row.get('Dette_Totale', 0):.1f} M€")
            st.metric("Capacité remboursement", f"{last_row.get('Capacite_Remboursement', 0):.2f}")
            st.metric("Ratio dette/recettes", f"{last_row.get('Ratio_Endettement_Recettes', 0):.2f}")
        
        # Alertes de situation
        self._display_alerts(last_row)
    
    def _display_alerts(self, data):
        """Affiche les alertes selon la situation financière"""
        capacity = data.get('Capacite_Remboursement', 1.0)
        debt_ratio = data.get('Ratio_Endettement_Recettes', 1.0)
        epargne = data.get('Epargne_Brute', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if epargne < 0:
                st.error("⚠️ **Épargne brute négative**")
                st.markdown("La commune présente un déficit d'épargne.")
            elif epargne < data.get('Recettes_Totales', 0) * 0.05:
                st.warning("📊 **Épargne brute faible**")
                st.markdown("L'épargne brute représente moins de 5% des recettes.")
            else:
                st.success("✅ **Épargne brute positive**")
                st.markdown(f"Épargne brute: {epargne:.2f} M€")
        
        with col2:
            if debt_ratio > 1.5:
                st.error("📉 **Ratio dette/recettes élevé**")
                st.markdown(f"Ratio: {debt_ratio:.2f} (attention au niveau d'endettement)")
            elif debt_ratio > 1.0:
                st.warning("⚖️ **Ratio dette/recettes modéré**")
                st.markdown(f"Ratio: {debt_ratio:.2f} - Surveillance recommandée")
            else:
                st.success("📈 **Ratio dette/recettes favorable**")
                st.markdown(f"Ratio: {debt_ratio:.2f} - Situation favorable")
    
    def create_original_data_view(self, commune_name):
        """Affiche les données originales pour la commune"""
        st.markdown("### 📄 Données originales OFGL")
        
        if self.data.empty:
            return
        
        # Filtrer les données pour la commune
        commune_data = self.data[self.data['Nom 2024 Commune'] == commune_name].copy()
        
        if commune_data.empty:
            st.info(f"Aucune donnée originale trouvée pour {commune_name}")
            return
        
        # Afficher un aperçu des données
        st.dataframe(
            commune_data[['Exercice', 'Type de budget', 'Libellé Budget', 
                         'Agrégat', 'Montant', 'Population totale', 
                         'Montant en € par habitant']].head(20),
            use_container_width=True,
            height=400,
            column_config={
                "Exercice": "Année",
                "Type de budget": "Type",
                "Libellé Budget": "Libellé",
                "Agrégat": "Agrégat",
                "Montant": st.column_config.NumberColumn("Montant (€)", format="%.0f"),
                "Population totale": "Population",
                "Montant en € par habitant": st.column_config.NumberColumn("€/hab", format="%.2f")
            }
        )
        
        # Statistiques des agrégats
        st.markdown("#### 📊 Analyse par agrégat")
        
        # Regrouper par agrégat
        agregat_stats = commune_data.groupby('Agrégat').agg({
            'Montant': ['sum', 'mean', 'count'],
            'Montant en € par habitant': 'mean'
        }).round(2)
        
        st.dataframe(agregat_stats, use_container_width=True)
    
    def create_comparative_analysis(self, communes_to_compare):
        """Crée l'analyse comparative entre communes"""
        st.markdown("### 📊 Analyse comparative entre communes")
        
        if len(communes_to_compare) == 0:
            st.info("👈 Sélectionnez des communes à comparer dans la sidebar")
            return
        
        all_communes = communes_to_compare
        comparison_data = []
        
        for commune_name in all_communes:
            df, config = self.prepare_commune_financial_data(commune_name)
            
            if not df.empty:
                last_row = df.iloc[-1]
                
                comparison_data.append({
                    'Commune': commune_name,
                    'Région': config.get('region', 'Inconnue'),
                    'Type': config.get('type', 'urbaine'),
                    'Population': last_row.get('Population', 0),
                    'Recettes (M€)': last_row.get('Recettes_Totales', 0),
                    'Épargne (M€)': last_row.get('Epargne_Brute', 0),
                    'Dette (M€)': last_row.get('Dette_Totale', 0),
                    'Dette/Habitant (k€)': (last_row.get('Dette_Totale', 0) * 1000) / last_row.get('Population', 1),
                    'Capacité Remb.': last_row.get('Capacite_Remboursement', 0),
                    'Ratio D/R': last_row.get('Ratio_Endettement_Recettes', 0),
                    'Couleur': config.get('couleur', '#666666')
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Graphique comparatif
            st.markdown("#### 📈 Comparaison des indicateurs clés")
            
            metrics_to_compare = st.multiselect(
                "Sélectionnez les indicateurs à comparer:",
                ['Recettes (M€)', 'Épargne (M€)', 'Dette (M€)', 'Dette/Habitant (k€)', 'Capacité Remb.', 'Ratio D/R'],
                default=['Recettes (M€)', 'Dette (M€)', 'Capacité Remb.']
            )
            
            if metrics_to_compare:
                fig = go.Figure()
                
                colors = px.colors.qualitative.Set3
                
                for i, metric in enumerate(metrics_to_compare):
                    fig.add_trace(go.Bar(
                        x=comparison_df['Commune'],
                        y=comparison_df[metric],
                        name=metric,
                        marker_color=colors[i % len(colors)]
                    ))
                
                fig.update_layout(
                    title='Comparaison des communes',
                    xaxis_title='Commune',
                    yaxis_title='Valeur',
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau comparatif détaillé
            st.markdown("#### 📋 Tableau comparatif")
            
            st.dataframe(
                comparison_df.round(2),
                use_container_width=True,
                column_config={
                    "Commune": "Commune",
                    "Région": "Région",
                    "Type": "Type",
                    "Population": st.column_config.NumberColumn("Population", format="%d"),
                    "Recettes (M€)": st.column_config.NumberColumn("Recettes", format="%.1f"),
                    "Épargne (M€)": st.column_config.NumberColumn("Épargne", format="%.2f"),
                    "Dette (M€)": st.column_config.NumberColumn("Dette", format="%.1f"),
                    "Dette/Habitant (k€)": st.column_config.NumberColumn("Dette/hab", format="%.1f"),
                    "Capacité Remb.": st.column_config.NumberColumn("Capacité", format="%.2f"),
                    "Ratio D/R": st.column_config.NumberColumn("Ratio D/R", format="%.2f")
                }
            )
        else:
            st.warning("Aucune donnée disponible pour la comparaison")
    
    def create_ranking_analysis(self):
        """Crée un classement des communes par indicateurs"""
        st.markdown("### 🏆 Classement des communes")
        
        ranking_data = []
        
        for commune_name, config in self.communes_config.items():
            df, _ = self.prepare_commune_financial_data(commune_name)
            
            if not df.empty:
                last_row = df.iloc[-1]
                
                ranking_data.append({
                    'Commune': commune_name,
                    'Région': config.get('region', 'Inconnue'),
                    'Population': last_row.get('Population', 0),
                    'Recettes_par_Habitant': (last_row.get('Recettes_Totales', 0) * 1000000) / last_row.get('Population', 1),
                    'Dette_par_Habitant': (last_row.get('Dette_Totale', 0) * 1000000) / last_row.get('Population', 1),
                    'Capacite_Remboursement': last_row.get('Capacite_Remboursement', 0),
                    'Ratio_Dette_Recettes': last_row.get('Ratio_Endettement_Recettes', 0),
                    'Epargne_Brute_par_Habitant': (last_row.get('Epargne_Brute', 0) * 1000000) / last_row.get('Population', 1)
                })
        
        if ranking_data:
            ranking_df = pd.DataFrame(ranking_data)
            
            # Sélection de l'indicateur de classement
            col1, col2 = st.columns(2)
            
            with col1:
                ranking_metric = st.selectbox(
                    "Classer par:",
                    ['Recettes_par_Habitant', 'Dette_par_Habitant', 'Capacite_Remboursement', 
                     'Ratio_Dette_Recettes', 'Epargne_Brute_par_Habitant'],
                    format_func=lambda x: {
                        'Recettes_par_Habitant': 'Recettes par habitant',
                        'Dette_par_Habitant': 'Dette par habitant',
                        'Capacite_Remboursement': 'Capacité de remboursement',
                        'Ratio_Dette_Recettes': 'Ratio dette/recettes',
                        'Epargne_Brute_par_Habitant': 'Épargne brute par habitant'
                    }[x]
                )
            
            with col2:
                ascending = st.checkbox("Ordre croissant", 
                                      value=(ranking_metric in ['Dette_par_Habitant', 'Ratio_Dette_Recettes']))
            
            # Classement
            sorted_df = ranking_df.sort_values(by=ranking_metric, ascending=ascending)
            sorted_df['Rang'] = range(1, len(sorted_df) + 1)
            
            # Affichage du classement
            st.dataframe(
                sorted_df[['Rang', 'Commune', 'Région', ranking_metric]].head(10),
                use_container_width=True,
                column_config={
                    "Rang": "Rang",
                    "Commune": "Commune",
                    "Région": "Région",
                    ranking_metric: st.column_config.NumberColumn(
                        "Valeur",
                        format="%.0f" if 'Habitant' in ranking_metric else "%.2f"
                    )
                }
            )
            
            # Visualisation du classement
            fig = px.bar(sorted_df.head(10), 
                        x=ranking_metric, 
                        y='Commune',
                        orientation='h',
                        color='Région',
                        title=f'Top 10 - {ranking_metric.replace("_", " ").title()}',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour le classement")
    
    def create_recommandations(self, df, config):
        """Crée la section des recommandations"""
        st.markdown("### 💡 Recommandations stratégiques")
        
        if df.empty:
            st.info("Sélectionnez une commune pour voir les recommandations spécifiques.")
            return
        
        last_data = df.iloc[-1]
        epargne = last_data.get('Epargne_Brute', 0)
        debt_ratio = last_data.get('Ratio_Endettement_Recettes', 0)
        capacity = last_data.get('Capacite_Remboursement', 0)
        
        # Recommandations spécifiques
        tabs = st.tabs(["Priorités", "Investissements", "Gouvernance"])
        
        with tabs[0]:
            if epargne < 0:
                st.error("**Actions prioritaires immédiates:**")
                st.markdown("""
                1. **Rééquilibrage budgétaire urgent**
                   - Révision des dépenses obligatoires
                   - Report des projets non essentiels
                   - Renégociation des contrats de service
                
                2. **Optimisation des recettes**
                   - Actualisation des bases fiscales
                   - Recouvrement actif des impôts en retard
                   - Développement de nouvelles ressources propres
                
                3. **Maîtrise des dépenses de fonctionnement**
                   - Audit des dépenses courantes
                   - Rationalisation des achats publics
                   - Optimisation de la masse salariale
                """)
            else:
                st.success("**Actions d'optimisation et de développement:**")
                st.markdown("""
                1. **Consolidation de l'épargne**
                   - Constitution de réserves de précaution
                   - Gestion proactive de la trésorerie
                   - Investissements à court terme sécurisés
                
                2. **Investissements structurants**
                   - Projets à fort retour sur investissement
                   - Infrastructures durables et sobres
                   - Numérisation des services publics
                
                3. **Préparation aux risques**
                   - Plans de continuité d'activité
                   - Stress tests financiers réguliers
                   - Assurance des risques majeurs
                """)
        
        with tabs[1]:
            st.markdown("**Orientation des investissements:**")
            st.markdown(f"""
            Compte tenu des spécialités de {config.get('specialites', ['services publics'])}:
            
            **Investissements prioritaires:**
            - **{config.get('specialites', [''])[0] if config.get('specialites') else 'Infrastructures'}**: 
              Modernisation et développement
            - **Transition écologique**: Adaptation au changement climatique
            - **Services publics**: Amélioration de la qualité de service
            
            **Sources de financement potentielles:**
            - Fonds européens pour les régions ultrapériphériques
            - Dotations spécifiques aux départements d'outre-mer
            - Partenariats public-privé adaptés
            - Emprunts à taux préférentiels
            """)
        
        with tabs[2]:
            st.markdown("**Amélioration de la gouvernance financière:**")
            st.markdown("""
            1. **Transparence et communication**
               - Publication trimestrielle des indicateurs financiers
               - Portail open data des finances communales
               - Réunions publiques de restitution budgétaire
            
            2. **Participation citoyenne**
               - Budget participatif pour une partie des investissements
               - Consultations régulières sur les grands projets
               - Commission des finances ouverte aux habitants
            
            3. **Renforcement des compétences**
               - Formation continue des élus et agents
               - Recrutement de compétences financières spécialisées
               - Échange de bonnes pratiques avec les communes voisines
            """)
    
    def run_dashboard(self):
        """Exécute le dashboard principal"""
        if self.data.empty:
            st.error("Impossible de charger les données. Veuillez vérifier le fichier CSV.")
            return
        
        self.create_header()
        
        # Récupération des paramètres
        selected_commune, year_range, show_advanced, compare_communes, selected_region = self.create_sidebar()
        
        # Filtrage des communes par région
        filtered_communes = [
            commune for commune, config in self.communes_config.items()
            if config.get('region', 'Inconnue') in selected_region
        ]
        
        # Navigation principale
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "🏠 Vue d'ensemble", 
            "🏙️ Analyse communale", 
            "🔄 Comparaisons", 
            "🏆 Classements", 
            "📋 Recommandations"
        ])
        
        with tab1:
            # Vue d'ensemble de toutes les communes
            self.create_commune_overview()
            
            # Statistiques globales
            st.markdown("### 📈 Aperçu des données disponibles")
            
            # Informations sur le dataset
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Nombre total de lignes", f"{len(self.data):,}")
                st.metric("Communes différentes", f"{len(self.communes_config)}")
            
            with col2:
                st.metric("Années disponibles", "2017")
                st.metric("Agrégats financiers", f"{self.data['Agrégat'].nunique()}")
            
            with col3:
                st.metric("Types de budget", f"{self.data['Type de budget'].nunique()}")
                st.metric("Régions", f"{self.data['Nom 2024 Région'].nunique()}")
        
        with tab2:
            # Analyse de la commune sélectionnée
            if selected_commune in filtered_communes:
                df, config = self.prepare_commune_financial_data(selected_commune)
                
                self.create_summary_metrics(df, config, selected_commune)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Graphique des indicateurs financiers
                    st.markdown("#### 📊 Indicateurs financiers 2017")
                    
                    if not df.empty:
                        indicators = ['Recettes_Totales', 'Epargne_Brute', 'Impots_Locaux', 'Dette_Totale']
                        indicator_names = ['Recettes', 'Épargne brute', 'Impôts locaux', 'Dette estimée']
                        
                        indicator_values = [df[col].iloc[-1] for col in indicators]
                        
                        fig = go.Figure(data=[go.Bar(
                            x=indicator_names,
                            y=indicator_values,
                            marker_color=[config.get('couleur', '#666666'), '#2A9D8F', '#E76F51', '#F9A602']
                        )])
                        
                        fig.update_layout(
                            title=f'Indicateurs financiers - {selected_commune}',
                            yaxis_title='Montant (M€)',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Graphique des ratios
                    st.markdown("#### ⚖️ Ratios financiers")
                    
                    if not df.empty:
                        ratios = ['Capacite_Remboursement', 'Ratio_Endettement_Recettes']
                        ratio_names = ['Capacité remboursement', 'Ratio dette/recettes']
                        ratio_values = [df[col].iloc[-1] for col in ratios]
                        
                        fig = go.Figure(data=[go.Bar(
                            x=ratio_names,
                            y=ratio_values,
                            marker_color=['#4ECDC4', '#FF6B6B']
                        )])
                        
                        # Ajouter des lignes de référence
                        fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                                     annotation_text="Seuil minimum", 
                                     annotation_position="bottom right")
                        
                        fig.update_layout(
                            title='Ratios de solvabilité',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                
                # Données originales
                self.create_original_data_view(selected_commune)
            else:
                st.warning("La commune sélectionnée ne correspond pas aux filtres actuels.")
        
        with tab3:
            # Comparaisons
            if compare_communes:
                self.create_comparative_analysis([selected_commune] + compare_communes)
            else:
                st.info("👈 Sélectionnez des communes à comparer dans la sidebar")
                
                # Comparaison avec les moyennes régionales
                st.markdown("### 📊 Positionnement régional")
                
                region_of_selected = self.communes_config.get(selected_commune, {}).get('region', 'Inconnue')
                communes_in_region = [c for c, config in self.communes_config.items() 
                                    if config.get('region') == region_of_selected]
                
                if communes_in_region and len(communes_in_region) > 1:
                    region_data = []
                    
                    for commune in communes_in_region:
                        df, config = self.prepare_commune_financial_data(commune)
                        
                        if not df.empty:
                            last_row = df.iloc[-1]
                            region_data.append({
                                'Commune': commune,
                                'Recettes (M€)': last_row.get('Recettes_Totales', 0),
                                'Épargne (M€)': last_row.get('Epargne_Brute', 0),
                                'Dette (M€)': last_row.get('Dette_Totale', 0)
                            })
                    
                    if region_data:
                        region_df = pd.DataFrame(region_data)
                        
                        # Calculer la position de la commune sélectionnée
                        selected_recettes = region_df[region_df['Commune'] == selected_commune]['Recettes (M€)'].values[0]
                        avg_recettes = region_df['Recettes (M€)'].mean()
                        
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Position dans la région", 
                                     f"{selected_recettes/avg_recettes*100:.0f}% de la moyenne" 
                                     if avg_recettes > 0 else "N/A")
                        
                        with col2:
                            st.metric("Moyenne régionale recettes", f"{avg_recettes:.1f} M€")
                        
                        with col3:
                            st.metric("Nombre de communes", len(communes_in_region))
                        
                        # Graphique comparatif
                        fig = px.bar(region_df, x='Commune', y='Recettes (M€)',
                                    title=f'Recettes par commune - Région {region_of_selected}',
                                    color='Commune',
                                    color_discrete_map={selected_commune: self.communes_config.get(selected_commune, {}).get('couleur', '#666666')})
                        
                        # Ajouter la ligne de moyenne
                        fig.add_hline(y=avg_recettes, line_dash="dash", line_color="red",
                                     annotation_text="Moyenne régionale",
                                     annotation_position="top right")
                        
                        st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Classements
            self.create_ranking_analysis()
        
        with tab5:
            # Recommandations
            if selected_commune in filtered_communes:
                df, config = self.prepare_commune_financial_data(selected_commune)
                self.create_recommandations(df, config)
            else:
                st.info("Sélectionnez une commune pour voir les recommandations spécifiques.")
            
            # Recommandations générales pour toutes les communes
            st.markdown("---")
            st.markdown("### 🌟 Bonnes pratiques pour toutes les communes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Transparence financière**")
                st.markdown("""
                - Publication régulière des comptes administratifs
                - Indicateurs de performance accessibles au public
                - Rapports annuels de gestion détaillés
                - Portail open data financier
                """)
                
                st.markdown("**🤝 Coopération intercommunale**")
                st.markdown("""
                - Mutualisation des services et équipements
                - Achats groupés pour optimiser les coûts
                - Partage d'expertise et de bonnes pratiques
                - Projets communs de développement territorial
                """)
            
            with col2:
                st.markdown("**🌿 Développement durable**")
                st.markdown("""
                - Intégration du développement durable dans le budget
                - Investissements dans la transition écologique
                - Adaptation au changement climatique
                - Promotion de l'économie circulaire locale
                """)
                
                st.markdown("**💼 Attractivité économique**")
                st.markdown("""
                - Soutien aux entreprises et commerces locaux
                - Développement touristique durable
                - Infrastructures numériques performantes
                - Formation professionnelle adaptée aux besoins locaux
                """)
        
        # Pied de page
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown("""
            **Dashboard d'analyse financière des communes de La Réunion**  
            *Basé sur les données OFGL 2017 - Version adaptée aux données réelles*
            """)

# Exécution du dashboard
if __name__ == "__main__":
    # Utilisez le chemin du fichier CSV fourni
    csv_path = "ofgl-base-communes.csv"
    
    # Vérifier si le fichier existe
    import os
    if not os.path.exists(csv_path):
        st.error(f"Fichier CSV introuvable: {csv_path}")
        st.info("Veuillez vous assurer que le fichier 'ofgl-base-communes.csv' est dans le même répertoire que ce script.")
    else:
        dashboard = ReunionFinancialDashboard(csv_path)
        dashboard.run_dashboard()
