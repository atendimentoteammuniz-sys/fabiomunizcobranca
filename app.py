import streamlit as st
import pandas as pd
import urllib.parse

# 1. ESTILO TEAM MUNIZ
st.set_page_config(page_title="Team Muniz - Performance", layout="wide", page_icon="📊")

# Inicializa o dicionário de contagem por contato na memória da sessão
if 'contagem_contatos' not in st.session_state:
    st.session_state.contagem_contatos = {}

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .card-aluno {
        background-color: #111111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #D4AF37;
    }
    .metric-badge {
        background-color: #D4AF37;
        color: black;
        padding: 2px 8px;
        border-radius: 10px;
        font-weight: bold;
        font-size: 12px;
        float: right;
    }
    .stLinkButton>a {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DOS DADOS (SEM CACHE PARA ATUALIZAÇÃO REAL)
@st.cache_data(ttl=0)
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        # Filtra apenas Pendentes
        return df[df['status'].str.lower().str.strip() == 'pendente']
    except:
        return None

# Função para incrementar o contador específico do aluno
def registrar_envio(nome_aluno):
    if nome_aluno not in st.session_state.contagem_contatos:
        st.session_state.contagem_contatos[nome_aluno] = 0
    st.session_state.contagem_contatos[nome_aluno] += 1

st.title("📊 PERFORMANCE POR CONTATO")

# Painel de Controle
if st.button("🔄 Atualizar Lista / Resetar Sessão"):
    st.session_state.contagem_contatos = {}
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
                nome = row['aluno']
                # Busca quantas vezes já foi clicado nesta sessão
                tentativas = st.session_state.contagem_contatos.get(nome, 0)
                
                # Interface com contador individual
                with st.expander(f"👤 {nome} | {row['valor']}"):
                    st.markdown(f"""
                    <div class="card-aluno">
                        <span class="metric-badge">Envios: {tentativas}</span>
                        <p><b>Pacote:</b> {row['pacote']}</p>
                        <p><b>Chave Pix:</b> {row['chave_pix']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    msg_formal = (
                        f"*Mensagem automática MFIT | Team Muniz*\n\n"
                        f"Seu pagamento com vencimento em *{data}*, no valor de *{row['valor']}*, encontra-se pendente.\n\n"
                        f"Para continuidade do seu acompanhamento e acesso à sua estratégia personalizada, é necessária a regularização.\n\n"
                        f"Chave Pix: *{row['chave_pix']}*"
                    )
                    
                    link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg_formal)}"
                    
                    st.write("")
                    # O botão agora chama o registro específico do aluno antes de abrir o link
                    st.link_button(f"🚀 ENVIAR COBRANÇA PARA {str(nome).upper()}", 
                                   link_wpp, 
                                   on_click=registrar_envio, 
                                   args=(nome,))
else:
    st.success("✅ Nenhum contato pendente encontrado!")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #D4AF37;'>Sem estratégia, esforço vira tentativa.</p>", unsafe_allow_html=True)
