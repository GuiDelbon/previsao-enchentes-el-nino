"""
02_processar_inmet.py
Processa e consolida os dados meteorológicos horários das estações automáticas
do INMET na cidade de São Paulo (A701 Mirante de Santana e A771 Interlagos).
Descarta explicitamente os arquivos da estação A302 (Arquipélago de São Pedro e São Paulo - RN).
Gera série diária com precipitação acumulada, chuva máxima horária, temperatura e umidade.
"""

import os
import glob
import pandas as pd
import numpy as np

def processar_inmet():
    inmet_dir = os.path.join("dados", "brutos", "inmet")
    output_path = os.path.join("dados", "processados", "inmet_sp_diario.csv")
    
    # Encontrar todos os arquivos CSV do INMET
    csv_files = glob.glob(os.path.join(inmet_dir, "**", "*.CSV"), recursive=True) + \
                glob.glob(os.path.join(inmet_dir, "**", "*.csv"), recursive=True)
    
    print(f"Total de arquivos encontrados em {inmet_dir}: {len(csv_files)}")
    
    sp_station_codes = ["A701", "A771"]
    dfs = []
    
    for fpath in csv_files:
        fname = os.path.basename(fpath).upper()
        # Verificar se é estação de São Paulo
        if any(code in fname for code in sp_station_codes):
            station_code = "A701" if "A701" in fname else "A771"
            print(f"Processando estação SP: {station_code} | Arquivo: {fname}")
            
            try:
                # Ler com skiprows=8 para pular metadados do cabeçalho
                df = pd.read_csv(fpath, sep=";", skiprows=8, encoding="latin1", decimal=",")
                
                # Identificar coluna de data e precipitação
                cols = df.columns
                col_data = [c for c in cols if "DATA" in c.upper()][0]
                col_chuva = [c for c in cols if "PRECIPITA" in c.upper()][0]
                
                # Colunas de temperatura e umidade
                col_temp = [c for c in cols if "TEMPERATURA DO AR - BULBO SECO" in c.upper()]
                col_umid = [c for c in cols if "UMIDADE RELATIVA DO AR, HORARIA" in c.upper()]
                
                # Tratar valores -9999 comuns no INMET como NaN
                df[col_chuva] = pd.to_numeric(df[col_chuva], errors="coerce").replace(-9999, np.nan)
                df[col_chuva] = df[col_chuva].apply(lambda x: x if x >= 0 else np.nan)
                
                # Padronizar formato da data (YYYY-MM-DD)
                df["data_limpa"] = pd.to_datetime(df[col_data].astype(str).str.replace("/", "-"), errors="coerce")
                df = df.dropna(subset=["data_limpa"])
                
                agg_dict = {
                    col_chuva: ["sum", "max", "count"]
                }
                
                if col_temp:
                    c_t = col_temp[0]
                    df[c_t] = pd.to_numeric(df[c_t], errors="coerce").replace(-9999, np.nan)
                    agg_dict[c_t] = ["mean", "max", "min"]
                    
                if col_umid:
                    c_u = col_umid[0]
                    df[c_u] = pd.to_numeric(df[c_u], errors="coerce").replace(-9999, np.nan)
                    agg_dict[c_u] = "mean"
                
                daily = df.groupby("data_limpa").agg(agg_dict)
                daily.columns = ['_'.join(c).strip() for c in daily.columns]
                daily = daily.reset_index()
                
                # Renomear colunas
                rename_map = {
                    "data_limpa": "data",
                    f"{col_chuva}_sum": "precipitacao_total_mm",
                    f"{col_chuva}_max": "precipitacao_max_horaria_mm",
                    f"{col_chuva}_count": "horas_com_leitura"
                }
                if col_temp:
                    rename_map[f"{col_temp[0]}_mean"] = "temp_media_c"
                    rename_map[f"{col_temp[0]}_max"] = "temp_max_c"
                    rename_map[f"{col_temp[0]}_min"] = "temp_min_c"
                if col_umid:
                    rename_map[f"{col_umid[0]}_mean"] = "umidade_relativa_media"
                    
                daily = daily.rename(columns=rename_map)
                daily["estacao"] = station_code
                dfs.append(daily)
                
            except Exception as e:
                print(f"Erro ao processar {fpath}: {e}")
                
        elif "A302" in fname:
            print(f"Descartando A302 (Arquipélago SP/RN - fora do escopo de SP): {fname}")
        else:
            print(f"Arquivo ignorado: {fname}")

    if not dfs:
        raise ValueError("Nenhum dado válido de São Paulo foi processado!")

    all_inmet = pd.concat(dfs, ignore_index=True)
    all_inmet["data"] = pd.to_datetime(all_inmet["data"])
    
    # Consolidar média/máxima diária das estações de São Paulo
    consolidado = all_inmet.groupby("data").agg({
        "precipitacao_total_mm": "mean",
        "precipitacao_max_horaria_mm": "max",
        "temp_media_c": "mean",
        "temp_max_c": "max",
        "temp_min_c": "min",
        "umidade_relativa_media": "mean"
    }).reset_index()

    consolidado["ano"] = consolidado["data"].dt.year
    consolidado["mes"] = consolidado["data"].dt.month
    consolidado["dia"] = consolidado["data"].dt.day
    consolidado["data"] = consolidado["data"].dt.strftime("%Y-%m-%d")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    consolidado.to_csv(output_path, index=False)
    print(f"\nSucesso: {len(consolidado)} dias consolidados salvos em {output_path}")
    print(consolidado.head())

if __name__ == "__main__":
    processar_inmet()
