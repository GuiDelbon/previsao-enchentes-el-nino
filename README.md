# Desenvolvimento e comparação de modelos de aprendizado de máquina para previsão de enchentes em períodos de El Niño e períodos não associados ao fenômeno

**Comparação de modelos de aprendizado de máquina em períodos com e sem El Niño.**

Projeto acadêmico desenvolvido na disciplina **Resolução de Problemas II**, da **Escola de Artes, Ciências e Humanidades da Universidade de São Paulo (EACH-USP)**.

> **Status:** proposta inicial de pesquisa. Este README apresenta o escopo e a metodologia planejada na primeira versão do projeto. Resultados experimentais e instruções de execução serão adicionados conforme o desenvolvimento.

## Sobre o projeto

As enchentes urbanas afetam a Região Metropolitana de São Paulo (RMSP) e estão relacionadas a fatores como características do terreno, uso do solo e condições climáticas. Este projeto propõe investigar como a suscetibilidade espacial a enchentes e a importância dos fatores associados variam entre períodos de El Niño e períodos não associados ao fenômeno.

Para isso, serão desenvolvidos e comparados modelos **Random Forest** e **XGBoost**, combinando registros históricos de inundação e variáveis geoespaciais. A interpretação dos modelos será realizada com **SHAP**, buscando compreender a contribuição das variáveis em cada cenário climático.

O foco do estudo é o **mapeamento de áreas suscetíveis a enchentes** na RMSP.

## Pergunta de pesquisa

**Como os padrões espaciais de suscetibilidade a enchentes e a importância das variáveis preditoras diferem entre períodos de El Niño e períodos não associados ao fenômeno?**

## Objetivos

- Construir uma base que integre registros históricos de enchentes e variáveis geoespaciais da RMSP.
- Separar os dados em cenários climáticos com e sem El Niño, utilizando o índice Oceanic Niño Index (ONI).
- Desenvolver modelos Random Forest e XGBoost para cada cenário.
- Comparar o desempenho dos modelos por meio de F1-score e AUC-ROC.
- Analisar a contribuição das variáveis com SHAP.
- Produzir e comparar mapas de suscetibilidade espacial a enchentes.

## Dados do projeto

A proposta prevê um inventário de enchentes e 15 variáveis geoespaciais condicionantes, com padronização para uma resolução espacial de **30 metros**. Entre os dados e fontes previstos estão:

