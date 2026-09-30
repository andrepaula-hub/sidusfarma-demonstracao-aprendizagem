"""
Visualização do relatório quantitativo do projeto Sidusfarma.
"""

import os
import sys
import json
import base64
import re
import pandas as pd
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import streamlit as st

st.set_page_config(
    page_title="Sidusfarma — Data Quality & Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
    .main-title { font-size: 2rem; font-weight: 700; color: #1e3a8a; margin-bottom: 0.2rem; }
    .sub-title  { font-size: 1rem; color: #64748b; margin-bottom: 1.2rem; }
    .badge-ok   { background:#dcfce7; color:#166534; padding:2px 8px; border-radius:4px; font-size:0.82rem; font-weight:600; }
    .badge-warn { background:#fef9c3; color:#854d0e; padding:2px 8px; border-radius:4px; font-size:0.82rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# ── Paths ──────────────────────────────────────────────────────────────────────
DATA_PATH    = os.path.join(BASE_DIR, "docs", "data")
QUALITY_JSON = os.path.join(DATA_PATH, "quality_report.json")
KPIS_JSON    = os.path.join(DATA_PATH, "kpis_summary.json")
CSV_PATH     = os.path.join(BASE_DIR, "DADOS")

@st.cache_data
def load_json():
    q, k = {}, {}
    if os.path.exists(QUALITY_JSON):
        with open(QUALITY_JSON, "r", encoding="utf-8") as f: q = json.load(f)
    if os.path.exists(KPIS_JSON):
        with open(KPIS_JSON,   "r", encoding="utf-8") as f: k = json.load(f)
    return q, k

@st.cache_data
def load_csv(filename):
    path = os.path.join(CSV_PATH, filename)
    if os.path.exists(path):
        return pd.read_csv(path, sep=";", encoding="utf-8", low_memory=False)
    return pd.DataFrame()

quality_data, kpi_data = load_json()
df_pesquisas = load_csv("pesquisas.csv")

report_path = os.path.join(BASE_DIR, "docs", "modelagem_quantitativa_de_dados_do_parceiro.md")
docs_dir = os.path.join(BASE_DIR, "docs")

if os.path.exists(report_path):
    with open(report_path, "r", encoding="utf-8") as f:
        content = f.read()

    def render_md_with_images(md_text, root_docs):
        def replace_img(match):
            alt_text = match.group(1)
            img_rel = match.group(2)
            possible_paths = [
                os.path.join(root_docs, img_rel),
                os.path.join(BASE_DIR, img_rel),
                os.path.join(root_docs, "images", os.path.basename(img_rel)),
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    with open(path, "rb") as img_file:
                        b64 = base64.b64encode(img_file.read()).decode("utf-8")
                    ext = os.path.splitext(path)[1].replace(".", "").lower()
                    mime = "image/png" if ext == "png" else f"image/{ext}"
                    return f'<div style="margin: 20px 0; text-align: center;"><img src="data:{mime};base64,{b64}" alt="{alt_text}" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);" /><p style="font-size: 0.85rem; color: #64748b; margin-top: 6px;"><em>{alt_text}</em></p></div>'
            return match.group(0)

        pattern = r"!\[(.*?)\]\((.*?)\)"
        processed_md = re.sub(pattern, replace_img, md_text)
        st.markdown(processed_md, unsafe_allow_html=True)

    render_md_with_images(content, docs_dir)

    st.download_button(
        "⬇️ Baixar relatório como .md",
        data=content.encode("utf-8"),
        file_name="modelagem_quantitativa_sidusfarma.md",
        mime="text/markdown",
    )
else:
    st.error("Relatório não encontrado. Execute o pipeline primeiro.")
