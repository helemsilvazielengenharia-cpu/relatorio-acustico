import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Ferramenta de Relatório Acústico - 1/3 Oitava", layout="wide")

st.title("📊 Processador de Espectro Acústico (1/3 de Oitava)")
st.write("Faça o upload do arquivo CSV do ensaio para calcular os níveis $LZ_{eq}$ e gerar o relatório e arquivo TXT.")

uploaded_file = st.file_uploader("Envie o arquivo CSV do ensaio", type=["csv"])

if uploaded_file is not None:
    # Leitura do CSV
    try:
        df = pd.read_csv(uploaded_file, sep=';')
    except Exception as e:
        df = pd.read_csv(uploaded_file, sep=',')
        
    st.success("Arquivo carregado com sucesso!")
    
    # Lista de colunas de frequência esperadas
    freq_cols = ['50 Hz', '63 Hz', '80 Hz', '100 Hz', '125 Hz', '160 Hz', '200 Hz', '250 Hz', '315 Hz', '400 Hz', '500 Hz', '630 Hz', '800 Hz', '1 kHz', '1,25 kHz', '1,6 kHz', '2 kHz', '2,5 kHz', '3,15 kHz', '4 kHz', '5 kHz', '6,3 kHz', '8 kHz', '10 kHz']
    
    # Verificar quais colunas existem no dataframe
    available_cols = [col for col in freq_cols if col in df.columns]
    
    if available_cols:
        results = {}
        for col in available_cols:
            vals = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
            # Média energética (média quadrática dos valores lineares > 0)
            valid_vals = vals[vals > 0]
            if len(valid_vals) > 0:
                mean_linear = valid_vals.mean()
                db_val = 10 * np.log10(mean_linear)
            else:
                db_val = 0.0
            results[col] = round(db_val, 2)
            
        res_df = pd.DataFrame(list(results.items()), columns=['Frequência', 'LZeq (dB)'])
        
        st.subheader("Tabela de Níveis $LZ_{eq}$ por Banda de 1/3 de Oitava")
        st.dataframe(res_df, use_container_width=True)
        
        # Gráfico de Espectro de Frequência
        st.subheader("Gráfico de Espectro de Frequência")
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.bar(res_df['Frequência'], res_df['LZeq (dB)'], color='#1f77b4', width=0.6)
        ax.set_xlabel('Frequência', fontsize=12)
        ax.set_ylabel('Nível de Pressão Sonora (dB)', fontsize=12)
        ax.set_title('Espectro de Frequência - 1/3 de Oitava ($LZ_{eq}$)', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        st.pyplot(fig)
        
        # Geração do conteúdo para arquivo TXT
        txt_content = "Frequencia;LZeq (dB)\n"
        for idx, row in res_df.iterrows():
            txt_content += f"{row['Frequência']};{row['LZeq (dB)']}\n"
            
        st.download_button(
            label="📥 Baixar TXT com os valores de 1/3 de oitava",
            data=txt_content,
            file_name="espectro_1_3_oitava.txt",
            mime="text/plain"
        )
    else:
        st.error("As colunas de frequência esperadas não foram encontradas no CSV.")
