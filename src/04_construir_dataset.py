"""
04_construir_dataset.py
Constrói o dataset consolidado para modelagem de suscetibilidade a enchentes:
- Carrega as 1.165 ocorrências históricas de alagamento do CGE (Classe 1).
- Gera 1.165 pontos pseudo-aleatórios de não-enchente com filtros físicos (Classe 0).
- Extrai as features geoespaciais (Altitude, Declividade, Distância à Drenagem).
- Cruza com o índice ONI (cenário El Niño vs. Não-El Niño).
- Cruza com os dados pluviométricos e meteorológicos do INMET São Paulo.
- Salva o dataset final em dados/processados/dataset_suscetibilidade_sp.csv.
"""

import os
import sys
import random
import numpy as np
import pandas as pd
from scipy.spatial import cKDTree

# Adiciona tanto o diretório 'src' quanto a raiz do repositório ao sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.dirname(__file__))

try:
    from extrair_features_espaciais import SRTMExtractor, DrainageExtractor
except ModuleNotFoundError:
    from src.extrair_features_espaciais import SRTMExtractor, DrainageExtractor

def construir_dataset():
    random.seed(42)
    np.random.seed(42)

    cge_path = os.path.join("dados", "brutos", "cge", "all_floods_cge_sp.csv")
    srtm_path = os.path.join("dados", "brutos", "srtm", "S24W047.tif")
    drainage_path = os.path.join("dados", "brutos", "geosampa", "drenagem_sp.geojson")
    oni_path = os.path.join("dados", "processados", "oni_mensal_classificado.csv")
    inmet_path = os.path.join("dados", "processados", "inmet_sp_diario.csv")
    output_path = os.path.join("dados", "processados", "dataset_suscetibilidade_sp.csv")

    print("1. Carregando extratores espaciais e bases climáticas...")
    srtm = SRTMExtractor(srtm_path)
    drainage = DrainageExtractor(drainage_path)
    df_oni = pd.read_csv(oni_path)
    df_inmet = pd.read_csv(inmet_path)

    # Dicionário de ONI por (ano, mes)
    oni_dict = {}
    for _, row in df_oni.iterrows():
        oni_dict[(int(row["ano"]), int(row["mes"]))] = {
            "valor_oni": row["valor_oni"],
            "cenario_climatico": row["cenario_climatico"]
        }

    # Dicionário do INMET por data YYYY-MM-DD
    inmet_dict = {}
    for _, row in df_inmet.iterrows():
        inmet_dict[str(row["data"])] = {
            "precipitacao_total_mm": row["precipitacao_total_mm"],
            "precipitacao_max_horaria_mm": row["precipitacao_max_horaria_mm"],
            "temp_media_c": row["temp_media_c"],
            "umidade_relativa_media": row["umidade_relativa_media"]
        }

    print("\n2. Processando Classe 1 (Ocorrências de Alagamento CGE)...")
    df_cge = pd.read_csv(cge_path)
    
    # Padronizar datas
    df_cge["data_formatada"] = pd.to_datetime(df_cge["DATA"].astype(str).str.replace("/", "-"), errors="coerce")
    df_cge = df_cge.dropna(subset=["data_formatada", "LAT", "LONG"])
    
    flood_points = []
    flood_coords = []
    
    for idx, row in df_cge.iterrows():
        lat = float(row["LAT"])
        lon = float(row["LONG"])
        dt = row["data_formatada"]
        ano = dt.year
        mes = dt.month
        data_str = dt.strftime("%Y-%m-%d")
        
        elev = srtm.get_elevation(lat, lon)
        s_deg, s_pct = srtm.get_slope(lat, lon)
        dist_d = drainage.get_distance_to_drainage(lat, lon)
        
        clima = oni_dict.get((ano, mes), {"valor_oni": 0.0, "cenario_climatico": "Nao El Nino"})
        meteo = inmet_dict.get(data_str, {
            "precipitacao_total_mm": 0.0,
            "precipitacao_max_horaria_mm": 0.0,
            "temp_media_c": 20.0,
            "umidade_relativa_media": 75.0
        })
        
        flood_points.append({
            "ponto_id": f"FLOOD_{idx:05d}",
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "data": data_str,
            "ano": ano,
            "mes": mes,
            "duracao_horas": row.get("DUR_H", 1.0),
            "local_referencia": str(row.get("LOCAL_ED", "")),
            "alvo_alagamento": 1,
            "altitude_m": round(elev, 1),
            "declividade_graus": round(s_deg, 2),
            "declividade_pct": round(s_pct, 2),
            "distancia_rio_m": round(dist_d, 1),
            "valor_oni": clima["valor_oni"],
            "cenario_climatico": clima["cenario_climatico"],
            "precipitacao_dia_mm": round(meteo["precipitacao_total_mm"], 1),
            "precipitacao_max_hora_mm": round(meteo["precipitacao_max_horaria_mm"], 1),
            "temp_media_c": round(meteo["temp_media_c"], 1),
            "umidade_relativa_media": round(meteo["umidade_relativa_media"], 1)
        })
        flood_coords.append([lon, lat])

    n_floods = len(flood_points)
    print(f"Total de pontos de alagamento processados (Classe 1): {n_floods}")

    print("\n3. Gerando Classe 0 (Pseudo-ausências com regras físicas em São Paulo)...")
    # Árvore espacial das coordenadas de enchente para evitar vizinhança imediata
    flood_tree = cKDTree(np.array(flood_coords))

    # Bounding box operacional de SP
    min_lat, max_lat = -23.75, -23.42
    min_lon, max_lon = -46.78, -46.42

    non_flood_points = []
    tentativas = 0
    max_tentativas = 200000

    # Pool de datas históricas de 2019 para associar às pseudo-ausências
    datas_pool = list(df_cge["data_formatada"].dt.strftime("%Y-%m-%d").unique())

    while len(non_flood_points) < n_floods and tentativas < max_tentativas:
        tentativas += 1
        cand_lat = random.uniform(min_lat, max_lat)
        cand_lon = random.uniform(min_lon, max_lon)

        # Regra 1: Distância mínima de qualquer ponto de alagamento (evitar falsos negativos)
        # 0.003 graus ~ 330 metros
        dist_nn, _ = flood_tree.query([cand_lon, cand_lat])
        if dist_nn < 0.003:
            continue

        # Regra 2: Distância à drenagem > 200 metros
        dist_d = drainage.get_distance_to_drainage(cand_lat, cand_lon)
        if dist_d < 200.0:
            continue

        # Regra 3: Topografia de área alta / encosta (onde não há estagnação de água)
        elev = srtm.get_elevation(cand_lat, cand_lon)
        if elev < 765.0:  # Acima da cota de várzea dos rios Tietê, Pinheiros e Tamanduateí (~720-740m)
            continue

        s_deg, s_pct = srtm.get_slope(cand_lat, cand_lon)
        if s_deg < 2.5:  # Terrenos perfeitamente planos em baixada têm risco de poças; morros/encostas drenam
            continue

        # Selecionar data do pool para vincular variáveis dinâmicas
        data_str = random.choice(datas_pool)
        dt = pd.to_datetime(data_str)
        ano, mes = dt.year, dt.month

        clima = oni_dict.get((ano, mes), {"valor_oni": 0.0, "cenario_climatico": "Nao El Nino"})
        meteo = inmet_dict.get(data_str, {
            "precipitacao_total_mm": 0.0,
            "precipitacao_max_horaria_mm": 0.0,
            "temp_media_c": 20.0,
            "umidade_relativa_media": 75.0
        })

        non_flood_points.append({
            "ponto_id": f"NOFLOOD_{len(non_flood_points):05d}",
            "latitude": round(cand_lat, 6),
            "longitude": round(cand_lon, 6),
            "data": data_str,
            "ano": ano,
            "mes": mes,
            "duracao_horas": 0.0,
            "local_referencia": "Ponto de Controle Pseudo-Ausencia SP",
            "alvo_alagamento": 0,
            "altitude_m": round(elev, 1),
            "declividade_graus": round(s_deg, 2),
            "declividade_pct": round(s_pct, 2),
            "distancia_rio_m": round(dist_d, 1),
            "valor_oni": clima["valor_oni"],
            "cenario_climatico": clima["cenario_climatico"],
            "precipitacao_dia_mm": round(meteo["precipitacao_total_mm"], 1),
            "precipitacao_max_hora_mm": round(meteo["precipitacao_max_horaria_mm"], 1),
            "temp_media_c": round(meteo["temp_media_c"], 1),
            "umidade_relativa_media": round(meteo["umidade_relativa_media"], 1)
        })

    print(f"Total de pontos de não-alagamento gerados (Classe 0): {len(non_flood_points)}")

    # Unir e embaralhar
    todos_pontos = flood_points + non_flood_points
    random.shuffle(todos_pontos)

    df_final = pd.DataFrame(todos_pontos)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_final.to_csv(output_path, index=False)

    print(f"\n==================================================================")
    print(f"Dataset de Suscetibilidade a Enchentes criado com SUCESSO!")
    print(f"Caminho: {output_path}")
    print(f"Total de registros: {len(df_final)}")
    print(f"Distribuição de Classes: \n{df_final['alvo_alagamento'].value_counts()}")
    print(f"Distribuição de Cenários Climáticos: \n{df_final['cenario_climatico'].value_counts()}")
    print(f"Médias comparativas:")
    print(df_final.groupby("alvo_alagamento")[["altitude_m", "declividade_graus", "distancia_rio_m", "precipitacao_dia_mm"]].mean())
    print(f"==================================================================")

if __name__ == "__main__":
    construir_dataset()
