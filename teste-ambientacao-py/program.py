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
    # Converte para um array NumPy
    imagem_np = np.array(imagem)

    # Converte para escala de cinza
    cinza = cv2.cvtColor(imagem_np, cv2.COLOR_RGBA2GRAY)

    # Cria uma máscara binária onde o branco é 255
    _, mascara = cv2.threshold(cinza, 240, 255, cv2.THRESH_BINARY)

    # Encontra contornos
    contornos, _ = cv2.findContours(255 - mascara, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contornos:
        # Encontra a área delimitadora dos contornos
        x, y, w, h = cv2.boundingRect(contornos[0])

        # Recorta a imagem na área delimitada
        imagem_cortada = imagem_np[y:y+h, x:x+w]

        return Image.fromarray(imagem_cortada)
    return imagem  # Retorna a imagem original se não houver bordas para recortar

#nova funçao para remoção de fundo branco
def remover_fundo_branco(imagem):
    #converte para um array numpy
    imagem_np = np.array(imagem)

    #identifica os canais rgba
    r, g, b, a = cv2.split(imagem_np)

    #cria máscara para o fundo branco (com tolerância de quase branco)
    mascara_fundo = (r > 240) & (g > 240) & (b > 240)

    #ajusta o canal alfa para remover o fundo
    a[mascara_fundo] = 0

    #recombina os canais em uma nova imagem
    imagem_sem_fundo = cv2.merge((r,g,b,a))

    return Image.fromarray(imagem_sem_fundo, 'RGBA')


# Processa cada tapete recortado
for nome_arquivo in os.listdir(pasta_tapetes):
    caminho_tapete = os.path.join(pasta_tapetes, nome_arquivo)
    
    # Carrega a imagem do tapete
    tapete = Image.open(caminho_tapete).convert("RGBA")  # Converte para RGBA para garantir canal de transparência

    # Recorta as bordas brancas
    #tapete_sem_bordas = recortar_bordas_brancas(tapete)

    tapete_sem_fundo = remover_fundo_branco(tapete)

    # Redimensiona o tapete para um tamanho adequado, se necessário
    tapete_redimensionado = tapete_sem_fundo.resize((550, 380))  # Ajuste o tamanho conforme necessário

    # Cria uma cópia da imagem de fundo para cada tapete
    imagem_com_tapete = imagem_fundo.copy()

    # Coloca o tapete na imagem de fundo na posição especificada
    imagem_com_tapete.paste(tapete_redimensionado, (posicao_x, posicao_y), tapete_redimensionado)

    # Salva a imagem final com o tapete posicionado
    caminho_salvar = os.path.join(saida_pasta, nome_arquivo)
    imagem_com_tapete.save(caminho_salvar)

    print(f"Imagem ambientada salva em: {caminho_salvar}")

print("Processamento concluído.")
