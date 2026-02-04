# Dashboard.py - Version avec analyse Dépenses/Recettes
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

# Fonctions utilitaires pour le formatage
def format_number_for_display(value, decimals=1, is_currency=False):
    """
    Formate un nombre pour l'affichage dans les tableaux (retourne une chaîne)
    """
    if pd.isna(value):
        return "-"
    
    try:
        value = float(value)
    except:
        return str(value)
    
    suffix = ""
    if abs(value) >= 1_000_000_000:  # Milliard
        value = value / 1_000_000_000
        suffix = "Md"
    elif abs(value) >= 1_000_000:  # Million
        value = value / 1_000_000
        suffix = "M"
    elif abs(value) >= 1_000:  # Millier
        value = value / 1_000
        suffix = "K"
    
    if is_currency:
        return f"€{value:,.{decimals}f}{suffix}"
    else:
        return f"{value:,.{decimals}f}{suffix}"

def format_population(value):
    """
    Formate un nombre de population
    """
    if pd.isna(value):
        return "-"
    return f"{value:,.0f}"

# Titre principal
st.markdown('<h1 class="main-header">📊 Dashboard Financier des Communes de La Réunion</h1>', unsafe_allow_html=True)
st.markdown("***Analyse budgétaire 2017 - Données OFGL***")

# Fonction pour charger et nettoyer les données
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('ofgl-base-communes.csv', sep=';', low_memory=False, encoding='utf-8')
    except:
        # Essayer d'autres encodages
        try:
            df = pd.read_csv('ofgl-base-communes.csv', sep=';', low_memory=False, encoding='latin-1')
        except:
            st.error("Impossible de lire le fichier CSV. Vérifiez le format et l'encodage.")
            return pd.DataFrame()
    
    # Nettoyage des colonnes
    df.columns = df.columns.str.strip()
    
    # Standardisation des noms de colonnes
    column_mapping = {
        'Exercice': 'Exercice',
        'Outre-mer': 'Outre_mer',
        'Code Insee 2024 Région': 'Code_Region',
        'Nom 2024 Région': 'Nom_Region',
        'Code Insee 2024 Département': 'Code_Departement',
        'Nom 2024 Département': 'Nom_Departement',
        'Code Siren 2024 EPCI': 'Code_EPCI',
        'Nom 2024 EPCI': 'Nom_EPCI',
        'Strate population 2024': 'Strate_population',
        'Commune rurale': 'Commune_rurale',
        'Commune de montagne': 'Commune_montagne',
        'Commune touristique': 'Commune_touristique',
        'Tranche revenu par habitant': 'Tranche_revenu',
        'Présence QPV': 'Presence_QPV',
        'Code Insee 2024 Commune': 'Code_Commune',
        'Nom 2024 Commune': 'Commune',
        'Catégorie': 'Categorie',
        'Code Siren Collectivité': 'Code_Siren_Collectivite',
        'Code Insee Collectivité': 'Code_Insee_Collectivite',
        'Siret Budget': 'Siret_Budget',
        'Libellé Budget': 'Libelle_Budget',
        'Type de budget': 'Type_budget',
        'Nomenclature': 'Nomenclature',
        'Agrégat': 'Agregat',
        'Montant': 'Montant',
        'Montant en millions': 'Montant_millions',
        'Population totale': 'Population',
        'Montant en € par habitant': 'Montant_par_habitant',
        'Compte 2024 Disponible': 'Compte_disponible',
        'code_type_budget': 'code_type_budget',
        'ordre_analyse1_section1': 'ordre_analyse1_section1',
        'Population totale du dernier exercice': 'Population_dernier_exercice'
    }
    
    # Renommer les colonnes existantes
    existing_columns = {}
    for old_name, new_name in column_mapping.items():
        if old_name in df.columns:
            existing_columns[old_name] = new_name
    
    df = df.rename(columns=existing_columns)
    
    # Conversion des colonnes numériques avec gestion des erreurs
    numeric_cols = ['Montant', 'Montant_millions', 'Population', 
                    'Montant_par_habitant', 'Population_dernier_exercice',
                    'Strate_population', 'Tranche_revenu']
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    # Nettoyage des colonnes texte
    text_cols = ['Commune_rurale', 'Commune_montagne', 'Commune_touristique', 'Presence_QPV']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.upper()
    
    # Filtre pour La Réunion
    if 'Code_Departement' in df.columns:
        df = df[df['Code_Departement'] == 974]
    
    return df

# Chargement des données
df = load_data()

if df.empty:
    st.error("Aucune donnée chargée. Vérifiez votre fichier CSV.")
    st.stop()

# Sidebar - Filtres
with st.sidebar:
    st.markdown("## 🔧 Filtres")
    
    # Filtre par EPCI
    if 'Nom_EPCI' in df.columns:
        epci_list = df['Nom_EPCI'].dropna().unique().tolist()
        selected_epci = st.multiselect(
            "EPCI (Intercommunalités)",
            options=epci_list,
            default=epci_list
        )
    else:
        selected_epci = []
        st.warning("Colonne 'Nom_EPCI' non trouvée")
    
    # Filtre par commune
    if 'Commune' in df.columns:
        commune_list = sorted(df['Commune'].dropna().unique().tolist())
        selected_communes = st.multiselect(
            "Communes (24 communes)",
            options=commune_list,
            default=commune_list
        )
    else:
        selected_communes = []
    
    # Filtre par type de budget
    if 'Type_budget' in df.columns:
        budget_types = df['Type_budget'].dropna().unique().tolist()
        selected_budget_types = st.multiselect(
            "Types de budget",
            options=budget_types,
            default=budget_types
        )
    else:
        selected_budget_types = []
    
    # Filtre par agrégat financier
    if 'Agregat' in df.columns:
        agregats = df['Agregat'].dropna().unique().tolist()
        selected_agregats = st.multiselect(
            "Indicateurs financiers",
            options=agregats,
            default=['Epargne brute', 'Capacité ou besoin de financement', 'Impôts et taxes', 'Recettes totales hors emprunts'] 
            if 'Epargne brute' in agregats else agregats[:3]
        )
    else:
        selected_agregats = []
    
    # Informations sur les données
    with st.expander("ℹ️ Informations sur les données"):
        st.write(f"**Total de lignes :** {len(df):,}")
        if 'Commune' in df.columns:
            st.write(f"**Nombre de communes :** {df['Commune'].nunique()}")
        if 'Agregat' in df.columns:
            st.write(f"**Indicateurs disponibles :** {', '.join(df['Agregat'].unique()[:5])}...")

