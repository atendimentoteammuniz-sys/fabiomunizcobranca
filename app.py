import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

# 1. ESTILO TEAM MUNIZ (DESIGN LIMPO E DIRETO)
st.set_page_config(page_title="Team Muniz - Cobrança", layout="wide", page_icon="📲")

st.markdown("""
    <style>
    .main { background-color: #000000; }
    h1, h2, h3 { color: #D4AF37 !important; }
    .card-aluno {
        background-color: #111111;
        padding: 10px 15px;
        border-radius: 8px;
        border-left: 4px solid #D4AF37;
        margin-bottom: 5px;
    }
    .stLinkButton>a {
        background-color: #D4AF37 !important;
        color: black !important;
        font-weight: bold !important;
        border-radius: 4px !important;
        height: 35px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    div[data-testid="stMetricValue"] { color: #D4AF37 !important; font-size: 24px !important; }
    hr { border: 0.1px solid #333; }
    </style>
    """, unsafe_allow_html=True)

# 2. PROCESSAMENTO DE DADOS
def carregar_dados():
    try:
        url_base = st.secrets["LINK_PLANILHA"]
        url_csv = url_base.replace("/edit?usp=sharing", "/export?format=csv&gid=2123746860")
        df = pd.read_csv(url_csv)
        
        # Ajuste de cabeçalhos conforme sua planilha
        if len(df.columns) >= 7:
            df.columns = ['aluno', 'whatsapp', 'valor', 'vencimento', 'status', 'pacote', 'chave_pix']
        
        # Tratamento de data para ordenação
        df['venc_dt'] = pd.to_datetime(df['vencimento'], dayfirst=True, errors='coerce')
        return df.sort_values(by='venc_dt') # Organiza do mais antigo para o mais novo
    except Exception as e:
        st.error(f"Erro ao carregar: {e}")
        return None

df = carregar_dados()

if df is not None:
    # --- RESUMO NO TOPO ---
    hoje = datetime.now().date()
    pendentes_total = df[df['status'].str.lower().str.strip() == 'pendente']
    vencem_hoje = pendentes_total[pendentes_total['venc_dt'].dt.date == hoje]
    
    st.title("🏆 LISTA DE COBRANÇA")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Vencem Hoje", len(vencem_hoje))
    m2.metric("Total Pendentes", len(pendentes_total))
    
    # Cálculo rápido de valor total pendente
    try:
        total_valor = pendentes_total['valor'].str.replace('R$ ', '').str.replace('.', '').str.replace(',', '.').astype(float).sum()
        m3.metric("Total R$", f"R$ {total_valor:,.2f}")
    except:
        m3.metric("Total R$", "---")
    
    st.markdown("---")

    # --- LISTA ÚNICA ---
    if pendentes_total.empty:
        st.success("✅ Nenhum aluno pendente na lista!")
    else:
        for _, row in pendentes_total.iterrows():
            # Define se é destaque (vence hoje)
            eh_hoje = "⭐ " if row['venc_dt'].date() == hoje else ""
            
            with st.container():
                col_info, col_btn = st.columns([4, 1])
                
                with col_info:
                    # Layout compacto: Nome | Vencimento | Valor
                    st.markdown(f"""
                    <div class="card-aluno">
                        <span style="color:white; font-weight:bold;">{eh_hoje}{row['aluno']}</span><br>
                        <span style="color:gray; font-size:14px;">Venc: {row['vencimento']} | {row['pacote']} | </span>
                        <span style="color:#D4AF37; font-size:14px;"><b>{row['valor']}</b></span>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col_btn:
                    primeiro_nome = str(row['aluno']).split()[0]
                    msg = (
                        f"Fala, {primeiro_nome}! 🏆\n\n"
                        f"Aqui é o Fábio da *Team Muniz*.\n"
                        f"O plano *{row['pacote']}* ({row['vencimento']}) está pendente.\n\n"
                        f"Pix: *{row['chave_pix']}*\n\n"
                        "Me envia o comprovante? 🔥"
                    )
                    link_wpp = f"https://wa.me/{row['whatsapp']}?text={urllib.parse.quote(msg)}"
                    st.write("") # Alinhamento vertical
                    st.link_button(f"📲 Cobrar", link_wpp)

else:
    st.info("💡 Verifique se a planilha está configurada corretamente.")
