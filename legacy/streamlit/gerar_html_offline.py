"""
Converte docs/modelagem_quantitativa_de_dados_do_parceiro.md em um arquivo HTML único e autônomo:
legacy/streamlit/relatorio_offline.html
- Estilos CSS limpos e responsivos (leitura perfeita no celular)
- Imagens PNG convertidas para Base64 inline
- Funciona 100% offline sem nenhum servidor
"""
import os
import sys
import re
import base64

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MD_PATH  = os.path.join(BASE_DIR, "docs", "modelagem_quantitativa_de_dados_do_parceiro.md")
HTML_OUT = os.path.join(BASE_DIR, "legacy", "streamlit", "relatorio_offline.html")
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def md_to_html(md_text):
    # Trata cabeçalhos
    md_text = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', md_text, flags=re.M)
    md_text = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', md_text, flags=re.M)
    md_text = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', md_text, flags=re.M)
    md_text = re.sub(r'^#### (.*?)$', r'<h4>\1</h4>', md_text, flags=re.M)
    
    # Formatação básica
    md_text = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', md_text)
    md_text = re.sub(r'\*(.*?)\*', r'<em>\1</em>', md_text)
    md_text = re.sub(r'`(.*?)`', r'<code>\1</code>', md_text)
    
    # Linha horizontal
    md_text = re.sub(r'^---$', r'<hr>', md_text, flags=re.M)

    # Imagens -> Base64
    def replace_img(match):
        alt = match.group(1)
        src = match.group(2)
        possible_paths = [
            os.path.join(DOCS_DIR, src),
            os.path.join(BASE_DIR, src),
            os.path.join(DOCS_DIR, "images", os.path.basename(src))
        ]
        for p in possible_paths:
            if os.path.exists(p):
                with open(p, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode('utf-8')
                return f'<div class="img-container"><img src="data:image/png;base64,{b64}" alt="{alt}"><p class="caption">{alt}</p></div>'
        return f'<p><em>[Imagem: {alt}]</em></p>'

    md_text = re.sub(r'!\[(.*?)\]\((.*?)\)', replace_img, md_text)

    # Converter tabelas Markdown em HTML
    lines = md_text.split('\n')
    in_table = False
    new_lines = []
    
    for line in lines:
        if line.strip().startswith('|') and line.strip().endswith('|'):
            if '---' in line:
                continue
            cells = [c.strip() for c in line.strip().split('|')[1:-1]]
            if not in_table:
                in_table = True
                new_lines.append('<table><thead><tr>' + ''.join(f'<th>{c}</th>' for c in cells) + '</tr></thead><tbody>')
            else:
                new_lines.append('<tr>' + ''.join(f'<td>{c}</td>' for c in cells) + '</tr>')
        else:
            if in_table:
                in_table = False
                new_lines.append('</tbody></table>')
            new_lines.append(line)
            
    if in_table:
        new_lines.append('</tbody></table>')
        
    content_html = '\n'.join(new_lines)
    
    # Parágrafos simples
    content_html = re.sub(r'\n\n+', '</p><p>', content_html)
    
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modelagem Quantitativa — Sidusfarma</title>
    <style>
        :root {{
            --primary: #1e3a8a;
            --text: #1e293b;
            --bg: #f8fafc;
            --card-bg: #ffffff;
            --border: #e2e8f0;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            line-height: 1.6;
            color: var(--text);
            background-color: var(--bg);
            margin: 0;
            padding: 16px;
        }}
        .container {{
            max-width: 900px;
            margin: 0 auto;
            background: var(--card-bg);
            padding: 24px;
            border-radius: 12px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        }}
        h1 {{ color: var(--primary); font-size: 1.8rem; margin-top: 0; border-bottom: 2px solid var(--border); padding-bottom: 8px; }}
        h2 {{ color: var(--primary); font-size: 1.4rem; margin-top: 24px; border-bottom: 1px solid var(--border); padding-bottom: 6px; }}
        h3 {{ font-size: 1.15rem; color: #334155; margin-top: 18px; }}
        p {{ margin-bottom: 16px; font-size: 0.98rem; }}
        hr {{ border: none; border-top: 1px solid var(--border); margin: 24px 0; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9rem; overflow-x: auto; display: block; }}
        th, td {{ padding: 10px 12px; border: 1px solid var(--border); text-align: left; }}
        th {{ background-color: #f1f5f9; color: var(--primary); font-weight: 600; }}
        tr:nth-child(even) {{ background-color: #f8fafc; }}
        code {{ background-color: #f1f5f9; padding: 2px 6px; border-radius: 4px; font-family: monospace; font-size: 0.88rem; color: #0f172a; }}
        .img-container {{ text-align: center; margin: 24px 0; }}
        .img-container img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); }}
        .caption {{ font-size: 0.85rem; color: #64748b; margin-top: 6px; font-style: italic; }}
        details {{ background: #f8fafc; border: 1px solid var(--border); padding: 12px; border-radius: 6px; margin: 16px 0; }}
        summary {{ font-weight: 600; cursor: pointer; color: var(--primary); }}
    </style>
</head>
<body>
    <div class="container">
        {content_html}
    </div>
</body>
</html>"""
    return html

with open(MD_PATH, "r", encoding="utf-8") as f:
    md_content = f.read()

html_output = md_to_html(md_content)

with open(HTML_OUT, "w", encoding="utf-8") as f:
    f.write(html_output)

print(f"✅ HTML offline gerado com sucesso em: {HTML_OUT}")
