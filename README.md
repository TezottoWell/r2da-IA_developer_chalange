# **📄 Document Quality Assessment Pipeline**

Este projeto implementa um pipeline automatizado para **avaliação da qualidade de documentos digitalizados (PDFs)** antes do processamento por OCR ou Inteligência Artificial.

O objetivo é **filtrar documentos inadequados** (borrados, com baixo contraste ou excesso de ruído), reduzindo custos operacionais, retrabalho e falhas na extração de texto.

## **🎯 Objetivo**

* Avaliar automaticamente a qualidade de documentos digitalizados.  
* Gerar um **score objetivo de qualidade**.  
* Classificar documentos para:  
  * Processamento por IA/OCR  
  * Revisão manual  
  * Redigitalização  
* Persistir resultados de forma resiliente (JSON por página).

## **🧩 Visão Geral da Solução**

O pipeline segue as etapas abaixo. A análise é feita **página a página**, permitindo decisões mais precisas mesmo em documentos com qualidade heterogênea.

graph TD;  
    A\[PDF\] \--\> B\[Conversão PDF → Imagem\];  
    B \--\> C\[Análise de Qualidade OpenCV\];  
    C \--\> D\[Score de Qualidade\];  
    D \--\> E\[Decisão Automática\];  
    E \--\> F\[Persistência em JSON\];

## **🧪 Métricas de Qualidade Utilizadas**

As métricas são extraídas via **OpenCV**, utilizando técnicas clássicas de visão computacional:

| Métrica | Técnica | Descrição |
| :---- | :---- | :---- |
| **Sharpness** (Nitidez) | Variância do Laplaciano | Detecta desfoque (blur). |
| **Contrast** (Contraste) | Desvio padrão da imagem | Avalia separação texto/fundo. |
| **Noise** (Ruído) | Diferença após Gaussian Blur | Identifica granulação e artefatos. |

Essas métricas são rápidas de computar, explicáveis e independentes de modelos treinados.

## **🧮 Estratégia de Score**

Cada métrica contribui de forma independente para um **score agregado**.

* Alta nitidez → mais pontos  
* Bom contraste → mais pontos  
* Baixo ruído → mais pontos

O score final é usado para classificação automática.

## **🚦 Estratégia de Decisão**

Os thresholds podem ser calibrados com base em dados reais de OCR.

| Score | Decisão |
| :---- | :---- |
| ≥ 60 | SEND\_TO\_AI |
| 40–59 | REVIEW\_MANUALLY |
| \< 40 | REDIGITALIZE |

## **🏗 Arquitetura**

┌──────────────┐  
│  PDFs Brutos │  
└──────┬───────┘  
       │  
       ▼  
┌─────────────────────┐  
│    PDF → Imagem     │  
│     (pdf2image)     │  
└──────┬──────────────┘  
       │  
       ▼  
┌─────────────────────┐  
│   Análise OpenCV    │  
│  \- Nitidez          │  
│  \- Contraste        │  
│  \- Ruído            │  
└──────┬──────────────┘  
       │  
       ▼  
┌─────────────────────┐  
│   Score \+ Decisão   │  
└──────┬──────────────┘  
       │  
       ▼  
┌─────────────────────┐  
│   JSON por Página   │  
└─────────────────────┘  
       │  
       ▼  
┌─────────────────────┐  
│  Microserviço de IA │  
│ (somente score bom) │  
└─────────────────────┘

## **📁 Estrutura do Projeto**

.  
├── pdfs/          \# PDFs de entrada  
├── saida/         \# JSONs gerados (um por página)  
├── main.py        \# Script principal  
└── README.md      \# Documentação

## **⚙️ Dependências**

pip install opencv-python numpy pdf2image pillow

**⚠️ Importante:**

O pdf2image requer o **Poppler** instalado no sistema.

**Ubuntu/Debian:**

sudo apt install poppler-utils

**macOS:**

brew install poppler

## **▶️ Execução**

1. Coloque os arquivos PDF na pasta pdfs/.  
2. Execute o script principal:

python main.py

Os resultados serão gerados na pasta saida/, sendo um arquivo JSON por página.

## **📄 Exemplo de Saída (JSON)**

{  
  "document\_name": "contrato.pdf",  
  "page\_number": 1,  
  "quality": {  
    "score": 72,  
    "metrics": {  
      "sharpness": 185.4,  
      "contrast": 52.1,  
      "noise": 14.3  
    }  
  },  
  "decision": "SEND\_TO\_AI",  
  "timestamp": "2026-01-29T15:42:10"  
}

## **📌 Considerações Finais**

Esta solução prioriza:

1. **Baixo custo computacional**  
2. **Explicabilidade**  
3. **Facilidade de manutenção**  
4. **Impacto direto no negócio**