import streamlit as st
import pandas as pd
import urllib.parse

# 1. ESTILO TEAM MUNIZ
st.set_page_config(page_title="Team Muniz - Cobrança", layout="centered", page_icon="📲")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1 { color: #D4AF37; text-align: center; }
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
        height: 45px;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO COM AJUSTE DE CABEÇALHO
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        # Forçando a leitura da aba correta
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        
        # Se os cabeçalhos estiverem grudados, tentamos renomear manualmente as colunas por posição
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        return df
    except Exception as e:
        st.error(f"Erro na conexão: {e}")
        return None

st.title("📲 CENTRAL DE COBRANÇA")
st.markdown("<p style='text-align: center; color: gray;'>Gestão de Pendências - Team Muniz</p>", unsafe_allow_html=True)

df = carregar_dados()

if df is not None:
    # Filtrar apenas quem está Pendente
    pendentes = df[df['status'].str.lower().str.strip() == 'pendente']
    
    if pendentes.empty:
        st.success("✅ Nenhuma cobrança pendente identificada!")
    else:
        st.info(f"Fábio, você tem {len(pendentes)} alunos para cobrar hoje.")
        
        for _, row in pendentes.iterrows():
            with st.container():
                st.markdown(f"""
                <div class="card-aluno">
                    <span style="color:white; font-size:18px;">👤 <b>{row['aluno']}</b></span><br>
                    <span style="color:#D4AF37;">💰 {row['valor']}</span> | 
                    <span style="color:gray;">📅 Venc: {row['vencimento']}</span><br>
                    <span style="color:gray;">📦 {row['pacote']}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Mensagem com a sua estratégia e a chave Pix inclusa
                primeiro_nome = str(row['aluno']).split()[0]
                msg = (
                    f"Fala, {primeiro_nome}! 🏆\n\n"
                    f"Aqui é o Fábio da *Team Muniz*.\n"
                    f"Passando para avisar que o seu plano *{row['pacote']}* ({row['vencimento']}) está pendente.\n\n"
                    f"Se quiser agilizar, segue minha chave Pix: *{row['chave_pix']}*\n\n"
                    "Após o pagamento, me envie o comprovante por aqui. 🔥"
                )
                
                link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg)}"
                st.link_button(f"🚀 COBRAR {primeiro_nome.upper()}", link_wpp)
                st.write("") 
else:
    st.info("Aguardando os dados da planilha...")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #D4AF37;'>Sem estratégia, esforço vira tentativa.</p>", unsafe_allow_html=True)
