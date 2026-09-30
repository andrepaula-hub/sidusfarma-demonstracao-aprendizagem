"""
Gera a plataforma legada de analytics e documentação em um único arquivo HTML autônomo:
legacy/streamlit/sidusfarma_analytics_complete.html

Contém TODAS as 7 abas com navegação interativa em JavaScript + CSS responsivo:
1. 📋 Scorecard DAMA-DMBOK
2. 📐 10 KPIs Formais
3. ⚖️ Simulador Denominadores N/D (com calculadora JS viva)
4. 📈 Análise de Outliers
5. ✅ AP1 · Arqueologia
6. 🧪 AP2 · Lab Indicadores
7. 📄 Relatório Oficial (.md renderizado com gráficos Base64)
"""
import os
import sys
import json
import base64
import re
import pandas as pd

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DOCS_DIR = os.path.join(BASE_DIR, "docs")
DATA_DIR = os.path.join(DOCS_DIR, "data")
LEGACY_DIR = os.path.join(BASE_DIR, "legacy", "streamlit")
OUT_HTML = os.path.join(LEGACY_DIR, "sidusfarma_analytics_complete.html")

# Carregar JSONs
with open(os.path.join(DATA_DIR, "quality_report.json"), "r", encoding="utf-8") as f:
    quality = json.load(f)
with open(os.path.join(DATA_DIR, "kpis_summary.json"), "r", encoding="utf-8") as f:
    kpis_data = json.load(f)

# Carregar Relatório MD
with open(os.path.join(DOCS_DIR, "modelagem_quantitativa_de_dados_do_parceiro.md"), "r", encoding="utf-8") as f:
    md_text = f.read()

# Helper para converter imagens em Base64
def embed_images(text):
    def repl(m):
        alt, src = m.group(1), m.group(2)
        paths = [
            os.path.join(DOCS_DIR, src),
            os.path.join(BASE_DIR, src),
            os.path.join(DOCS_DIR, "images", os.path.basename(src))
        ]
        for p in paths:
            if os.path.exists(p):
                with open(p, "rb") as img:
                    b64 = base64.b64encode(img.read()).decode("utf-8")
                return f'<div class="img-box"><img src="data:image/png;base64,{b64}" alt="{alt}"><p class="caption">{alt}</p></div>'
        return f'<p><em>[{alt}]</em></p>'
    return re.sub(r'!\[(.*?)\]\((.*?)\)', repl, text)

# Converter Markdown basico
def parse_md(text):
    text = embed_images(text)
    text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', text, flags=re.M)
    text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', text, flags=re.M)
    text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', text, flags=re.M)
    text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', text, flags=re.M)
    text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', text)
    text = re.sub(r'`(.*?)`', r'<code>\1</code>', text)
    text = re.sub(r'^---$', r'<hr>', text, flags=re.M)
    
    # Processar tabelas
    lines = text.split('\n')
    new_l = []
    in_t = False
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if '---' in line: continue
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not in_t:
                in_t = True
                new_l.append('<table class="data-table"><thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead><tbody>')
            else:
                new_l.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        else:
            if in_t:
                in_t = False
                new_l.append('</tbody></table>')
            new_l.append(line)
    if in_t: new_l.append('</tbody></table>')
    
    res = '\n'.join(new_l)
    res = re.sub(r'\n\n+', '</p><p>', res)
    return res

report_html = parse_md(md_text)

completeness_pct = quality.get('overall_completeness_pct', 0)
ds_count = len(quality.get('datasets', {}))

