import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

st.set_page_config(page_title="Processador Acústico - 1/3 Oitava", layout="wide")

st.title("📊 Processador de Espectro Acústico (1/3 de Oitava)")
st.write("Faça o upload do arquivo CSV do seu sonômetro para calcular os níveis $LZ_{eq}$ e exportar o relatório em TXT.")

uploaded_file = st.file_uploader("Arraste ou selecione o arquivo CSV do ensaio", type=["csv"])

if uploaded_file is not None:
    try:
        # Lê o CSV forçando o separador por ponto e vírgula
        uploaded_file.seek(0)
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
    except Exception:
        try:
            uploaded_file.seek(0)
            df = pd.read_csv(uploaded_file, sep=';', encoding='latin1')
        except Exception as e:
            st.error(f"Erro ao ler o arquivo CSV: {e}")
            df = None

    if df is not None:
        # Limpa espaços em branco nos nomes das colunas
        df.columns = df.columns.str.strip()
        
        st.success(f"✅ Arquivo processado com sucesso! Total de linhas: {len(df)}")
        
        freq_cols = [
            '50 Hz', '63 Hz', '80 Hz', '100 Hz', '125 Hz', '160 Hz', 
            '200 Hz', '250 Hz', '315 Hz', '400 Hz', '500 Hz', '630 Hz', 
            '800 Hz', '1 kHz', '1,25 kHz', '1,6 kHz', '2 kHz', '2,5 kHz', 
            '3,15 kHz', '4 kHz', '5 kHz', '6,3 kHz', '8 kHz', '10 kHz'
        ]
        
        available_cols = [col for col in freq_cols if col in df.columns]
        
        if available_cols:
            results = {}
            for col in available_cols:
                # Converte os valores substituindo vírgula por ponto
                vals = pd.to_numeric(df[col].astype(str).str.replace(',', '.'), errors='coerce').fillna(0)
                valid_vals = vals[vals > 0]
                if len(valid_vals) > 0:
                    mean_linear = valid_vals.mean()
                    db_val = 10 * np.log10(mean_linear)
                else:
                    db_val = 0.0
                results[col] = round(db_val, 2)
                
            res_df = pd.DataFrame(list(results.items()), columns=['Frequência', 'LZeq (dB)'])
            
            st.subheader("📋 Tabela de Níveis $LZ_{eq}$ por Banda")
            st.dataframe(res_df, use_container_width=True)
            
            st.subheader("📈 Gráfico de Espectro de Frequência")
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.bar(res_df['Frequência'], res_df['LZeq (dB)'], color='#1f77b4', width=0.6)
            ax.set_xlabel('Frequência', fontsize=12)
            ax.set_ylabel('Nível de Pressão Sonora (dB)', fontsize=12)
            ax.set_title('Espectro de Frequência - 1/3 de Oitava ($LZ_{eq}$)', fontsize=14, fontweight='bold')
            plt.xticks(rotation=45, ha='right')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            st.pyplot(fig)
            plt.close(fig)
            
            txt_content = "Frequencia;LZeq (dB)\n"
            for idx, row in res_df.iterrows():
                txt_content += f"{row['Frequência']};{row['LZeq (dB)']}\n"
                
            st.download_button(
                label="📥 Baixar arquivo TXT com os resultados",
                data=txt_content,
                file_name="resultado_espectro_1_3_oitava.txt",
                mime="text/plain"
            )
        else:
            # Mostra as colunas encontradas para ajudar a diagnosticar caso falte alguma
            st.error("As colunas de frequência em 1/3 de oitava não foram encontradas.")
            st.write("Colunas detetadas no seu arquivo:", list(df.columns))
else:
    st.info("💡 Por favor, faça o upload de um arquivo CSV para visualizar a análise e baixar o relatório TXT.")
