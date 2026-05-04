import streamlit as st
import pandas as pd
import urllib.parse

# 1. IDENTIDADE VISUAL EXCLUSIVA (PRETO E DOURADO)
st.set_page_config(page_title="Team Muniz - Cobrança", layout="centered", page_icon="📲")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1 { color: #D4AF37; text-align: center; font-size: 26px; }
    .card-aluno {
        background-color: #111111;
        padding: 20px;
        border: 1px solid #D4AF37;
        border-radius: 12px;
        margin-bottom: 15px;
    }
    .stLinkButton>a {
        width: 100% !important;
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        height: 50px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE LEITURA (FOCO NA ABA ESPECÍFICA)
def carregar_dados():
    try:
        # Puxando o link dos Secrets e forçando a aba correta (gid=2123746860)
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?gid=2123746860#gid=2123746860", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        # Padroniza nomes das colunas
        df.columns = [c.lower().strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Erro ao acessar a planilha: {e}")
        return None

# 3. INTERFACE DE OPERAÇÃO
st.title("📲 CENTRAL DE COBRANÇA")
st.markdown("<p style='text-align: center; color: gray;'>Fábio, aqui estão seus alunos pendentes:</p>", unsafe_allow_html=True)

df = carregar_dados()

if df is not None:
    # Filtrando quem está 'pendente' na coluna status
    if 'status' in df.columns:
        pendentes = df[df['status'].str.lower().str.strip() == 'pendente']
        
        if pendentes.empty:
            st.balloons()
            st.success("✅ Nenhum pagamento pendente nesta lista!")
        else:
            st.warning(f"Atenção: {len(pendentes)} cobranças para hoje.")
            
            for _, row in pendentes.iterrows():
                with st.container():
                    # Card com informações do aluno
                    st.markdown(f"""
                    <div class="card-aluno">
                        <span style="color:white; font-size:18px;">👤 <b>{row.get('aluno', 'N/A')}</b></span><br>
                        <span style="color:#D4AF37; font-size:16px;">💰 R$ {row.get('valor', 0):,.2f}</span> | 
                        <span style="color:gray;">📦 {row.get('pacote', 'Plano')}</span>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Preparação da mensagem automática
                    primeiro_nome = str(row.get('aluno', '')).split()[0]
                    pacote = row.get('pacote', 'Consultoria')
                    msg_wpp = (
                        f"Fala, {primeiro_nome}! 🏆\n\n"
                        f"Aqui é o Fábio da *Team Muniz*.\n"
                        f"Passando para avisar que o seu plano *{pacote}* consta como pendente aqui no sistema.\n\n"
                        "Consegue me enviar o comprovante ou prefere o Pix de novo? 🔥"
                    )
                    
                    # Formatação do link (limpa o número de telefone)
                    telefone = str(row.get('whatsapp', '')).split('.')[0]
                    link_final = f"https://wa.me/{telefone}?text={urllib.parse.quote(msg_wpp)}"
                    
                    # Botão de Disparo
                    st.link_button(f"🚀 ENVIAR PARA {primeiro_nome.upper()}", link_final)
                    st.write("") 
    else:
        st.error("A coluna 'status' não foi encontrada na sua planilha.")
else:
    st.info("💡 Certifique-se de que o LINK_PLANILHA está correto nos Secrets do Streamlit Cloud.")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #D4AF37;'>Sem estratégia, esforço vira tentativa.</p>", unsafe_allow_html=True)
