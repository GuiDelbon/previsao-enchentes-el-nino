# Metadados das Bases Coletadas

Este documento registra as informações de proveniência, parâmetros técnicos e transformações aplicadas a cada base de dados integrada ao projeto.

---

## 1. Inventário de Alagamentos (CGE São Paulo)

### Identificação do conjunto
- **Nome da base:** Pontos Históricos de Alagamento - São Paulo
- **Instituição responsável:** Centro de Gerenciamento de Emergências Climáticas (CGE / PMSP)
- **URL da página de origem:** https://www.cgesp.org/
- **Arquivos no repositório:** `dados/brutos/cge/all_floods_cge_sp.csv`
- **Período coberto:** 2019 (série consolidada)
- **Recorte geográfico:** Município de São Paulo, SP (Latitude: -23.40 a -23.84; Longitude: -46.38 a -46.79)
- **Formato e codificação:** CSV, UTF-8, delimitador vírgula
- **Variáveis e unidades:**
  - `SEQ`: Identificador da ocorrência
  - `LONG`, `LAT`: Coordenadas geográficas (WGS84, graus decimais)
  - `LOCAL_ED`: Logradouro / Cruzamento
  - `DATA`: Data da ocorrência (YYYY/MM/DD)
  - `H_INICIO`, `H_FIM`: Horários de início e término do alagamento
  - `DUR_H`: Duração do alagamento em horas

---

## 2. Topografia e Relevo (SRTM 30m)

### Identificação do conjunto
- **Nome da base:** Shuttle Radar Topography Mission (SRTM GL1 30m)
- **Instituição responsável:** NASA / USGS / OpenTopography
- **URL da página de origem:** https://opentopography.org/
- **URL de download:** https://opentopography.s3.sdsc.edu/raster/SRTM_GL1/SRTM_GL1_srtm/S24W047.tif
- **Versão da base:** SRTM GL1 (Global 1 arc-second ~ 30 metros)
- **Arquivos no repositório:** `dados/brutos/srtm/S24W047.tif`
- **Recorte geográfico:** Tile `S24W047` (Lat -23° a -24°; Lon -46° a -47°), cobrindo integralmente o município de São Paulo.
- **Formato:** Cloud Optimized GeoTIFF (COG), matriz 3601 x 3601 pixels, int16.
- **Variáveis derivadas no projeto:**
  - `altitude_m`: Elevação pontual do terreno em metros.
  - `declividade_graus` e `declividade_pct`: Declividade calculada pela derivada espacial de Horn (janela 3x3).

---

## 3. Rede de Drenagem e Hidrografia (GeoSampa)

### Identificação do conjunto
- **Nome da base:** Rede Hidrográfica e Drenagem do Município de São Paulo
- **Instituição responsável:** Prefeitura do Município de São Paulo (GeoSampa)
- **URL do serviço WFS:** `http://wfs.geosampa.prefeitura.sp.gov.br/geoserver/geoportal/wfs`
- **Camada WFS:** `geoportal:drenagem`
- **Arquivos no repositório:** `dados/brutos/geosampa/drenagem_sp.geojson`
- **Recorte geográfico:** Município de São Paulo
- **Formato:** GeoJSON, projeção WGS84 (EPSG:4326)
- **Variável derivada:**
  - `distancia_rio_m`: Distância euclidiana em metros do ponto ao curso d'água / canal mais próximo (indexado via `scipy.spatial.cKDTree`).

---

## 4. Índice Climatológico ONI (NOAA)

### Identificação do conjunto
- **Nome da base:** Oceanic Niño Index (ONI) - ERSSTv6
- **Instituição responsável:** National Oceanic and Atmospheric Administration (NOAA / CPC)
- **URL da página de origem:** https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/
- **Arquivos no repositório:**
  - Bruto: `dados/brutos/oni/oni_ersstv6.html`
  - Processado: `dados/processados/oni_mensal_classificado.csv`
- **Período coberto:** 1950 a 2026
- **Regra de classificação climática (Proposta Seção 3.3):**
  - `El Nino`: valor do índice $\ge +0{,}5$ °C.
  - `Nao El Nino`: valor do índice $< +0{,}5$ °C (Neutro / La Niña).

---

## 5. Estações Meteorológicas Automáticas (INMET)

### Identificação do conjunto
- **Nome da base:** Dados Históricos Meteorológicos Anuais
- **Instituição responsável:** Instituto Nacional de Meteorologia (INMET)
- **URL da página de origem:** https://portal.inmet.gov.br/dadoshistoricos
- **Estações selecionadas em São Paulo:**
  - `A701`: São Paulo - Mirante de Santana (Lat: -23.496294, Lon: -46.620088, Alt: 785.64m)
  - `A771`: São Paulo - Interlagos (Lat: -23.724504, Lon: -46.677519, Alt: 775.14m)
- **Atenção / Descarte de arquivos:**
  - Arquivos da estação `A302` (Arquipélago de São Pedro e São Paulo - RN) foram explicitamente ignorados pelo script de processamento.
- **Arquivo de saída processado:** `dados/processados/inmet_sp_diario.csv`
- **Variáveis consolidadas:**
  - `precipitacao_total_mm`: Chuva acumulada no dia (soma de 24 horas).
  - `precipitacao_max_horaria_mm`: Chuva máxima registrada em uma única hora no dia.
  - `temp_media_c`, `temp_max_c`, `temp_min_c`: Temperaturas do ar em °C.
  - `umidade_relativa_media`: Umidade relativa média diária (%).