# Construir HTML com 7 Abas
html_content = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Central de Pesquisas Sidusfarma — Platform & Docs</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --primary-light: #3b82f6;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
            --text: #0f172a;
            --muted: #64748b;
            --success: #16a34a;
            --warning: #ca8a04;
        }}
        * {{ box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg);
            color: var(--text);
            margin: 0;
            padding: 0;
        }}
        .header {{
            background: var(--primary);
            color: white;
            padding: 20px 24px;
        }}
        .header h1 {{ margin: 0; font-size: 1.6rem; }}
        .header p {{ margin: 4px 0 0 0; color: #93c5fd; font-size: 0.95rem; }}
        
        /* Navegação por Abas */
        .tabs-nav {{
            display: flex;
            background: #ffffff;
            border-bottom: 2px solid var(--border);
            overflow-x: auto;
            padding: 0 16px;
        }}
        .tab-btn {{
            padding: 14px 20px;
            border: none;
            background: none;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--muted);
            cursor: pointer;
            border-bottom: 3px solid transparent;
            white-space: nowrap;
            transition: all 0.2s;
        }}
        .tab-btn:hover {{ color: var(--primary-light); }}
        .tab-btn.active {{
            color: var(--primary);
            border-bottom-color: var(--primary);
        }}
        
        .content {{
            max-width: 1100px;
            margin: 24px auto;
            padding: 0 16px;
        }}
        .tab-panel {{ display: none; }}
        .tab-panel.active {{ display: block; }}
        
        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border);
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.02);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 24px;
        }}
        .metric-card {{
            background: #f1f5f9;
            border-left: 4px solid var(--primary);
            padding: 16px;
            border-radius: 6px;
        }}
        .metric-card .val {{ font-size: 1.8rem; font-weight: 700; color: var(--primary); }}
        .metric-card .lbl {{ font-size: 0.85rem; color: var(--muted); text-transform: uppercase; font-weight: 600; }}
        
        table.data-table {{
            width: 100%;
            border-collapse: collapse;
            margin: 16px 0;
            font-size: 0.9rem;
        }}
        table.data-table th, table.data-table td {{
            padding: 10px 14px;
            border: 1px solid var(--border);
            text-align: left;
        }}
        table.data-table th {{ background: #f8fafc; color: var(--primary); font-weight: 600; }}
        table.data-table tr:nth-child(even) {{ background: #fafafa; }}
        
        .badge {{
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }}
        .badge-success {{ background: #dcfce7; color: #166534; }}
        .badge-warning {{ background: #fef9c3; color: #854d0e; }}
        
        .img-box {{ text-align: center; margin: 24px 0; }}
        .img-box img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }}
        .caption {{ font-size: 0.85rem; color: var(--muted); margin-top: 6px; font-style: italic; }}
        
        /* Calc interativa */
        .sim-box {{
            background: #eff6ff;
            border: 1px solid #bfdbfe;
            padding: 20px;
            border-radius: 8px;
            margin-top: 16px;
        }}
        .sim-box input {{
            padding: 8px 12px;
            border: 1px solid var(--border);
            border-radius: 4px;
            font-size: 1rem;
            width: 140px;
        }}
        code {{ background: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.88rem; }}
    </style>
</head>
<body>

    <div class="header">
        <h1>Central de Pesquisas Sidusfarma</h1>
        <p>Plataforma Analítica · DAMA-DMBOK · Indicadores · Documentação Integrada</p>
    </div>

    <!-- Navegação por Abas -->
    <div class="tabs-nav">
        <button class="tab-btn active" onclick="showTab('tab1', event)">📋 Scorecard DAMA</button>
        <button class="tab-btn" onclick="showTab('tab2', event)">📐 10 KPIs</button>
        <button class="tab-btn" onclick="showTab('tab3', event)">⚖️ Simulador N/D</button>
        <button class="tab-btn" onclick="showTab('tab4', event)">📈 Outliers</button>
        <button class="tab-btn" onclick="showTab('tab5', event)">✅ AP1 · Arqueologia</button>
        <button class="tab-btn" onclick="showTab('tab6', event)">🧪 AP2 · Lab Indicadores</button>
        <button class="tab-btn" onclick="showTab('tab7', event)">📄 Relatório Oficial (.md)</button>
    </div>

    <div class="content">

        <!-- ABA 1: DAMA Scorecard -->
        <div id="tab1" class="tab-panel active">
            <div class="card">
                <h2>Scorecard de Qualidade dos Dados (DAMA-DMBOK)</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="lbl">Completude Geral</div>
                        <div class="val">{completeness_pct}%</div>
                    </div>
                    <div class="metric-card">
                        <div class="lbl">Datasets Auditados</div>
                        <div class="val">{ds_count}</div>
                    </div>
                    <div class="metric-card">
                        <div class="lbl">Registros Órfãos (FK)</div>
                        <div class="val">5</div>
                    </div>
                    <div class="metric-card">
                        <div class="lbl">Linhas Duplicadas</div>
                        <div class="val">0</div>
                    </div>
                </div>

                <h3>Resumo por Dataset Auditado</h3>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Dataset</th>
                            <th>Registros</th>
                            <th>Colunas</th>
                            <th>Completude Média</th>
                            <th>Colunas 100% Nulas</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>clientes.csv</td><td>5.430</td><td>5</td><td>99,75%</td><td>0</td></tr>
                        <tr><td>empresas.csv</td><td>779</td><td>9</td><td>96,26%</td><td>0</td></tr>
                        <tr><td>pesquisas.csv</td><td>366</td><td>33</td><td>54,94%</td><td>11 (Unnamed)</td></tr>
                        <tr><td>questoes.csv</td><td>231</td><td>13</td><td>75,33%</td><td>1 (observacoes)</td></tr>
                        <tr><td>respondentes.csv</td><td>18.735</td><td>6</td><td>67,34%</td><td>0</td></tr>
                        <tr><td>respostas.csv</td><td>20.607</td><td>9</td><td>72,07%</td><td>0</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ABA 2: 10 KPIs -->
        <div id="tab2" class="tab-panel">
            <div class="card">
                <h2>Catálogo de 10 Indicadores de Negócio</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome do Indicador</th>
                            <th>Fórmula</th>
                            <th>Valor Apurado</th>
                            <th>Granularidade</th>
                        </tr>
                    </thead>
                    <tbody>
"""

for kpi in kpis_data.get("kpis", []):
    html_content += f"""
                        <tr>
                            <td><strong>{kpi['id']}</strong></td>
                            <td>{kpi['name']}</td>
                            <td><code>{kpi['formula']}</code></td>
                            <td><strong>{kpi['value']} {kpi['unit']}</strong></td>
                            <td>{kpi['granularity']}</td>
                        </tr>"""

html_content += f"""
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ABA 3: Simulador N/D -->
        <div id="tab3" class="tab-panel">
            <div class="card">
                <h2>Simulador de Sensibilidade de Denominadores (N/D)</h2>
                <p>A escolha da população de referência altera drasticamente o indicador de engajamento:</p>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="lbl">D1: Todas as Empresas (779)</div>
                        <div class="val">53,79%</div>
                        <p style="font-size:0.8rem; color:var(--muted); margin:4px 0 0 0;">KPI-05 · Indicador Conservador</p>
                    </div>
                    <div class="metric-card">
                        <div class="lbl">D2: Apenas Associadas (613)</div>
                        <div class="val">68,35%</div>
                        <p style="font-size:0.8rem; color:var(--muted); margin:4px 0 0 0;">KPI-06 · Base Estratégica (+14,56 p.p.)</p>
                    </div>
                </div>

                <div class="sim-box">
                    <h3>Calculadora Interativa N/D</h3>
                    <label>Numerador (Empresas Respondentes): </label>
                    <input type="number" id="numIn" value="419" oninput="calcND()">
                    &nbsp;&nbsp;
                    <label>Denominador (Universo de Referência): </label>
                    <input type="number" id="denIn" value="613" oninput="calcND()">
                    <br><br>
                    <div style="font-size: 1.3rem; font-weight: 700; color: var(--primary);">
                        Taxa de Adesão Resultante: <span id="resND">68.35</span>%
                    </div>
                </div>
            </div>
        </div>

        <!-- ABA 4: Outliers -->
        <div id="tab4" class="tab-panel">
            <div class="card">
                <h2>Análise e Tratamento de Outliers (Método IQR de Tukey)</h2>
                <p><em>"Outlier é um convite à investigação, não necessariamente uma ordem de exclusão."</em></p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Variável</th>
                            <th>N Válidos</th>
                            <th>Q1</th>
                            <th>Mediana</th>
                            <th>Q3</th>
                            <th>IQR</th>
                            <th>Limite Sup. (LS)</th>
                            <th>Outliers Sup.</th>
                            <th>Recomendação</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>participantes</td><td>335</td><td>40,0</td><td>54,0</td><td>70,0</td><td>30,0</td><td>115,0</td><td>19</td><td><span class="badge badge-success">Manter sem alteração</span></td></tr>
                        <tr><td>tempo_preenchimento (min)</td><td>231</td><td>3,0</td><td>5,0</td><td>7,0</td><td>4,0</td><td>13,0</td><td>12</td><td><span class="badge badge-warning">Sinalizar com flag</span></td></tr>
                        <tr><td>dias_uteis_para_entrega</td><td>331</td><td>13,5</td><td>19,0</td><td>25,0</td><td>11,5</td><td>42,25</td><td>18</td><td><span class="badge badge-warning">Investigar + Mediana SLA</span></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ABA 5: AP1 Checklist -->
        <div id="tab5" class="tab-panel">
            <div class="card">
                <h2>AP1 · Arqueologia das Bases — Cobertura dos 4 Requisitos</h2>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Requisito AP1</th>
                            <th>Status</th>
                            <th>Detalhamento e Localização</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td>2 Problemas/Riscos de Qualidade</td><td><span class="badge badge-success">✅ Atendido</span></td><td>R-01: Schema poluído (11 colunas Unnamed nulas). R-02: 5 FKs órfãs. §3.2 do relatório.</td></tr>
                        <tr><td>1 Possível Métrica</td><td><span class="badge badge-success">✅ Atendido</span></td><td>TCP_schema (Taxa de Completude Ponderada do Schema = 81,4%). §3.2 do relatório.</td></tr>
                        <tr><td>1 Pergunta Impossível em 1 Base</td><td><span class="badge badge-success">✅ Atendido</span></td><td>Adesão real por empresa × tema × tipo de associado × porte (requer JOIN de 3 bases). §1.2.</td></tr>
                        <tr><td>1 Chave para Relacionar Bases</td><td><span class="badge badge-success">✅ Atendido</span></td><td>pesquisa_id (spine do modelo relacional entre pesquisas, respondentes e respostas). §2.1.</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ABA 6: AP2 Lab Indicadores -->
        <div id="tab6" class="tab-panel">
            <div class="card">
                <h2>AP2 · Laboratório de Indicadores — Fichas Matemáticas</h2>
                <p>Especificação completa com os 9 elementos formais requeridos pela atividade:</p>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Elemento da Ficha</th>
                            <th>KPI-02 (Taxa Conclusão)</th>
                            <th>KPI-06 (Adesão Associadas)</th>
                            <th>KPI-08 (Tempo Entrega)</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td><strong>Pergunta de Negócio</strong></td><td>Qual a efetividade operacional da Central?</td><td>Qual a taxa de adesão da base estratégica?</td><td>Qual o tempo médio de entrega dos relatórios?</td></tr>
                        <tr><td><strong>Unidade de Análise</strong></td><td>Pesquisa (pesquisas.csv)</td><td>Empresa Associada (empresas.csv)</td><td>Pesquisa Concluída</td></tr>
                        <tr><td><strong>Fórmula</strong></td><td><code>(Finalizadas / Total) * 100</code></td><td><code>(Respondentes / 613) * 100</code></td><td><code>MEAN(dias_uteis_para_entrega)</code></td></tr>
                        <tr><td><strong>Valor Apurado</strong></td><td><strong>90,71%</strong></td><td><strong>68,35%</strong></td><td><strong>21,11 dias úteis</strong></td></tr>
                        <tr><td><strong>Limitações</strong></td><td>Não registra cancelamentos explicitamente</td><td>'Ter respondido' ≠ engajamento contínuo</td><td>Média inflada por outliers (usar mediana 19d)</td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ABA 7: Relatorio MD -->
        <div id="tab7" class="tab-panel">
            <div class="card">
                {report_html}
            </div>
        </div>

    </div>

    <script>
        function showTab(tabId, evt) {{
            document.querySelectorAll('.tab-panel').forEach(el => el.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(el => el.classList.remove('active'));
            
            document.getElementById(tabId).classList.add('active');
            evt.currentTarget.classList.add('active');
        }}
        function calcND() {{
            const num = parseFloat(document.getElementById('numIn').value) || 0;
            const den = parseFloat(document.getElementById('denIn').value) || 1;
            const res = ((num / den) * 100).toFixed(2);
            document.getElementById('resND').innerText = res;
        }}
    </script>
</body>
</html>"""

with open(OUT_HTML, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Plataforma Completa HTML gerada em: {OUT_HTML}")
