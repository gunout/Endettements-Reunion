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
    page_title="Analyse d'Endettement Communal - La Réunion",
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

class ReunionEndettementDashboard:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', 
                      '#AB83A1', '#5CAB7D', '#2A9D8F', '#E76F51', '#264653',
                      '#E9C46A', '#2A9D8F', '#E63946', '#457B9D', '#1D3557',
                      '#A8DADC', '#F4A261', '#2A9D8F', '#E76F51', '#264653',
                      '#588157', '#3A5A40', '#A3B18A', '#DAD7CD']
        self.start_year = 2002
        self.end_year = 2025
        
        # Configuration complète des 24 communes réunionnaises
        self.communes_config = self._get_communes_config()
        
    def _get_communes_config(self):
        """Retourne la configuration complète des 24 communes"""
        return {
            "Saint-Denis": {
                "population_base": 150000,
                "budget_base": 180,
                "type": "capitale_regionale",
                "specialites": ["administration", "services", "commerce", "sante", "education"],
                "endettement_base": 120,
                "fiscalite_base": 0.45,
                "couleur": "#264653",
                "region": "Nord",
                "arrondissement": "Saint-Denis"
            },
            "Saint-Paul": {
                "population_base": 105000,
                "budget_base": 95,
                "type": "urbaine_cotiere",
                "specialites": ["tourisme", "commerce", "grands_projets"],
                "endettement_base": 85,
                "fiscalite_base": 0.42,
                "couleur": "#2A9D8F",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Saint-Pierre": {
                "population_base": 85000,
                "budget_base": 80,
                "type": "urbaine_sud",
                "specialites": ["port", "commerce", "enseignement_superieur"],
                "endettement_base": 65,
                "fiscalite_base": 0.44,
                "couleur": "#E76F51",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Le Tampon": {
                "population_base": 80000,
                "budget_base": 70,
                "type": "periurbaine",
                "specialites": ["agriculture", "equipements_collectifs"],
                "endettement_base": 55,
                "fiscalite_base": 0.40,
                "couleur": "#F9A602",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Saint-Louis": {
                "population_base": 55000,
                "budget_base": 50,
                "type": "urbaine",
                "specialites": ["sucrerie", "zones_industrielles"],
                "endettement_base": 45,
                "fiscalite_base": 0.43,
                "couleur": "#6A0572",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Saint-Leu": {
                "population_base": 34000,
                "budget_base": 35,
                "type": "cotiere_touristique",
                "specialites": ["tourisme", "surf", "infrastructures_touristiques"],
                "endettement_base": 30,
                "fiscalite_base": 0.38,
                "couleur": "#AB83A1",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Le Port": {
                "population_base": 35000,
                "budget_base": 45,
                "type": "portuaire_industrielle",
                "specialites": ["port", "industrie", "logistique"],
                "endettement_base": 40,
                "fiscalite_base": 0.41,
                "couleur": "#5CAB7D",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "La Possession": {
                "population_base": 34000,
                "budget_base": 38,
                "type": "periurbaine_nord",
                "specialites": ["transport", "infrastructures_routieres"],
                "endettement_base": 32,
                "fiscalite_base": 0.39,
                "couleur": "#45B7D1",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Saint-André": {
                "population_base": 58000,
                "budget_base": 52,
                "type": "est_urbaine",
                "specialites": ["agriculture", "sucrerie"],
                "endettement_base": 48,
                "fiscalite_base": 0.42,
                "couleur": "#4ECDC4",
                "region": "Est",
                "arrondissement": "Saint-Benoît"
            },
            "Saint-Benoît": {
                "population_base": 37000,
                "budget_base": 40,
                "type": "est_rurale",
                "specialites": ["vanille", "tourisme_vert"],
                "endettement_base": 35,
                "fiscalite_base": 0.37,
                "couleur": "#FF6B6B",
                "region": "Est",
                "arrondissement": "Saint-Benoît"
            },
            "Saint-Joseph": {
                "population_base": 38000,
                "budget_base": 36,
                "type": "rurale_cotiere",
                "specialites": ["agriculture", "pêche"],
                "endettement_base": 32,
                "fiscalite_base": 0.36,
                "couleur": "#A8DADC",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Saint-Philippe": {
                "population_base": 5200,
                "budget_base": 12,
                "type": "rurale_isolee",
                "specialites": ["agriculture", "tourisme_aventure"],
                "endettement_base": 8,
                "fiscalite_base": 0.32,
                "couleur": "#457B9D",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Sainte-Marie": {
                "population_base": 34000,
                "budget_base": 32,
                "type": "urbaine_nord",
                "specialites": ["aeroport", "commerce"],
                "endettement_base": 28,
                "fiscalite_base": 0.38,
                "couleur": "#1D3557",
                "region": "Nord",
                "arrondissement": "Saint-Denis"
            },
            "Sainte-Suzanne": {
                "population_base": 24000,
                "budget_base": 28,
                "type": "urbaine_nord",
                "specialites": ["agriculture", "industrie_legere"],
                "endettement_base": 22,
                "fiscalite_base": 0.37,
                "couleur": "#E63946",
                "region": "Nord",
                "arrondissement": "Saint-Denis"
            },
            "Les Avirons": {
                "population_base": 11000,
                "budget_base": 18,
                "type": "rurale_ouest",
                "specialites": ["agriculture", "artisanat"],
                "endettement_base": 15,
                "fiscalite_base": 0.35,
                "couleur": "#F4A261",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Entre-Deux": {
                "population_base": 7000,
                "budget_base": 15,
                "type": "rurale_interieure",
                "specialites": ["agriculture", "tourisme_vert"],
                "endettement_base": 12,
                "fiscalite_base": 0.34,
                "couleur": "#2A9D8F",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "L'Étang-Salé": {
                "population_base": 14000,
                "budget_base": 22,
                "type": "cotiere_residentielle",
                "specialites": ["tourisme", "commerce"],
                "endettement_base": 18,
                "fiscalite_base": 0.36,
                "couleur": "#588157",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Petite-Île": {
                "population_base": 12000,
                "budget_base": 16,
                "type": "cotiere_sud",
                "specialites": ["pêche", "agriculture"],
                "endettement_base": 13,
                "fiscalite_base": 0.33,
                "couleur": "#3A5A40",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "La Plaine-des-Palmistes": {
                "population_base": 6600,
                "budget_base": 14,
                "type": "rurale_altitude",
                "specialites": ["tourisme_vert", "agriculture"],
                "endettement_base": 11,
                "fiscalite_base": 0.32,
                "couleur": "#A3B18A",
                "region": "Est",
                "arrondissement": "Saint-Benoît"
            },
            "Bras-Panon": {
                "population_base": 13000,
                "budget_base": 20,
                "type": "rurale_est",
                "specialites": ["vanille", "agriculture"],
                "endettement_base": 16,
                "fiscalite_base": 0.34,
                "couleur": "#DAD7CD",
                "region": "Est",
                "arrondissement": "Saint-Benoît"
            },
            "Cilaos": {
                "population_base": 5500,
                "budget_base": 13,
                "type": "cirque_montagne",
                "specialites": ["tourisme_thermal", "vin"],
                "endettement_base": 10,
                "fiscalite_base": 0.31,
                "couleur": "#E9C46A",
                "region": "Sud",
                "arrondissement": "Saint-Pierre"
            },
            "Salazie": {
                "population_base": 7500,
                "budget_base": 15,
                "type": "cirque_nord",
                "specialites": ["agriculture", "tourisme"],
                "endettement_base": 12,
                "fiscalite_base": 0.33,
                "couleur": "#2A9D8F",
                "region": "Nord",
                "arrondissement": "Saint-Denis"
            },
            "Trois-Bassins": {
                "population_base": 7000,
                "budget_base": 14,
                "type": "rurale_ouest",
                "specialites": ["agriculture", "artisanat"],
                "endettement_base": 11,
                "fiscalite_base": 0.32,
                "couleur": "#E76F51",
                "region": "Ouest",
                "arrondissement": "Saint-Paul"
            },
            "Sainte-Rose": {
                "population_base": 6500,
                "budget_base": 12,
                "type": "rurale_est",
                "specialites": ["pêche", "volcan"],
                "endettement_base": 9,
                "fiscalite_base": 0.30,
                "couleur": "#264653",
                "region": "Est",
                "arrondissement": "Saint-Benoît"
            }
        }
    
    def generate_financial_data(self, commune_name):
        """Génère des données financières simulées pour une commune"""
        config = self.communes_config[commune_name]
        
        # Créer une base de données annuelle
        dates = pd.date_range(start=f'{self.start_year}-01-01', 
                             end=f'{self.end_year}-12-31', freq='Y')
        
        data = {'Annee': [date.year for date in dates]}
        
        # Données démographiques
        data['Population'] = []
        for i, date in enumerate(dates):
            if config["type"] in ["capitale_regionale", "urbaine"]:
                growth_rate = 0.015
            elif config["type"] in ["touristique", "cotiere_touristique"]:
                growth_rate = 0.018
            else:
                growth_rate = 0.012
            growth = 1 + growth_rate * i
            data['Population'].append(config["population_base"] * growth)
        
        # Recettes totales
        data['Recettes_Totales'] = []
        for i, date in enumerate(dates):
            if config["type"] in ["capitale_regionale", "urbaine"]:
                growth_rate = 0.035
            elif config["type"] in ["touristique", "cotiere_touristique"]:
                growth_rate = 0.038
            else:
                growth_rate = 0.030
            growth = 1 + growth_rate * i
            noise = np.random.normal(1, 0.07)
            data['Recettes_Totales'].append(config["budget_base"] * growth * noise)
        
        # Dépenses totales
        data['Depenses_Totales'] = []
        for i, date in enumerate(dates):
            growth = 1 + 0.032 * i
            noise = np.random.normal(1, 0.06)
            data['Depenses_Totales'].append(config["budget_base"] * 0.96 * growth * noise)
        
        # Dette totale avec variations réalistes
        data['Dette_Totale'] = []
        for i, date in enumerate(dates):
            year = date.year
            base_debt = config["endettement_base"]
            
            # Évolution avec pics d'investissement
            if year in [2007, 2013, 2019, 2024]:
                change = 1.3
            elif year in [2009, 2015, 2021]:
                change = 0.95
            else:
                change = 1.02
            
            # Ajustement selon le type de commune
            if config["type"] in ["capitale_regionale", "urbaine"]:
                multiplier = 1.1
            elif config["type"] in ["rurale", "rurale_isolee"]:
                multiplier = 0.9
            else:
                multiplier = 1.0
            
            noise = np.random.normal(1, 0.08)
            data['Dette_Totale'].append(base_debt * change * multiplier * noise)
        
        # Impôts locaux
        data['Impots_Locaux'] = []
        for i, date in enumerate(dates):
            base_tax = config["budget_base"] * 0.38
            growth = 1 + 0.025 * i
            noise = np.random.normal(1, 0.08)
            data['Impots_Locaux'].append(base_tax * growth * noise)
        
        # Dotations État
        data['Dotations_Etat'] = []
        for i, date in enumerate(dates):
            year = date.year
            base_grants = config["budget_base"] * 0.40
            if year >= 2010:
                increase = 1 + 0.01 * (year - 2010)
            else:
                increase = 1
            noise = np.random.normal(1, 0.05)
            data['Dotations_Etat'].append(base_grants * increase * noise)
        
        # Ratios financiers
        data['Taux_Endettement'] = []
        for i, date in enumerate(dates):
            year = date.year
            base_ratio = 0.65
            if year >= 2010:
                improvement = 1 - 0.008 * (year - 2010)
            else:
                improvement = 1
            noise = np.random.normal(1, 0.05)
            data['Taux_Endettement'].append(base_ratio * improvement * noise)
        
        # Capacité de remboursement
        data['Capacite_Remboursement'] = []
        data['Epargne_Brute'] = []
        for i, date in enumerate(dates):
            year = date.year
            base_saving = config["budget_base"] * 0.04
            if year >= 2010:
                improvement = 1 + 0.006 * (year - 2010)
            else:
                improvement = 1
            noise = np.random.normal(1, 0.12)
            epargne = base_saving * improvement * noise
            data['Epargne_Brute'].append(epargne)
            
            # Simulation des annuités
            dette = data['Dette_Totale'][i]
            annuites = dette * 0.10 * np.random.normal(1, 0.06)
            
            if annuites > 0:
                cap = epargne / annuites
            else:
                cap = 2.0
            
            noise_cap = np.random.normal(1, 0.08)
            data['Capacite_Remboursement'].append(cap * noise_cap)
        
        # Ratio dette/recettes
        data['Ratio_Endettement_Recettes'] = []
        for i in range(len(data['Annee'])):
            dette = data['Dette_Totale'][i]
            recettes = data['Recettes_Totales'][i]
            if recettes > 0:
                ratio = dette / recettes
            else:
                ratio = 1.0
            data['Ratio_Endettement_Recettes'].append(ratio)
        
        df = pd.DataFrame(data)
        
        # Ajouter des événements spécifiques à La Réunion
        self._add_reunion_events(df, config)
        
        return df, config
    
    def _add_reunion_events(self, df, config):
        """Ajoute l'impact des événements historiques sur les données"""
        for i, row in df.iterrows():
            year = row['Annee']
            
            # Plan de développement réunionnais (2003-2007)
            if 2003 <= year <= 2007:
                df.loc[i, 'Recettes_Totales'] *= 1.15
                df.loc[i, 'Dette_Totale'] *= 1.25
            
            # Crise économique (2008-2009)
            if 2008 <= year <= 2009:
                df.loc[i, 'Recettes_Totales'] *= 0.97
                df.loc[i, 'Dette_Totale'] *= 1.05
            
            # Plan de relance DOM (2010-2013)
            if 2010 <= year <= 2013:
                df.loc[i, 'Dotations_Etat'] *= 1.18
                df.loc[i, 'Dette_Totale'] *= 1.10
            
            # Contrat de projet État-Région (2014-2018)
            if 2014 <= year <= 2018:
                df.loc[i, 'Dette_Totale'] *= 1.15
            
            # Mouvements sociaux (2018-2019)
            if year in [2018, 2019]:
                df.loc[i, 'Depenses_Totales'] *= 1.08
            
            # Crise COVID-19 (2020-2021)
            if 2020 <= year <= 2021:
                if year == 2020:
                    df.loc[i, 'Dotations_Etat'] *= 1.25
                    df.loc[i, 'Recettes_Totales'] *= 0.95
                else:
                    df.loc[i, 'Recettes_Totales'] *= 0.92
            
            # Plan de relance (2022-2025)
            if year >= 2022:
                df.loc[i, 'Dotations_Etat'] *= 1.15
                df.loc[i, 'Capacite_Remboursement'] *= 1.1
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Analyse d\'Endettement des 24 Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            **Dashboard d'analyse financière comparative des communes réunionnaises**  
            *Période d'analyse: 2002-2025 • Données simulées pour analyse stratégique*
            """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les paramètres"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            st.markdown("## 🔧 Paramètres d'analyse")
            
            # Sélection de la commune avec recherche
            commune_options = list(self.communes_config.keys())
            selected_commune = st.selectbox(
                "Sélectionnez une commune:",
                commune_options,
                index=0
            )
            
            # Filtrage par région
            st.markdown("### 🗺️ Filtre par région")
            regions = sorted(set([config["region"] for config in self.communes_config.values()]))
            selected_region = st.multiselect(
                "Filtrer par région:",
                regions,
                default=regions
            )
            
            # Filtrage par type de commune
            st.markdown("### 🏙️ Filtre par type")
            commune_types = sorted(set([config["type"] for config in self.communes_config.values()]))
            selected_types = st.multiselect(
                "Filtrer par type de commune:",
                commune_types,
                default=commune_types
            )
            
            # Période d'analyse
            st.markdown("### 📅 Période d'analyse")
            year_range = st.slider(
                "Sélectionnez la période:",
                min_value=self.start_year,
                max_value=self.end_year,
                value=(self.start_year, self.end_year)
            )
            
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
            
            total_population = sum([config["population_base"] for config in self.communes_config.values()])
            total_debt = sum([config["endettement_base"] for config in self.communes_config.values()])
            
            st.metric("Population totale", f"{total_population:,}")
            st.metric("Dette totale estimée", f"{total_debt:.0f} M€")
            st.metric("Nombre de communes", "24")
            
            st.markdown("---")
            st.markdown("#### ℹ️ À propos")
            st.markdown("""
            **Source:** Données simulées pour démonstration  
            **Période:** 2002-2025  
            **Mise à jour:** Février 2024
            """)
            
            return selected_commune, year_range, show_advanced, compare_communes, selected_region, selected_types
    
    def create_commune_overview(self):
        """Crée une vue d'ensemble de toutes les communes"""
        st.markdown("### 🗺️ Vue d'ensemble des 24 communes")
        
        # Créer un dataframe récapitulatif
        overview_data = []
        for commune_name, config in self.communes_config.items():
            df, _ = self.generate_financial_data(commune_name)
            last_row = df.iloc[-1]
            
            overview_data.append({
                'Commune': commune_name,
                'Région': config['region'],
                'Type': config['type'],
                'Population': config['population_base'],
                'Budget (M€)': config['budget_base'],
                'Dette (M€)': last_row['Dette_Totale'],
                'Taux Endettement (%)': last_row['Taux_Endettement'] * 100,
                'Capacité Remb.': last_row['Capacite_Remboursement'],
                'Couleur': config['couleur']
            })
        
        overview_df = pd.DataFrame(overview_data)
        
        # Tableau interactif
        st.dataframe(
            overview_df.style.format({
                'Dette (M€)': '{:.1f}',
                'Taux Endettement (%)': '{:.1f}',
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
                "Budget (M€)": st.column_config.NumberColumn("Budget", format="%.1f"),
                "Dette (M€)": st.column_config.NumberColumn("Dette", format="%.1f"),
                "Taux Endettement (%)": st.column_config.NumberColumn("Taux", format="%.1f"),
                "Capacité Remb.": st.column_config.NumberColumn("Capacité", format="%.2f")
            }
        )
        
        # Graphique de répartition par région
        st.markdown("#### 📊 Répartition par région")
        
        region_data = overview_df.groupby('Région').agg({
            'Commune': 'count',
            'Population': 'sum',
            'Dette (M€)': 'sum'
        }).reset_index()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig = px.pie(region_data, values='Commune', names='Région',
                        title='Nombre de communes par région',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.pie(region_data, values='Population', names='Région',
                        title='Population par région',
                        color_discrete_sequence=px.colors.qualitative.Set2)
            st.plotly_chart(fig, use_container_width=True)
        
        with col3:
            fig = px.bar(region_data, x='Région', y='Dette (M€)',
                        title='Dette totale par région (M€)',
                        color='Région',
                        color_discrete_sequence=px.colors.qualitative.Set1)
            st.plotly_chart(fig, use_container_width=True)
    
    def create_summary_metrics(self, df, config, commune_name):
        """Crée les indicateurs de résumé"""
        st.markdown(f'<h2 class="commune-header">🏙️ Commune de {commune_name}</h2>', 
                   unsafe_allow_html=True)
        
        # Informations sur la commune
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📍 Caractéristiques")
            st.markdown(f"**Région:** {config['region']}")
            st.markdown(f"**Type:** {config['type']}")
            st.markdown(f"**Spécialités:** {', '.join(config['specialites'])}")
            st.markdown(f"**Population 2025:** {df['Population'].iloc[-1]:,.0f} hab")
        
        with col2:
            st.markdown("#### 💰 Situation financière 2025")
            last_row = df.iloc[-1]
            st.metric("Dette totale", f"{last_row['Dette_Totale']:.1f} M€")
            st.metric("Recettes annuelles", f"{last_row['Recettes_Totales']:.1f} M€")
            st.metric("Taux d'endettement", f"{last_row['Taux_Endettement']*100:.1f}%")
        
        with col3:
            st.markdown("#### 📈 Évolution et capacité")
            debt_growth = ((df['Dette_Totale'].iloc[-1] / df['Dette_Totale'].iloc[0]) - 1) * 100
            revenue_growth = ((df['Recettes_Totales'].iloc[-1] / df['Recettes_Totales'].iloc[0]) - 1) * 100
            st.metric("Croissance dette", f"{debt_growth:+.1f}%")
            st.metric("Croissance recettes", f"{revenue_growth:+.1f}%")
            st.metric("Capacité remboursement", f"{last_row['Capacite_Remboursement']:.2f}")
        
        # Alertes de situation
        self._display_alerts(df.iloc[-1])
    
    def _display_alerts(self, last_data):
        """Affiche les alertes selon la situation financière"""
        capacity = last_data['Capacite_Remboursement']
        debt_ratio = last_data['Ratio_Endettement_Recettes']
        
        col1, col2 = st.columns(2)
        
        with col1:
            if capacity < 1.2:
                st.error("⚠️ **Situation préoccupante**")
                st.markdown("La capacité de remboursement est faible. Actions correctives urgentes nécessaires.")
            elif capacity < 2.0:
                st.warning("📊 **Situation sous contrôle**")
                st.markdown("Endettement maîtrisé mais vigilance requise sur les dépenses.")
            else:
                st.success("✅ **Situation saine**")
                st.markdown("Bonne capacité de remboursement et endettement maîtrisé.")
        
        with col2:
            if debt_ratio > 1.5:
                st.error("📉 **Ratio dette/recettes élevé**")
                st.markdown(f"Ratio: {debt_ratio:.2f} (la dette représente {debt_ratio:.1f}x les recettes annuelles)")
            elif debt_ratio > 1.0:
                st.warning("⚖️ **Ratio dette/recettes modéré**")
                st.markdown(f"Ratio: {debt_ratio:.2f} - Surveillance recommandée")
            else:
                st.success("📈 **Ratio dette/recettes favorable**")
                st.markdown(f"Ratio: {debt_ratio:.2f} - Situation favorable")
    
    def create_debt_evolution_chart(self, df, commune_name, config):
        """Crée le graphique d'évolution de la dette"""
        st.markdown("### 📈 Évolution de la dette (2002-2025)")
        
        fig = go.Figure()
        
        # Dette totale
        fig.add_trace(go.Scatter(
            x=df['Annee'],
            y=df['Dette_Totale'],
            mode='lines+markers',
            name='Dette Totale (M€)',
            line=dict(color=config['couleur'], width=3),
            hovertemplate='Année: %{x}<br>Dette: %{y:.1f} M€<extra></extra>'
        ))
        
        # Recettes pour comparaison
        fig.add_trace(go.Scatter(
            x=df['Annee'],
            y=df['Recettes_Totales'],
            mode='lines',
            name='Recettes Annuelles (M€)',
            line=dict(color='#2A9D8F', width=2, dash='dash'),
            yaxis='y2',
            hovertemplate='Année: %{x}<br>Recettes: %{y:.1f} M€<extra></extra>'
        ))
        
        # Marqueurs pour événements importants
        events = {
            2007: "Plan développement",
            2009: "Crise économique",
            2013: "Plan relance DOM",
            2018: "Mouvements sociaux",
            2020: "COVID-19",
            2024: "Plan relance"
        }
        
        for year, event in events.items():
            if year in df['Annee'].values:
                idx = df[df['Annee'] == year].index[0]
                fig.add_annotation(
                    x=year,
                    y=df.loc[idx, 'Dette_Totale'],
                    text=event,
                    showarrow=True,
                    arrowhead=1,
                    arrowsize=1,
                    arrowwidth=2,
                    arrowcolor=config['couleur']
                )
        
        fig.update_layout(
            title=f'Évolution de la dette - {commune_name}',
            xaxis_title='Année',
            yaxis_title='Dette Totale (M€)',
            yaxis2=dict(
                title='Recettes (M€)',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_financial_ratios_chart(self, df, commune_name, config):
        """Crée le graphique des ratios financiers"""
        st.markdown("### 📊 Ratios financiers clés")
        
        fig = go.Figure()
        
        # Taux d'endettement
        fig.add_trace(go.Scatter(
            x=df['Annee'],
            y=df['Taux_Endettement'] * 100,
            mode='lines+markers',
            name='Taux d\'endettement (%)',
            line=dict(color='#E76F51', width=3),
            hovertemplate='Année: %{x}<br>Taux: %{y:.1f}%<extra></extra>'
        ))
        
        # Capacité de remboursement
        fig.add_trace(go.Scatter(
            x=df['Annee'],
            y=df['Capacite_Remboursement'],
            mode='lines',
            name='Capacité de remboursement',
            line=dict(color='#F9A602', width=2),
            yaxis='y2',
            hovertemplate='Année: %{x}<br>Capacité: %{y:.2f}<extra></extra>'
        ))
        
        # Seuil d'alerte
        fig.add_hline(y=1.0, line_dash="dash", line_color="red", 
                     annotation_text="Seuil de danger", 
                     annotation_position="bottom right")
        
        fig.update_layout(
            title='Ratios de soutenabilité de la dette',
            xaxis_title='Année',
            yaxis_title='Taux d\'endettement (%)',
            yaxis2=dict(
                title='Capacité de remboursement',
                overlaying='y',
                side='right'
            ),
            hovermode='x unified',
            height=400,
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    def create_revenue_structure_chart(self, df, commune_name, config):
        """Crée le graphique de la structure des recettes"""
        st.markdown("### 💰 Structure des recettes communales")
        
        # Calcul des parts
        df['Autres_Recettes'] = df['Recettes_Totales'] - df['Impots_Locaux'] - df['Dotations_Etat']
        
        # Dernières 5 années
        years = df['Annee'].tail(5).tolist()
        
        categories = {
            'Impôts Locaux': df['Impots_Locaux'].tail(5).values,
            'Dotations État': df['Dotations_Etat'].tail(5).values,
            'Autres Recettes': df['Autres_Recettes'].tail(5).values
        }
        
        fig = go.Figure()
        
        colors = ['#264653', '#2A9D8F', '#E76F51']
        for i, (category, values) in enumerate(categories.items()):
            fig.add_trace(go.Bar(
                name=category,
                x=years,
                y=values,
                marker_color=colors[i],
                hovertemplate='Année: %{x}<br>Montant: %{y:.1f} M€<extra></extra>'
            ))
        
        fig.update_layout(
            title='Répartition des recettes (dernières 5 années)',
            barmode='stack',
            xaxis_title='Année',
            yaxis_title='Montant (M€)',
            height=400,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Analyse de la structure moyenne
        avg_tax_share = (df['Impots_Locaux'].mean() / df['Recettes_Totales'].mean()) * 100
        avg_state_share = (df['Dotations_Etat'].mean() / df['Recettes_Totales'].mean()) * 100
        avg_other_share = 100 - avg_tax_share - avg_state_share
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Part moyenne impôts", f"{avg_tax_share:.1f}%")
        with col2:
            st.metric("Part moyenne État", f"{avg_state_share:.1f}%")
        with col3:
            st.metric("Autres recettes", f"{avg_other_share:.1f}%")
    
    def create_comparative_analysis(self, communes_to_compare, year_range):
        """Crée l'analyse comparative entre communes"""
        st.markdown("### 📊 Analyse comparative entre communes")
        
        if len(communes_to_compare) == 0:
            st.info("👈 Sélectionnez des communes à comparer dans la sidebar")
            return
        
        all_communes = communes_to_compare
        comparison_data = []
        
        for commune_name in all_communes:
            df, config = self.generate_financial_data(commune_name)
            df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
            
            last_row = df_filtered.iloc[-1]
            first_row = df_filtered.iloc[0]
            
            comparison_data.append({
                'Commune': commune_name,
                'Région': config['region'],
                'Type': config['type'],
                'Dette_2025': last_row['Dette_Totale'],
                'Recettes_2025': last_row['Recettes_Totales'],
                'Taux_Endettement': last_row['Taux_Endettement'] * 100,
                'Capacite_Remboursement': last_row['Capacite_Remboursement'],
                'Croissance_Dette': ((last_row['Dette_Totale'] / first_row['Dette_Totale']) - 1) * 100,
                'Ratio_Dette_Recettes': last_row['Ratio_Endettement_Recettes'],
                'Couleur': config['couleur']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Graphique radar pour comparaison multicritères
        st.markdown("#### 📈 Profil financier comparé")
        
        categories = ['Dette_2025', 'Recettes_2025', 'Taux_Endettement', 
                     'Capacite_Remboursement', 'Ratio_Dette_Recettes']
        
        fig = go.Figure()
        
        for idx, row in comparison_df.iterrows():
            # Normalisation des valeurs pour le radar
            values = [
                row['Dette_2025'] / comparison_df['Dette_2025'].max(),
                row['Recettes_2025'] / comparison_df['Recettes_2025'].max(),
                row['Taux_Endettement'] / 100,  # Déjà en pourcentage
                row['Capacite_Remboursement'] / comparison_df['Capacite_Remboursement'].max(),
                row['Ratio_Dette_Recettes'] / comparison_df['Ratio_Dette_Recettes'].max()
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=['Dette', 'Recettes', 'Taux Endett.', 'Capacité', 'Ratio D/R'],
                name=row['Commune'],
                line_color=row['Couleur'],
                fill='toself'
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            showlegend=True,
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau comparatif détaillé
        st.markdown("#### 📋 Indicateurs comparatifs")
        
        display_df = comparison_df.copy()
        display_df['Classification'] = display_df['Capacite_Remboursement'].apply(
            lambda x: '✅ Saine' if x > 2.0 else '⚠️ Sous contrôle' if x > 1.2 else '❌ Préoccupante'
        )
        
        st.dataframe(
            display_df[['Commune', 'Région', 'Type', 'Dette_2025', 'Recettes_2025', 
                       'Taux_Endettement', 'Capacite_Remboursement', 'Croissance_Dette',
                       'Ratio_Dette_Recettes', 'Classification']].round(2),
            use_container_width=True,
            column_config={
                "Commune": "Commune",
                "Région": "Région",
                "Type": "Type",
                "Dette_2025": st.column_config.NumberColumn("Dette 2025 (M€)", format="%.1f"),
                "Recettes_2025": st.column_config.NumberColumn("Recettes 2025 (M€)", format="%.1f"),
                "Taux_Endettement": st.column_config.NumberColumn("Taux Endett. (%)", format="%.1f"),
                "Capacite_Remboursement": st.column_config.NumberColumn("Capacité", format="%.2f"),
                "Croissance_Dette": st.column_config.NumberColumn("Croiss. Dette (%)", format="%.1f"),
                "Ratio_Dette_Recettes": st.column_config.NumberColumn("Ratio D/R", format="%.2f"),
                "Classification": "Situation"
            }
        )
    
    def create_ranking_analysis(self, year_range):
        """Crée un classement des communes par indicateurs"""
        st.markdown("### 🏆 Classement des communes")
        
        ranking_data = []
        
        for commune_name, config in self.communes_config.items():
            df, _ = self.generate_financial_data(commune_name)
            df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
            last_row = df_filtered.iloc[-1]
            
            ranking_data.append({
                'Commune': commune_name,
                'Région': config['region'],
                'Dette_par_Habitant': (last_row['Dette_Totale'] * 1000000) / df_filtered['Population'].mean(),
                'Capacite_Remboursement': last_row['Capacite_Remboursement'],
                'Taux_Endettement': last_row['Taux_Endettement'] * 100,
                'Ratio_Dette_Recettes': last_row['Ratio_Endettement_Recettes'],
                'Epargne_Brute': last_row['Epargne_Brute']
            })
        
        ranking_df = pd.DataFrame(ranking_data)
        
        # Sélection de l'indicateur de classement
        col1, col2 = st.columns(2)
        
        with col1:
            ranking_metric = st.selectbox(
                "Classer par:",
                ['Capacite_Remboursement', 'Dette_par_Habitant', 'Taux_Endettement', 
                 'Ratio_Dette_Recettes', 'Epargne_Brute'],
                format_func=lambda x: {
                    'Capacite_Remboursement': 'Capacité de remboursement',
                    'Dette_par_Habitant': 'Dette par habitant',
                    'Taux_Endettement': 'Taux d\'endettement',
                    'Ratio_Dette_Recettes': 'Ratio dette/recettes',
                    'Epargne_Brute': 'Épargne brute'
                }[x]
            )
        
        with col2:
            ascending = st.checkbox("Ordre croissant", 
                                  value=(ranking_metric in ['Dette_par_Habitant', 'Taux_Endettement', 'Ratio_Dette_Recettes']))
        
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
                    format="%.2f" if ranking_metric != 'Dette_par_Habitant' else "%.0f"
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
    
    def create_recommandations(self, df, config):
        """Crée la section des recommandations"""
        st.markdown("### 💡 Recommandations stratégiques")
        
        last_data = df.iloc[-1]
        capacity = last_data['Capacite_Remboursement']
        debt_ratio = last_data['Ratio_Endettement_Recettes']
        
        # Recommandations spécifiques
        tabs = st.tabs(["Priorités", "Investissements", "Gouvernance"])
        
        with tabs[0]:
            if capacity < 1.2:
                st.error("**Actions prioritaires immédiates:**")
                st.markdown("""
                1. **Révision du plan pluriannuel d'investissement**
                   - Report des projets non prioritaires
                   - Rééchelonnement des projets en cours
                
                2. **Optimisation des recettes**
                   - Actualisation des bases fiscales
                   - Recouvrement des impôts en retard
                   - Développement de nouvelles ressources
                
                3. **Maîtrise des dépenses**
                   - Audit des contrats de service
                   - Rationalisation des achats
                   - Optimisation des effectifs
                """)
            else:
                st.success("**Actions d'optimisation:**")
                st.markdown("""
                1. **Investissements structurants**
                   - Projets à fort retour sur investissement
                   - Infrastructures durables
                   - Numérisation des services
                
                2. **Renforcement de l'épargne**
                   - Constitution de réserves
                   - Gestion proactive de la trésorerie
                   - Optimisation des placements
                
                3. **Préparation aux risques**
                   - Plans de continuité d'activité
                   - Stress tests financiers
                   - Assurance des risques majeurs
                """)
        
        with tabs[1]:
            st.markdown("**Orientation des investissements:**")
            st.markdown(f"""
            Compte tenu des spécialités de {config['specialites']}:
            
            **Investissements prioritaires:**
            - {config['specialites'][0]}: Modernisation des équipements
            - {config['specialites'][1] if len(config['specialites']) > 1 else 'Infrastructures'}: Développement des capacités
            - Transition écologique: Adaptation au changement climatique
            
            **Financement recommandé:**
            - Fonds européens: {config['region']} est éligible
            - Dotations spécifiques DOM
            - Partenariats public-privé
            """)
        
        with tabs[2]:
            st.markdown("**Amélioration de la gouvernance:**")
            st.markdown("""
            1. **Transparence financière**
               - Publication trimestrielle des indicateurs
               - Portail open data des finances communales
               - Réunions publiques de restitution
            
            2. **Participation citoyenne**
               - Budget participatif
               - Consultations sur les grands projets
               - Commission des finances ouverte
            
            3. **Formation et compétences**
               - Formation continue des élus
               - Recrutement de compétences financières
               - Échange de bonnes pratiques intercommunales
            """)
    
    def run_dashboard(self):
        """Exécute le dashboard principal"""
        self.create_header()
        
        # Récupération des paramètres
        selected_commune, year_range, show_advanced, compare_communes, selected_region, selected_types = self.create_sidebar()
        
        # Filtrage des communes par région et type
        filtered_communes = [
            commune for commune, config in self.communes_config.items()
            if config['region'] in selected_region and config['type'] in selected_types
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
            st.markdown("### 📈 Tendances globales")
            
            total_data = []
            for commune in filtered_communes:
                df, _ = self.generate_financial_data(commune)
                df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
                
                for _, row in df_filtered.iterrows():
                    total_data.append({
                        'Annee': row['Annee'],
                        'Commune': commune,
                        'Dette': row['Dette_Totale'],
                        'Recettes': row['Recettes_Totales']
                    })
            
            total_df = pd.DataFrame(total_data)
            annual_totals = total_df.groupby('Annee').agg({
                'Dette': 'sum',
                'Recettes': 'sum'
            }).reset_index()
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=annual_totals['Annee'], y=annual_totals['Dette'],
                                    name='Dette totale (M€)', line=dict(color='#E76F51', width=3)))
            fig.add_trace(go.Scatter(x=annual_totals['Annee'], y=annual_totals['Recettes'],
                                    name='Recettes totales (M€)', line=dict(color='#2A9D8F', width=3)))
            
            fig.update_layout(title='Évolution de la dette et des recettes - Toutes communes',
                            xaxis_title='Année', yaxis_title='Montant (M€)',
                            height=400)
            
            st.plotly_chart(fig, use_container_width=True)
        
        with tab2:
            # Analyse de la commune sélectionnée
            if selected_commune in filtered_communes:
                df, config = self.generate_financial_data(selected_commune)
                df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
                
                self.create_summary_metrics(df_filtered, config, selected_commune)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    self.create_debt_evolution_chart(df_filtered, selected_commune, config)
                    self.create_revenue_structure_chart(df_filtered, selected_commune, config)
                
                with col2:
                    self.create_financial_ratios_chart(df_filtered, selected_commune, config)
                    
                    # Tableau des données annuelles
                    st.markdown("#### 📊 Données annuelles")
                    st.dataframe(
                        df_filtered[['Annee', 'Dette_Totale', 'Recettes_Totales', 
                                    'Depenses_Totales', 'Taux_Endettement', 
                                    'Capacite_Remboursement']].style.format({
                            'Dette_Totale': '{:.1f}',
                            'Recettes_Totales': '{:.1f}',
                            'Depenses_Totales': '{:.1f}',
                            'Taux_Endettement': '{:.3f}',
                            'Capacite_Remboursement': '{:.2f}'
                        }),
                        use_container_width=True,
                        height=300
                    )
            else:
                st.warning("La commune sélectionnée ne correspond pas aux filtres actuels.")
        
        with tab3:
            # Comparaisons
            if compare_communes:
                self.create_comparative_analysis([selected_commune] + compare_communes, year_range)
            else:
                st.info("👈 Sélectionnez des communes à comparer dans la sidebar")
                
                # Comparaison avec les moyennes régionales
                st.markdown("### 📊 Positionnement régional")
                
                region_data = []
                for commune in filtered_communes:
                    df, config = self.generate_financial_data(commune)
                    df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
                    last_row = df_filtered.iloc[-1]
                    
                    region_data.append({
                        'Commune': commune,
                        'Région': config['region'],
                        'Dette': last_row['Dette_Totale'],
                        'Capacité': last_row['Capacite_Remboursement']
                    })
                
                region_df = pd.DataFrame(region_data)
                regional_avg = region_df.groupby('Région').agg({
                    'Dette': 'mean',
                    'Capacité': 'mean'
                }).reset_index()
                
                fig = px.box(region_df, x='Région', y='Dette',
                            title='Distribution de la dette par région',
                            color='Région')
                st.plotly_chart(fig, use_container_width=True)
        
        with tab4:
            # Classements
            self.create_ranking_analysis(year_range)
            
            # Analyse par région
            st.markdown("### 🗺️ Performance par région")
            
            region_performance = []
            for region in selected_region:
                region_communes = [c for c in filtered_communes 
                                 if self.communes_config[c]['region'] == region]
                if region_communes:
                    total_debt = sum([self.generate_financial_data(c)[0]['Dette_Totale'].iloc[-1] 
                                    for c in region_communes])
                    avg_capacity = np.mean([self.generate_financial_data(c)[0]['Capacite_Remboursement'].iloc[-1] 
                                          for c in region_communes])
                    
                    region_performance.append({
                        'Région': region,
                        'Nombre Communes': len(region_communes),
                        'Dette Totale': total_debt,
                        'Capacité Moyenne': avg_capacity,
                        'Dette par Commune': total_debt / len(region_communes)
                    })
            
            if region_performance:
                perf_df = pd.DataFrame(region_performance)
                
                col1, col2 = st.columns(2)
                with col1:
                    fig = px.bar(perf_df, x='Région', y='Dette Totale',
                                title='Dette totale par région (M€)')
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    fig = px.bar(perf_df, x='Région', y='Capacité Moyenne',
                                title='Capacité de remboursement moyenne')
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab5:
            # Recommandations
            if selected_commune in filtered_communes:
                df, config = self.generate_financial_data(selected_commune)
                df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
                self.create_recommandations(df_filtered, config)
            else:
                st.info("Sélectionnez une commune pour voir les recommandations spécifiques.")
            
            # Recommandations générales
            st.markdown("---")
            st.markdown("### 🌟 Bonnes pratiques pour toutes les communes")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 Transparence financière**")
                st.markdown("""
                - Publication des comptes administratifs
                - Indicateurs de performance accessibles
                - Rapports annuels de gestion
                - Portail open data financier
                """)
                
                st.markdown("**🤝 Coopération intercommunale**")
                st.markdown("""
                - Mutualisation des services
                - Achats groupés
                - Partage d'expertise
                - Projets communs
                """)
            
            with col2:
                st.markdown("**🌿 Développement durable**")
                st.markdown("""
                - Budget vert
                - Investissements écologiques
                - Adaptation climatique
                - Économie circulaire
                """)
                
                st.markdown("**💼 Attractivité économique**")
                st.markdown("""
                - Soutien aux entreprises locales
                - Développement touristique
                - Infrastructures numériques
                - Formation professionnelle
                """)
        
        # Pied de page
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col2:
            st.markdown("""
            **Dashboard développé pour l'analyse stratégique des finances communales réunionnaises**  
            *Données simulées - Version 1.0 - Février 2024*
            """)

# Exécution du dashboard
if __name__ == "__main__":
    dashboard = ReunionEndettementDashboard()
    dashboard.run_dashboard()
