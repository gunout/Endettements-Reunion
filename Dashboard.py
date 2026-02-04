# app.py
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuration de la page
st.set_page_config(
    page_title="Dashboard Financier Communal - La Réunion",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.8rem;
        color: #374151;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .kpi-card {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .kpi-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E3A8A;
    }
    .kpi-label {
        font-size: 0.9rem;
        color: #6B7280;
    }
    .positive {
        color: #10B981;
    }
    .negative {
        color: #EF4444;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-header">📊 Dashboard Financier des Communes de La Réunion</h1>', unsafe_allow_html=True)
st.markdown("***Analyse budgétaire 2017 - Données OFGL***")

# Fonction pour charger les données
@st.cache_data
def load_data():
    df = pd.read_csv('ofgl-base-communes.csv', sep=';', low_memory=False)
    
    # Nettoyage des colonnes
    df.columns = df.columns.str.strip()
    
    # Conversion des colonnes numériques
    numeric_cols = ['Montant', 'Montant en millions', 'Population totale', 
                    'Montant en € par habitant', 'Population totale du dernier exercice']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Filtre pour La Réunion
    df = df[df['Code Insee 2024 Département'] == 974]
    
    return df

# Chargement des données
df = load_data()

# Sidebar - Filtres
with st.sidebar:
    st.markdown("## 🔧 Filtres")
    
    # Filtre par EPCI
    epci_list = df['Nom 2024 EPCI'].unique().tolist()
    selected_epci = st.multiselect(
        "EPCI (Intercommunalités)",
        options=epci_list,
        default=epci_list
    )
    
    # Filtre par caractéristique
    st.markdown("### Caractéristiques")
    col1, col2 = st.columns(2)
    with col1:
        montagne = st.checkbox("🏔️ Commune de montagne", value=True)
        rurale = st.checkbox("🌾 Commune rurale", value=True)
    with col2:
        touristique = st.checkbox("🏖️ Commune touristique", value=True)
        qpv = st.checkbox("🏙️ Présence QPV", value=True)
    
    # Filtre par agrégat financier
    agregats = df['Agrégat'].unique().tolist()
    selected_agregats = st.multiselect(
        "Indicateurs financiers",
        options=agregats,
        default=['Epargne brute', 'Capacité ou besoin de financement', 'Impôts et taxes']
    )
    
    # Filtre par type de budget
    budget_types = df['Type de budget'].unique().tolist()
    selected_budget_types = st.multiselect(
        "Types de budget",
        options=budget_types,
        default=budget_types
    )

# Application des filtres
filtered_df = df.copy()
if selected_epci:
    filtered_df = filtered_df[filtered_df['Nom 2024 EPCI'].isin(selected_epci)]

# Section 1: KPI Principaux
st.markdown('<h2 class="sub-header">📈 Vue d\'ensemble - Santé Financière</h2>', unsafe_allow_html=True)

# Calcul des KPI
df_principal = filtered_df[filtered_df['Type de budget'] == 'Budget principal']
df_principal_epargne = df_principal[df_principal['Agrégat'] == 'Epargne brute']
df_principal_financement = df_principal[df_principal['Agrégat'] == 'Capacité ou besoin de financement']

# KPI en colonnes
col1, col2, col3, col4 = st.columns(4)

with col1:
    total_epargne = df_principal_epargne['Montant'].sum() / 1_000_000
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_epargne:.1f} M€</div>
        <div class="kpi-label">Épargne brute totale</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    communes_positives = len(df_principal_financement[df_principal_financement['Montant'] > 0])
    communes_totales = len(df_principal_financement['Nom 2024 Commune'].unique())
    pourcentage_positives = (communes_positives / communes_totales * 100) if communes_totales > 0 else 0
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{pourcentage_positives:.0f}%</div>
        <div class="kpi-label">Communes avec capacité de financement</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    avg_epargne_hab = df_principal_epargne['Montant en € par habitant'].mean()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{avg_epargne_hab:.0f} €</div>
        <div class="kpi-label">Épargne brute moyenne/habitant</div>
    </div>
    """, unsafe_allow_html=True)

with col4:
    total_population = df_principal['Population totale'].sum()
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-value">{total_population:,.0f}</div>
        <div class="kpi-label">Population totale couverte</div>
    </div>
    """, unsafe_allow_html=True)

