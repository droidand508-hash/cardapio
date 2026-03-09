import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.request

# Configuração da página
st.title("Gerador de Cardápio - Boca Doce")

# --- 1. PREPARAÇÃO DA FONTE ---
# Baixa a fonte Roboto automaticamente se não existir na pasta
font_path = "Roboto-Bold.ttf"
if not os.path.exists(font_path):
    url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
    try:
        urllib.request.urlretrieve(url, font_path)
    except Exception as e:
        st.error(f"Erro ao baixar a fonte: {e}")

# --- 2. ENTRADAS DO USUÁRIO ---
col1, col2 = st.columns(2)
with col1:
    data_cardapio = st.text_input("Data do Cardápio", "09/03/2026")
with col2:
    dia_semana = st.text_input("Dia da Semana", "Segunda")

st.write("### Opções do Dia")
dados_iniciais = {
    "Prato": ["Bife Acebolado", "Bife Empanado", "Frango Frito", "Frango na Chapa", "Isca de Frango", "Bisteca Bovina"],
    "Valor (R$)": ["17,00", "18,00", "16,00", "16,00", "16,00", "17,00"]
}
df = pd.DataFrame(dados_iniciais)
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- 3. GERAÇÃO DA IMAGEM ---
if st.button("Gerar Imagem do Cardápio"):
    try:
        # Carrega a imagem de fundo (template limpo)
        img = Image.open("template.jpg")
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size # Pega as dimensões da imagem dinamicamente
        
        # Define os tamanhos das fontes
        tamanho_titulo = int(img_w * 0.055) # Fonte do título ajusta com a largura da imagem
        tamanho_item = int(img_w * 0.045)   # Fonte dos pratos
        
        fonte_titulo = ImageFont.truetype(font_path, tamanho_titulo)
        fonte_item = ImageFont.truetype(font_path, tamanho_item)

        # Cor do texto (Preto)
        cor_texto = (0, 0, 0)

        # --- TEXTOS SUPERIORES (CENTRALIZADOS) ---
        texto_data = f"Cardápio do dia {data_cardapio}"
        bbox_data = draw.textbbox((0, 0), texto_data, font=fonte_titulo)
        w_data = bbox_data[2] - bbox_data[0]
        # Centraliza horizontalmente e fixa a altura (Ajuste o 260 se necessário)
        draw.text(((img_w - w_data) / 2, img_h * 0.28), texto_data, font=fonte_titulo, fill=cor_texto)

        bbox_dia = draw.textbbox((0, 0), dia_semana, font=fonte_titulo)
        w_dia = bbox_dia[2] - bbox_dia[0]
        draw.text(((img_w - w_dia) / 2, img_h * 0.34), dia_semana, font=fonte_titulo, fill=cor_texto)

        # --- ITENS DO CARDÁPIO (ALINHADOS) ---
        pos_y = img_h * 0.43 # Altura onde começam os pratos
        margem_esq = img_w * 0.12 # Pratos começam a 12% da margem esquerda
        margem_dir = img_w * 0.88 # Preços alinham a 88% da margem direita (antes do final)
        
        espacamento_linhas = img_h * 0.045 # Espaçamento entre cada item

        for index, row in df_editado.iterrows():
            prato = f"• {row['Prato']}"
            valor = f"R$ {row['Valor (R$)']}"
            
            # Desenha prato (Alinhado à esquerda)
            draw.text((margem_esq, pos_y), prato, font=fonte_item, fill=cor_texto)
            
            # Desenha valor (Alinhado à direita)
            bbox_valor = draw.textbbox((0, 0), valor, font=fonte_item)
            w_valor = bbox_valor[2] - bbox_valor[0]
            draw.text((margem_dir - w_valor, pos_y), valor, font=fonte_item, fill=cor_texto)
            
            pos_y += espacamento_linhas

        # --- PREPARA O DOWNLOAD ---
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()

        st.success("Cardápio gerado com sucesso!")
        st.image(img, caption="Preview do Cardápio", use_container_width=True)
        st.download_button(
            label="Baixar Imagem para Compartilhar",
            data=byte_im,
            file_name=f"cardapio_{data_cardapio.replace('/', '-')}.jpg",
            mime="image/jpeg",
        )
    except FileNotFoundError:
        st.error("Erro: Certifique-se de que a imagem 'template.jpg' está na mesma pasta do script app.py.")
