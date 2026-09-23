"""
01_processar_oni.py
Processa a série histórica do índice Oceanic Niño Index (ONI) da NOAA/CPC
a partir do arquivo bruto oni_ersstv6.html e gera a tabela mensal classificada.
Regra de segregação climática (proposta Seção 3.3):
- El Niño (Ativo): anomalia ONI >= +0.5 °C
- Não-El Niño (Neutro / La Niña): anomalia ONI < +0.5 °C
"""

import re
import os
import pandas as pd

def processar_oni():
    input_path = os.path.join("dados", "brutos", "oni", "oni_ersstv6.html")
    output_path = os.path.join("dados", "processados", "oni_mensal_classificado.csv")
    
    with open(input_path, "r", encoding="latin1") as f:
        content = f.read()

    tables = re.findall(r'<table.*?</table>', content, re.DOTALL | re.IGNORECASE)
    # Tabela 5 contém a matriz Year x Trimestres
    tabela_oni = tables[5]
    rows = re.findall(r'<tr.*?</tr>', tabela_oni, re.DOTALL | re.IGNORECASE)
    
    headers = ['Year', 'DJF', 'JFM', 'FMA', 'MAM', 'AMJ', 'MJJ', 'JJA', 'JAS', 'ASO', 'SON', 'OND', 'NDJ']
    
    records = []
    trimestres_mes = {
        'DJF': 1, 'JFM': 2, 'FMA': 3, 'MAM': 4,
        'AMJ': 5, 'MJJ': 6, 'JJA': 7, 'JAS': 8,
        'ASO': 9, 'SON': 10, 'OND': 11, 'NDJ': 12
    }
    
    for r in rows:
        cells = re.sub(r'<.*?>', ' ', r).split()
        if not cells or cells[0] == 'Year' or not cells[0].isdigit():
            continue
        ano = int(cells[0])
        valores = cells[1:]
        
        for idx, (tri, mes) in enumerate(trimestres_mes.items()):
            if idx < len(valores):
                val_str = valores[idx].replace(',', '.')
                try:
                    val = float(val_str)
                    cenario = "El Nino" if val >= 0.5 else "Nao El Nino"
                    detalhe = "El Nino" if val >= 0.5 else ("La Nina" if val <= -0.5 else "Neutro")
                    records.append({
                        "ano": ano,
                        "mes": mes,
                        "trimestre_oni": tri,
                        "valor_oni": val,
                        "cenario_climatico": cenario,
                        "classificacao_detalhada": detalhe
                    })
                except ValueError:
                    pass

    df = pd.DataFrame(records)
    df.sort_values(by=["ano", "mes"], inplace=True)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Sucesso: {len(df)} registros mensais de ONI processados e salvos em {output_path}")
    print(df.tail(15))

if __name__ == "__main__":
    processar_oni()