# Onglets pour les différentes analyses
tab1, tab2, tab3, tab4 = st.tabs([
    "🏛️ Santé Financière Communes",
    "📊 Comparaison Intercommunalités",
    "💧 Budgets Annexes",
    "💰 Focus Épargne Brute"
])

# TAB 1: Santé Financière des Communes
with tab1:
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### Capacité/Besoin de Financement par Commune")
        
        # Préparation des données
        df_financement = df_principal[df_principal['Agrégat'] == 'Capacité ou besoin de financement']
        df_financement = df_financement.sort_values('Montant en € par habitant', ascending=False)
        
        # Création du graphique
        fig = px.bar(
            df_financement,
            x='Nom 2024 Commune',
            y='Montant en € par habitant',
            color='Montant en € par habitant',
            color_continuous_scale=['#EF4444', '#FBBF24', '#10B981'],
            title="Capacité (+) ou Besoin (-) de Financement par Habitant",
            labels={'Montant en € par habitant': '€ par habitant', 'Nom 2024 Commune': 'Commune'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("### Top 5 - Meilleure santé financière")
        
        top_5 = df_financement.nlargest(5, 'Montant en € par habitant')[['Nom 2024 Commune', 'Montant en € par habitant']]
        for idx, row in top_5.iterrows():
            st.metric(
                label=row['Nom 2024 Commune'],
                value=f"{row['Montant en € par habitant']:,.0f} €/hab",
                delta=None
            )
        
        st.markdown("### Bottom 5")
        bottom_5 = df_financement.nsmallest(5, 'Montant en € par habitant')[['Nom 2024 Commune', 'Montant en € par habitant']]
        for idx, row in bottom_5.iterrows():
            st.metric(
                label=row['Nom 2024 Commune'],
                value=f"{row['Montant en € par habitant']:,.0f} €/hab",
                delta=None,
                delta_color="inverse"
            )
    
    # Carte de santé financière
    st.markdown("### Carte de Santé Financière")
    
    # Création d'une classification simplifiée
    def classify_health(value):
        if value > 100:
            return "Très bonne"
        elif value > 0:
            return "Bonne"
        elif value > -100:
            return "Difficultés"
        else:
            return "Situation difficile"
    
    df_financement['Santé financière'] = df_financement['Montant en € par habitant'].apply(classify_health)
    
    # Graphique en barres groupées
    health_counts = df_financement['Santé financière'].value_counts().reset_index()
    health_counts.columns = ['Santé financière', 'Nombre de communes']
    
    fig2 = px.bar(
        health_counts,
        x='Santé financière',
        y='Nombre de communes',
        color='Santé financière',
        color_discrete_map={
            "Très bonne": "#10B981",
            "Bonne": "#34D399",
            "Difficultés": "#FBBF24",
            "Situation difficile": "#EF4444"
        },
        title="Répartition des communes par santé financière"
    )
    fig2.update_layout(xaxis_title="", yaxis_title="Nombre de communes")
    st.plotly_chart(fig2, use_container_width=True)

# TAB 2: Comparaison Intercommunalités
with tab2:
    st.markdown("### Comparaison des Performances par EPCI")
    
    # Préparation des données par EPCI
    epci_metrics = []
    
    for epci in filtered_df['Nom 2024 EPCI'].unique():
        df_epci = filtered_df[filtered_df['Nom 2024 EPCI'] == epci]
        df_epci_principal = df_epci[df_epci['Type de budget'] == 'Budget principal']
        
        # Calcul des métriques
        epargne = df_epci_principal[df_epci_principal['Agrégat'] == 'Epargne brute']['Montant'].sum()
        financement = df_epci_principal[df_epci_principal['Agrégat'] == 'Capacité ou besoin de financement']['Montant'].sum()
        taxes = df_epci_principal[df_epci_principal['Agrégat'] == 'Impôts et taxes']['Montant'].sum()
        population = df_epci_principal['Population totale'].sum() / len(df_epci_principal['Nom 2024 Commune'].unique()) if len(df_epci_principal['Nom 2024 Commune'].unique()) > 0 else 0
        
        epci_metrics.append({
            'EPCI': epci,
            'Épargne brute (M€)': epargne / 1_000_000,
            'Capacité financement (M€)': financement / 1_000_000,
            'Impôts et taxes (M€)': taxes / 1_000_000,
            'Population moyenne': population
        })
    
    epci_df = pd.DataFrame(epci_metrics)
    
    # Graphique comparatif
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Épargne brute (M€)', 'Capacité financement (M€)', 
                       'Impôts et taxes (M€)', 'Population moyenne'),
        vertical_spacing=0.15
    )
    
    # Graphique 1: Épargne brute
    fig.add_trace(
        go.Bar(
            x=epci_df['EPCI'],
            y=epci_df['Épargne brute (M€)'],
            name='Épargne brute',
            marker_color='#3B82F6'
        ),
        row=1, col=1
    )
    
    # Graphique 2: Capacité financement
    fig.add_trace(
        go.Bar(
            x=epci_df['EPCI'],
            y=epci_df['Capacité financement (M€)'],
            name='Capacité financement',
            marker_color=epci_df['Capacité financement (M€)'].apply(
                lambda x: '#10B981' if x > 0 else '#EF4444'
            )
        ),
        row=1, col=2
    )
    
    # Graphique 3: Impôts et taxes
    fig.add_trace(
        go.Bar(
            x=epci_df['EPCI'],
            y=epci_df['Impôts et taxes (M€)'],
            name='Impôts et taxes',
            marker_color='#8B5CF6'
        ),
        row=2, col=1
    )
    
    # Graphique 4: Population
    fig.add_trace(
        go.Bar(
            x=epci_df['EPCI'],
            y=epci_df['Population moyenne'],
            name='Population moyenne',
            marker_color='#F59E0B'
        ),
        row=2, col=2
    )
    
    fig.update_layout(height=700, showlegend=False, title_text="Comparaison des EPCI")
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tableau détaillé
    st.markdown("### Tableau comparatif détaillé")
    st.dataframe(
        epci_df.style.format({
            'Épargne brute (M€)': '{:.2f}',
            'Capacité financement (M€)': '{:.2f}',
            'Impôts et taxes (M€)': '{:.2f}',
            'Population moyenne': '{:.0f}'
        }).background_gradient(subset=['Épargne brute (M€)'], cmap='Blues')
        .background_gradient(subset=['Capacité financement (M€)'], cmap='RdYlGn'),
        use_container_width=True
    )