# Application des filtres
filtered_df = df.copy()

if selected_epci:
    filtered_df = filtered_df[filtered_df['Nom_EPCI'].isin(selected_epci)]

if selected_communes:
    filtered_df = filtered_df[filtered_df['Commune'].isin(selected_communes)]

if selected_budget_types:
    filtered_df = filtered_df[filtered_df['Type_budget'].isin(selected_budget_types)]

if selected_agregats:
    filtered_df = filtered_df[filtered_df['Agregat'].isin(selected_agregats)]

# Section 1: KPI Principaux
st.markdown('<h2 class="sub-header">📈 Vue d\'ensemble - Santé Financière</h2>', unsafe_allow_html=True)

# Calcul des KPI avec vérifications
try:
    df_principal = filtered_df[filtered_df['Type_budget'] == 'Budget principal']
    
    if not df_principal.empty:
        # KPI en colonnes
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if 'Agregat' in df_principal.columns and 'Montant' in df_principal.columns:
                total_epargne = df_principal[df_principal['Agregat'] == 'Epargne brute']['Montant'].sum() / 1_000_000
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_epargne:.1f} M€</div>
                    <div class="kpi-label">Épargne brute totale</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div class="kpi-card">
                    <div class="kpi-value">N/A</div>
                    <div class="kpi-label">Données manquantes</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            if 'Commune' in df_principal.columns:
                communes_count = df_principal['Commune'].nunique()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{communes_count}</div>
                    <div class="kpi-label">Communes analysées</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col3:
            if 'Population' in df_principal.columns:
                total_population = df_principal['Population'].sum()
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_population:,.0f}</div>
                    <div class="kpi-label">Population totale</div>
                </div>
                """, unsafe_allow_html=True)
        
        with col4:
            if 'Agregat' in df_principal.columns and 'Montant' in df_principal.columns:
                df_recettes = df_principal[df_principal['Agregat'] == 'Recettes totales hors emprunts']
                total_recettes = df_recettes['Montant'].sum() / 1_000_000 if not df_recettes.empty else 0
                st.markdown(f"""
                <div class="kpi-card">
                    <div class="kpi-value">{total_recettes:.1f} M€</div>
                    <div class="kpi-label">Recettes totales</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("Aucune donnée de budget principal disponible avec les filtres actuels.")
        
except Exception as e:
    st.error(f"Erreur dans le calcul des KPI : {str(e)}")

# Onglets pour les différentes analyses
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Santé Financière",
    "📊 Comparaison EPCI",
    "💧 Budgets Annexes",
    "💰 Focus Épargne",
    "📈 Analyse Dépenses/Recettes"
])

# TAB 1: Santé Financière des Communes
with tab1:
    try:
        # Vérifier les données nécessaires
        required_cols = ['Agregat', 'Commune', 'Montant_par_habitant', 'Montant']
        missing_cols = [col for col in required_cols if col not in df_principal.columns]
        
        if missing_cols:
            st.warning(f"Colonnes manquantes pour l'analyse : {', '.join(missing_cols)}")
        else:
            # Données de capacité de financement
            df_financement = df_principal[df_principal['Agregat'] == 'Capacité ou besoin de financement']
            
            if not df_financement.empty:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    # Nettoyage des données pour le graphique
                    df_financement_clean = df_financement.dropna(subset=['Montant_par_habitant', 'Commune'])
                    df_financement_clean = df_financement_clean.sort_values('Montant_par_habitant', ascending=False)
                    
                    if not df_financement_clean.empty:
                        fig = px.bar(
                            df_financement_clean,
                            x='Commune',
                            y='Montant_par_habitant',
                            color='Montant_par_habitant',
                            color_continuous_scale=['#EF4444', '#FBBF24', '#10B981'],
                            title="Capacité (+) ou Besoin (-) de Financement par Habitant",
                            labels={'Montant_par_habitant': '€ par habitant', 'Commune': 'Commune'}
                        )
                        fig.update_layout(height=500, xaxis_tickangle=45)
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.info("Aucune donnée valide pour le graphique de capacité de financement")
                
                with col2:
                    st.markdown("### Classement")
                    
                    if not df_financement_clean.empty:
                        # Top 5
                        st.markdown("**Top 5 - Meilleure santé**")
                        top_5 = df_financement_clean.nlargest(5, 'Montant_par_habitant')
                        for idx, row in top_5.iterrows():
                            value = row['Montant_par_habitant']
                            st.metric(
                                label=row['Commune'][:20],
                                value=f"{value:,.0f} €/hab" if pd.notnull(value) else "N/A"
                            )
                        
                        st.markdown("---")
                        
                        # Bottom 5
                        st.markdown("**Bottom 5**")
                        bottom_5 = df_financement_clean.nsmallest(5, 'Montant_par_habitant')
                        for idx, row in bottom_5.iterrows():
                            value = row['Montant_par_habitant']
                            st.metric(
                                label=row['Commune'][:20],
                                value=f"{value:,.0f} €/hab" if pd.notnull(value) else "N/A"
                            )
                
                # Statistiques de santé financière
                st.markdown("### 📊 Statistiques de santé financière")
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    if not df_financement_clean.empty:
                        mean_val = df_financement_clean['Montant_par_habitant'].mean()
                        st.metric("Moyenne par habitant", f"{mean_val:,.0f} €")
                
                with col_stat2:
                    if not df_financement_clean.empty:
                        positive_count = (df_financement_clean['Montant_par_habitant'] > 0).sum()
                        total_count = len(df_financement_clean)
                        percentage = (positive_count / total_count * 100) if total_count > 0 else 0
                        st.metric("Communes avec capacité positive", f"{percentage:.1f}%")
                
                with col_stat3:
                    if not df_financement_clean.empty:
                        max_val = df_financement_clean['Montant_par_habitant'].max()
                        min_val = df_financement_clean['Montant_par_habitant'].min()
                        st.metric("Écart max/min", f"{max_val - min_val:,.0f} €")
                
            else:
                st.info("Aucune donnée de capacité de financement disponible")
        
    except Exception as e:
        st.error(f"Erreur dans l'analyse de santé financière : {str(e)}")

