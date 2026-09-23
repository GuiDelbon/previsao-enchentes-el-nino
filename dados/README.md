# Dados do Projeto: Predição de Suscetibilidade a Enchentes em São Paulo

Esta pasta reúne as bases de dados brutas e processadas utilizadas nos experimentos de suscetibilidade e previsão espacial de enchentes no **Município de São Paulo**, comparando períodos de **El Niño** e períodos não associados ao fenômeno.

---

## Estrutura de Diretórios

```text
dados/
├── README.md                          # Este documento descritivo
├── brutos/
│   ├── cge/
│   │   └── all_floods_cge_sp.csv      # Inventário histórico de alagamentos CGE (1.165 ocorrências)
│   ├── geosampa/
│   │   └── drenagem_sp.geojson        # Eixos e canais de drenagem da Prefeitura de SP
│   ├── inmet/                         # Dados horários das estações A701 (Mirante) e A771 (Interlagos)
│   ├── oni/
│   │   └── oni_ersstv6.html           # Série histórica oficial do ONI (NOAA/CPC)
│   └── srtm/
│       └── S24W047.tif                # Modelo Digital de Elevação SRTM GL1 30m
├── processados/
│   ├── inmet_sp_diario.csv            # Série meteorológica diária consolidada para SP (2019-2026)
│   ├── oni_mensal_classificado.csv    # Série mensal ONI com rotulação El Niño vs Não-El Niño
│   └── dataset_suscetibilidade_sp.csv # Dataset final integrado para treinamento de ML (2.330 registros)
└── metadados/
    └── README.md                      # Fichas técnicas e dicionário de metadados das bases
```

---

## Fontes e Bases de Dados

| Base | Instituição / Origem | Recorte | Formato | Status |
| :--- | :--- | :--- | :--- | :--- |
| **Inventário de Alagamentos (Classe 1)** | CGE / Defesa Civil de São Paulo | Município de SP | CSV (`all_floods_cge_sp.csv`) | **Coletado e Integrado** |
| **Topografia (SRTM GL1 30m)** | NASA / USGS / OpenTopography | Tile `S24W047` | GeoTIFF (`S24W047.tif`) | **Coletado e Integrado** |
| **Rede de Drenagem** | GeoSampa (Prefeitura de SP) | Município de SP | GeoJSON (`drenagem_sp.geojson`) | **Coletado e Integrado** |
| **Índice Climático ONI** | NOAA / CPC (ERSSTv6) | Global / Pacíﬁco Nino 3.4 | HTML / CSV | **Coletado e Integrado** |
| **Meteorologia / Pluviometria** | INMET (A701 e A771) | São Paulo (Capital) | CSV | **Coletado e Integrado** |

> **Nota Metodológica sobre o INMET:** Os arquivos da estação `A302` presentes no histórico bruto correspondem ao Arquipélago de São Pedro e São Paulo (RN) e foram descartados no processamento. Apenas as estações `A701` (Mirante de Santana) e `A771` (Interlagos) foram utilizadas na consolidação.

---

## Regras de Processamento e Engenharia de Atributos

1. **Variável Alvo (`alvo_alagamento`)**:
   * **Classe 1 (Alagamento)**: 1.165 registros de alagamento do CGE ocorridos na cidade de São Paulo, contendo coordenadas geográficas, data, hora e duração.
   * **Classe 0 (Controle / Pseudo-Ausência)**: 1.165 pontos amostrados com filtros físicos restritivos: cota altimétrica $> 765$ m (acima da planície aluvial), declividade $> 2{,}5^\circ$, distância $> 200$ m de canais de drenagem e distância $> 300$ m de pontos históricos de alagamento.
2. **Variáveis Topográficas**:
   * **Altitude**: Extraída pontualmente da grade regular SRTM 30m.
   * **Declividade (Slope)**: Calculada pelo algoritmo diferencial de Horn (janela $3 \times 3$) em graus e percentual.
3. **Variável Hidrográfica**:
   * **Distância ao rio (`distancia_rio_m`)**: Distância euclidiana mínima aos vértices da rede de drenagem municipal calculada via árvore espacial `cKDTree`.
4. **Classificação Climática (ONI)**:
   * Meses com anomalia $\ge +0{,}5$ °C classificados como `El Nino`.
   * Meses com anomalia $< +0{,}5$ °C classificados como `Nao El Nino`.
5. **Variáveis Pluviométricas**:
   * Precipitação acumulada diária e intensidade horária máxima registradas no dia do evento pelas estações do INMET.

---

## Como Reproduzir o Pipeline

Execute os scripts em ordem a partir da raiz do repositório:

```bash
# 1. Processar o índice ONI da NOAA
python src/01_processar_oni.py

# 2. Consolidar as leituras diárias do INMET (Mirante e Interlagos)
python src/02_processar_inmet.py

# 3. Construir o dataset final de modelagem (unindo CGE, SRTM, GeoSampa e clima)
python src/04_construir_dataset.py

# 4. Treinar os modelos Random Forest (Geral, El Niño e Não-El Niño)
python src/05_treinar_random_forest.py
```
