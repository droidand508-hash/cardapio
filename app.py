import streamlit as st
import pandas as pd
from PIL import Image, ImageDraw, ImageFont
import io

# Configuração da página
st.title("Gerador de Cardápio - Boca Doce")

# 1. Entradas de Dados (Simples para o usuário)
col1, col2 = st.columns(2)
with col1:
    data_cardapio = st.text_input("Data do Cardápio", "09/03/2026")
with col2:
    dia_semana = st.text_input("Dia da Semana", "Segunda")

st.write("### Opções do Dia")
# Tabela editável para a pessoa preencher facilmente
dados_iniciais = {
    "Prato": ["Bife a Cavalo", "Bife Acebolado", "Frango Frito"],
    "Valor (R$)": ["18,00", "17,00", "16,00"]
}
df = pd.DataFrame(dados_iniciais)
df_editado = st.data_editor(df, num_rows="dynamic", use_container_width=True)

# 2. Geração da Imagem
if st.button("Gerador Imagem do Cardápio"):
    try:
        # Carrega a imagem de fundo em branco (sem os textos)
        img = Image.open("template.jpg")
        draw = ImageDraw.Draw(img)
        
        # Carrega uma fonte (você precisa ter um arquivo .ttf na mesma pasta, ex: arial.ttf)
        # Se não tiver, pode usar o padrão do PIL, mas fica sem formatação bonita.
        try:
            fonte_titulo = ImageFont.truetype("arial.ttf", 45)
            fonte_item = ImageFont.truetype("arial.ttf", 35)
        except IOError:
            fonte_titulo = ImageFont.load_default()
            fonte_item = ImageFont.load_default()
            st.warning("Arquivo de fonte 'arial.ttf' não encontrado. Usando fonte padrão.")

        # Escreve a Data e Dia da Semana (As coordenadas X, Y precisam ser ajustadas pro seu template)
        draw.text((200, 250), f"Cardápio do dia {data_cardapio}", font=fonte_titulo, fill=(0, 0, 0))
        draw.text((350, 310), dia_semana, font=fonte_titulo, fill=(0, 0, 0))

        # Escreve os itens do cardápio
        pos_y = 400
        for index, row in df_editado.iterrows():
            prato = f"• {row['Prato']}"
            valor = f"R$ {row['Valor (R$)']}"
            
            draw.text((100, pos_y), prato, font=fonte_item, fill=(0, 0, 0))
            draw.text((600, pos_y), valor, font=fonte_item, fill=(0, 0, 0))
            pos_y += 45 # Espaçamento entre as linhas

        # Converte a imagem gerada para um formato baixável
        buf = io.BytesIO()
        img.save(buf, format="JPEG")
        byte_im = buf.getvalue()

        st.success("Cardápio gerado com sucesso!")
        
        # Mostra um preview e o botão de download
        st.image(img, caption="Preview do Cardápio", use_container_width=True)
        st.download_button(
            label="Baixar Imagem para Compartilhar",
            data=byte_im,
            file_name=f"cardapio_{data_cardapio.replace('/', '-')}.jpg",
            mime="image/jpeg",
        )
    except FileNotFoundError:
        st.error("Erro: O arquivo 'template.jpg' não foi encontrado na pasta.")