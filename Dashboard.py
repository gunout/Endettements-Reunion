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
</style>
""", unsafe_allow_html=True)

class ReunionEndettementDashboard:
    def __init__(self):
        self.colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#F9A602', '#6A0572', 
                      '#AB83A1', '#5CAB7D', '#2A9D8F', '#E76F51', '#264653']
        self.start_year = 2002
        self.end_year = 2025
        
        # Configuration des communes réunionnaises
        self.communes_config = self._get_communes_config()
        
    def _get_communes_config(self):
        """Retourne la configuration de toutes les communes"""
        return {
            "Saint-Denis": {
                "population_base": 150000,
                "budget_base": 180,
                "type": "capitale_regionale",
                "specialites": ["administration", "services", "commerce", "sante", "education"],
                "endettement_base": 120,
                "fiscalite_base": 0.45,
                "couleur": "#264653"
            },
            "Saint-Paul": {
                "population_base": 105000,
                "budget_base": 95,
                "type": "urbaine_cotiere",
                "specialites": ["tourisme", "commerce", "grands_projets"],
                "endettement_base": 85,
                "fiscalite_base": 0.42,
                "couleur": "#2A9D8F"
            },
            "Saint-Pierre": {
                "population_base": 85000,
                "budget_base": 80,
                "type": "urbaine_sud",
                "specialites": ["port", "commerce", "enseignement_superieur"],
                "endettement_base": 65,
                "fiscalite_base": 0.44,
                "couleur": "#E76F51"
            },
            "Le Tampon": {
                "population_base": 80000,
                "budget_base": 70,
                "type": "periurbaine",
                "specialites": ["agriculture", "equipements_collectifs"],
                "endettement_base": 55,
                "fiscalite_base": 0.40,
                "couleur": "#F9A602"
            },
            "Saint-Louis": {
                "population_base": 55000,
                "budget_base": 50,
                "type": "urbaine",
                "specialites": ["sucrerie", "zones_industrielles"],
                "endettement_base": 45,
                "fiscalite_base": 0.43,
                "couleur": "#6A0572"
            }
        }
    
    def generate_financial_data(self, commune_name):
        """Génère des données financières simulées pour une commune"""
        config = self.communes_config[commune_name]
        
        # Créer une base de données annuelle
        dates = pd.date_range(start=f'{self.start_year}-01-01', 
                             end=f'{self.end_year}-12-31', freq='Y')
        
        data = {'Annee': [date.year for date in dates]}
        
        # Simulation simplifiée pour le dashboard
        # Recettes
        base_revenue = config["budget_base"]
        data['Recettes_Totales'] = [base_revenue * (1 + 0.035*i) * np.random.normal(1, 0.07) 
                                   for i, date in enumerate(dates)]
        
        # Dépenses
        base_expenses = config["budget_base"] * 0.96
        data['Depenses_Totales'] = [base_expenses * (1 + 0.032*i) * np.random.normal(1, 0.06) 
                                   for i, date in enumerate(dates)]
        
        # Dette
        base_debt = config["endettement_base"]
        data['Dette_Totale'] = []
        for i, date in enumerate(dates):
            year = date.year
            if year in [2007, 2013, 2019, 2024]:
                change = 1.3
            elif year in [2009, 2015, 2021]:
                change = 0.95
            else:
                change = 1.02
            data['Dette_Totale'].append(base_debt * change * np.random.normal(1, 0.08))
        
        # Ratios
        data['Taux_Endettement'] = [0.65 * (1 - 0.008*max(0, year-2010)) * np.random.normal(1, 0.05) 
                                   for year in data['Annee']]
        
        data['Capacite_Remboursement'] = []
        for i, row in enumerate(data['Annee']):
            cap = 2.0 - 0.05*i + np.random.normal(0, 0.1)
            data['Capacite_Remboursement'].append(max(0.5, cap))
        
        data['Ratio_Endettement_Recettes'] = [data['Dette_Totale'][i] / data['Recettes_Totales'][i] 
                                             for i in range(len(data['Annee']))]
        
        # Épargne brute
        data['Epargne_Brute'] = [config["budget_base"] * 0.04 * (1 + 0.006*max(0, year-2010)) * np.random.normal(1, 0.12)
                                for year in data['Annee']]
        
        # Structure des recettes
        data['Impots_Locaux'] = [data['Recettes_Totales'][i] * 0.38 * np.random.normal(1, 0.08) 
                                for i in range(len(data['Annee']))]
        data['Dotations_Etat'] = [data['Recettes_Totales'][i] * 0.40 * np.random.normal(1, 0.05) 
                                 for i in range(len(data['Annee']))]
        
        df = pd.DataFrame(data)
        return df, config
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Analyse d\'Endettement Communal - La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
            **Dashboard d'analyse financière des communes réunionnaises**  
            *Période d'analyse: 2002-2025 • Données simulées pour analyse comparative*
            """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les paramètres"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            st.markdown("## 🔧 Paramètres d'analyse")
            
            # Sélection de la commune
            commune_options = list(self.communes_config.keys())
            selected_commune = st.selectbox(
                "Sélectionnez une commune:",
                commune_options,
                index=0
            )
            
            # Période d'analyse
            st.markdown("### 📅 Période d'analyse")
            year_range = st.slider(
                "Sélectionnez la période:",
                min_value=self.start_year,
                max_value=self.end_year,
                value=(self.start_year, self.end_year)
            )
            
            # Filtres additionnels
            st.markdown("### ⚙️ Options d'affichage")
            show_advanced = st.checkbox("Afficher les indicateurs avancés")
            compare_mode = st.checkbox("Mode comparatif (max 3 communes)")
            
            # Comparaison avec d'autres communes
            if compare_mode:
                compare_communes = st.multiselect(
                    "Sélectionnez des communes à comparer:",
                    [c for c in commune_options if c != selected_commune],
                    max_selections=2
                )
            else:
                compare_communes = []
            
            # Téléchargement des données
            st.markdown("### 💾 Export des données")
            if st.button("📥 Exporter les données au format CSV"):
                # Code pour exporter les données
                pass
            
            # Information sur la commune
            st.markdown("---")
            st.markdown("### ℹ️ À propos")
            st.markdown("""
            Ce dashboard présente une analyse **simulée** de l'endettement des communes réunionnaises.
            
            **Note:** Les données sont générées à des fins de démonstration et ne représentent pas les chiffres réels.
            """)
            
            return selected_commune, year_range, show_advanced, compare_communes
    
    def create_summary_metrics(self, df, config, commune_name):
        """Crée les indicateurs de résumé"""
        st.markdown(f'<h2 class="commune-header">🏙️ Commune de {commune_name}</h2>', 
                   unsafe_allow_html=True)
        
        # Informations sur la commune
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📍 Caractéristiques")
            st.markdown(f"**Type:** {config['type']}")
            st.markdown(f"**Spécialités:** {', '.join(config['specialites'])}")
            st.markdown(f"**Population estimée:** {config['population_base']:,} hab")
        
        with col2:
            st.markdown("#### 💰 Budget")
            st.markdown(f"**Budget de base:** {config['budget_base']} M€")
            st.markdown(f"**Dette de base:** {config['endettement_base']} M€")
            st.markdown(f"**Taux fiscalité:** {config['fiscalite_base']*100:.1f}%")
        
        with col3:
            st.markdown("#### 📊 Indicateurs 2025")
            last_row = df.iloc[-1]
            st.metric("Dette totale", f"{last_row['Dette_Totale']:.1f} M€")
            st.metric("Taux d'endettement", f"{last_row['Taux_Endettement']*100:.1f}%")
            st.metric("Capacité remboursement", f"{last_row['Capacite_Remboursement']:.2f}")
        
        # Alertes de situation
        self._display_alerts(df.iloc[-1])
    
    def _display_alerts(self, last_data):
        """Affiche les alertes selon la situation financière"""
        capacity = last_data['Capacite_Remboursement']
        debt_ratio = last_data['Ratio_Endettement_Recettes']
        
        if capacity < 1.2:
            st.markdown('<div class="warning-box">', unsafe_allow_html=True)
            st.warning("⚠️ **Situation préoccupante** - La capacité de remboursement est faible. Actions correctives recommandées.")
            st.markdown('</div>', unsafe_allow_html=True)
        elif capacity < 2.0:
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.info("📊 **Situation sous contrôle** - Endettement maîtrisé mais vigilance requise.")
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="highlight-box">', unsafe_allow_html=True)
            st.success("✅ **Situation saine** - Bonne capacité de remboursement et endettement maîtrisé.")
            st.markdown('</div>', unsafe_allow_html=True)
    
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
        
        # Métriques d'évolution
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            debt_growth = ((df['Dette_Totale'].iloc[-1] / df['Dette_Totale'].iloc[0]) - 1) * 100
            st.metric("Croissance dette", f"{debt_growth:.1f}%")
        
        with col2:
            revenue_growth = ((df['Recettes_Totales'].iloc[-1] / df['Recettes_Totales'].iloc[0]) - 1) * 100
            st.metric("Croissance recettes", f"{revenue_growth:.1f}%")
        
        with col3:
            avg_debt = df['Dette_Totale'].mean()
            st.metric("Dette moyenne", f"{avg_debt:.1f} M€")
        
        with col4:
            max_debt = df['Dette_Totale'].max()
            st.metric("Dette maximale", f"{max_debt:.1f} M€")
    
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
        
        # Analyse des ratios
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_capacity = df['Capacite_Remboursement'].mean()
            status = "✅ Bonne" if avg_capacity > 1.5 else "⚠️ Moyenne" if avg_capacity > 1.0 else "❌ Faible"
            st.metric("Capacité moyenne", f"{avg_capacity:.2f}", status)
        
        with col2:
            min_capacity = df['Capacite_Remboursement'].min()
            st.metric("Capacité minimale", f"{min_capacity:.2f}")
        
        with col3:
            current_ratio = df['Ratio_Endettement_Recettes'].iloc[-1]
            st.metric("Ratio dette/recettes", f"{current_ratio:.2f}")
    
    def create_revenue_structure_chart(self, df, commune_name, config):
        """Crée le graphique de la structure des recettes"""
        st.markdown("### 💰 Structure des recettes communales")
        
        # Préparation des données
        years = df['Annee'].tail(5)  # Dernières 5 années
        
        categories = {
            'Impôts Locaux': df['Impots_Locaux'].tail(5).values,
            'Dotations État': df['Dotations_Etat'].tail(5).values,
            'Autres Recettes': (df['Recettes_Totales'] - df['Impots_Locaux'] - df['Dotations_Etat']).tail(5).values
        }
        
        fig = go.Figure()
        
        colors = ['#264653', '#2A9D8F', '#E76F51']
        for i, (category, values) in enumerate(categories.items()):
            fig.add_trace(go.Bar(
                name=category,
                x=years,
                y=values,
                marker_color=colors[i],
                hovertemplate='Année: %{x}<br>Montant: %{y:.1f} M€<br>Part: %{customdata:.1f}%<extra></extra>',
                customdata=[(values[j] / df['Recettes_Totales'].iloc[-5+j]) * 100 for j in range(5)]
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
        
        # Analyse de la structure
        col1, col2, col3 = st.columns(3)
        
        with col1:
            tax_share = (df['Impots_Locaux'].mean() / df['Recettes_Totales'].mean()) * 100
            st.metric("Part des impôts", f"{tax_share:.1f}%")
        
        with col2:
            state_share = (df['Dotations_Etat'].mean() / df['Recettes_Totales'].mean()) * 100
            st.metric("Part de l'État", f"{state_share:.1f}%")
        
        with col3:
            other_share = 100 - tax_share - state_share
            st.metric("Autres recettes", f"{other_share:.1f}%")
    
    def create_comparative_analysis(self, communes_to_compare, year_range):
        """Crée l'analyse comparative entre communes"""
        st.markdown("### 📊 Analyse comparative entre communes")
        
        comparison_data = []
        
        for commune_name in communes_to_compare:
            df, config = self.generate_financial_data(commune_name)
            df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
            
            comparison_data.append({
                'Commune': commune_name,
                'Dette_Moyenne': df_filtered['Dette_Totale'].mean(),
                'Recettes_Moyennes': df_filtered['Recettes_Totales'].mean(),
                'Taux_Endettement_Moyen': df_filtered['Taux_Endettement'].mean() * 100,
                'Capacite_Moyenne': df_filtered['Capacite_Remboursement'].mean(),
                'Couleur': config['couleur']
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Graphique comparatif
        fig = go.Figure()
        
        for _, row in comparison_df.iterrows():
            fig.add_trace(go.Bar(
                x=['Dette Moyenne (M€)', 'Recettes Moyennes (M€)', 'Taux Endettement (%)', 'Capacité Remboursement'],
                y=[row['Dette_Moyenne'], row['Recettes_Moyennes'], row['Taux_Endettement_Moyen'], row['Capacite_Moyenne']],
                name=row['Commune'],
                marker_color=row['Couleur'],
                hovertemplate='Commune: %{customdata}<br>Valeur: %{y:.1f}<extra></extra>',
                customdata=[row['Commune']] * 4
            ))
        
        fig.update_layout(
            title='Comparaison des indicateurs clés',
            barmode='group',
            height=500,
            hovermode='x unified',
            yaxis=dict(title='Valeur'),
            legend=dict(
                yanchor="top",
                y=0.99,
                xanchor="left",
                x=0.01
            )
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau comparatif
        st.markdown("#### 📋 Tableau comparatif détaillé")
        
        display_df = comparison_df.copy()
        display_df['Dette/Recettes'] = display_df['Dette_Moyenne'] / display_df['Recettes_Moyennes']
        display_df['Classification'] = display_df['Capacite_Moyenne'].apply(
            lambda x: '✅ Saine' if x > 2.0 else '⚠️ Sous contrôle' if x > 1.2 else '❌ Préoccupante'
        )
        
        st.dataframe(
            display_df[['Commune', 'Dette_Moyenne', 'Recettes_Moyennes', 
                       'Taux_Endettement_Moyen', 'Capacite_Moyenne', 
                       'Dette/Recettes', 'Classification']].round(2),
            use_container_width=True,
            column_config={
                "Commune": "Commune",
                "Dette_Moyenne": st.column_config.NumberColumn("Dette Moyenne (M€)", format="%.1f"),
                "Recettes_Moyennes": st.column_config.NumberColumn("Recettes Moyennes (M€)", format="%.1f"),
                "Taux_Endettement_Moyen": st.column_config.NumberColumn("Taux Endettement (%)", format="%.1f"),
                "Capacite_Moyenne": st.column_config.NumberColumn("Capacité Moyenne", format="%.2f"),
                "Dette/Recettes": st.column_config.NumberColumn("Ratio Dette/Recettes", format="%.2f"),
                "Classification": "Situation"
            }
        )
    
    def create_recommandations(self, df, config):
        """Crée la section des recommandations"""
        st.markdown("### 💡 Recommandations stratégiques")
        
        last_data = df.iloc[-1]
        capacity = last_data['Capacite_Remboursement']
        debt_ratio = last_data['Ratio_Endettement_Recettes']
        
        if capacity < 1.2:
            st.error("**Situation nécessitant des actions urgentes:**")
            st.markdown("""
            1. **Maîtrise des dépenses de fonctionnement**
               - Révision des contrats de services
               - Optimisation des achats publics
               - Rationalisation des effectifs
            
            2. **Restructuration de la dette**
               - Renégociation des taux d'intérêt
               - Rééchelonnement si nécessaire
               - Consolidation des emprunts
            
            3. **Augmentation des recettes**
               - Révision des bases fiscales
               - Développement de nouvelles sources
               - Optimisation du patrimoine communal
            """)
            
        elif capacity < 2.0:
            st.warning("**Actions de consolidation recommandées:**")
            st.markdown("""
            1. **Maintenir la discipline budgétaire**
               - Suivi rigoureux des engagements
               - Contrôle des dépenses discrétionnaires
               - Renforcement de l'épargne brute
            
            2. **Investissements sélectifs**
               - Prioriser les projets générateurs d'économies
               - Privilégier les infrastructures durables
               - Développer les partenariats public-privé
            
            3. **Anticipation des risques**
               - Stress tests financiers réguliers
               - Constitution de provisions
               - Plans de contingence
            """)
            
        else:
            st.success("**Opportunités d'optimisation:**")
            st.markdown("""
            1. **Investissements structurants**
               - Modernisation des équipements publics
               - Transition écologique et énergétique
               - Développement numérique
            
            2. **Optimisation de la trésorerie**
               - Placement des excédents
               - Réduction des délais de paiement
               - Gestion proactive des flux
            
            3. **Développement territorial**
               - Projets d'aménagement concertés
               - Valorisation du patrimoine
               - Attractivité économique
            """)
        
        # Recommandations générales
        st.markdown("#### 🌟 Bonnes pratiques pour toutes les communes")
        st.markdown("""
        - **Transparence financière:** Publication régulière des comptes
        - **Gouvernance:** Implication des citoyens dans les choix budgétaires
        - **Formation:** Renforcement des compétences des élus et agents
        - **Prospective:** Élaboration de scénarios à moyen et long terme
        - **Coopération intercommunale:** Mutualisation des moyens et compétences
        """)
    
    def create_historical_context(self):
        """Crée la section du contexte historique réunionnais"""
        st.markdown("### 📅 Contexte historique de La Réunion")
        
        tabs = st.tabs(["2002-2007", "2008-2013", "2014-2019", "2020-2025"])
        
        with tabs[0]:
            st.markdown("""
            #### Plan de développement réunionnais (2002-2007)
            - **Investissements massifs** dans les infrastructures
            - Augmentation des **dotations spécifiques DOM**
            - Développement des **services publics** locaux
            - **Croissance démographique** soutenue
            """)
        
        with tabs[1]:
            st.markdown("""
            #### Crise économique et plans de relance (2008-2013)
            - Impact de la **crise financière mondiale**
            - Plans de **relance spécifiques aux DOM**
            - Accentuation des **déséquilibres sociaux**
            - Renforcement des **aides de l'État**
            """)
        
        with tabs[2]:
            st.markdown("""
            #### Contrat de projet État-Région (2014-2019)
            - **Grands travaux d'infrastructure** (routes, équipements)
            - Mouvements **sociaux de 2018-2019**
            - Augmentation de la **fiscalité locale**
            - Développement des **politiques sociales**
            """)
        
        with tabs[3]:
            st.markdown("""
            #### Crise COVID-19 et transition (2020-2025)
            - **Choc économique** de la pandémie
            - **Plans de soutien exceptionnels** de l'État
            - Accélération de la **transition écologique**
            - **Relance spécifique DOM** post-crise
            """)
    
    def run_dashboard(self):
        """Exécute le dashboard principal"""
        self.create_header()
        
        # Récupération des paramètres
        selected_commune, year_range, show_advanced, compare_communes = self.create_sidebar()
        
        # Génération des données
        df, config = self.generate_financial_data(selected_commune)
        
        # Filtrage par année
        df_filtered = df[(df['Annee'] >= year_range[0]) & (df['Annee'] <= year_range[1])]
        
        # Affichage principal
        tab1, tab2, tab3, tab4 = st.tabs([
            "📊 Vue d'ensemble", 
            "📈 Analyse détaillée", 
            "🔄 Comparaisons", 
            "📋 Recommandations"
        ])
        
        with tab1:
            # Vue d'ensemble
            self.create_summary_metrics(df_filtered, config, selected_commune)
            
            col1, col2 = st.columns(2)
            
            with col1:
                self.create_debt_evolution_chart(df_filtered, selected_commune, config)
            
            with col2:
                self.create_financial_ratios_chart(df_filtered, selected_commune, config)
            
            # Structure des recettes
            self.create_revenue_structure_chart(df_filtered, selected_commune, config)
        
        with tab2:
            # Analyse détaillée
            st.markdown(f"### 🔍 Analyse financière détaillée - {selected_commune}")
            
            # Tableau des données
            st.markdown("#### 📋 Données financières complètes")
            st.dataframe(
                df_filtered.style.format({
                    'Dette_Totale': '{:.1f}',
                    'Recettes_Totales': '{:.1f}',
                    'Depenses_Totales': '{:.1f}',
                    'Taux_Endettement': '{:.3f}',
                    'Capacite_Remboursement': '{:.2f}',
                    'Ratio_Endettement_Recettes': '{:.2f}'
                }),
                use_container_width=True,
                height=400
            )
            
            # Téléchargement des données
            csv = df_filtered.to_csv(index=False)
            st.download_button(
                label="📥 Télécharger les données (CSV)",
                data=csv,
                file_name=f"{selected_commune}_donnees_financieres_{year_range[0]}_{year_range[1]}.csv",
                mime="text/csv"
            )
            
            # Graphiques supplémentaires
            if show_advanced:
                st.markdown("#### 📊 Analyse avancée")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Évolution de l'épargne brute
                    fig = px.area(df_filtered, x='Annee', y='Epargne_Brute',
                                 title='Évolution de l\'épargne brute',
                                 labels={'Epargne_Brute': 'Épargne brute (M€)', 'Annee': 'Année'})
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Correlation dette-recettes
                    fig = px.scatter(df_filtered, x='Recettes_Totales', y='Dette_Totale',
                                     trendline="ols",
                                     title='Correlation entre recettes et dette',
                                     labels={'Recettes_Totales': 'Recettes (M€)', 
                                            'Dette_Totale': 'Dette (M€)'})
                    st.plotly_chart(fig, use_container_width=True)
        
        with tab3:
            # Comparaisons
            if compare_communes:
                self.create_comparative_analysis([selected_commune] + compare_communes, year_range)
            else:
                st.info("👈 Activez le mode comparatif dans la sidebar pour comparer plusieurs communes")
                
                # Comparaison avec la moyenne des communes
                st.markdown("### 📊 Positionnement par rapport aux autres communes")
                
                # Calcul des moyennes
                all_data = []
                for commune in self.communes_config.keys():
                    df_comm, _ = self.generate_financial_data(commune)
                    df_comm_filtered = df_comm[(df_comm['Annee'] >= year_range[0]) & 
                                              (df_comm['Annee'] <= year_range[1])]
                    all_data.append(df_comm_filtered)
                
                # Indicateurs comparatifs
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    avg_debt_all = np.mean([df['Dette_Totale'].mean() for df in all_data])
                    current_debt = df_filtered['Dette_Totale'].mean()
                    diff = ((current_debt / avg_debt_all) - 1) * 100
                    st.metric("Dette vs moyenne communes", 
                             f"{current_debt:.1f} M€", 
                             f"{diff:+.1f}%")
                
                with col2:
                    avg_capacity_all = np.mean([df['Capacite_Remboursement'].mean() for df in all_data])
                    current_capacity = df_filtered['Capacite_Remboursement'].mean()
                    diff_cap = current_capacity - avg_capacity_all
                    st.metric("Capacité vs moyenne", 
                             f"{current_capacity:.2f}", 
                             f"{diff_cap:+.2f}")
                
                with col3:
                    avg_ratio_all = np.mean([df['Taux_Endettement'].mean() for df in all_data]) * 100
                    current_ratio = df_filtered['Taux_Endettement'].mean() * 100
                    diff_ratio = current_ratio - avg_ratio_all
                    st.metric("Taux endettement vs moyenne", 
                             f"{current_ratio:.1f}%", 
                             f"{diff_ratio:+.1f}%")
        
        with tab4:
            # Recommandations et contexte
            col1, col2 = st.columns([2, 1])
            
            with col1:
                self.create_recommandations(df_filtered, config)
            
            with col2:
                self.create_historical_context()
            
            # Résumé exécutif
            st.markdown("---")
            st.markdown("### 🎯 Résumé exécutif")
            
            summary_cols = st.columns(3)
            
            with summary_cols[0]:
                st.markdown("#### 📈 Tendances")
                st.markdown(f"- Dette totale: **{df_filtered['Dette_Totale'].iloc[-1]:.1f} M€**")
                st.markdown(f"- Évolution: **{((df_filtered['Dette_Totale'].iloc[-1]/df_filtered['Dette_Totale'].iloc[0])-1)*100:+.1f}%**")
            
            with summary_cols[1]:
                st.markdown("#### ⚖️ Équilibre")
                st.markdown(f"- Recettes/dépenses: **{(df_filtered['Recettes_Totales'].mean()/df_filtered['Depenses_Totales'].mean()):.2f}**")
                st.markdown(f"- Épargne brute: **{df_filtered['Epargne_Brute'].mean():.1f} M€**")
            
            with summary_cols[2]:
                st.markdown("#### 🎯 Priorités")
                capacity = df_filtered['Capacite_Remboursement'].iloc[-1]
                if capacity < 1.2:
                    st.markdown("**Maîtrise de la dette**")
                elif capacity < 2.0:
                    st.markdown("**Consolidation budgétaire**")
                else:
                    st.markdown("**Investissements structurants**")

# Exécution du dashboard
if __name__ == "__main__":
    dashboard = ReunionEndettementDashboard()
    dashboard.run_dashboard()
