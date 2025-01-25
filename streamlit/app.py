import streamlit as st
import pandas as pd
import plotly.express as px
import os
from dotenv import load_dotenv
from pathlib import Path
import boto3

# Configuration de la page
st.set_page_config(layout="wide")

# Chargement des variables d'environnement
parent_dir = Path(__file__).parent.parent
load_dotenv(parent_dir / '.env')
load_dotenv(parent_dir / '.secrets')

# Titre principal
st.title("🌲 Forest Cover Type - MLOps Monitor")

# Ajout de l'onglet Dashboard
tabs = st.tabs(["📊 Dashboard"])

with tabs[0]:
    st.header("🧪 Test Results")

    try:
        # Configuration du client S3
        s3 = boto3.client(
            's3',
            aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
            aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY']
        )

        # Récupération du dernier rapport de test sur S3
        response = s3.list_objects_v2(
            Bucket='covertype-final-project-jedha',
            Prefix='covertype/test_reports/'
        )
        
        # Vérification que des fichiers sont disponibles
        if 'Contents' not in response or not response['Contents']:
            st.warning("No test reports found in the specified S3 bucket.")
        else:
            latest_file = sorted([obj['Key'] for obj in response['Contents']])[-1]
            obj = s3.get_object(Bucket='covertype-final-project-jedha', Key=latest_file)
            test_df = pd.read_csv(obj['Body'])

            # Résumé des tests
            st.subheader("Test Summary")
            col1, col2 = st.columns([1, 2])  # Mise en page en colonnes
            
            with col1:
                # Distribution des résultats des tests
                test_status = test_df['status'].value_counts()
                fig = px.pie(
                    values=test_status.values, 
                    names=test_status.index,
                    title="Test Results Distribution",
                    color_discrete_map={'passed': '#2ecc71', 'failed': '#e74c3c'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Détails des résultats des tests
                st.subheader("Test Details")
                display_df = test_df[['name', 'status', 'doc']].copy()
                display_df = display_df.style.apply(
                    lambda x: ['background-color: #2ecc71' if v == 'passed' 
                               else 'background-color: #e74c3c' for v in x], 
                    subset=['status']
                )
                st.dataframe(display_df, use_container_width=True)

    except Exception as e:
        # Gestion des erreurs
        st.error(f"Error loading test results: {str(e)}")
