import streamlit as st
import fitz  # PyMuPDF
import pandas as pd
import re
import tempfile
from datetime import datetime

st.set_page_config(page_title="Extrator de CTEs", layout="centered")

st.title("📄 Extrator de Dados de CTEs")
st.markdown("Envie um PDF contendo CTEs para extrair os dados em Excel.")

uploaded_file = st.file_uploader("Selecione o PDF", type=["pdf"])

def extrair_ctes(pdf_path):
    doc = fitz.open(pdf_path)
    dados = []

    for pagina in doc:
        texto = pagina.get_text()

        match_cte = re.search(r"SÉRIE\s+\d+\s+(\d{6})", texto)
        numero_cte = match_cte.group(1) if match_cte else ""

        match_valor = re.search(r"VALOR TOTAL DO SERVIÇO\s+([\d.,]+)", texto)
        valor_cte = match_valor.group(1).replace(".", "").replace(",", ".") if match_valor else ""

        match_icms = re.search(r"VALOR ICMS\s+([\d.,]+)", texto)
        valor_icms = match_icms.group(1).replace(".", "").replace(",", ".") if match_icms else ""

        match_carga = re.findall(r"Número do Pedido/Carga:0*(\d+)", texto)
        numero_carga = next((c for c in match_carga if c.startswith("7")), "")

        if numero_cte:
            dados.append({
                "Número do CTE": numero_cte,
                "Valor do CTE": valor_cte,
                "Valor ICMS": valor_icms,
                "Número da Carga": numero_carga
            })

    return dados

if uploaded_file:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        caminho_pdf = tmp_file.name

    st.success("PDF carregado com sucesso! Processando...")

    dados = extrair_ctes(caminho_pdf)
    if dados:
        df = pd.DataFrame(dados)
        agora = datetime.now().strftime("%Y-%m-%d_%H-%M")
        nome_arquivo = f"Resumo_CTEs_{agora}.xlsx"
        df.to_excel(nome_arquivo, index=False)

        st.dataframe(df)

        with open(nome_arquivo, "rb") as f:
            st.download_button("📥 Baixar Excel", f, file_name=nome_arquivo)
    else:
        st.warning("Nenhum CTE encontrado no arquivo.")
