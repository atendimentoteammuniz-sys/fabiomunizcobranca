import streamlit as st
import pandas as pd
import urllib.parse

# 1. ESTILO TEAM MUNIZ
st.set_page_config(page_title="Team Muniz - Performance", layout="wide", page_icon="📊")

# Inicializa o contador na memória da sessão (zera se atualizar a página)
if 'total_disparos' not in st.session_state:
    st.session_state.total_disparos = 0

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .metric-container {
        background-color: #111111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #D4AF37;
        text-align: center;
    }
    .stLinkButton>a {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNÇÃO DE CARREGAMENTO
@st.cache_data(ttl=0)
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        return df[df['status'].str.lower().str.strip() == 'pendente']
    except:
        return None

# Função para contar o clique
def contar_clique():
    st.session_state.total_disparos += 1

st.title("📊 PERFORMANCE DE COBRANÇA")

# --- PAINEL DE MÉTRICAS ---
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.markdown(f"""<div class="metric-container">
        <p style="color:gray; margin:0;">Mensagens preparadas nesta sessão</p>
        <h2 style="margin:0;">{st.session_state.total_disparos}</h2>
    </div>""", unsafe_allow_html=True)

with col_m2:
    if st.button("🔄 Resetar Contador / Atualizar"):
        st.session_state.total_disparos = 0
        st.cache_data.clear()
        st.rerun()

st.markdown("---")

df = carregar_dados()

if df is not None and not df.empty:
    datas_pendentes = sorted(df['vencimento'].unique())
    tabs = st.tabs(datas_pendentes)
    
    for i, data in enumerate(datas_pendentes):
        with tabs[i]:
            alunos = df[df['vencimento'] == data]
            for _, row in alunos.iterrows():
                with st.expander(f"👤 {row['aluno']} | {row['valor']}"):
                    
                    msg_formal = (
                        f"*Mensagem automática MFIT | Team Muniz*\n\n"
                        f"Seu pagamento com vencimento em *{data}*, no valor de *{row['valor']}*, encontra-se pendente.\n\n"
                        f"Para continuidade do seu acompanhamento e acesso à sua estratégia personalizada, é necessária a regularização.\n\n"
                        f"Chave Pix: *{row['chave_pix']}*"
                    )
                    
                    link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg_formal)}"
                    
                    # O segredo: On_click dispara a função que soma +1 no contador
                    st.link_button(f"🚀 ENVIAR PARA {str(row['aluno']).upper()}", 
                                   link_wpp, 
                                   on_click=contar_clique)
else:
    st.success("✅ Tudo limpo por aqui!")
