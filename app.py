import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. ESTILO TEAM MUNIZ (FOCO EM PERFORMANCE)
st.set_page_config(page_title="Team Muniz - Cobrança", layout="wide", page_icon="📲")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .card-aluno {
        background-color: #111111;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #333;
        margin-bottom: 10px;
    }
    .stLinkButton>a {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        width: 100%;
    }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; }
    </style>
    """, unsafe_allow_html=True)

# 2. CARREGAMENTO E TRATAMENTO DOS DADOS
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        
        # Ajuste de colunas baseado no seu envio
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        
        # Converte vencimento para data real para podermos filtrar
        df['vencimento_dt'] = pd.to_datetime(df['vencimento'], dayfirst=True, errors='coerce')
        return df
    except Exception as e:
        st.error(f"Erro: {e}")
        return None

df = carregar_dados()

if df is not None:
    # --- BARRA SUPERIOR (COBRANÇAS DO DIA) ---
    hoje = datetime.now().date()
    df_hoje = df[(df['vencimento_dt'].dt.date == hoje) & (df['status'].str.lower().str.strip() == 'pendente')]
    
    st.title("🏆 CENTRAL TEAM MUNIZ")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Pendentes Hoje", len(df_hoje))
    c2.metric("Valor Hoje", f"R$ {df_hoje['valor'].str.replace('R$ ', '').str.replace(',', '.').astype(float).sum():.2f}" if not df_hoje.empty else "R$ 0,00")
    c3.metric("Total Geral", len(df[df['status'].str.lower().str.strip() == 'pendente']))
    
    st.divider()

    # --- FILTRO POR DATA ---
    col_f1, col_f2 = st.columns([1, 2])
    with col_f1:
        data_filtro = st.date_input("Filtrar por data de vencimento:", hoje)
    
    # --- LISTA DE ALUNOS ---
    # Filtra os dados com base na data selecionada e status pendente
    pendentes_filtrados = df[(df['vencimento_dt'].dt.date == data_filtro) & (df['status'].str.lower().str.strip() == 'pendente')]

    if pendentes_filtrados.empty:
        st.info(f"Nenhuma pendência para o dia {data_filtro.strftime('%d/%m/%Y')}")
    else:
        for _, row in pendentes_filtrados.iterrows():
            with st.container():
                # Layout: Nome e Info na esquerda, Botão na direita
                col_info, col_btn = st.columns([3, 1])
                
                with col_info:
                    st.markdown(f"**{row['aluno']}** | {row['pacote']} | <span style='color:#D4AF37;'>{row['valor']}</span>", unsafe_allow_html=True)
                
                with col_btn:
                    primeiro_nome = str(row['aluno']).split()[0]
                    msg = (
                        f"Fala, {primeiro_nome}! 🏆\n\n"
                        f"Aqui é o Fábio da *Team Muniz*.\n"
                        f"O plano *{row['pacote']}* venceu dia {row['vencimento']}.\n\n"
                        f"Chave Pix: *{row['chave_pix']}*\n"
                        "Me envia o comprovante? 🔥"
                    )
                    link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg)}"
                    st.link_button(f"📲 Cobrar", link_wpp)
                st.divider()
else:
    st.info("Conecte sua planilha para começar.")
