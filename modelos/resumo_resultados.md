# Resultados dos Modelos Random Forest - Suscetibilidade a Enchentes em São Paulo

## 1. Desempenho do Modelo Geral

- **Acurácia:** 97.85%
- **F1-Score:** 0.9781
- **AUC-ROC:** 0.9910
- **Validação Cruzada (5-Fold CV F1):** 0.9765

### Importância das Variáveis (Ranking Geral)

1. **altitude_m**: 64.6%
1. **distancia_rio_m**: 14.3%
1. **declividade_graus**: 11.6%
1. **precipitacao_dia_mm**: 4.0%
1. **precipitacao_max_hora_mm**: 2.9%
1. **umidade_relativa_media**: 1.2%
1. **temp_media_c**: 1.0%
1. **valor_oni**: 0.6%

## 2. Comparativo por Cenário Climático

- **Cenário El Niño (F1):** 0.9594 (AUC: 0.9890)
- **Cenário Não-El Niño (F1):** 0.9730 (AUC: 0.9971)