# TAB 3: Analyse des Budgets Annexes
with tab3:
    st.markdown("### Analyse des Budgets Annexes (Services Publics)")
    
    # Filtre pour budgets annexes
    df_annexes = filtered_df[filtered_df['Type de budget'] == 'Budget annexe']
    
    # Classification des budgets annexes
    def classify_budget(libelle):
        libelle_lower = str(libelle).lower()
        if 'eau' in libelle_lower:
            return 'Eau'
        elif 'assain' in libelle_lower:
            return 'Assainissement'
        elif 'pompes funebres' in libelle_lower or 'pompe funèbre' in libelle_lower:
            return 'Pompes funèbres'
        elif 'spanc' in libelle_lower:
            return 'SPANC'
        elif 'touris' in libelle_lower:
            return 'Tourisme'
        else:
            return 'Autres'
    
    df_annexes['Type service'] = df_annexes['Libellé Budget'].apply(classify_budget)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Répartition par type de service
        service_dist = df_annexes['Type service'].value_counts().reset_index()
        service_dist.columns = ['Service', 'Nombre de budgets']
        
        fig = px.pie(
            service_dist,
            values='Nombre de budgets',
            names='Service',
            title="Répartition des budgets annexes par type de service",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Performance financière des services
        service_performance = df_annexes.groupby('Type service').agg({
            'Montant': 'sum',
            'Montant en € par habitant': 'mean'
        }).reset_index()
        
        service_performance = service_performance.sort_values('Montant', ascending=False)
        
        fig2 = px.bar(
            service_performance,
            x='Type service',
            y='Montant',
            color='Montant',
            color_continuous_scale='RdYlGn',
            title="Montant total par type de service (€)",
            labels={'Montant': 'Total (€)', 'Type service': 'Service'}
        )
        fig2.update_layout(height=400)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Analyse détaillée Eau vs Assainissement
    st.markdown("### Comparaison détaillée: Eau vs Assainissement")
    
    df_eau_assainissement = df_annexes[df_annexes['Type service'].isin(['Eau', 'Assainissement'])]
    
    if not df_eau_assainissement.empty:
        # Pivot table pour comparaison
        comparison_data = []
        for commune in df_eau_assainissement['Nom 2024 Commune'].unique():
            df_commune = df_eau_assainissement[df_eau_assainissement['Nom 2024 Commune'] == commune]
            
            eau = df_commune[df_commune['Type service'] == 'Eau']
            assain = df_commune[df_commune['Type service'] == 'Assainissement']
            
            eau_montant = eau['Montant'].sum() if not eau.empty else 0
            assain_montant = assain['Montant'].sum() if not assain.empty else 0
            
            comparison_data.append({
                'Commune': commune,
                'Eau (€)': eau_montant,
                'Assainissement (€)': assain_montant,
                'Ratio Eau/Assain': eau_montant/assain_montant if assain_montant != 0 else None
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        
        # Graphique comparatif
        fig3 = go.Figure()
        
        fig3.add_trace(go.Bar(
            x=comparison_df['Commune'],
            y=comparison_df['Eau (€)'],
            name='Eau',
            marker_color='#60A5FA'
        ))
        
        fig3.add_trace(go.Bar(
            x=comparison_df['Commune'],
            y=comparison_df['Assainissement (€)'],
            name='Assainissement',
            marker_color='#34D399'
        ))
        
        fig3.update_layout(
            title="Comparaison budgets Eau et Assainissement par commune",
            barmode='group',
            height=500,
            xaxis_title="Commune",
            yaxis_title="Montant (€)",
            xaxis_tickangle=45
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Statistiques
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric(
                "Budget Eau moyen",
                f"{comparison_df['Eau (€)'].mean():,.0f} €",
                delta=None
            )
        with col2:
            st.metric(
                "Budget Assainissement moyen",
                f"{comparison_df['Assainissement (€)'].mean():,.0f} €",
                delta=None
            )
        with col3:
            ratio_moyen = comparison_df['Ratio Eau/Assain'].mean()
            st.metric(
                "Ratio Eau/Assain moyen",
                f"{ratio_moyen:.2f}" if ratio_moyen else "N/A",
                delta=None
            )

# TAB 4: Focus sur l'Épargne Brute
with tab4:
    st.markdown("### Analyse approfondie de l'Épargne Brute")
    
    # Données pour l'analyse
    df_epargne = df_principal[df_principal['Agrégat'] == 'Epargne brute']
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribution de l'épargne brute par habitant
        fig = px.histogram(
            df_epargne,
            x='Montant en € par habitant',
            nbins=20,
            title="Distribution de l'épargne brute par habitant",
            labels={'Montant en € par habitant': '€ par habitant'},
            color_discrete_sequence=['#3B82F6']
        )
        fig.update_layout(
            xaxis_title="Épargne brute par habitant (€)",
            yaxis_title="Nombre de communes"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Corrélation épargne brute vs population
        fig2 = px.scatter(
            df_epargne,
            x='Population totale',
            y='Montant',
            size='Montant en € par habitant',
            color='Nom 2024 EPCI',
            hover_name='Nom 2024 Commune',
            title="Épargne brute vs Population",
            labels={
                'Population totale': 'Population',
                'Montant': 'Épargne brute (€)',
                'Montant en € par habitant': '€/habitant'
            },
            log_x=True,
            size_max=30
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # Analyse par caractéristique
    st.markdown("### Analyse par caractéristique communale")
    
    # Préparation des données
    characteristics = ['Commune de montagne', 'Commune touristique', 'Commune rurale']
    
    char_data = []
    for char in characteristics:
        if char in df_epargne.columns:
            df_char = df_epargne[df_epargne[char] == 'Oui']
            df_non_char = df_epargne[df_epargne[char] == 'Non']
            
            if not df_char.empty and not df_non_char.empty:
                char_data.append({
                    'Caractéristique': char.replace('Commune ', ''),
                    'Avec caractéristique': df_char['Montant en € par habitant'].mean(),
                    'Sans caractéristique': df_non_char['Montant en € par habitant'].mean(),
                    'Différence': df_char['Montant en € par habitant'].mean() - df_non_char['Montant en € par habitant'].mean()
                })
    
    if char_data:
        char_df = pd.DataFrame(char_data)
        
        fig3 = px.bar(
            char_df,
            x='Caractéristique',
            y=['Avec caractéristique', 'Sans caractéristique'],
            barmode='group',
            title="Épargne brute moyenne par caractéristique",
            labels={'value': 'Épargne brute moyenne (€/hab)', 'variable': ''},
            color_discrete_sequence=['#10B981', '#EF4444']
        )
        
        st.plotly_chart(fig3, use_container_width=True)
    
    # Top 10 des communes par épargne brute
    st.markdown("### Top 10 des communes par épargne brute")
    
    top_10_epargne = df_epargne.nlargest(10, 'Montant')[['Nom 2024 Commune', 'Nom 2024 EPCI', 
                                                         'Montant', 'Montant en € par habitant', 
                                                         'Population totale']].copy()
    top_10_epargne['Montant (M€)'] = top_10_epargne['Montant'] / 1_000_000
    
    fig4 = px.bar(
        top_10_epargne,
        x='Nom 2024 Commune',
        y='Montant (M€)',
        color='Nom 2024 EPCI',
        title="Top 10 communes - Épargne brute totale",
        labels={'Montant (M€)': 'Épargne brute (M€)', 'Nom 2024 Commune': 'Commune'},
        text='Montant (M€)'
    )
    fig4.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    fig4.update_layout(height=500)
    
    st.plotly_chart(fig4, use_container_width=True)
    
    # Tableau détaillé
    st.dataframe(
        top_10_epargne[['Nom 2024 Commune', 'Nom 2024 EPCI', 'Montant (M€)', 
                       'Montant en € par habitant', 'Population totale']]
        .style.format({
            'Montant (M€)': '{:.2f}',
            'Montant en € par habitant': '{:.0f}',
            'Population totale': '{:,}'
        }),
        use_container_width=True
    )

# Section d'export et téléchargement
st.markdown("---")
st.markdown("### 📥 Export des données")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("📊 Exporter données filtrées (CSV)"):
        csv = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger CSV",
            data=csv,
            file_name="donnees_filtrees_communes.csv",
            mime="text/csv"
        )

with col2:
    if st.button("📈 Exporter rapport d'analyse"):
        # Création d'un rapport simplifié
        rapport_data = {
            'Métrique': [
                'Nombre de communes analysées',
                'Épargne brute totale (M€)',
                'Capacité financement moyenne/hab',
                'Communes avec capacité positive',
                'Budget annexes moyen/commune (€)'
            ],
            'Valeur': [
                len(df_principal['Nom 2024 Commune'].unique()),
                total_epargne,
                df_principal_financement['Montant en € par habitant'].mean(),
                f"{pourcentage_positives:.1f}%",
                df_annexes.groupby('Nom 2024 Commune')['Montant'].sum().mean() if not df_annexes.empty else 0
            ]
        }
        rapport_df = pd.DataFrame(rapport_data)
        csv_rapport = rapport_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Télécharger Rapport",
            data=csv_rapport,
            file_name="rapport_analyse_communes.csv",
            mime="text/csv"
        )

with col3:
    st.info("""
    **Instructions :**
    1. Utilisez les filtres pour affiner l'analyse
    2. Cliquez sur les onglets pour naviguer
    3. Passez la souris sur les graphiques pour les détails
    4. Téléchargez les données pour analyse externe
    """)

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>Dashboard créé avec Streamlit | Données OFGL 2017 | La Réunion</p>
    <p>Analyse financière communale - Version 1.0</p>
</div>
""", unsafe_allow_html=True)
