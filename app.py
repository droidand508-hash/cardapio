import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io
import os
import urllib.request
from datetime import datetime, timedelta, timezone

# --- LÓGICA DE DATA E HORA ---
fuso_br = timezone(timedelta(hours=-3))
hoje = datetime.now(fuso_br)
data_atual = hoje.strftime("%d/%m/%Y")
dias_semana = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
dia_atual = dias_semana[hoje.weekday()]

# Configuração da página
st.title("Gerador de Cardápio - Boca Doce")

# --- 1. PREPARAÇÃO DA FONTE ---
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
    data_cardapio = st.text_input("Data do Cardápio", data_atual)
with col2:
    dia_semana = st.text_input("Dia da Semana", dia_atual)

st.write("### Opções do Dia")
dados_iniciais = {
    "Prato": ["Bife Acebolado", "Bife a Cavalo", "Bife Empanado", "Frango Frito", "Frango na Chapa", "Frango Empanado", "Isca de Frango", "Bisteca Bovina", "Bife de Fígado", "Isca de Fígado", "Língua de Panela", "Omelete de Car Móid", "Picadinho com Legumes", "Misto (Carn, Fran, Calab)"],
    "Valor (R$)": ["17,00", "18,00", "18,00", "16,00", "16,00", "17,00", "16,00", "17,00", "16,00", "16,00", "18,00", "18,00", "18,00", "18,00"]
}
df = pd.DataFrame(dados_iniciais)
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# --- 3. GERAÇÃO DA IMAGEM ---
if st.button("Gerar Imagem do Cardápio"):
    try:
        img = Image.open("template.jpg")
        draw = ImageDraw.Draw(img)
        img_w, img_h = img.size

        # --- NOVO: CÁLCULO DINÂMICO PARA CABER NA TELA ---
        num_itens = len(df_editado)
        pos_y_inicial = img_h * 0.42  # Posição onde os pratos começam
        pos_y_limite = img_h * 0.90   # Posição máxima antes de encostar na borda de baixo
        espaco_disponivel = pos_y_limite - pos_y_inicial

        tamanho_titulo = int(img_w * 0.055)
        
        # Valores base de formatação
        tamanho_item_base = int(img_w * 0.045)
        espacamento_base = img_h * 0.045

        # Verifica se os itens vão passar do limite da imagem
        if (num_itens * espacamento_base) > espaco_disponivel:
            # Recalcula o espaçamento para espremer os itens no espaço disponível
            espacamento_linhas = espaco_disponivel / num_itens
            # Reduz a fonte proporcionalmente (com um leve fator de gordura de 1.1 para legibilidade)
            fator_escala = espacamento_linhas / espacamento_base
            tamanho_item = int(tamanho_item_base * fator_escala * 1.1)
        else:
            espacamento_linhas = espacamento_base
            tamanho_item = tamanho_item_base

        fonte_titulo = ImageFont.truetype(font_path, tamanho_titulo)
        fonte_item = ImageFont.truetype(font_path, tamanho_item)
        cor_texto = (0, 0, 0)

        # --- TEXTOS SUPERIORES (CENTRALIZADOS) ---
        texto_data = f"Cardápio do dia {data_cardapio}"
        bbox_data = draw.textbbox((0, 0), texto_data, font=fonte_titulo)
        w_data = bbox_data[2] - bbox_data[0]
        draw.text(((img_w - w_data) / 2, img_h * 0.28), texto_data, font=fonte_titulo, fill=cor_texto)

        bbox_dia = draw.textbbox((0, 0), dia_semana, font=fonte_titulo)
        w_dia = bbox_dia[2] - bbox_dia[0]
        draw.text(((img_w - w_dia) / 2, img_h * 0.34), dia_semana, font=fonte_titulo, fill=cor_texto)

        # --- ITENS DO CARDÁPIO (ALINHADOS) ---
        pos_y = pos_y_inicial
        margem_esq = img_w * 0.12
        margem_dir = img_w * 0.88

        for index, row in df_editado.iterrows():
            prato = f"• {row['Prato']}"
            valor = f"R$ {row['Valor (R$)']}"

            # Desenha prato (Esquerda)
            draw.text((margem_esq, pos_y), prato, font=fonte_item, fill=cor_texto)

            # Desenha valor (Direita)
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
