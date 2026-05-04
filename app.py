import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. ESTILO TEAM MUNIZ (INTERFACE DE AGENDA)
st.set_page_config(page_title="Team Muniz - Agenda", layout="wide", page_icon="📅")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3 { color: #D4AF37 !important; text-align: center; }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: #111111;
        border: 1px solid #333;
        border-radius: 5px;
        color: white;
        padding: 10px 20px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold;
    }
    .card-aluno {
        background-color: #111111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #D4AF37;
        margin-top: 10px;
    }
    .stLinkButton>a {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO DOS DADOS
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        
        # Filtra apenas Pendentes e limpa espaços
        df = df[df['status'].str.lower().str.strip() == 'pendente']
        df['vencimento'] = df['vencimento'].astype(str).str.strip()
        return df
    except:
        return None

df = carregar_dados()

st.title("📅 AGENDA DE COBRANÇA")
st.markdown("---")

if df is not None and not df.empty:
    # Datas únicas para os botões
    datas_disponiveis = sorted(df['vencimento'].unique())
    tabs = st.tabs(datas_disponiveis)
    
    for i, data in enumerate(datas_disponiveis):
        with tabs[i]:
            st.subheader(f"Vencimentos em {data}")
            alunos_do_dia = df[df['vencimento'] == data]
            
            for _, row in alunos_do_dia.iterrows():
                # Ao clicar no nome (vencimento), abre os detalhes do aluno
                with st.expander(f"👤 {row['aluno']} | {row['valor']}", expanded=False):
                    st.markdown(f"""
                    <div class="card-aluno">
                        <p><b>Pacote:</b> {row['pacote']}</p>
                        <p><b>Valor:</b> {row['valor']}</p>
                        <p><b>Chave Pix:</b> {row['chave_pix']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # MENSAGEM COM O TOM SOLICITADO
                    msg_formal = (
                        f"*Mensagem automática MFIT | Team Muniz*\n\n"
                        f"Seu pagamento com vencimento em *{data}*, no valor de *{row['valor']}*, encontra-se pendente.\n\n"
                        f"Para continuidade do seu acompanhamento e acesso à sua estratégia personalizada, é necessária a regularização.\n\n"
                        f"Chave Pix: *{row['chave_pix']}*"
                    )
                    
                    link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg_formal)}"
                    
                    st.write("")
                    st.link_button(f"🚀 ENVIAR COBRANÇA FORMAL", link_wpp)

else:
    st.success("✅ Nenhuma cobrança pendente!")

st.markdown("---")
st.markdown("<p style='text-align: center; color: #D4AF37;'>Sem estratégia, esforço vira tentativa.</p>", unsafe_allow_html=True)