# TAB 2: Comparaison Intercommunalités
with tab2:
    try:
        st.markdown("### Comparaison des Performances par EPCI")
        
        if 'Nom_EPCI' in df_principal.columns and 'Agregat' in df_principal.columns:
            # Préparation des données par EPCI
            epci_data = []
            
            for epci in df_principal['Nom_EPCI'].dropna().unique():
                df_epci = df_principal[df_epci['Nom_EPCI'] == epci]
                
                # Calcul des métriques de base
                metrics = {
                    'EPCI': epci,
                    'Nombre_communes': df_epci['Commune'].nunique() if 'Commune' in df_epci.columns else 0,
                    'Population_totale': df_epci['Population'].sum() if 'Population' in df_epci.columns else 0
                }
                
                # Ajout des indicateurs financiers
                for agregat in ['Epargne brute', 'Capacité ou besoin de financement', 'Impôts et taxes']:
                    df_agregat = df_epci[df_epci['Agregat'] == agregat]
                    if not df_agregat.empty and 'Montant' in df_agregat.columns:
                        # Utiliser des nombres bruts pour les graphiques
                        metrics[f'{agregat}_M€'] = df_agregat['Montant'].sum() / 1_000_000
                        metrics[f'{agregat}_€'] = df_agregat['Montant'].sum()
                    else:
                        metrics[f'{agregat}_M€'] = 0
                        metrics[f'{agregat}_€'] = 0
                
                epci_data.append(metrics)
            
            if epci_data:
                epci_df = pd.DataFrame(epci_data)
                
                # Graphique 1: Épargne brute par EPCI
                st.markdown("#### Épargne brute par EPCI")
                
                if 'Epargne brute_M€' in epci_df.columns:
                    # Trier pour un meilleur affichage
                    epci_df_sorted = epci_df.sort_values('Epargne brute_M€', ascending=True)
                    
                    fig1 = px.bar(
                        epci_df_sorted,
                        x='Epargne brute_M€',
                        y='EPCI',
                        orientation='h',
                        title="Épargne brute totale par EPCI (en millions d'€)",
                        color='Epargne brute_M€',
                        color_continuous_scale='Blues',
                        text='Epargne brute_M€'
                    )
                    fig1.update_traces(
                        texttemplate='%{text:.1f} M€',
                        textposition='outside'
                    )
                    fig1.update_layout(
                        height=400,
                        xaxis_title="Montant (M€)",
                        yaxis_title="EPCI"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                # Graphique 2: Capacité de financement
                st.markdown("#### Capacité/Besoin de financement par EPCI")
                
                if 'Capacité ou besoin de financement_M€' in epci_df.columns:
                    # Trier par valeur
                    epci_df_sorted_fin = epci_df.sort_values('Capacité ou besoin de financement_M€', ascending=True)
                    
                    # Déterminer la couleur en fonction du signe
                    colors = []
                    for val in epci_df_sorted_fin['Capacité ou besoin de financement_M€']:
                        if val < 0:
                            colors.append('#EF4444')  # Rouge pour les besoins
                        elif val == 0:
                            colors.append('#FBBF24')  # Jaune pour neutre
                        else:
                            colors.append('#10B981')  # Vert pour les capacités
                    
                    fig2 = go.Figure(data=[
                        go.Bar(
                            x=epci_df_sorted_fin['EPCI'],
                            y=epci_df_sorted_fin['Capacité ou besoin de financement_M€'],
                            marker_color=colors,
                            text=epci_df_sorted_fin['Capacité ou besoin de financement_M€'],
                            texttemplate='%{text:.1f}',
                            textposition='outside'
                        )
                    ])
                    
                    fig2.update_layout(
                        title="Capacité (+) ou Besoin (-) de financement par EPCI (M€)",
                        xaxis_tickangle=45,
                        height=400,
                        yaxis_title="Montant (M€)",
                        xaxis_title="EPCI"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
                
                # Tableau de synthèse
                st.markdown("#### Tableau comparatif")
                
                # Créer un DataFrame pour l'affichage (formaté pour l'utilisateur)
                display_df = epci_df.copy()
                
                # Renommer les colonnes pour l'affichage
                column_display_names = {
                    'EPCI': 'EPCI',
                    'Nombre_communes': 'Nb Communes',
                    'Population_totale': 'Population',
                    'Epargne brute_M€': 'Épargne brute (M€)',
                    'Capacité ou besoin de financement_M€': 'Capacité/Besoin (M€)',
                    'Impôts et taxes_M€': 'Impôts/Taxes (M€)'
                }
                
                # Sélectionner et renommer les colonnes disponibles
                available_cols = {}
                for internal_name, display_name in column_display_names.items():
                    if internal_name in display_df.columns:
                        available_cols[internal_name] = display_name
                
                display_df = display_df[list(available_cols.keys())].copy()
                display_df = display_df.rename(columns=available_cols)
                
                # Formater les nombres pour l'affichage
                if 'Population' in display_df.columns:
                    display_df['Population'] = display_df['Population'].apply(format_population)
                
                for col in ['Épargne brute (M€)', 'Capacité/Besoin (M€)', 'Impôts/Taxes (M€)']:
                    if col in display_df.columns:
                        display_df[col] = display_df[col].apply(
                            lambda x: format_number_for_display(x, 1, True)
                        )
                
                # Trier par épargne brute
                if 'Épargne brute (M€)' in display_df.columns:
                    # Extraire les valeurs numériques pour le tri
                    try:
                        display_df['_sort_key'] = display_df['Épargne brute (M€)'].str.replace('€', '').str.replace('M', '').str.replace('K', '').astype(float)
                        # Ajuster pour les suffixes
                        display_df['_sort_key'] = display_df.apply(
                            lambda row: row['_sort_key'] * 1_000_000 if 'M' in str(row['Épargne brute (M€)']) else 
                            (row['_sort_key'] * 1_000 if 'K' in str(row['Épargne brute (M€)']) else row['_sort_key']),
                            axis=1
                        )
                        display_df = display_df.sort_values('_sort_key', ascending=False)
                        display_df = display_df.drop('_sort_key', axis=1)
                    except:
                        # Si le tri échoue, trier alphabétiquement
                        display_df = display_df.sort_values('EPCI')
                
                # Afficher le tableau
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    height=400
                )
                
                # Statistiques globales
                st.markdown("#### 📊 Statistiques globales")
                
                col_stat1, col_stat2, col_stat3 = st.columns(3)
                
                with col_stat1:
                    if 'Epargne brute_M€' in epci_df.columns:
                        total_epargne = epci_df['Epargne brute_M€'].sum()
                        st.metric(
                            "Épargne brute totale",
                            f"{total_epargne:,.1f} M€",
                            delta=None
                        )
                
                with col_stat2:
                    if 'Capacité ou besoin de financement_M€' in epci_df.columns:
                        # Nombre d'EPCI avec capacité positive
                        positive_epci = (epci_df['Capacité ou besoin de financement_M€'] > 0).sum()
                        total_epci = len(epci_df)
                        percentage = (positive_epci / total_epci * 100) if total_epci > 0 else 0
                        st.metric(
                            "EPCI avec capacité positive",
                            f"{percentage:.0f}%",
                            delta=None
                        )
                
                with col_stat3:
                    if 'Population_totale' in epci_df.columns:
                        total_pop = epci_df['Population_totale'].sum()
                        avg_pop = epci_df['Population_totale'].mean()
                        st.metric(
                            "Population moyenne par EPCI",
                            f"{avg_pop:,.0f}",
                            delta=None
                        )
                        
            else:
                st.info("Aucune donnée EPCI disponible")
        else:
            st.warning("Colonnes nécessaires pour l'analyse EPCI non disponibles")
            
    except Exception as e:
        st.error(f"Erreur dans l'analyse comparative EPCI : {str(e)}")

# TAB 3: Analyse des Budgets Annexes
with tab3:
    try:
        st.markdown("### Analyse des Budgets Annexes")
        
        # Filtrer pour budgets annexes
        df_annexes = filtered_df[filtered_df['Type_budget'] == 'Budget annexe']
        
        if not df_annexes.empty:
            # Analyse par type de service
            if 'Libelle_Budget' in df_annexes.columns:
                # Classification simplifiée des budgets annexes
                def classify_service(libelle):
                    if isinstance(libelle, str):
                        libelle_lower = libelle.lower()
                        if 'eau' in libelle_lower:
                            return 'Eau'
                        elif 'assain' in libelle_lower:
                            return 'Assainissement'
                        elif 'pompe' in libelle_lower and ('funebre' in libelle_lower or 'funèbre' in libelle_lower):
                            return 'Pompes funèbres'
                        elif 'spanc' in libelle_lower:
                            return 'SPANC'
                        elif 'touris' in libelle_lower:
                            return 'Tourisme'
                    return 'Autres services'
                
                df_annexes['Type_service'] = df_annexes['Libelle_Budget'].apply(classify_service)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Distribution des types de service
                    service_counts = df_annexes['Type_service'].value_counts().reset_index()
                    service_counts.columns = ['Service', 'Nombre']
                    
                    fig1 = px.pie(
                        service_counts,
                        values='Nombre',
                        names='Service',
                        title="Répartition des budgets annexes par type de service",
                        hole=0.4
                    )
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    # Montant total par service
                    if 'Montant' in df_annexes.columns:
                        service_amounts = df_annexes.groupby('Type_service')['Montant'].sum().reset_index()
                        service_amounts = service_amounts.sort_values('Montant', ascending=False)
                        
                        fig2 = px.bar(
                            service_amounts,
                            x='Type_service',
                            y='Montant',
                            title="Montant total par type de service (€)",
                            color='Montant',
                            color_continuous_scale='Viridis'
                        )
                        fig2.update_layout(xaxis_tickangle=45)
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Analyse détaillée pour eau et assainissement
                st.markdown("#### Analyse Eau et Assainissement")
                
                services_focus = ['Eau', 'Assainissement']
                df_focus = df_annexes[df_annexes['Type_service'].isin(services_focus)]
                
                if not df_focus.empty and 'Commune' in df_focus.columns:
                    # Pivot table pour comparaison
                    pivot_data = []
                    communes = df_focus['Commune'].unique()
                    
                    for commune in communes:
                        df_commune = df_focus[df_focus['Commune'] == commune]
                        
                        row = {'Commune': commune}
                        for service in services_focus:
                            service_data = df_commune[df_commune['Type_service'] == service]
                            row[service] = service_data['Montant'].sum() if not service_data.empty else 0
                        
                        pivot_data.append(row)
                    
                    pivot_df = pd.DataFrame(pivot_data)
                    
                    if not pivot_df.empty:
                        # Graphique comparatif
                        fig3 = go.Figure()
                        
                        for service in services_focus:
                            if service in pivot_df.columns:
                                fig3.add_trace(go.Bar(
                                    x=pivot_df['Commune'],
                                    y=pivot_df[service],
                                    name=service,
                                    text=pivot_df[service].apply(lambda x: f"{x/1000:.0f}K" if x != 0 else "0"),
                                    textposition='auto'
                                ))
                        
                        fig3.update_layout(
                            title="Comparaison budgets Eau vs Assainissement par commune (€)",
                            barmode='group',
                            height=500,
                            xaxis_tickangle=45,
                            yaxis_title="Montant (€)"
                        )
                        
                        st.plotly_chart(fig3, use_container_width=True)
                        
                        # Statistiques
                        col_stat1, col_stat2, col_stat3 = st.columns(3)
                        
                        with col_stat1:
                            if 'Eau' in pivot_df.columns:
                                avg_eau = pivot_df['Eau'].mean()
                                st.metric("Budget Eau moyen", f"{avg_eau:,.0f} €")
                        
                        with col_stat2:
                            if 'Assainissement' in pivot_df.columns:
                                avg_assain = pivot_df['Assainissement'].mean()
                                st.metric("Budget Assainissement moyen", f"{avg_assain:,.0f} €")
                        
                        with col_stat3:
                            if 'Eau' in pivot_df.columns and 'Assainissement' in pivot_df.columns:
                                # Éviter la division par zéro
                                assain_values = pivot_df['Assainissement'].replace(0, np.nan)
                                ratio_series = pivot_df['Eau'] / assain_values
                                avg_ratio = ratio_series.mean(skipna=True)
                                if pd.notnull(avg_ratio):
                                    st.metric("Ratio Eau/Assain moyen", f"{avg_ratio:.2f}")
                                else:
                                    st.metric("Ratio Eau/Assain moyen", "N/A")
            else:
                st.info("Libellé des budgets annexes non disponible")
        else:
            st.info("Aucun budget annexe disponible avec les filtres actuels")
            
    except Exception as e:
        st.error(f"Erreur dans l'analyse des budgets annexes : {str(e)}")

# TAB 4: Focus sur l'Épargne Brute
with tab4:
    try:
        st.markdown("### Analyse approfondie de l'Épargne Brute")
        
        # Données d'épargne brute
        if 'Agregat' in df_principal.columns:
            df_epargne = df_principal[df_principal['Agregat'] == 'Epargne brute']
            
            if not df_epargne.empty:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Histogramme de distribution
                    if 'Montant_par_habitant' in df_epargne.columns:
                        df_hist = df_epargne.dropna(subset=['Montant_par_habitant'])
                        
                        if not df_hist.empty:
                            fig1 = px.histogram(
                                df_hist,
                                x='Montant_par_habitant',
                                nbins=20,
                                title="Distribution de l'épargne brute par habitant",
                                labels={'Montant_par_habitant': 'Épargne brute par habitant (€)'},
                                color_discrete_sequence=['#3B82F6']
                            )
                            fig1.update_layout(
                                xaxis_title="€ par habitant",
                                yaxis_title="Nombre de communes"
                            )
                            st.plotly_chart(fig1, use_container_width=True)
                        else:
                            st.info("Données insuffisantes pour l'histogramme")
                
                with col2:
                    # Top 10 des communes
                    if 'Commune' in df_epargne.columns and 'Montant' in df_epargne.columns:
                        df_top = df_epargne.sort_values('Montant', ascending=False).head(10)
                        
                        fig2 = px.bar(
                            df_top,
                            x='Commune',
                            y='Montant',
                            title="Top 10 communes - Épargne brute totale",
                            color='Montant',
                            color_continuous_scale='Greens',
                            text_auto='.2s'
                        )
                        fig2.update_layout(
                            xaxis_tickangle=45,
                            yaxis_title="Épargne brute (€)",
                            height=400
                        )
                        st.plotly_chart(fig2, use_container_width=True)
                
                # Analyse par strate de population
                st.markdown("#### Analyse par caractéristiques")
                
                if 'Strate_population' in df_epargne.columns:
                    # Nettoyage de la strate
                    df_epargne_clean = df_epargne.dropna(subset=['Strate_population', 'Montant_par_habitant'])
                    df_epargne_clean['Strate'] = df_epargne_clean['Strate_population'].astype(str)
                    
                    if not df_epargne_clean.empty:
                        fig3 = px.box(
                            df_epargne_clean,
                            x='Strate',
                            y='Montant_par_habitant',
                            title="Épargne brute par habitant selon la strate de population",
                            points="all",
                            color='Strate'
                        )
                        fig3.update_layout(
                            xaxis_title="Strate de population",
                            yaxis_title="Épargne brute par habitant (€)",
                            height=400
                        )
                        st.plotly_chart(fig3, use_container_width=True)
                
                # Tableau des données d'épargne
                st.markdown("#### Données détaillées")
                
                display_cols = ['Commune', 'Nom_EPCI', 'Montant', 'Montant_par_habitant', 'Population']
                available_cols = [col for col in display_cols if col in df_epargne.columns]
                
                if available_cols:
                    display_df = df_epargne[available_cols].copy()
                    
                    # Formater les nombres pour l'affichage
                    if 'Montant' in display_df.columns:
                        display_df['Montant'] = display_df['Montant'].apply(
                            lambda x: format_number_for_display(x, 1, True)
                        )
                    
                    if 'Montant_par_habitant' in display_df.columns:
                        display_df['Montant_par_habitant'] = display_df['Montant_par_habitant'].apply(
                            lambda x: f"€{x:,.0f}" if pd.notnull(x) else "N/A"
                        )
                    
                    if 'Population' in display_df.columns:
                        display_df['Population'] = display_df['Population'].apply(
                            lambda x: format_population(x)
                        )
                    
                    # Trier
                    sort_col = 'Montant_par_habitant' if 'Montant_par_habitant' in display_df.columns else 'Commune'
                    try:
                        if 'Montant_par_habitant' in display_df.columns:
                            # Extraire les valeurs numériques pour le tri
                            display_df['_sort_key'] = display_df['Montant_par_habitant'].str.replace('€', '').str.replace(',', '').astype(float)
                            display_df = display_df.sort_values('_sort_key', ascending=False)
                            display_df = display_df.drop('_sort_key', axis=1)
                        else:
                            display_df = display_df.sort_values('Commune')
                    except:
                        display_df = display_df.sort_values('Commune')
                    
                    st.dataframe(
                        display_df,
                        use_container_width=True,
                        height=400
                    )
            else:
                st.info("Aucune donnée d'épargne brute disponible")
        else:
            st.warning("Colonne 'Agregat' non disponible")
            
    except Exception as e:
        st.error(f"Erreur dans l'analyse de l'épargne brute : {str(e)}")

# TAB 5: NOUVELLE ANALYSE DÉPENSES/RECETTES
with tab5:
    try:
        st.markdown("### 📈 Analyse Dépenses vs Recettes - 24 Communes de La Réunion")
        
        # Vérifier que nous avons les données nécessaires
        if 'Agregat' not in df_principal.columns or 'Montant' not in df_principal.columns:
            st.warning("Données nécessaires pour l'analyse dépenses/recettes non disponibles")
        else:
            # 1. ANALYSE DES RECETTES
            st.markdown("#### 1. Analyse des Recettes")
            
            # Récupérer les données de recettes
            df_recettes = df_principal[df_principal['Agregat'] == 'Recettes totales hors emprunts']
            
            if not df_recettes.empty:
                # A. Top 10 des communes par recettes
                col_rec1, col_rec2 = st.columns(2)
                
                with col_rec1:
                    df_top_recettes = df_recettes.sort_values('Montant', ascending=False).head(10)
                    
                    fig_rec1 = px.bar(
                        df_top_recettes,
                        x='Commune',
                        y='Montant',
                        title="Top 10 communes - Recettes totales",
                        color='Montant',
                        color_continuous_scale='Blues',
                        text_auto='.2s'
                    )
                    fig_rec1.update_layout(
                        xaxis_tickangle=45,
                        yaxis_title="Recettes (€)",
                        height=400
                    )
                    st.plotly_chart(fig_rec1, use_container_width=True)
                
                with col_rec2:
                    # B. Recettes par habitant
                    df_recettes_hab = df_recettes.dropna(subset=['Montant_par_habitant'])
                    df_recettes_hab = df_recettes_hab.sort_values('Montant_par_habitant', ascending=False).head(10)
                    
                    fig_rec2 = px.bar(
                        df_recettes_hab,
                        x='Commune',
                        y='Montant_par_habitant',
                        title="Top 10 - Recettes par habitant",
                        color='Montant_par_habitant',
                        color_continuous_scale='Purples',
                        text_auto='.0f'
                    )
                    fig_rec2.update_layout(
                        xaxis_tickangle=45,
                        yaxis_title="Recettes par habitant (€)",
                        height=400
                    )
                    st.plotly_chart(fig_rec2, use_container_width=True)
                
                # Statistiques des recettes
                st.markdown("##### 📊 Statistiques des recettes")
                
                col_stat_rec1, col_stat_rec2, col_stat_rec3 = st.columns(3)
                
                with col_stat_rec1:
                    total_recettes = df_recettes['Montant'].sum() / 1_000_000
                    st.metric("Recettes totales", f"{total_recettes:,.1f} M€")
                
                with col_stat_rec2:
                    avg_recettes_hab = df_recettes['Montant_par_habitant'].mean()
                    st.metric("Moyenne par habitant", f"{avg_recettes_hab:,.0f} €")
                
                with col_stat_rec3:
                    max_recettes_commune = df_recettes.loc[df_recettes['Montant'].idxmax(), 'Commune'] if not df_recettes.empty else "N/A"
                    max_recettes = df_recettes['Montant'].max() / 1_000_000 if not df_recettes.empty else 0
                    st.metric("Commune avec plus de recettes", f"{max_recettes:.1f} M€", delta=max_recettes_commune)
            
            else:
                st.info("Aucune donnée de recettes disponible")
            
            # 2. ANALYSE DES DÉPENSES (approximation via capacité de financement et épargne)
            st.markdown("#### 2. Analyse des Dépenses")
            
            # Calcul approximatif des dépenses : Recettes - Épargne brute
            df_epargne = df_principal[df_principal['Agregat'] == 'Epargne brute']
            
            if not df_recettes.empty and not df_epargne.empty:
                # Créer un DataFrame combiné
                depenses_data = []
                
                for commune in df_principal['Commune'].unique():
                    recettes_commune = df_recettes[df_recettes['Commune'] == commune]
                    epargne_commune = df_epargne[df_epargne['Commune'] == commune]
                    
                    if not recettes_commune.empty and not epargne_commune.empty:
                        recettes = recettes_commune['Montant'].iloc[0]
                        epargne = epargne_commune['Montant'].iloc[0]
                        
                        # Dépenses = Recettes - Épargne (approximation)
                        depenses = recettes - epargne
                        
                        # Population pour calcul par habitant
                        population = recettes_commune['Population'].iloc[0] if pd.notnull(recettes_commune['Population'].iloc[0]) else 0
                        
                        depenses_data.append({
                            'Commune': commune,
                            'Recettes': recettes,
                            'Épargne': epargne,
                            'Dépenses': depenses,
                            'Population': population,
                            'Dépenses_par_habitant': depenses / population if population > 0 else 0,
                            'Taux_depenses_recettes': (depenses / recettes * 100) if recettes > 0 else 0
                        })
                
                if depenses_data:
                    df_depenses = pd.DataFrame(depenses_data)
                    
                    # A. Top 10 des communes par dépenses
                    col_dep1, col_dep2 = st.columns(2)
                    
                    with col_dep1:
                        df_top_depenses = df_depenses.sort_values('Dépenses', ascending=False).head(10)
                        
                        fig_dep1 = px.bar(
                            df_top_depenses,
                            x='Commune',
                            y='Dépenses',
                            title="Top 10 communes - Dépenses estimées",
                            color='Dépenses',
                            color_continuous_scale='Reds',
                            text_auto='.2s'
                        )
                        fig_dep1.update_layout(
                            xaxis_tickangle=45,
                            yaxis_title="Dépenses (€)",
                            height=400
                        )
                        st.plotly_chart(fig_dep1, use_container_width=True)
                    
                    with col_dep2:
                        # B. Dépenses par habitant
                        df_depenses_hab = df_depenses.sort_values('Dépenses_par_habitant', ascending=False).head(10)
                        
                        fig_dep2 = px.bar(
                            df_depenses_hab,
                            x='Commune',
                            y='Dépenses_par_habitant',
                            title="Top 10 - Dépenses par habitant",
                            color='Dépenses_par_habitant',
                            color_continuous_scale='Oranges',
                            text_auto='.0f'
                        )
                        fig_dep2.update_layout(
                            xaxis_tickangle=45,
                            yaxis_title="Dépenses par habitant (€)",
                            height=400
                        )
                        st.plotly_chart(fig_dep2, use_container_width=True)
                    
                    # Statistiques des dépenses
                    st.markdown("##### 📊 Statistiques des dépenses")
                    
                    col_stat_dep1, col_stat_dep2, col_stat_dep3 = st.columns(3)
                    
                    with col_stat_dep1:
                        total_depenses = df_depenses['Dépenses'].sum() / 1_000_000
                        st.metric("Dépenses totales estimées", f"{total_depenses:,.1f} M€")
                    
                    with col_stat_dep2:
                        avg_depenses_hab = df_depenses['Dépenses_par_habitant'].mean()
                        st.metric("Moyenne dépenses/habitant", f"{avg_depenses_hab:,.0f} €")
                    
                    with col_stat_dep3:
                        taux_moyen = df_depenses['Taux_depenses_recettes'].mean()
                        st.metric("Taux dépenses/recettes moyen", f"{taux_moyen:.1f}%")
                    
                    # 3. COMPARAISON DÉPENSES VS RECETTES
                    st.markdown("#### 3. Comparaison Dépenses vs Recettes")
                    
                    # Sélectionner les 15 communes avec les plus gros budgets
                    df_comparison = df_depenses.sort_values('Recettes', ascending=False).head(15)
                    
                    # Graphique comparatif
                    fig_comparison = go.Figure()
                    
                    fig_comparison.add_trace(go.Bar(
                        x=df_comparison['Commune'],
                        y=df_comparison['Recettes'],
                        name='Recettes',
                        marker_color='#3B82F6',
                        text=df_comparison['Recettes'].apply(lambda x: f"{x/1_000_000:.1f}M"),
                        textposition='outside'
                    ))
                    
                    fig_comparison.add_trace(go.Bar(
                        x=df_comparison['Commune'],
                        y=df_comparison['Dépenses'],
                        name='Dépenses',
                        marker_color='#EF4444',
                        text=df_comparison['Dépenses'].apply(lambda x: f"{x/1_000_000:.1f}M"),
                        textposition='outside'
                    ))
                    
                    fig_comparison.update_layout(
                        title="Comparaison Recettes vs Dépenses (15 plus grosses communes)",
                        barmode='group',
                        height=500,
                        xaxis_tickangle=45,
                        yaxis_title="Montant (€)",
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    
                    st.plotly_chart(fig_comparison, use_container_width=True)
                    
                    # 4. ANALYSE DU SOLDE (RECETTES - DÉPENSES)
                    st.markdown("#### 4. Analyse du Solde (Recettes - Dépenses)")
                    
                    # Calcul du solde
                    df_depenses['Solde'] = df_depenses['Recettes'] - df_depenses['Dépenses']
                    df_depenses['Solde_par_habitant'] = df_depenses['Solde'] / df_depenses['Population']
                    
                    col_solde1, col_solde2 = st.columns(2)
                    
                    with col_solde1:
                        # Communes avec solde positif
                        df_solde_positif = df_depenses[df_depenses['Solde'] > 0].sort_values('Solde', ascending=False)
                        
                        if not df_solde_positif.empty:
                            fig_solde1 = px.bar(
                                df_solde_positif.head(10),
                                x='Commune',
                                y='Solde',
                                title="Top 10 communes - Excédent (Recettes > Dépenses)",
                                color='Solde',
                                color_continuous_scale='Greens',
                                text_auto='.2s'
                            )
                            fig_solde1.update_layout(
                                xaxis_tickangle=45,
                                yaxis_title="Excédent (€)",
                                height=400
                            )
                            st.plotly_chart(fig_solde1, use_container_width=True)
                    
                    with col_solde2:
                        # Communes avec solde négatif
                        df_solde_negatif = df_depenses[df_depenses['Solde'] < 0].sort_values('Solde', ascending=True)
                        
                        if not df_solde_negatif.empty:
                            fig_solde2 = px.bar(
                                df_solde_negatif.head(10),
                                x='Commune',
                                y='Solde',
                                title="Top 10 communes - Déficit (Dépenses > Recettes)",
                                color='Solde',
                                color_continuous_scale='Reds',
                                text_auto='.2s'
                            )
                            fig_solde2.update_layout(
                                xaxis_tickangle=45,
                                yaxis_title="Déficit (€)",
                                height=400
                            )
                            st.plotly_chart(fig_solde2, use_container_width=True)
                    
                    # 5. TABLEAU SYNTHÈSE DÉPENSES/RECETTES
                    st.markdown("#### 5. Tableau synthèse - Toutes les communes")
                    
                    # Créer un tableau formaté
                    df_synthese = df_depenses.copy()
                    
                    # Formater les colonnes
                    df_synthese['Recettes'] = df_synthese['Recettes'].apply(
                        lambda x: format_number_for_display(x, 1, True)
                    )
                    df_synthese['Dépenses'] = df_synthese['Dépenses'].apply(
                        lambda x: format_number_for_display(x, 1, True)
                    )
                    df_synthese['Épargne'] = df_synthese['Épargne'].apply(
                        lambda x: format_number_for_display(x, 1, True)
                    )
                    df_synthese['Solde'] = df_synthese['Solde'].apply(
                        lambda x: format_number_for_display(x, 1, True)
                    )
                    df_synthese['Dépenses_par_habitant'] = df_synthese['Dépenses_par_habitant'].apply(
                        lambda x: f"€{x:,.0f}"
                    )
                    df_synthese['Taux_depenses_recettes'] = df_synthese['Taux_depenses_recettes'].apply(
                        lambda x: f"{x:.1f}%"
                    )
                    df_synthese['Population'] = df_synthese['Population'].apply(format_population)
                    
                    # Trier par recettes
                    df_synthese = df_synthese.sort_values('Recettes', ascending=False)
                    
                    # Afficher le tableau
                    st.dataframe(
                        df_synthese[['Commune', 'Population', 'Recettes', 'Dépenses', 
                                    'Épargne', 'Solde', 'Dépenses_par_habitant', 'Taux_depenses_recettes']],
                        use_container_width=True,
                        height=500
                    )
                    
                    # 6. ANALYSE PAR HABITANT
                    st.markdown("#### 6. Analyse par habitant")
                    
                    col_hab1, col_hab2 = st.columns(2)
                    
                    with col_hab1:
                        # Recettes vs Dépenses par habitant
                        df_hab_comparison = df_depenses.sort_values('Dépenses_par_habitant', ascending=False).head(15)
                        
                        fig_hab1 = go.Figure()
                        
                        fig_hab1.add_trace(go.Bar(
                            x=df_hab_comparison['Commune'],
                            y=df_hab_comparison['Dépenses_par_habitant'],
                            name='Dépenses/habitant',
                            marker_color='#EF4444'
                        ))
                        
                        fig_hab1.add_trace(go.Bar(
                            x=df_hab_comparison['Commune'],
                            y=df_hab_comparison['Solde_par_habitant'],
                            name='Solde/habitant',
                            marker_color='#10B981'
                        ))
                        
                        fig_hab1.update_layout(
                            title="Dépenses et Solde par habitant (Top 15)",
                            barmode='group',
                            height=400,
                            xaxis_tickangle=45,
                            yaxis_title="€ par habitant",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                        )
                        
                        st.plotly_chart(fig_hab1, use_container_width=True)
                    
                    with col_hab2:
                        # Nuage de points : Population vs Dépenses par habitant
                        fig_hab2 = px.scatter(
                            df_depenses,
                            x='Population',
                            y='Dépenses_par_habitant',
                            size='Dépenses',
                            color='Solde',
                            hover_name='Commune',
                            title="Dépenses par habitant vs Population",
                            labels={
                                'Population': 'Population',
                                'Dépenses_par_habitant': 'Dépenses par habitant (€)',
                                'Dépenses': 'Dépenses totales',
                                'Solde': 'Solde'
                            },
                            color_continuous_scale='RdYlGn',
                            size_max=30
                        )
                        
                        fig_hab2.update_layout(height=400)
                        st.plotly_chart(fig_hab2, use_container_width=True)
                    
            else:
                st.info("Données insuffisantes pour l'analyse des dépenses")
        
    except Exception as e:
        st.error(f"Erreur dans l'analyse dépenses/recettes : {str(e)}")
        with st.expander("Détails de l'erreur"):
            st.write(f"Erreur : {str(e)}")

# Section d'export
st.markdown("---")
st.markdown("### 📥 Export des données")

try:
    col_export1, col_export2 = st.columns(2)
    
    with col_export1:
        # Export CSV
        if st.button("📄 Exporter données filtrées (CSV)"):
            csv = filtered_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="Télécharger CSV",
                data=csv,
                file_name="donnees_filtrees_communes.csv",
                mime="text/csv"
            )
    
    with col_export2:
        # Export synthèse
        if st.button("📊 Exporter synthèse statistique"):
            # Créer une synthèse
            synthèse_data = {
                'Métrique': ['Lignes de données', 'Communes uniques', 'EPCI représentés'],
                'Valeur': [
                    len(filtered_df),
                    filtered_df['Commune'].nunique() if 'Commune' in filtered_df.columns else 0,
                    filtered_df['Nom_EPCI'].nunique() if 'Nom_EPCI' in filtered_df.columns else 0
                ]
            }
            
            # Ajouter des métriques financières si disponibles
            if 'Agregat' in filtered_df.columns and 'Montant' in filtered_df.columns:
                for agregat in ['Epargne brute', 'Capacité ou besoin de financement', 'Recettes totales hors emprunts']:
                    df_agregat = filtered_df[filtered_df['Agregat'] == agregat]
                    if not df_agregat.empty:
                        total = df_agregat['Montant'].sum() / 1_000_000
                        synthèse_data['Métrique'].append(f"{agregat} (M€)")
                        synthèse_data['Valeur'].append(f"{total:.2f}")
            
            synthèse_df = pd.DataFrame(synthèse_data)
            csv_synthèse = synthèse_df.to_csv(index=False, encoding='utf-8-sig')
            
            st.download_button(
                label="Télécharger Synthèse",
                data=csv_synthèse,
                file_name="synthese_statistique.csv",
                mime="text/csv"
            )
            
except Exception as e:
    st.warning(f"Export non disponible : {str(e)}")

# Pied de page
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
    <p>Dashboard créé avec Streamlit | Données OFGL 2017 | La Réunion</p>
    <p>Analyse financière communale - Version 3.0 (avec analyse Dépenses/Recettes)</p>
</div>
""", unsafe_allow_html=True)
