import os
import cv2
from pdf2image import convert_from_path
import numpy as np
import json
from datetime import datetime

def pdf_to_images(pdf_path: str) -> list:
    imagens = convert_from_path(pdf_path, dpi=200)
    return imagens

def medir_nitidez(image_gray: np.ndarray) -> float:
    laplacian_var = cv2.Laplacian(image_gray, cv2.CV_64F).var()
    return laplacian_var

def medir_contraste(image_gray: np.ndarray) -> float:
   return image_gray.std()

def medir_ruido(image_gray: np.ndarray) -> float:
   imagem_suave = cv2.GaussianBlur(image_gray, (5, 5), 0)
   return np.mean(np.abs(image_gray - imagem_suave))

def calcular_score(nitidez: float, contraste: float, ruido: float) ->  int:
    score = 0

    if nitidez >= 300:
        score += 60
    elif nitidez >= 150:
        score += 25
    elif nitidez >= 50:
        score += 10
    else:
        score -= 10

    if contraste >= 50:
        score += 30
    elif contraste >= 20:
        score += 15
    else:
        score -= 10

    if ruido <= 8:
        score += 40
    elif ruido <= 20:
        score += 15
    else:
        score -= 10

    return score

def decidir(score: int) -> str:
    if score >= 60:
        return "SEND_TO_AI"
    elif score >= 40:
        return "REVIEW_MANUALLY"
    else:
        return "REDIGITALIZE"

def main():
    PDF_DIR = "pdfs"
    SAIDA_DIR = "saida"

    os.makedirs(SAIDA_DIR, exist_ok=True)

    for arquivo in os.listdir(PDF_DIR):
        if not arquivo.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(PDF_DIR, arquivo)

        try:
            paginas = pdf_to_images(pdf_path)
        except Exception as e:
            print(f"Erro ao converter {arquivo}: {e}")
            continue

        for i, pagina in enumerate(paginas):
            imagem = cv2.cvtColor(np.array(pagina), cv2.COLOR_RGB2BGR)
            imagem_gray = cv2.cvtColor(imagem, cv2.COLOR_BGR2GRAY)

            nitidez = medir_nitidez(imagem_gray)
            contraste = medir_contraste(imagem_gray)
            ruido = medir_ruido(imagem_gray)

            score = calcular_score(nitidez, contraste, ruido)
            decisao = decidir(score)

            resultado = {
                "document_name": arquivo,
                "page_number": i + 1,
                "quality": {
                    "score": score,
                    "metrics": {
                        "sharpness": nitidez,
                        "contrast": contraste,
                        "noise": ruido
                    }
                },
                "decision": decisao,
                "timestamp": datetime.now().isoformat()
            }

            nome_saida = f"{arquivo.replace('.pdf', '')}_page_{i + 1}.json"

            with open(os.path.join(SAIDA_DIR, nome_saida), "w") as f:
                json.dump(resultado, f, indent=4)

if __name__ == "__main__":
    main()