| Componente | Dados e fontes previstos |
| --- | --- |
| Registros de enchentes | Pontos históricos georreferenciados do CGE e da Defesa Civil municipal |
| Relevo | SRTM DEM e variáveis como altitude, declividade, curvatura, índice de umidade topográfica e profundidade de vale |
| Uso e cobertura da terra | MapBiomas, distâncias de rios e rodovias e Curve Number (CN Grid) |
| Índices espectrais | NDVI, NDWI e NDMI derivados de imagens Sentinel-2 |
| Classificação climática | [Oceanic Niño Index (ONI), NOAA/CPC, versão ERSSTv6](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/) |
| Dados meteorológicos | [Dados históricos anuais de estações automáticas do INMET](https://portal.inmet.gov.br/dadoshistoricos), para análise das condições meteorológicas no recorte do estudo |

O inventário será organizado em duas classes: **ocorrência de enchente (1)** e **não-enchente (0)**. Para a segunda classe, a proposta prevê a geração de pontos pseudoaleatórios filtrados por critérios físicos de elevação e NDWI.

O período histórico, a relação final de variáveis e os procedimentos de obtenção e preparação dos dados serão documentados durante a implementação.

### Fontes selecionadas

- **ONI (NOAA/CPC):** será utilizado para separar os cenários climáticos. A série apresenta médias móveis de três meses; a definição histórica de episódios considera o limiar de ±0,5 °C por pelo menos cinco trimestres sobrepostos consecutivos. A classificação adotada no projeto deverá explicitar se segue esse critério ou apenas o limiar da proposta inicial. [Fonte](https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/enso/oni/v6/).
- **INMET:** disponibiliza arquivos históricos anuais de estações automáticas. Serão selecionadas as estações e os anos pertinentes ao estudo. Os dados meteorológicos complementarão a análise; os registros de ocorrência de enchentes precisarão ser obtidos separadamente. [Fonte](https://portal.inmet.gov.br/dadoshistoricos).

### Organização dos arquivos

```text
dados/
├── README.md          # Fontes, obtenção e regras de organização
├── brutos/
│   ├── oni/           # Cópia dos dados ONI utilizados
│   └── inmet/         # Arquivos originais das estações selecionadas
├── processados/       # Dados limpos e integrados
└── metadados/         # Origem, período, estações e alterações
```

Consulte o [guia dos dados](dados/README.md) para preencher as pastas. Os arquivos das bases ainda não estão incluídos nesta versão: os links indicam as fontes selecionadas, e o recorte temporal e as estações do INMET estão a definir.

## Metodologia proposta

1. **Coleta e integração:** reunir o inventário de enchentes e as camadas geoespaciais, padronizando sua resolução.
2. **Separação climática:** organizar registros e variáveis dinâmicas em dois grupos, com base no ONI: períodos de El Niño e períodos não associados ao fenômeno, incluindo condições neutras e La Niña.
3. **Preparação dos dados:** realizar a seleção de atributos com RFE e o balanceamento das classes com SMOTE no conjunto de treinamento.
4. **Treinamento:** desenvolver modelos Random Forest e XGBoost para cada cenário, com divisão prevista de 80% dos dados para treinamento e 20% para teste.
5. **Ajuste e validação:** aplicar Grid Search com validação cruzada espacial de cinco dobras.
6. **Avaliação:** comparar o desempenho utilizando F1-score e AUC-ROC.
7. **Interpretação e mapeamento:** utilizar SHAP para analisar a contribuição das variáveis e comparar os mapas de suscetibilidade entre os cenários.

## Métodos e técnicas previstos

| Método ou técnica | Finalidade |
| --- | --- |
| Random Forest | Modelagem da suscetibilidade a enchentes |
| XGBoost | Modelagem e comparação com Random Forest |
| RFE | Seleção de atributos |
| SMOTE | Balanceamento das classes no treinamento |
| Grid Search | Ajuste de hiperparâmetros |
| Validação cruzada espacial | Avaliação considerando a estrutura espacial dos dados |
| SHAP | Interpretação das contribuições das variáveis |

## Etapas do projeto

- [x] Definição do tema e dos objetivos.
- [x] Levantamento inicial de trabalhos relacionados.
- [x] Elaboração da metodologia e do cronograma inicial.
- [ ] Coleta e organização das bases de dados.
- [ ] Construção do inventário de enchentes.
- [ ] Separação dos dados por cenário climático.
- [ ] Pré-processamento e seleção de atributos.
- [ ] Treinamento, ajuste e avaliação dos modelos.
- [ ] Análise de explicabilidade e geração dos mapas.
- [ ] Discussão dos resultados e elaboração do relatório final.

## Resultados esperados

Espera-se produzir mapas de suscetibilidade a enchentes para os dois cenários climáticos, comparar o desempenho dos algoritmos e identificar possíveis diferenças na contribuição das variáveis preditoras.

Esses resultados deverão apoiar a discussão sobre a relação entre variabilidade climática e suscetibilidade espacial a enchentes na RMSP. As conclusões dependerão das análises e da validação dos modelos.

## Execução e reprodução

As instruções de instalação, preparação dos dados e execução dos experimentos serão incluídas após a definição do ambiente e a implementação dos códigos.

## Equipe

- Érica Marques de Santana
- Guilherme Delbon Souza
- Kauã Amaral Moreno

**Instituição:** Escola de Artes, Ciências e Humanidades - Universidade de São Paulo (EACH-USP).  
**Disciplina:** Resolução de Problemas II.

## Referências da proposta inicial

- Alcântara et al. (2025). *Interpretable machine learning for flood susceptibility mapping in the metropolitan region of São Paulo, southeast Brazil*. Discover Geoscience.
- Eloy, Ferreira e Ferruzzi (2024). *Modelo de predição da precipitação na cidade de São Paulo por meio de redes neurais recorrentes*. Anais do 15º Congresso de Inovação, Ciência e Tecnologia do IFSP (CONICT).
- Lee et al. (2023). *Synthesis report of the IPCC sixth assessment report (AR6), longer report*. IPCC.
- Oluwadare et al. (2025). *Applying machine learning algorithms for spatial modeling of flood susceptibility prediction over São Paulo sub-region*. Land.
- Tella et al. (2026). *Advancing flood susceptibility mapping with explainable AI: A novel application of accumulated local effects (ALE)*. Water Resources Management.
