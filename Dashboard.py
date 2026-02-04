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
import os  # <--- AJOUT POUR VÉRIFIER LE FICHIER LOCAL
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
        
    def _load_data(self):
        """Charge les données via fichier local ou upload"""
        st.sidebar.markdown("### 📁 Chargement des données")
        
        # Nom du fichier attendu dans le même dossier
        csv_filename = "ofgl-base-communes.csv"
        
        # Variable pour stocker la source du fichier (objet fichier)
        file_source = None
        
        # 1. Vérifier si le fichier existe localement
        if os.path.exists(csv_filename):
            try:
                # Ouvrir le fichier local en mode lecture binaire (pour compatibilité avec chardet)
                file_source = open(csv_filename, 'rb')
                st.sidebar.success(f"✅ Fichier local '{csv_filename}' détecté et chargé !")
            except Exception as e:
                st.sidebar.error(f"Erreur lecture fichier local: {str(e)}")
        
        # 2. Option d'upload (écrase le fichier local si un nouveau fichier est uploadé)
        uploaded_file = st.sidebar.file_uploader(
            "Ou téléchargez un autre fichier CSV",
            type=['csv', 'txt'],
            help="Le fichier doit contenir les données financières des communes"
        )
        
        # Si l'utilisateur upload un fichier, on l'utilise à la place du fichier local
        if uploaded_file is not None:
            file_source = uploaded_file
            st.sidebar.info("📄 Utilisation du fichier uploadé par l'utilisateur")
        
        # 3. Traitement des données si une source est disponible
        if file_source is not None:
            try:
                # Détection de l'encodage
                raw_data = file_source.read()
                result = chardet.detect(raw_data)
                encoding = result['encoding']
                
                # Réinitialiser le pointeur du fichier
                file_source.seek(0)
                
                # Essayer différents séparateurs
                data_loaded = False
                for sep in [';', ',', '\t', '|']:
                    try:
                        # Essayer de lire avec l'encodage détecté
                        df = pd.read_csv(file_source, sep=sep, encoding=encoding, low_memory=False)
                        
                        # Réinitialiser le pointeur pour le prochain essai
                        file_source.seek(0)
                        
                        # Si on a réussi à lire avec au moins 10 colonnes
                        if len(df.columns) >= 10:
                            self.data = df
                            st.sidebar.success(f"✅ Données chargées avec succès ({len(df)} lignes, {len(df.columns)} colonnes)")
                            
                            # Afficher les premières lignes pour vérification
                            with st.sidebar.expander("Aperçu des données chargées"):
                                st.write(f"Colonnes: {list(df.columns)}")
                                st.dataframe(df.head(3))
                            
                            data_loaded = True
                            break
                            
                    except Exception as e:
                        file_source.seek(0)
                        continue
                
                # Si aucune méthode n'a fonctionné, essayer avec latin-1
                if not data_loaded:
                    file_source.seek(0)
                    try:
                        # Lire avec latin-1 (encodage commun pour les fichiers CSV français)
                        self.data = pd.read_csv(file_source, sep=';', encoding='latin-1', low_memory=False)
                        st.sidebar.success(f"✅ Fichier chargé avec latin-1 ({len(self.data)} lignes)")
                        data_loaded = True
                    except:
                        file_source.seek(0)
                        # Dernier essai avec utf-8 et gestion des erreurs
                        self.data = pd.read_csv(file_source, sep=None, encoding='utf-8', engine='python', on_bad_lines='skip')
                        st.sidebar.success(f"✅ Fichier chargé avec gestion d'erreurs ({len(self.data)} lignes)")
                
                # Nettoyage des noms de colonnes
                if not self.data.empty:
                    self.data.columns = [str(col).strip() for col in self.data.columns]
                    
                    # Afficher les informations sur les données
                    st.sidebar.markdown("### 📊 Informations sur les données")
                    st.sidebar.write(f"**Lignes:** {len(self.data):,}")
                    st.sidebar.write(f"**Colonnes:** {len(self.data.columns)}")
                    st.sidebar.write(f"**Années:** {sorted(self.data['Exercice'].unique()) if 'Exercice' in self.data.columns else 'Non trouvé'}")
                    
                    # Extraire la configuration des communes
                    self.communes_config = self._extract_communes_config()
                
                # Fermer le fichier local si on l'a ouvert (pas nécessaire pour uploaded_file qui est géré par Streamlit)
                if os.path.exists(csv_filename) and uploaded_file is None:
                    file_source.close()

            except Exception as e:
                st.sidebar.error(f"Erreur lors du chargement: {str(e)}")
                self.data = pd.DataFrame()
        else:
            # Mode démonstration avec données d'exemple
            st.sidebar.info("📝 Mode démonstration - Fichier 'ofgl-base-communes.csv' introuvable et aucun fichier uploadé.")
            self._create_sample_data()
    
    def _create_sample_data(self):
        """Crée des données d'exemple pour la démonstration"""
        st.info("Mode démonstration - Voici un aperçu de ce que vous verrez avec vos données réelles")
        
        # Données d'exemple pour les 24 communes de La Réunion
        sample_data = []
        communes = [
            'Saint-Denis', 'Saint-Paul', 'Saint-Pierre', 'Le Tampon', 'Saint-Louis',
            'Saint-Leu', 'Le Port', 'La Possession', 'Saint-André', 'Saint-Benoît',
            'Saint-Joseph', 'Saint-Philippe', 'Sainte-Marie', 'Sainte-Suzanne',
            'Les Avirons', 'Entre-Deux', 'L\'Étang-Salé', 'Petite-Île',
            'La Plaine-des-Palmistes', 'Bras-Panon', 'Cilaos', 'Salazie',
            'Les Trois-Bassins', 'Sainte-Rose'
        ]
        
        for i, commune in enumerate(communes):
            for year in [2017]:
                sample_data.append({
                    'Exercice': year,
                    'Nom 2024 Commune': commune,
                    'Agrégat': 'Recettes totales hors emprunts',
                    'Type de budget': 'Budget principal',
                    'Montant': np.random.uniform(10000000, 50000000),
                    'Population totale': np.random.randint(5000, 150000),
                    'Nom 2024 Région': 'La Réunion',
                    'Code Insee 2024 Département': '974',
                    'Nom 2024 EPCI': f'Communauté d\'agglomération {["Nord", "Sud", "Est", "Ouest"][i % 4]}'
                })
        
        self.data = pd.DataFrame(sample_data)
        self.communes_config = self._extract_communes_config()
    
    def _extract_communes_config(self):
        """Extrait la configuration des communes depuis les données"""
        if self.data.empty:
            return {}
        
        # Obtenir la liste unique des communes
        if 'Nom 2024 Commune' in self.data.columns:
            communes_list = self.data['Nom 2024 Commune'].unique()
        else:
            # Essayer de trouver la colonne des noms de commune
            commune_cols = [col for col in self.data.columns if 'commune' in str(col).lower() or 'nom' in str(col).lower()]
            if commune_cols:
                communes_list = self.data[commune_cols[0]].unique()
            else:
                st.error("Colonne des noms de communes non trouvée")
                return {}
        
        # Créer un dictionnaire de configuration pour chaque commune
        communes_config = {}
        
        for commune in communes_list:
            # Filtrer les données pour cette commune
            if 'Nom 2024 Commune' in self.data.columns:
                commune_data = self.data[self.data['Nom 2024 Commune'] == commune]
            else:
                commune_col = commune_cols[0]
                commune_data = self.data[self.data[commune_col] == commune]
            
            if commune_data.empty:
                continue
            
            # Obtenir la population (dernière valeur disponible)
            if 'Population totale' in commune_data.columns:
                population_series = commune_data['Population totale']
                population = population_series.mean() if not population_series.empty else 0
            else:
                population = np.random.randint(5000, 150000)  # Valeur par défaut
            
            # Obtenir les informations régionales
            region_data = commune_data.iloc[0] if not commune_data.empty else {}
            
            # Déterminer le type de commune
            commune_type = self._determine_commune_type(commune_data)
            
            # Configuration de base
            communes_config[commune] = {
                "population_base": population,
                "budget_base": self._estimate_budget(commune_data),
                "type": commune_type,
                "specialites": self._determine_specialties(str(commune), commune_data),
                "endettement_base": 0,
                "fiscalite_base": self._estimate_tax_rate(commune_data),
                "couleur": self._get_commune_color(str(commune)),
                "region": region_data.get('Nom 2024 Région', 'La Réunion') if not commune_data.empty else 'La Réunion',
                "arrondissement": self._get_arrondissement(str(commune)),
                "intercommunalite": region_data.get('Nom 2024 EPCI', 'Inconnue') if not commune_data.empty else 'Inconnue'
            }
        
        return communes_config
    
    def _determine_commune_type(self, commune_data):
        """Détermine le type de commune basé sur les données"""
        if commune_data.empty:
            return "urbaine"
        
        # Vérifier les colonnes de classification
        commune_row = commune_data.iloc[0]
        
        # Essayer différentes colonnes possibles
        rural_cols = [col for col in commune_data.columns if 'rural' in str(col).lower()]
        mountain_cols = [col for col in commune_data.columns if 'montagne' in str(col).lower()]
        tourist_cols = [col for col in commune_data.columns if 'tourist' in str(col).lower()]
        
        if rural_cols and commune_row.get(rural_cols[0], 'Non') == 'Oui':
            return "rurale"
        elif mountain_cols and commune_row.get(mountain_cols[0], 'Non') == 'Oui':
            return "montagne"
        elif tourist_cols and commune_row.get(tourist_cols[0], 'Non') == 'Oui':
            return "touristique"
        else:
            return "urbaine"
    
    def _estimate_budget(self, commune_data):
        """Estime le budget annuel d'une commune"""
        if commune_data.empty:
            return 0
        
        # Chercher les colonnes d'agrégat et de montant
        agregat_cols = [col for col in commune_data.columns if 'agrégat' in str(col).lower() or 'agregat' in str(col).lower()]
        montant_cols = [col for col in commune_data.columns if 'montant' in str(col).lower()]
        
        if not agregat_cols or not montant_cols:
            return 0
        
        agregat_col = agregat_cols[0]
        montant_col = montant_cols[0]
        
        # Chercher les recettes totales
        recettes_mask = commune_data[agregat_col].astype(str).str.contains('recettes totales', case=False, na=False)
        recettes_data = commune_data[recettes_mask]
        
        if not recettes_data.empty:
            return recettes_data[montant_col].mean() / 1000000
        
        return 0
    
    def _estimate_tax_rate(self, commune_data):
        """Estime le taux de fiscalité"""
        if commune_data.empty:
            return 0.35
        
        # Chercher les colonnes d'agrégat et de montant
        agregat_cols = [col for col in commune_data.columns if 'agrégat' in str(col).lower() or 'agregat' in str(col).lower()]
        montant_cols = [col for col in commune_data.columns if 'montant' in str(col).lower()]
        
        if not agregat_cols or not montant_cols:
            return 0.35
        
        agregat_col = agregat_cols[0]
        montant_col = montant_cols[0]
        
        # Chercher les impôts
        impots_mask = commune_data[agregat_col].astype(str).str.contains('impôt|impot|taxe', case=False, na=False)
        impots_data = commune_data[impots_mask]
        
        if not impots_data.empty:
            total_impots = impots_data[montant_col].sum()
            total_recettes = self._estimate_budget(commune_data) * 1000000
            
            if total_recettes > 0:
                return min(max(total_impots / total_recettes, 0.2), 0.5)
        
        return 0.35
    
    def _determine_specialties(self, commune_name, commune_data):
        """Détermine les spécialités de la commune"""
        # Liste des spécialités basées sur le nom
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
    
    def get_years_available(self):
        """Retourne les années disponibles dans les données"""
        if self.data.empty:
            return [2017]
        
        # Chercher la colonne des années
        year_cols = [col for col in self.data.columns if 'exercice' in str(col).lower() or 'annee' in str(col).lower() or 'année' in str(col).lower()]
        
        if year_cols:
            years = sorted(self.data[year_cols[0]].dropna().unique())
            return [int(y) for y in years] if len(years) > 0 else [2017]
        
        return [2017]
    
    def prepare_commune_financial_data(self, commune_name):
        """Prépare les données financières d'une commune"""
        if self.data.empty:
            return pd.DataFrame(), {}
        
        # Filtrer les données pour la commune spécifiée
        commune_cols = [col for col in self.data.columns if 'commune' in str(col).lower() or 'nom' in str(col).lower()]
        
        if not commune_cols:
            return pd.DataFrame(), {}
        
        commune_col = commune_cols[0]
        commune_data = self.data[self.data[commune_col] == commune_name].copy()
        
        if commune_data.empty:
            return pd.DataFrame(), {}
        
        # Agréger les données par année
        financial_metrics = {}
        years_available = self.get_years_available()
        
        # Chercher les colonnes nécessaires
        year_cols = [col for col in commune_data.columns if 'exercice' in str(col).lower() or 'annee' in str(col).lower()]
        pop_cols = [col for col in commune_data.columns if 'population' in str(col).lower()]
        agregat_cols = [col for col in commune_data.columns if 'agrégat' in str(col).lower() or 'agregat' in str(col).lower()]
        montant_cols = [col for col in commune_data.columns if 'montant' in str(col).lower()]
        
        if not year_cols or not agregat_cols or not montant_cols:
            return pd.DataFrame(), {}
        
        year_col = year_cols[0]
        agregat_col = agregat_cols[0]
        montant_col = montant_cols[0]
        pop_col = pop_cols[0] if pop_cols else None
        
        for year in years_available:
            year_data = commune_data[commune_data[year_col] == year]
            
            if year_data.empty:
                continue
            
            # Population
            if pop_col and pop_col in year_data.columns:
                pop_data = year_data[pop_col].mean()
            else:
                pop_data = self.communes_config.get(commune_name, {}).get('population_base', 0)
            
            # Recettes totales hors emprunts
            recettes_mask = year_data[agregat_col].astype(str).str.contains('recettes totales', case=False, na=False)
            recettes_data = year_data[recettes_mask]
            recettes = recettes_data[montant_col].sum() / 1000000 if not recettes_data.empty else 0
            
            # Épargne brute
            epargne_mask = year_data[agregat_col].astype(str).str.contains('épargne brute|epargne brute', case=False, na=False)
            epargne_data = year_data[epargne_mask]
            epargne_totale = epargne_data[montant_col].sum() / 1000000 if not epargne_data.empty else 0
            
            # Capacité ou besoin de financement
            financement_mask = year_data[agregat_col].astype(str).str.contains('capacité|besoin|financement', case=False, na=False)
            financement_data = year_data[financement_mask]
            financement = financement_data[montant_col].sum() / 1000000 if not financement_data.empty else 0
            
            # Impôts et taxes
            impots_mask = year_data[agregat_col].astype(str).str.contains('impôt|impot|taxe', case=False, na=False)
            impots_data = year_data[impots_mask]
            impots = impots_data[montant_col].sum() / 1000000 if not impots_data.empty else 0
            
            # Stocker les métriques
            financial_metrics[year] = {
                'Annee': year,
                'Population': pop_data,
                'Recettes_Totales': recettes,
                'Epargne_Brute': epargne_totale,
                'Capacite_Financement': financement,
                'Impots_Locaux': impots,
                'Dette_Totale': self._estimate_debt_from_data(year_data, recettes, agregat_col, montant_col),
                'Depenses_Totales': max(recettes - epargne_totale, recettes * 0.9),
                'Dotations_Etat': recettes * 0.4 if recettes > 0 else 0,
                'Taux_Endettement': self._calculate_debt_ratio_from_data(year_data, recettes, agregat_col, montant_col),
                'Capacite_Remboursement': self._calculate_repayment_capacity(epargne_totale, financement),
                'Ratio_Endettement_Recettes': self._calculate_debt_revenue_ratio(year_data, recettes, agregat_col, montant_col)
            }
        
        # Créer le DataFrame
        if financial_metrics:
            df = pd.DataFrame.from_dict(financial_metrics, orient='index')
            df = df.sort_values('Annee')
        else:
            df = pd.DataFrame()
        
        # Récupérer la configuration de la commune
        config = self.communes_config.get(commune_name, {})
        
        return df, config
    
    def _estimate_debt_from_data(self, year_data, revenue, agregat_col, montant_col):
        """Estime la dette totale à partir des données disponibles"""
        if revenue <= 0:
            return 0
        
        # Chercher les données de capacité de financement
        financement_mask = year_data[agregat_col].astype(str).str.contains('capacité|besoin|financement', case=False, na=False)
        financement_data = year_data[financement_mask]
        
        if not financement_data.empty:
            financement = financement_data[montant_col].sum() / 1000000
            return abs(financement) * 5
        
        return revenue * 1.2
    
    def _calculate_debt_ratio_from_data(self, year_data, revenue, agregat_col, montant_col):
        """Calcule le taux d'endettement à partir des données"""
        if revenue <= 0:
            return 0.5
        
        # Chercher l'épargne brute
        epargne_mask = year_data[agregat_col].astype(str).str.contains('épargne brute|epargne brute', case=False, na=False)
        epargne_data = year_data[epargne_mask]
        
        if not epargne_data.empty:
            epargne = epargne_data[montant_col].sum() / 1000000
        else:
            epargne = revenue * 0.04
        
        # Ratio basé sur l'épargne
        base_ratio = 0.6
        if epargne < revenue * 0.03:
            base_ratio = 0.8
        elif epargne < revenue * 0.06:
            base_ratio = 0.7
        
        return min(max(base_ratio, 0.3), 0.9)
    
    def _calculate_repayment_capacity(self, epargne, financement):
        """Calcule la capacité de remboursement"""
        if epargne <= 0:
            return 0.8
        
        if financement > 0:
            base_capacity = 2.0 + (epargne / 5)
        else:
            base_capacity = 1.0 + (epargne / 10)
        
        return max(min(base_capacity, 3.0), 0.5)
    
    def _calculate_debt_revenue_ratio(self, year_data, revenue, agregat_col, montant_col):
        """Calcule le ratio dette/recettes"""
        if revenue <= 0:
            return 1.0
        
        debt = self._estimate_debt_from_data(year_data, revenue, agregat_col, montant_col)
        ratio = debt / revenue
        
        return min(max(ratio, 0.5), 2.5)
    
    def create_header(self):
        """Crée l'en-tête du dashboard"""
        st.markdown('<h1 class="main-header">🏝️ Analyse Financière des Communes de La Réunion</h1>', 
                   unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if self.data.empty:
                st.markdown("""
                **Dashboard d'analyse financière**  
                *Téléchargez votre fichier CSV pour commencer l'analyse*
                """)
            else:
                st.markdown(f"""
                **Dashboard d'analyse financière**  
                *{len(self.communes_config)} communes analysées - Données {self.get_years_available()[0]}*
                """)
    
    def create_sidebar(self):
        """Crée la sidebar avec les paramètres"""
        with st.sidebar:
            st.image("https://upload.wikimedia.org/wikipedia/commons/6/66/Flag_of_R%C3%A9union.svg", 
                    width=200)
            
            # Chargement des données
            self._load_data()
            
            if self.data.empty or not self.communes_config:
                st.warning("Aucune donnée de commune chargée")
                return None, None, False, [], []
            
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
            years = self.get_years_available()
            
            if len(years) > 1:
                year_range = st.slider(
                    "Sélectionnez la période:",
                    min_value=min(years),
                    max_value=max(years),
                    value=(min(years), max(years))
                )
            else:
                st.info(f"**Année disponible :** {years[0]}")
                year_range = (years[0], years[0])
            
            # Options d'affichage
            st.markdown("### ⚙️ Options d'affichage")
            show_advanced = st.checkbox("Afficher les données brutes")
            compare_mode = st.checkbox("Mode comparatif", value=False)
            
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
            
            st.metric("Communes analysées", f"{num_communes}")
            st.metric("Population totale", f"{total_population:,.0f}")
            st.metric("Année de référence", f"{years[0]}")
            
            st.markdown("---")
            st.markdown("#### ℹ️ À propos")
            st.markdown("""
            **Source:** Données OFGL  
            **Format:** CSV avec séparateur ';'  
            **Encodage:** UTF-8 ou Latin-1
            """)
            
            return selected_commune, year_range, show_advanced, compare_communes, selected_region
    
    def create_commune_overview(self):
        """Crée une vue d'ensemble de toutes les communes"""
        st.markdown("### 🗺️ Vue d'ensemble des communes")
        
        if not self.communes_config:
            st.warning("Aucune donnée de commune disponible")
            return
        
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
                    'Épargne (M€)': last_row.get('Epargne_Brute', 0),
                    'Dette (M€)': last_row.get('Dette_Totale', 0),
                    'Capacité': last_row.get('Capacite_Remboursement', 0),
                    'Intercommunalité': config.get('intercommunalite', 'Inconnue')
                })
        
        if overview_data:
            overview_df = pd.DataFrame(overview_data)
            
            # Tableau interactif
            st.dataframe(
                overview_df[['Commune', 'Région', 'Type', 'Population', 
                           'Recettes (M€)', 'Épargne (M€)', 
                           'Dette (M€)', 'Capacité', 'Intercommunalité']].round(2),
                use_container_width=True,
                height=600
            )
            
            # Graphiques de répartition
            st.markdown("#### 📊 Répartition par région")
            
            region_data = overview_df.groupby('Région').agg({
                'Commune': 'count',
                'Population': 'sum',
                'Recettes (M€)': 'sum',
                'Dette (M€)': 'sum'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.pie(region_data, values='Commune', names='Région',
                            title='Nombre de communes par région',
                            color_discrete_sequence=px.colors.qualitative.Set3)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(region_data, x='Région', y='Dette (M€)',
                            title='Dette estimée par région (M€)',
                            color='Région',
                            color_discrete_sequence=px.colors.qualitative.Set1)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée financière disponible")
    
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
            st.markdown(f"**Type:** {config.get('type', 'urbaine').title()}")
            st.markdown(f"**Spécialités:** {', '.join(config.get('specialites', []))}")
            st.markdown(f"**Population:** {last_row.get('Population', 0):,.0f} hab")
            st.markdown(f"**Intercommunalité:** {config.get('intercommunalite', 'Inconnue')}")
        
        with col2:
            st.markdown("#### 💰 Situation financière")
            year = int(last_row.get('Annee', 2017))
            st.metric(f"Recettes totales ({year})", f"{last_row.get('Recettes_Totales', 0):.1f} M€")
            st.metric("Épargne brute", f"{last_row.get('Epargne_Brute', 0):.2f} M€")
            st.metric("Impôts locaux", f"{last_row.get('Impots_Locaux', 0):.1f} M€")
            st.metric("Capacité/Besoin financement", f"{last_row.get('Capacite_Financement', 0):.2f} M€")
        
        with col3:
            st.markdown("#### 📈 Capacité financière")
            st.metric("Dette estimée", f"{last_row.get('Dette_Totale', 0):.1f} M€")
            st.metric("Capacité de remboursement", f"{last_row.get('Capacite_Remboursement', 0):.2f}")
            st.metric("Ratio dette/recettes", f"{last_row.get('Ratio_Endettement_Recettes', 0):.2f}")
            st.metric("Taux d'endettement", f"{last_row.get('Taux_Endettement', 0)*100:.1f}%")
        
        # Alertes de situation
        self._display_alerts(last_row)
    
    def _display_alerts(self, data):
        """Affiche les alertes selon la situation financière"""
        capacity = data.get('Capacite_Remboursement', 1.0)
        debt_ratio = data.get('Ratio_Endettement_Recettes', 1.0)
        epargne = data.get('Epargne_Brute', 0)
        financement = data.get('Capacite_Financement', 0)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if financement < 0:
                st.error("⚠️ **Besoin de financement**")
                st.markdown("La commune présente un besoin de financement.")
            elif epargne < data.get('Recettes_Totales', 0) * 0.05:
                st.warning("📊 **Épargne brute faible**")
                st.markdown("L'épargne brute représente moins de 5% des recettes.")
            else:
                st.success("✅ **Situation financière stable**")
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
    
    def create_data_explorer(self):
        """Crée un explorateur de données"""
        st.markdown("### 🔍 Explorateur de données")
        
        if self.data.empty:
            st.warning("Aucune donnée à explorer")
            return
        
        # Afficher les premières lignes
        st.markdown("#### 📄 Aperçu des données")
        st.dataframe(self.data.head(100), use_container_width=True, height=400)
        
        # Statistiques des colonnes
        st.markdown("#### 📊 Statistiques des colonnes")
        col_info = pd.DataFrame({
            'Colonne': self.data.columns,
            'Type': self.data.dtypes.astype(str),
            'Valeurs uniques': [self.data[col].nunique() for col in self.data.columns],
            'Valeurs nulles': [self.data[col].isnull().sum() for col in self.data.columns]
        })
        st.dataframe(col_info, use_container_width=True)
    
    def create_comparative_analysis(self, communes_to_compare):
        """Crée l'analyse comparative entre communes"""
        st.markdown("### 📊 Analyse comparative")
        
        if len(communes_to_compare) < 2:
            st.info("Sélectionnez au moins 2 communes à comparer")
            return
        
        comparison_data = []
        
        for commune_name in communes_to_compare:
            df, config = self.prepare_commune_financial_data(commune_name)
            
            if not df.empty:
                last_row = df.iloc[-1]
                
                comparison_data.append({
                    'Commune': commune_name,
                    'Région': config.get('region', 'Inconnue'),
                    'Population': last_row.get('Population', 0),
                    'Recettes (M€)': last_row.get('Recettes_Totales', 0),
                    'Épargne (M€)': last_row.get('Epargne_Brute', 0),
                    'Dette (M€)': last_row.get('Dette_Totale', 0),
                    'Dette/Habitant (k€)': (last_row.get('Dette_Totale', 0) * 1000) / last_row.get('Population', 1) if last_row.get('Population', 0) > 0 else 0,
                    'Capacité': last_row.get('Capacite_Remboursement', 0),
                    'Ratio D/R': last_row.get('Ratio_Endettement_Recettes', 0)
                })
        
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            
            # Graphique comparatif
            st.markdown("#### 📈 Comparaison des indicateurs")
            
            metrics = st.multiselect(
                "Sélectionnez les indicateurs:",
                ['Recettes (M€)', 'Épargne (M€)', 'Dette (M€)', 'Dette/Habitant (k€)', 'Capacité', 'Ratio D/R'],
                default=['Recettes (M€)', 'Dette (M€)', 'Capacité']
            )
            
            if metrics:
                fig = go.Figure()
                
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
                    xaxis_title='Commune',
                    yaxis_title='Valeur',
                    barmode='group',
                    height=500
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Tableau comparatif
            st.markdown("#### 📋 Tableau comparatif")
            st.dataframe(
                comparison_df.round(2),
                use_container_width=True
            )
        else:
            st.warning("Aucune donnée disponible pour la comparaison")
    
    def create_ranking_analysis(self):
        """Crée un classement des communes"""
        st.markdown("### 🏆 Classement des communes")
        
        if not self.communes_config:
            st.warning("Aucune donnée disponible")
            return
        
        ranking_data = []
        
        for commune_name, config in self.communes_config.items():
            df, _ = self.prepare_commune_financial_data(commune_name)
            
            if not df.empty:
                last_row = df.iloc[-1]
                
                ranking_data.append({
                    'Commune': commune_name,
                    'Région': config.get('region', 'Inconnue'),
                    'Population': last_row.get('Population', 0),
                    'Recettes_par_Habitant': (last_row.get('Recettes_Totales', 0) * 1000000) / last_row.get('Population', 1) if last_row.get('Population', 0) > 0 else 0,
                    'Dette_par_Habitant': (last_row.get('Dette_Totale', 0) * 1000000) / last_row.get('Population', 1) if last_row.get('Population', 0) > 0 else 0,
                    'Capacite_Remboursement': last_row.get('Capacite_Remboursement', 0),
                    'Ratio_Dette_Recettes': last_row.get('Ratio_Endettement_Recettes', 0)
                })
        
        if ranking_data:
            ranking_df = pd.DataFrame(ranking_data)
            
            # Sélection de l'indicateur
            col1, col2 = st.columns(2)
            
            with col1:
                ranking_metric = st.selectbox(
                    "Classer par:",
                    ['Recettes_par_Habitant', 'Dette_par_Habitant', 'Capacite_Remboursement', 'Ratio_Dette_Recettes'],
                    format_func=lambda x: {
                        'Recettes_par_Habitant': 'Recettes par habitant',
                        'Dette_par_Habitant': 'Dette par habitant',
                        'Capacite_Remboursement': 'Capacité de remboursement',
                        'Ratio_Dette_Recettes': 'Ratio dette/recettes'
                    }[x]
                )
            
            with col2:
                ascending = st.checkbox("Ordre croissant", value=(ranking_metric in ['Dette_par_Habitant', 'Ratio_Dette_Recettes']))
            
            # Classement
            sorted_df = ranking_df.sort_values(by=ranking_metric, ascending=ascending)
            sorted_df['Rang'] = range(1, len(sorted_df) + 1)
            
            # Affichage
            st.dataframe(
                sorted_df[['Rang', 'Commune', 'Région', ranking_metric]].head(15),
                use_container_width=True
            )
            
            # Visualisation
            fig = px.bar(sorted_df.head(10), 
                        x=ranking_metric, 
                        y='Commune',
                        orientation='h',
                        color='Région',
                        title=f'Top 10 - {ranking_metric.replace("_", " ")}',
                        color_discrete_sequence=px.colors.qualitative.Set3)
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Aucune donnée disponible pour le classement")
    
    def create_recommandations(self, df, config):
        """Crée la section des recommandations"""
        st.markdown("### 💡 Recommandations stratégiques")
        
        if df.empty:
            st.info("Sélectionnez une commune pour voir les recommandations")
            return
        
        last_data = df.iloc[-1]
        epargne = last_data.get('Epargne_Brute', 0)
        financement = last_data.get('Capacite_Financement', 0)
        capacity = last_data.get('Capacite_Remboursement', 0)
        
        # Recommandations
        tabs = st.tabs(["Priorités", "Investissements", "Gouvernance"])
        
        with tabs[0]:
            if financement < 0:
                st.error("**Actions prioritaires:**")
                st.markdown("""
                1. **Rééquilibrage budgétaire**
                   - Révision des dépenses
                   - Report des projets non essentiels
                
                2. **Optimisation des recettes**
                   - Actualisation des bases fiscales
                   - Recouvrement des impôts
                
                3. **Maîtrise des dépenses**
                   - Audit des dépenses courantes
                   - Rationalisation des achats
                """)
            else:
                st.success("**Actions d'optimisation:**")
                st.markdown("""
                1. **Consolidation de l'épargne**
                   - Constitution de réserves
                   - Gestion proactive
                
                2. **Investissements structurants**
                   - Projets à fort retour
                   - Infrastructures durables
                
                3. **Préparation aux risques**
                   - Plans de continuité
                   - Stress tests financiers
                """)
        
        with tabs[1]:
            st.markdown("**Orientation des investissements:**")
            specialties = config.get('specialites', ['services publics'])
            st.markdown(f"""
            **Investissements prioritaires:**
            - **{specialties[0]}**: Modernisation et développement
            - **Transition écologique**: Adaptation climatique
            - **Services publics**: Amélioration qualité
            
            **Financement:**
            - Fonds européens
            - Dotations spécifiques DOM
            - Partenariats public-privé
            """)
        
        with tabs[2]:
            st.markdown("**Gouvernance financière:**")
            st.markdown("""
            1. **Transparence**
               - Publication des indicateurs
               - Portail open data
               - Réunions publiques
            
            2. **Participation**
               - Budget participatif
               - Consultations régulières
               - Commission des finances
            
            3. **Compétences**
               - Formation des élus
               - Recrutement spécialisé
               - Échange de pratiques
            """)
    
    def run_dashboard(self):
        """Exécute le dashboard principal"""
        self.create_header()
        
        # Récupération des paramètres
        params = self.create_sidebar()
        
        if params is None:
            # Si aucune donnée n'est chargée même après chargement (ex: fichier vide)
            if not self.data.empty:
                 # Si on est en mode démo ou chargé mais params None (ne devrait pas arriver normalement avec la correction)
                 params = (list(self.communes_config.keys())[0], (2017, 2017), False, [], ["La Réunion"])
            else:
                return
        
        selected_commune, year_range, show_advanced, compare_communes, selected_region = params
        
        # Navigation principale
        tab_names = ["🏠 Vue d'ensemble", "🏙️ Analyse communale", "🔄 Comparaisons", "🏆 Classements", "📋 Recommandations"]
        
        if show_advanced:
            tab_names.append("🔍 Données brutes")
        
        tabs = st.tabs(tab_names)
        
        tab_index = 0
        
        with tabs[tab_index]:  # Vue d'ensemble
            self.create_commune_overview()
            
            # Statistiques globales
            if not self.data.empty:
                st.markdown("### 📈 Informations sur le dataset")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Lignes totales", f"{len(self.data):,}")
                    st.metric("Communes", f"{len(self.communes_config)}")
                
                with col2:
                    st.metric("Années", f"{len(self.get_years_available())}")
                    st.metric("Colonnes", f"{len(self.data.columns)}")
                
                with col3:
                    st.metric("Données financières", "Disponibles" if not self.data.empty else "Non disponibles")
        
        tab_index += 1
        
        with tabs[tab_index]:  # Analyse communale
            if selected_commune and selected_commune in self.communes_config:
                df, config = self.prepare_commune_financial_data(selected_commune)
                
                if not df.empty:
                    self.create_summary_metrics(df, config, selected_commune)
                    
                    # Graphiques
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("#### 📊 Indicateurs financiers")
                        
                        indicators = ['Recettes_Totales', 'Epargne_Brute', 'Impots_Locaux', 'Dette_Totale']
                        indicator_names = ['Recettes', 'Épargne', 'Impôts', 'Dette']
                        indicator_values = [df[col].iloc[-1] for col in indicators]
                        
                        fig = go.Figure(data=[go.Bar(
                            x=indicator_names,
                            y=indicator_values,
                            marker_color=['#264653', '#2A9D8F', '#E76F51', '#F9A602']
                        )])
                        
                        fig.update_layout(
                            title=f'Indicateurs - {selected_commune}',
                            yaxis_title='M€',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        st.markdown("#### ⚖️ Ratios financiers")
                        
                        ratios = ['Capacite_Remboursement', 'Ratio_Endettement_Recettes']
                        ratio_names = ['Capacité', 'Ratio D/R']
                        ratio_values = [df[col].iloc[-1] for col in ratios]
                        
                        fig = go.Figure(data=[go.Bar(
                            x=ratio_names,
                            y=ratio_values,
                            marker_color=['#4ECDC4', '#FF6B6B']
                        )])
                        
                        fig.add_hline(y=1.0, line_dash="dash", line_color="red")
                        
                        fig.update_layout(
                            title='Ratios de solvabilité',
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(f"Aucune donnée financière pour {selected_commune}")
            else:
                st.info("Sélectionnez une commune pour voir son analyse")
        
        tab_index += 1
        
        with tabs[tab_index]:  # Comparaisons
            if compare_communes and len(compare_communes) >= 1:
                self.create_comparative_analysis([selected_commune] + compare_communes)
            else:
                st.info("Activez le mode comparatif et sélectionnez des communes à comparer")
        
        tab_index += 1
        
        with tabs[tab_index]:  # Classements
            self.create_ranking_analysis()
        
        tab_index += 1
        
        with tabs[tab_index]:  # Recommandations
            if selected_commune and selected_commune in self.communes_config:
                df, config = self.prepare_commune_financial_data(selected_commune)
                self.create_recommandations(df, config)
            else:
                st.info("Sélectionnez une commune pour voir les recommandations")
        
        tab_index += 1
        
        if show_advanced and tab_index < len(tabs):  # Données brutes
            with tabs[tab_index]:
                self.create_data_explorer()
        
        # Pied de page
        st.markdown("---")
        st.markdown("""
        **Dashboard d'analyse financière des communes de La Réunion**  
        *Basé sur les données OFGL*
        
        ℹ️ **Note:** Les indicateurs financiers sont estimés à partir des données disponibles.
        """)

# Exécution du dashboard
if __name__ == "__main__":
    dashboard = ReunionFinancialDashboard()
    dashboard.run_dashboard()
