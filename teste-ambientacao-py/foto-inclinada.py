import cv2
from PIL import Image
import numpy as np
import os

# Caminho para a imagem de fundo (entrada da casa) e para a pasta com os tapetes recortados
imagem_fundo_caminho = r"C:\\Users\\jean.marques\\Desktop\\teste-ambienta-py\\teste-ambientacao-py\\banheiro1.png"  # Substitua pelo caminho da sua imagem de fundo
pasta_tapetes = r"C:\\Users\\jean.marques\\Desktop\\teste-ambienta-py\\teste-ambientacao-py\\ambientar"  # Pasta onde estão as imagens recortadas
saida_pasta = r"C:\\Users\\jean.marques\\Desktop\\teste-ambienta-py\\teste-ambientacao-py\\ambientadas"  # Pasta onde a imagem final será salva
os.makedirs(saida_pasta, exist_ok=True)  # Cria a pasta 'ambientadas' se não existir

# Carrega a imagem de fundo
imagem_fundo = Image.open(imagem_fundo_caminho)

# Define a posição (x, y) onde o tapete será colocado na imagem de fundo
posicao_x = 150
posicao_y = 300

# Função para recortar bordas brancas
def recortar_bordas_brancas(imagem):
    imagem_np = np.array(imagem)
    cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGBA2GRAY)
    _, mascara = cv2.threshold(cinza, 240, 255, cv2.THRESH_BINARY)
    contornos, _ = cv2.findContours(255 - mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contornos:
        x, y, w, h = cv2.boundingRect(contornos[0])
        imagem_cortada = imagem_np[y:y+h, x:x+w]
        return Image.fromarray(imagem_cortada)
    return imagem

# Função para remoção de fundo branco
def remover_fundo_branco(imagem):
    imagem_np = np.array(imagem)
    r, g, b, a = cv2.split(imagem_np)
    mascara_fundo = (r > 240) & (g > 240) & (b > 240)
    a[mascara_fundo] = 0
    imagem_sem_fundo = cv2.merge((r, g, b, a))
    return Image.fromarray(imagem_sem_fundo, 'RGBA')

# Função para aplicar transformação de perspectiva (inclinação nivelada)
def aplicar_transformacao_perspectiva(imagem, pontos_destino):
    largura, altura = imagem.size
    imagem_np = np.array(imagem)

    # Define os pontos originais da imagem (retângulo original)
    pontos_origem = np.float32([
        [0, 0],
        [largura, 0],
        [largura, altura],
        [0, altura]
    ])

    # Define os pontos de destino (ajustar a inclinação)
    matriz_transformacao = cv2.getPerspectiveTransform(pontos_origem, pontos_destino)

    # Aplica a transformação de perspectiva
    transformada = cv2.warpPerspective(
        imagem_np, 
        matriz_transformacao, 
        (largura, altura),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_CONSTANT,
        borderValue=(255, 255, 255, 0)
    )
    return Image.fromarray(transformada)

# Processa cada tapete recortado
for nome_arquivo in os.listdir(pasta_tapetes):
    caminho_tapete = os.path.join(pasta_tapetes, nome_arquivo)
    tapete = Image.open(caminho_tapete).convert("RGBA")

    tapete_sem_fundo = remover_fundo_branco(tapete)
    tapete_redimensionado = tapete_sem_fundo.resize((550, 380))

    # Pontos de destino para transformação de perspectiva
    pontos_destino = np.float32([
        [50, 0],         # Superior esquerdo
        [500, 30],       # Superior direito
        [520, 350],      # Inferior direito
        [30, 370]        # Inferior esquerdo
    ])

    tapete_transformado = aplicar_transformacao_perspectiva(tapete_redimensionado, pontos_destino)

    imagem_com_tapete = imagem_fundo.copy()
    imagem_com_tapete.paste(tapete_transformado, (posicao_x, posicao_y), tapete_transformado)

    caminho_salvar = os.path.join(saida_pasta, nome_arquivo)
    imagem_com_tapete.save(caminho_salvar)
    print(f"Imagem ambientada salva em: {caminho_salvar}")

print("Processamento concluído.")
