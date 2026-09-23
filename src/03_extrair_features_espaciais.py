"""
03_extrair_features_espaciais.py
Módulo para extração de variáveis geoespaciais condicionantes:
1. Altitude (Elevação em metros a partir do SRTM 30m)
2. Declividade (Slope em graus e porcentagem usando algoritmo de Horn)
3. Distância euclidiana ao eixo de drenagem mais próximo (a partir do GeoSampa)
"""

import os
import json
import math
import numpy as np
import tifffile as tiff
from scipy.spatial import cKDTree

class SRTMExtractor:
    def __init__(self, tif_path):
        if not os.path.exists(tif_path):
            raise FileNotFoundError(f"Arquivo SRTM não encontrado: {tif_path}")
        self.data = tiff.imread(tif_path)
        self.rows, self.cols = self.data.shape  # 3601 x 3601
        self.lat_north = -23.0
        self.lat_south = -24.0
        self.lon_west = -47.0
        self.lon_east = -46.0
        
        # Resolução em metros aproximada para Horn's method (em ~23.5°S)
        self.dx = 28.2  # metros por arco-segundo em longitude
        self.dy = 30.8  # metros por arco-segundo em latitude

    def get_indices(self, lat, lon):
        r = int(round((self.lat_north - lat) / 1.0 * (self.rows - 1)))
        c = int(round((lon - self.lon_west) / 1.0 * (self.cols - 1)))
        r = max(1, min(self.rows - 2, r))
        c = max(1, min(self.cols - 2, c))
        return r, c

    def get_elevation(self, lat, lon):
        r, c = self.get_indices(lat, lon)
        elev = float(self.data[r, c])
        return elev if elev > -100 else np.nan

    def get_slope(self, lat, lon):
        r, c = self.get_indices(lat, lon)
        # Horn's 3x3 window method
        z = self.data[r-1:r+2, c-1:c+2].astype(float)
        dz_dx = ((z[0, 2] + 2*z[1, 2] + z[2, 2]) - (z[0, 0] + 2*z[1, 0] + z[2, 0])) / (8.0 * self.dx)
        dz_dy = ((z[2, 0] + 2*z[2, 1] + z[2, 2]) - (z[0, 0] + 2*z[0, 1] + z[0, 2])) / (8.0 * self.dy)
        
        slope_rad = math.atan(math.sqrt(dz_dx**2 + dz_dy**2))
        slope_deg = math.degrees(slope_rad)
        slope_pct = math.tan(slope_rad) * 100.0
        return slope_deg, slope_pct

class DrainageExtractor:
    def __init__(self, geojson_path):
        if not os.path.exists(geojson_path):
            raise FileNotFoundError(f"Arquivo GeoSampa de drenagem não encontrado: {geojson_path}")
        
        with open(geojson_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        points = []
        for feat in data.get("features", []):
            geom = feat.get("geometry", {})
            gtype = geom.get("type", "")
            coords = geom.get("coordinates", [])
            
            if gtype == "LineString":
                for pt in coords:
                    points.append(pt[:2])
            elif gtype == "MultiLineString":
                for line in coords:
                    for pt in line:
                        points.append(pt[:2])
            elif gtype == "Point":
                points.append(coords[:2])
                
        if not points:
            raise ValueError("Nenhuma coordenada de drenagem extraída!")
            
        pts_np = np.array(points)  # [ [lon, lat], ... ]
        # Converter para coordenadas métricas centradas em SP (-23.55, -46.63)
        self.ref_lat = -23.55
        self.ref_lon = -46.63
        self.m_per_deg_lat = 110800.0
        self.m_per_deg_lon = 102000.0
        
        x_m = (pts_np[:, 0] - self.ref_lon) * self.m_per_deg_lon
        y_m = (pts_np[:, 1] - self.ref_lat) * self.m_per_deg_lat
        
        self.tree = cKDTree(np.column_stack([x_m, y_m]))
        print(f"Extrator de drenagem inicializado com {len(points)} nós de rede.")

    def get_distance_to_drainage(self, lat, lon):
        x = (lon - self.ref_lon) * self.m_per_deg_lon
        y = (lat - self.ref_lat) * self.m_per_deg_lat
        dist_m, _ = self.tree.query([x, y])
        return float(dist_m)

if __name__ == "__main__":
    srtm = SRTMExtractor(os.path.join("dados", "brutos", "srtm", "S24W047.tif"))
    drainage = DrainageExtractor(os.path.join("dados", "brutos", "geosampa", "drenagem_sp.geojson"))
    
    # Teste no marco zero de SP (Praça da Sé)
    test_lat, test_lon = -23.5505, -46.6333
    elev = srtm.get_elevation(test_lat, test_lon)
    s_deg, s_pct = srtm.get_slope(test_lat, test_lon)
    dist_d = drainage.get_distance_to_drainage(test_lat, test_lon)
    
    print("\n--- Teste de Validação Geoespacial (Praça da Sé) ---")
    print(f"Coordenadas: Lat {test_lat}, Lon {test_lon}")
    print(f"Altitude: {elev:.1f} m")
    print(f"Declividade: {s_deg:.2f}° ({s_pct:.1f}%)")
    print(f"Distância ao curso d'água mais próximo: {dist_d:.1f} m")
