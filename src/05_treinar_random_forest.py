"""
05_treinar_random_forest.py
Treina o primeiro modelo Random Forest para suscetibilidade e previsão de enchentes
na cidade de São Paulo, conforme a metodologia do projeto:
1. Modelo Geral de Suscetibilidade (Random Forest Baseline).
2. Validação Cruzada estratificada em 5 dobras.
3. Teste em conjunto de teste independente (20%).
4. Modelagem segregada por cenário climático:
   - Cenário sob El Niño ativo (ONI >= +0.5 °C).
   - Cenário Não-El Niño (Neutro / La Niña).
5. Extração da importância relativa das variáveis (Feature Importance).
6. Exportação dos modelos (.pkl) e métricas consolidadas (.json e .md).
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score,
    f1_score, roc_auc_score, confusion_matrix, classification_report
)

def treinar_e_avaliar():
    dataset_path = os.path.join("dados", "processados", "dataset_suscetibilidade_sp.csv")
    modelos_dir = "modelos"
    os.makedirs(modelos_dir, exist_ok=True)
    
    print(f"Carregando dataset de {dataset_path}...")
    df = pd.read_csv(dataset_path)
    print(f"Dimensões do dataset: {df.shape}")

    # Definição das variáveis preditoras (Features)
    feature_cols = [
        "altitude_m",
        "declividade_graus",
        "distancia_rio_m",
        "precipitacao_dia_mm",
        "precipitacao_max_hora_mm",
        "temp_media_c",
        "umidade_relativa_media",
        "valor_oni"
    ]
    target_col = "alvo_alagamento"

    resultados = {}

    # =========================================================================
    # 1. MODELO GERAL (BASELINE RANDOM FOREST)
    # =========================================================================
    print("\n" + "="*60)
    print("1. TREINANDO MODELO RANDOM FOREST GERAL (BASELINE)")
    print("="*60)

    X = df[feature_cols]
    y = df[target_col]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    rf_geral = RandomForestClassifier(
        n_estimators=150,
        max_depth=12,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1
    )

    # Validação cruzada de 5 dobras no treino
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_f1 = cross_val_score(rf_geral, X_train, y_train, cv=cv, scoring="f1")
    cv_auc = cross_val_score(rf_geral, X_train, y_train, cv=cv, scoring="roc_auc")

    print(f"5-Fold CV F1-Score (Treino): {cv_f1.mean():.4f} (+/- {cv_f1.std():.4f})")
    print(f"5-Fold CV AUC-ROC (Treino):  {cv_auc.mean():.4f} (+/- {cv_auc.std():.4f})")

    # Treinamento final no conjunto de treino
    rf_geral.fit(X_train, y_train)

    # Avaliação no conjunto de teste independente (20%)
    y_pred = rf_geral.predict(X_test)
    y_prob = rf_geral.predict_proba(X_test)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    prec = precision_score(y_test, y_pred)
    rec = recall_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    auc = roc_auc_score(y_test, y_prob)
    cm = confusion_matrix(y_test, y_pred).tolist()

    print("\n--- Desempenho no Teste (Geral) ---")
    print(f"Acurácia:  {acc*100:.2f}%")
    print(f"Precisão:  {prec*100:.2f}%")
    print(f"Revocação: {rec*100:.2f}%")
    print(f"F1-Score:  {f1:.4f}")
    print(f"AUC-ROC:   {auc:.4f}")
    print(f"Matriz de Confusão:\n{np.array(cm)}")

    # Importância das variáveis
    importancias = dict(zip(feature_cols, [round(float(v), 4) for v in rf_geral.feature_importances_]))
    importancias_ordenadas = dict(sorted(importancias.items(), key=lambda item: item[1], reverse=True))

    print("\nImportância das Variáveis (Gini Importance):")
    for k, v in importancias_ordenadas.items():
        print(f"  - {k:<25}: {v*100:.1f}%")

    resultados["modelo_geral"] = {
        "n_amostras_treino": len(X_train),
        "n_amostras_teste": len(X_test),
        "cv_f1_medio": round(float(cv_f1.mean()), 4),
        "cv_auc_medio": round(float(cv_auc.mean()), 4),
        "teste_acuracia": round(float(acc), 4),
        "teste_precisao": round(float(prec), 4),
        "teste_revocacao": round(float(rec), 4),
        "teste_f1_score": round(float(f1), 4),
        "teste_auc_roc": round(float(auc), 4),
        "matriz_confusao": cm,
        "importancia_variaveis": importancias_ordenadas
    }

    with open(os.path.join(modelos_dir, "baseline_rf_geral.pkl"), "wb") as f:
        pickle.dump(rf_geral, f)

    # =========================================================================
    # 2. MODELAGEM SEGREGADA POR CENÁRIO CLIMÁTICO (EL NIÑO VS NÃO-EL NIÑO)
    # =========================================================================
    print("\n" + "="*60)
    print("2. MODELAGEM SEGREGADA POR CENÁRIO CLIMÁTICO (EL NIÑO)")
    print("="*60)

    df_elnino = df[df["cenario_climatico"] == "El Nino"]
    if len(df_elnino) > 100:
        X_en = df_elnino[feature_cols]
        y_en = df_elnino[target_col]
        X_tr_en, X_te_en, y_tr_en, y_te_en = train_test_split(
            X_en, y_en, test_size=0.20, random_state=42, stratify=y_en
        )
        rf_en = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42, n_jobs=-1)
        rf_en.fit(X_tr_en, y_tr_en)
        y_pred_en = rf_en.predict(X_te_en)
        y_prob_en = rf_en.predict_proba(X_te_en)[:, 1]

        f1_en = f1_score(y_te_en, y_pred_en)
        auc_en = roc_auc_score(y_te_en, y_prob_en)
        imp_en = dict(sorted(zip(feature_cols, [round(float(v), 4) for v in rf_en.feature_importances_]), key=lambda x: x[1], reverse=True))

        print(f"Cenário El Niño - Teste F1: {f1_en:.4f} | AUC: {auc_en:.4f}")
        resultados["cenario_el_nino"] = {
            "n_amostras": len(df_elnino),
            "teste_f1_score": round(float(f1_en), 4),
            "teste_auc_roc": round(float(auc_en), 4),
            "importancia_variaveis": imp_en
        }
        with open(os.path.join(modelos_dir, "baseline_rf_elnino.pkl"), "wb") as f:
            pickle.dump(rf_en, f)

    df_nao_elnino = df[df["cenario_climatico"] == "Nao El Nino"]
    if len(df_nao_elnino) >= 30 and len(df_nao_elnino[target_col].unique()) > 1:
        X_nen = df_nao_elnino[feature_cols]
        y_nen = df_nao_elnino[target_col]
        X_tr_nen, X_te_nen, y_tr_nen, y_te_nen = train_test_split(
            X_nen, y_nen, test_size=0.25, random_state=42, stratify=y_nen
        )
        rf_nen = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42, n_jobs=-1)
        rf_nen.fit(X_tr_nen, y_tr_nen)
        y_pred_nen = rf_nen.predict(X_te_nen)
        y_prob_nen = rf_nen.predict_proba(X_te_nen)[:, 1]

        f1_nen = f1_score(y_te_nen, y_pred_nen)
        auc_nen = roc_auc_score(y_te_nen, y_prob_nen)
        imp_nen = dict(sorted(zip(feature_cols, [round(float(v), 4) for v in rf_nen.feature_importances_]), key=lambda x: x[1], reverse=True))

        print(f"Cenário Não-El Niño - Teste F1: {f1_nen:.4f} | AUC: {auc_nen:.4f}")
        resultados["cenario_nao_el_nino"] = {
            "n_amostras": len(df_nao_elnino),
            "teste_f1_score": round(float(f1_nen), 4),
            "teste_auc_roc": round(float(auc_nen), 4),
            "importancia_variaveis": imp_nen
        }
        with open(os.path.join(modelos_dir, "baseline_rf_nao_elnino.pkl"), "wb") as f:
            pickle.dump(rf_nen, f)

    # Salvar resultados em JSON
    metricas_path = os.path.join(modelos_dir, "metricas_avaliacao.json")
    with open(metricas_path, "w", encoding="utf-8") as f:
        json.dump(resultados, f, indent=4, ensure_ascii=False)
    print(f"\nMétricas salvas em: {metricas_path}")

    # Salvar relatório síntese em Markdown
    resumo_path = os.path.join(modelos_dir, "resumo_resultados.md")
    with open(resumo_path, "w", encoding="utf-8") as f:
        f.write("# Resultados dos Modelos Random Forest - Suscetibilidade a Enchentes em São Paulo\n\n")
        f.write("## 1. Desempenho do Modelo Geral\n\n")
        f.write(f"- **Acurácia:** {resultados['modelo_geral']['teste_acuracia']*100:.2f}%\n")
        f.write(f"- **F1-Score:** {resultados['modelo_geral']['teste_f1_score']:.4f}\n")
        f.write(f"- **AUC-ROC:** {resultados['modelo_geral']['teste_auc_roc']:.4f}\n")
        f.write(f"- **Validação Cruzada (5-Fold CV F1):** {resultados['modelo_geral']['cv_f1_medio']:.4f}\n\n")
        f.write("### Importância das Variáveis (Ranking Geral)\n\n")
        for k, v in resultados['modelo_geral']['importancia_variaveis'].items():
            f.write(f"1. **{k}**: {v*100:.1f}%\n")
        f.write("\n## 2. Comparativo por Cenário Climático\n\n")
        if "cenario_el_nino" in resultados:
            f.write(f"- **Cenário El Niño (F1):** {resultados['cenario_el_nino']['teste_f1_score']:.4f} (AUC: {resultados['cenario_el_nino']['teste_auc_roc']:.4f})\n")
        if "cenario_nao_el_nino" in resultados:
            f.write(f"- **Cenário Não-El Niño (F1):** {resultados['cenario_nao_el_nino']['teste_f1_score']:.4f} (AUC: {resultados['cenario_nao_el_nino']['teste_auc_roc']:.4f})\n")
    print(f"Resumo executivo salvo em: {resumo_path}")

if __name__ == "__main__":
    treinar_e_avaliar()
