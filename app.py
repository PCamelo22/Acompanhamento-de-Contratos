# ─────────────────────────────────────────────────────────────────────────────
# app.py — Acompanhamento de Contratos v2.0
# ─────────────────────────────────────────────────────────────────────────────

import time
import streamlit as st
from datetime import datetime
from config import (
    APP_NOME, APP_VERSAO, APP_LOGO,
    ADMIN_SENHA, CORES,
    TV_COLS, TV_ROWS, TV_CARDS_POR_TELA, TV_ROTACAO_SEG, TV_CARD_VAZIO,
)
from data import carregar_dados, resumo_orgao, fmt_num, fmt_mes
from graficos import grafico_barras, grafico_rosca

st.set_page_config(
    page_title=APP_NOME,
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

BG      = CORES['bg']
SURFACE = CORES['surface']
BORDER  = CORES['border']
ACCENT  = CORES['accent']
ACCENT2 = CORES['accent2']
BLUE    = CORES['blue']
TEXTO   = CORES['texto']
MUTED   = CORES['muted']
VERDE   = CORES['verde']
AMARELO = CORES['amarelo']
VERM    = CORES['vermelho']

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {{
  font-family: 'DM Sans', sans-serif !important;
  background-color: {BG} !important;
  color: {TEXTO} !important;
}}
.block-container {{ padding: 1.5rem 2rem !important; }}
#MainMenu, footer, header {{ visibility: hidden; }}

/* Partículas / grid animado */
.stApp::before {{
  content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 0;
  background-image:
    linear-gradient(rgba(59,130,246,.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(59,130,246,.04) 1px, transparent 1px);
  background-size: 40px 40px;
  animation: gridMove 20s linear infinite;
}}
@keyframes gridMove {{
  0% {{ background-position: 0 0; }}
  100% {{ background-position: 40px 40px; }}
}}

/* Glassmorphism card */
.card-glass {{
  background: rgba(17,24,39,0.75);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 16px;
  padding: 20px;
  margin-bottom: 6px;
  position: relative;
  overflow: hidden;
  box-shadow: 0 8px 32px rgba(0,0,0,.4), inset 0 1px 0 rgba(255,255,255,.05);
  transition: all .3s ease;
}}
.card-glass::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, {ACCENT}, {BLUE}, transparent);
}}
.card-glass:hover {{
  border-color: rgba(59,130,246,0.5);
  box-shadow: 0 0 20px rgba(59,130,246,.15), 0 8px 32px rgba(0,0,0,.4);
  transform: translateY(-2px);
}}

/* Neon status */
.neon-verde {{ box-shadow: 0 0 12px rgba(16,185,129,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(16,185,129,.4) !important; }}
.neon-amarelo {{ box-shadow: 0 0 12px rgba(245,158,11,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(245,158,11,.4) !important; }}
.neon-vermelho {{ box-shadow: 0 0 12px rgba(239,68,68,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(239,68,68,.4) !important; animation: pulse-red 2s infinite; }}
@keyframes pulse-red {{
  0%, 100% {{ box-shadow: 0 0 12px rgba(239,68,68,.3); }}
  50% {{ box-shadow: 0 0 24px rgba(239,68,68,.6); }}
}}

/* Card TV */
.card-tv {{
  background: rgba(17,24,39,0.8);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(59,130,246,0.25);
  border-radius: 20px; padding: 20px;
  position: relative; overflow: hidden; min-height: 220px;
  box-shadow: 0 8px 32px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.05);
  transition: all .3s ease;
}}
.card-tv::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, {ACCENT}, {BLUE}, transparent);
}}
.card-tv:hover {{
  border-color: rgba(59,130,246,.5);
  box-shadow: 0 0 24px rgba(59,130,246,.2), 0 8px 32px rgba(0,0,0,.5);
}}

/* Card vazio */
.card-vazio {{
  background: rgba(17,24,39,.3); border: 1px dashed rgba(59,130,246,.15);
  border-radius: 20px; padding: 24px;
  display: flex; align-items: center; justify-content: center;
  min-height: 220px; color: {MUTED};
  font-family: DM Mono, monospace; font-size: 13px;
}}

/* Metric card */
.metric-card {{
  background: rgba(17,24,39,0.75);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 14px; padding: 18px 20px;
  position: relative; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.04);
  display: flex; align-items: center; gap: 16px;
}}
.metric-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, {ACCENT}, transparent);
}}
.metric-icon {{
  font-size: 32px; opacity: .85; flex-shrink: 0;
  filter: drop-shadow(0 0 8px currentColor);
}}
.metric-info {{ flex: 1; }}
.metric-label {{
  font-family: DM Mono, monospace; font-size: 10px; color: {MUTED};
  text-transform: uppercase; letter-spacing: .1em; margin-bottom: 4px;
}}
.metric-value {{
  font-size: 24px; font-weight: 800; line-height: 1;
  font-variant-numeric: tabular-nums;
}}
.metric-unit {{ font-size: 13px; font-weight: 400; color: {MUTED}; margin-left: 4px; }}
.metric-sub {{ font-family: DM Mono, monospace; font-size: 10px; color: {MUTED}; margin-top: 4px; }}
.metric-trend {{ font-size: 12px; margin-top: 3px; }}

/* Banner status */
.status-banner {{
  border-radius: 14px; padding: 20px 28px; margin-bottom: 20px;
  text-align: center; position: relative; overflow: hidden;
  border: 1px solid rgba(59,130,246,.3);
  background: linear-gradient(135deg, rgba(17,24,39,.9), rgba(26,34,54,.9));
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 24px rgba(0,0,0,.3);
}}
.status-banner-title {{
  font-size: 22px; font-weight: 800; letter-spacing: .05em;
  text-transform: uppercase; margin-bottom: 4px;
}}
.status-banner-sub {{
  font-family: DM Mono, monospace; font-size: 12px; color: {MUTED};
}}

/* Produto tag */
.produto-tag {{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px;
  background: rgba(59,130,246,.1);
  border-left: 3px solid {ACCENT};
  border-radius: 0 8px 8px 0;
  font-family: DM Mono, monospace; font-size: 11px; color: {ACCENT2};
  text-transform: uppercase; letter-spacing: .1em; margin-bottom: 16px;
}}

/* Linha do tempo */
.timeline-wrap {{
  background: rgba(17,24,39,.6); border: 1px solid rgba(59,130,246,.15);
  border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;
}}
.timeline-bar {{
  height: 8px; background: rgba(31,46,74,.8); border-radius: 4px;
  overflow: hidden; margin: 8px 0;
}}
.timeline-fill {{
  height: 100%; border-radius: 4px;
  background: linear-gradient(90deg, {ACCENT}, {VERDE});
  transition: width .8s ease;
}}
.timeline-labels {{
  display: flex; justify-content: space-between;
  font-family: DM Mono, monospace; font-size: 10px; color: {MUTED};
}}

/* Ticker rodapé */
.ticker-wrap {{
  position: fixed; bottom: 0; left: 0; right: 0;
  background: rgba(10,14,26,.95); backdrop-filter: blur(8px);
  border-top: 1px solid rgba(59,130,246,.2);
  padding: 6px 0; z-index: 100; overflow: hidden;
}}
.ticker-content {{
  display: inline-block;
  white-space: nowrap;
  animation: ticker 60s linear infinite;
  font-family: DM Mono, monospace; font-size: 11px; color: {MUTED};
}}
@keyframes ticker {{
  0% {{ transform: translateX(100vw); }}
  100% {{ transform: translateX(-100%); }}
}}

/* Filtro ano */
.filtro-ano {{
  display: flex; gap: 8px; align-items: center; margin-bottom: 16px;
  font-family: DM Mono, monospace; font-size: 11px; color: {MUTED};
}}

/* Timer bar */
.timer-bar-bg {{
  background: rgba(31,46,74,.8); border-radius: 2px;
  height: 3px; width: 100%; overflow: hidden; margin-top: 6px;
}}

/* Relógio */
.relogio {{
  font-family: DM Mono, monospace; font-size: 13px;
  color: {MUTED}; letter-spacing: .05em;
}}

/* Botões */
.stButton > button {{
  background: rgba(59,130,246,.1) !important; color: {ACCENT2} !important;
  border: 1px solid rgba(59,130,246,.25) !important; border-radius: 8px !important;
  font-family: DM Mono, monospace !important; font-size: 12px !important;
  padding: 6px 16px !important; transition: all .2s !important;
  backdrop-filter: blur(4px) !important;
}}
.stButton > button:hover {{
  background: rgba(59,130,246,.2) !important;
  border-color: {ACCENT} !important;
  box-shadow: 0 0 12px rgba(59,130,246,.2) !important;
}}

/* Contador animado */
@keyframes countUp {{
  from {{ opacity: 0; transform: translateY(10px); }}
  to {{ opacity: 1; transform: translateY(0); }}
}}
.metric-value {{ animation: countUp .6s ease forwards; }}

/* Selectbox */
.stSelectbox > div > div {{
  background: rgba(17,24,39,.8) !important;
  border-color: rgba(59,130,246,.25) !important;
  color: {TEXTO} !important;
  backdrop-filter: blur(8px) !important;
}}

/* Dataframe */
.stDataFrame {{ border-radius: 12px; overflow: hidden; }}
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "dados": None, "ultima_atualizacao": None,
    "modo": "painel", "orgao_ativo": None,
    "tv_pagina": 0, "tv_ultimo_tick": time.time(),
    "tv_produto_idx": {}, "tv_produto_tick": {},
    "autenticado": False, "show_login": False,
    "detalhe_origem": "painel", "ano_filtro": "Todos",
    "orgao_selecionado": None,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────

def carregar():
    with st.spinner("Carregando dados..."):
        st.session_state.dados = carregar_dados()
        st.session_state.ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.rerun()

def ir_para(modo, orgao=None, origem=None):
    st.session_state.modo = modo
    if orgao: st.session_state.orgao_ativo = orgao
    if origem: st.session_state.detalhe_origem = origem
    st.rerun()

def autenticar(senha):
    if senha == ADMIN_SENHA:
        st.session_state.autenticado = True
        return True
    return False

def ts(): return st.session_state.ultima_atualizacao or "—"

def neon_class(pct):
    if pct >= 80: return "neon-verde"
    if pct >= 50: return "neon-amarelo"
    return "neon-vermelho"

def icone_produto(produto):
    p = produto.lower()
    if "digital" in p: return "🗂️"
    if "tratamento" in p or "arquiv" in p: return "📦"
    if "livro" in p or "scan" in p: return "📚"
    if "imagem" in p: return "🖼️"
    if "metro" in p: return "📏"
    if "planta" in p: return "🗺️"
    return "📄"

def icone_metrica(tipo, produto):
    p = produto.lower()
    digital = "digital" in p
    if tipo == "total":    return "🗂️" if digital else "📦"
    if tipo == "meta":     return "🎯"
    if tipo == "saldo":    return "⚖️"
    if tipo == "mensal":   return "📅"
    return "📄"

def unidade(produto):
    p = produto.lower()
    if "metro" in p: return "m/l"
    if "livro" in p or "scan" in p: return "livros"
    if "imagem" in p: return "imagens"
    return "docs"

def tendencia(rows):
    prod = [r["producao"] for r in rows if r["producao"] is not None]
    if len(prod) < 2: return ""
    diff = prod[-1] - prod[-2]
    if diff > 0: return f'<span style="color:{VERDE}">↑ {fmt_num(diff,0)}</span>'
    if diff < 0: return f'<span style="color:{VERM}">↓ {fmt_num(abs(diff),0)}</span>'
    return f'<span style="color:{MUTED}">→ estável</span>'

def previsao(total, meta, meta_m, rows):
    if not meta or not meta_m or total >= meta: return None
    prod_recentes = [r["producao"] for r in rows[-3:] if r["producao"]]
    if not prod_recentes: return None
    media = sum(prod_recentes) / len(prod_recentes)
    if media <= 0: return None
    meses = int((meta - total) / media)
    return meses

def melhor_mes_idx(rows):
    prods = [r["producao"] or 0 for r in rows]
    return prods.index(max(prods)) if prods else -1

def anos_disponiveis(rows):
    anos = set()
    for r in rows:
        if r["mes"]:
            try: anos.add(int(r["mes"][:4]))
            except: pass
    return sorted(anos)

def filtrar_por_ano(rows, ano):
    if ano == "Todos" or ano is None: return rows
    return [r for r in rows if r["mes"] and r["mes"][:4] == str(ano)]

def ticker_text(dados):
    parts = []
    for orgao, rows in dados.items():
        calcs = resumo_orgao(rows)
        for c in calcs:
            emoji = c["emoji"]
            parts.append(f"{emoji} {orgao} ({c['produto'][:4]}): {c['pct']}%")
    return "  ·  ".join(parts) + "  ·  "

# ── Card HTML builder ─────────────────────────────────────────────────────────

def build_card_html(orgao, calcs, css_class="card-glass"):
    pct_max = max((c["pct"] for c in calcs), default=0)
    neon = neon_class(pct_max)
    produtos_html = ""
    for c in calcs:
        pct = c["pct"]; cor = c["cor"]
        bar_w = min(100, pct)
        produtos_html += (
            f'<div style="margin-top:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase;display:flex;align-items:center;gap:6px">'
            f'{icone_produto(c["produto"])} {c["produto"]}</div>'
            f'<div style="font-size:12px;font-weight:700;color:{cor}">{c["emoji"]} {pct}%</div>'
            f'</div>'
            f'<div style="background:rgba(31,46,74,.8);border-radius:6px;height:8px;overflow:hidden">'
            f'<div style="width:{bar_w}%;background:{cor};height:100%;border-radius:6px;'
            f'box-shadow:0 0 8px {cor}40"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;font-family:DM Mono,monospace;font-size:10px;color:{MUTED};margin-top:3px">'
            f'<span>{c["fmt_total"]}</span><span>Meta: {c["fmt_meta"]}</span>'
            f'</div></div>'
        )
    return (
        f'<div class="{css_class} {neon}">'
        f'<div style="font-size:17px;font-weight:800;margin-bottom:2px">{orgao}</div>'
        f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">{len(calcs)} produto(s)</div>'
        f'{produtos_html}'
        f'</div>'
    )

# ── Metric card ───────────────────────────────────────────────────────────────

def metric_card(label, value, unit="", sub=None, cor=None, icone="📄", trend_html=""):
    cor_v = cor or TEXTO
    sub_h = f'<div class="metric-sub">{sub}</div>' if sub else ""
    trend_h = f'<div class="metric-trend">{trend_html}</div>' if trend_html else ""
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-icon">{icone}</div>'
        f'<div class="metric-info">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="color:{cor_v}">{value}'
        f'<span class="metric-unit">{unit}</span></div>'
        f'{sub_h}{trend_h}'
        f'</div></div>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────

def header(mostrar_nav=True):
    c1, c2, c3 = st.columns([2, 4, 3])
    with c1:
        logo_html = (
            f'<div style="display:flex;align-items:center;gap:12px">'
            f'<div style="width:44px;height:44px;background:linear-gradient(135deg,{BLUE},{ACCENT});'
            f'border-radius:10px;display:flex;align-items:center;justify-content:center;'
            f'font-size:20px;font-weight:800;color:#fff;'
            f'box-shadow:0 0 16px rgba(59,130,246,.4)">P</div>'
            f'<div>'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">Dashboard</div>'
            f'<div style="font-size:22px;font-weight:800">{APP_NOME}</div>'
            f'</div></div>'
        )
        st.markdown(logo_html, unsafe_allow_html=True)
    with c2:
        if mostrar_nav:
            b1, b2, b3, b4 = st.columns(4)
            with b1:
                if st.button("📊 Painel", key="btn_painel"): ir_para("painel")
            with b2:
                if st.button("📺 TV", key="btn_tv"): ir_para("tv")
            with b3:
                if st.button("🔄 Atualizar", key="btn_atualizar"):
                    if st.session_state.autenticado: carregar()
                    else: st.session_state.show_login = True; st.rerun()
    with c3:
        agora = datetime.now()
        st.markdown(
            f'<div style="text-align:right">'
            f'<div class="relogio">{agora.strftime("%H:%M:%S")}</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED}">'
            f'{agora.strftime("%d/%m/%Y")} · Atualizado: {ts()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.markdown(f"<hr style='border:none;border-top:1px solid rgba(59,130,246,.15);margin:14px 0 20px 0'>", unsafe_allow_html=True)

# ── Login ─────────────────────────────────────────────────────────────────────

def tela_login():
    _, col, _ = st.columns([1, 2, 1])
    with col:
        st.markdown(
            f'<div style="background:rgba(17,24,39,.85);backdrop-filter:blur(12px);'
            f'border:1px solid rgba(59,130,246,.25);border-radius:16px;padding:32px;'
            f'box-shadow:0 0 32px rgba(59,130,246,.1);margin-top:60px">'
            f'<div style="font-size:20px;font-weight:800;margin-bottom:4px">🔒 Acesso restrito</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};margin-bottom:24px">'
            f'Insira a senha para atualizar os dados</div></div>',
            unsafe_allow_html=True,
        )
        senha = st.text_input("Senha", type="password", label_visibility="collapsed", placeholder="Digite a senha...")
        if st.button("Entrar", use_container_width=True):
            if autenticar(senha): st.session_state.show_login = False; carregar()
            else: st.error("Senha incorreta.")
        if st.button("← Voltar", use_container_width=True):
            st.session_state.show_login = False; st.rerun()

# ── Modo Painel ───────────────────────────────────────────────────────────────

def modo_painel():
    header()
    dados = st.session_state.dados
    if not dados:
        st.info("Nenhum dado carregado. Clique em 🔄 Atualizar.")
        return

    orgaos = list(dados.keys())

    # Ordenar por melhor desempenho
    def pct_medio(org):
        calcs = resumo_orgao(dados[org])
        return sum(c["pct"] for c in calcs) / len(calcs) if calcs else 0
    orgaos_sorted = sorted(orgaos, key=pct_medio, reverse=True)

    st.markdown(
        f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};margin-bottom:16px">'
        f'📋 {len(orgaos)} CONTRATOS ATIVOS · ordenados por desempenho</div>',
        unsafe_allow_html=True,
    )

    for i in range(0, len(orgaos_sorted), 3):
        cols = st.columns(3)
        for j, col in enumerate(cols):
            idx = i + j
            if idx >= len(orgaos_sorted): break
            orgao = orgaos_sorted[idx]
            calcs = resumo_orgao(dados[orgao])
            with col:
                st.markdown(build_card_html(orgao, calcs), unsafe_allow_html=True)
                if st.button("Ver detalhes →", key=f"det_{idx}"):
                    ir_para("detalhe", orgao, "painel")

    # Ticker rodapé
    ticker = ticker_text(dados)
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-content">{ticker}</div></div>',
        unsafe_allow_html=True,
    )

# ── Modo TV ───────────────────────────────────────────────────────────────────

def modo_tv():
    dados = st.session_state.dados
    if not dados:
        st.warning("Sem dados.")
        if st.button("← Voltar"): ir_para("painel")
        return

    orgaos      = list(dados.keys())
    total_pag   = -(-len(orgaos) // TV_CARDS_POR_TELA)
    agora       = time.time()

    # Rotação automática de tela
    if agora - st.session_state.tv_ultimo_tick >= TV_ROTACAO_SEG:
        st.session_state.tv_pagina      = (st.session_state.tv_pagina + 1) % total_pag
        st.session_state.tv_ultimo_tick = agora

    pagina      = st.session_state.tv_pagina
    inicio      = pagina * TV_CARDS_POR_TELA
    orgaos_tela = orgaos[inicio:inicio + TV_CARDS_POR_TELA]
    elapsed     = agora - st.session_state.tv_ultimo_tick
    rest_pct    = max(0, (1 - elapsed / TV_ROTACAO_SEG)) * 100
    rest_seg    = max(0, int(TV_ROTACAO_SEG - elapsed))

    # Header TV
    c1, c2, c3 = st.columns([3, 4, 3])
    with c1:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:12px">'
            f'<div style="width:36px;height:36px;background:linear-gradient(135deg,{BLUE},{ACCENT});'
            f'border-radius:8px;display:flex;align-items:center;justify-content:center;'
            f'font-weight:800;font-size:16px;color:#fff;box-shadow:0 0 12px rgba(59,130,246,.4)">P</div>'
            f'<div>'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">Modo Apresentação</div>'
            f'<div style="font-size:15px;font-weight:800">{APP_NOME}</div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">'
            f'Tela {pagina+1} de {total_pag} · próxima em {rest_seg}s</div>'
            f'<div class="timer-bar-bg">'
            f'<div style="height:3px;background:{ACCENT};border-radius:2px;width:{rest_pct}%;'
            f'box-shadow:0 0 6px {ACCENT}"></div></div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        # Menu suspenso de contratos
        col_sel, col_nav = st.columns([3, 1])
        with col_sel:
            sel = st.selectbox(
                "Ir para contrato",
                ["— Selecionar —"] + orgaos,
                key="tv_select",
                label_visibility="collapsed",
            )
            if sel != "— Selecionar —":
                idx_sel = orgaos.index(sel)
                st.session_state.tv_pagina = idx_sel // TV_CARDS_POR_TELA
                st.session_state.tv_ultimo_tick = time.time()
                st.rerun()
        with col_nav:
            cs, ce = st.columns(2)
            with cs:
                if st.button("✕", key="tv_sair"): ir_para("painel")

    st.markdown(f"<div style='border-top:1px solid rgba(59,130,246,.15);margin:10px 0 18px 0'></div>", unsafe_allow_html=True)

    # Grid 2x2
    rows_tv = [orgaos_tela[i:i+TV_COLS] for i in range(0, len(orgaos_tela), TV_COLS)]
    while len(rows_tv) < TV_ROWS: rows_tv.append([])

    for row_orgaos in rows_tv:
        cols = st.columns(TV_COLS)
        for ci in range(TV_COLS):
            with cols[ci]:
                if ci < len(row_orgaos):
                    orgao = row_orgaos[ci]
                    calcs = resumo_orgao(dados[orgao])
                    _card_tv_completo(orgao, calcs, agora)
                else:
                    st.markdown(f'<div class="card-vazio">{TV_CARD_VAZIO}</div>', unsafe_allow_html=True)

    # Ticker
    ticker = ticker_text(dados)
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-content">{ticker}</div></div>',
        unsafe_allow_html=True,
    )

    time.sleep(1)
    st.rerun()

def _card_tv_completo(orgao, calcs, agora):
    """Card TV com gráficos, alternância de produto a cada 10s."""
    if not calcs: return

    # Rotação de produto
    key_idx  = f"tv_prod_idx_{orgao}"
    key_tick = f"tv_prod_tick_{orgao}"
    if key_idx  not in st.session_state: st.session_state[key_idx]  = 0
    if key_tick not in st.session_state: st.session_state[key_tick] = agora

    if agora - st.session_state[key_tick] >= 10:
        st.session_state[key_idx]  = (st.session_state[key_idx] + 1) % len(calcs)
        st.session_state[key_tick] = agora

    idx = st.session_state[key_idx] % len(calcs)
    c   = calcs[idx]
    cor = c["cor"]
    pct = c["pct"]
    neon = neon_class(pct)

    # Indicador de produto (pontos)
    dots = "".join(
        f'<span style="display:inline-block;width:7px;height:7px;border-radius:50%;'
        f'background:{"#3b82f6" if i==idx else "rgba(59,130,246,.2)"};margin:0 2px"></span>'
        for i in range(len(calcs))
    )

    st.markdown(
        f'<div class="card-tv {neon}">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:6px">'
        f'<div>'
        f'<div style="font-size:17px;font-weight:800">{orgao}</div>'
        f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};display:flex;align-items:center;gap:6px;margin-top:2px">'
        f'{icone_produto(c["produto"])} {c["produto"]}</div>'
        f'</div>'
        f'<div style="text-align:right">'
        f'<div style="font-size:22px;font-weight:800;color:{cor};text-shadow:0 0 12px {cor}40">{pct}%</div>'
        f'<div>{dots}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    # Gráficos
    col_bar, col_donut = st.columns([3, 2])
    with col_bar:
        st.plotly_chart(grafico_barras(c), use_container_width=True, config={"displayModeBar": False})
    with col_donut:
        st.plotly_chart(grafico_rosca(c), use_container_width=True, config={"displayModeBar": False})

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button(f"Ver {orgao}", key=f"tv_det_{orgao}"):
        ir_para("detalhe", orgao, "tv")

# ── Modo Detalhe ──────────────────────────────────────────────────────────────

def modo_detalhe():
    orgao = st.session_state.orgao_ativo
    dados = st.session_state.dados
    if not orgao or not dados or orgao not in dados:
        ir_para("painel"); return

    c1, c2 = st.columns([6, 1])
    with c1:
        st.markdown(
            f'<div style="margin-bottom:16px">'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">Acompanhamento de Contratos</div>'
            f'<div style="font-size:28px;font-weight:800">{orgao}</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">Última Atualização: {ts()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        origem = st.session_state.detalhe_origem
        label  = "📺 TV" if origem == "tv" else "← Painel"
        if st.button(label, key="btn_voltar"): ir_para(origem)

    st.markdown(f"<div style='border-top:1px solid rgba(59,130,246,.15);margin-bottom:20px'></div>", unsafe_allow_html=True)

    rows_all = dados[orgao]
    calcs_all = resumo_orgao(rows_all)

    for c_full in calcs_all:
        produto  = c_full["produto"]
        cor      = c_full["cor"]
        pct_full = c_full["pct"]
        neon     = neon_class(pct_full)

        # ── Filtro de ano ──
        anos = ["Todos"] + [str(a) for a in anos_disponiveis(c_full["rows"])]
        col_tag, col_ano = st.columns([3, 1])
        with col_tag:
            st.markdown(
                f'<div class="produto-tag">{icone_produto(produto)} {produto}</div>',
                unsafe_allow_html=True,
            )
        with col_ano:
            ano_sel = st.selectbox(
                "Ano", anos,
                key=f"ano_{orgao}_{produto}",
                label_visibility="collapsed",
            )

        # Recalcular com filtro de ano
        rows_f = filtrar_por_ano(c_full["rows"], None if ano_sel == "Todos" else ano_sel)
        from data import calcular
        c = calcular(c_full["rows"], produto)  # métricas globais
        c_f = calcular(rows_f, produto) if rows_f else c  # métricas filtradas p/ gráficos

        uni = unidade(produto)

        # ── Banner status ──
        status_txt = "EM ANDAMENTO"
        if c["saldo"] and c["saldo"] <= 0: status_txt = "CONCLUÍDO ✅"
        elif c["pct"] < 50: status_txt = "ATENÇÃO ⚠️"

        periodo = ""
        if c["rows"]:
            anos_list = [r["mes"][:4] for r in c["rows"] if r["mes"]]
            if anos_list:
                periodo = f"{min(anos_list)} - {max(anos_list)}"

        st.markdown(
            f'<div class="status-banner {neon}">'
            f'<div class="status-banner-title" style="color:{cor}">STATUS DO CONTRATO {orgao}: {status_txt}</div>'
            f'<div class="status-banner-sub">{produto} · {pct_full}% Concluído · Período: {periodo}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # ── Linha do tempo ──
        if c["rows"]:
            n_preenchidos = sum(1 for r in c["rows"] if r["producao"] is not None)
            pct_tempo     = round((n_preenchidos / len(c["rows"])) * 100, 1)
            mes_inicio    = fmt_mes(c["rows"][0]["mes"])
            mes_fim       = fmt_mes(c["rows"][-1]["mes"])
            st.markdown(
                f'<div class="timeline-wrap">'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase;margin-bottom:6px">Linha do Tempo do Contrato</div>'
                f'<div class="timeline-labels"><span>{mes_inicio}</span><span style="color:{cor}">{n_preenchidos} de {len(c["rows"])} entregas · {pct_tempo}%</span><span>{mes_fim}</span></div>'
                f'<div class="timeline-bar"><div class="timeline-fill" style="width:{pct_tempo}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── 4 Metric cards ──
        trend_h = tendencia(c["rows"])
        prev    = previsao(c["total"], c["meta"], c["meta_mensal"], c["rows"])
        prev_txt = f"~{prev} meses p/ concluir" if prev else ""

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card(
                f"Total Produzido ({produto[:4]}...)",
                c["fmt_total"], uni,
                f'{c["duracao"]} meses de contrato',
                icone=icone_metrica("total", produto),
                trend_html=trend_h,
            )
        with col2:
            metric_card(
                "Meta Contratual Total", c["fmt_meta"], uni,
                "(Total do Contrato)",
                icone=icone_metrica("meta", produto),
            )
        with col3:
            sub3 = "✅ Meta batida!" if c["saldo"] and c["saldo"] <= 0 else "(Ainda Faltam)"
            metric_card(
                "Saldo Remanescente", c["fmt_saldo"], uni,
                sub3, cor,
                icone=icone_metrica("saldo", produto),
            )
        with col4:
            metric_card(
                "Meta Mensal Média", c["fmt_meta_m"], uni,
                prev_txt or f'(Média em {c["duracao"]} meses)',
                icone=icone_metrica("mensal", produto),
            )

        st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

        # ── Gráficos ──
        melhor = melhor_mes_idx(c_f["rows"])
        col_bar, col_donut = st.columns([3, 1])
        with col_bar:
            st.markdown(
                f'<div style="background:rgba(17,24,39,.75);backdrop-filter:blur(12px);'
                f'border:1px solid rgba(59,130,246,.2);border-radius:14px;padding:18px;'
                f'box-shadow:0 4px 20px rgba(0,0,0,.3)">'
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};text-transform:uppercase;margin-bottom:4px">'
                f'Histórico Mensal de Produção ({produto})</div>'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};margin-bottom:10px">Período: {periodo}{" · " + ano_sel if ano_sel != "Todos" else ""}</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafico_barras(c_f, melhor_idx=melhor), use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        with col_donut:
            st.markdown(
                f'<div style="background:rgba(17,24,39,.75);backdrop-filter:blur(12px);'
                f'border:1px solid rgba(59,130,246,.2);border-radius:14px;padding:18px;'
                f'box-shadow:0 4px 20px rgba(0,0,0,.3)">'
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};text-transform:uppercase;margin-bottom:10px">% da Meta Contratual</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafico_rosca(c), use_container_width=True, config={"displayModeBar": False})
            st.markdown(
                f'<div style="text-align:center;font-size:14px;font-weight:700;color:{cor};margin-top:4px">{c["status"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

        # ── Tabela ──
        import pandas as pd
        meta_m = c_f["meta_mensal"] or 0
        acum   = 0
        melhor_prod = max((r["producao"] or 0 for r in c_f["rows"]), default=0)
        rows_t = []
        for r in c_f["rows"]:
            acum  += r["producao"] or 0
            prod   = r["producao"]
            status = "✅ Atingiu" if prod and prod >= meta_m else ("— Pendente" if prod is None else "⚠️ Abaixo")
            badge  = "🏆 Melhor mês" if prod and prod == melhor_prod else ""
            rows_t.append({
                "Entrega":     r["entrega"] or "—",
                "Mês":         fmt_mes(r["mes"]),
                "Produção":    fmt_num(prod, 2) if prod is not None else "—",
                "Meta Mensal": fmt_num(meta_m, 2),
                "Acumulado":   fmt_num(acum, 2),
                "Status":      status,
                "Destaque":    badge,
            })

        st.markdown(
            f'<div style="background:rgba(17,24,39,.75);backdrop-filter:blur(12px);'
            f'border:1px solid rgba(59,130,246,.2);border-radius:14px;padding:18px;'
            f'box-shadow:0 4px 20px rgba(0,0,0,.3)">'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};text-transform:uppercase;margin-bottom:12px">Detalhamento Mensal</div>',
            unsafe_allow_html=True,
        )
        df = pd.DataFrame(rows_t)
        st.dataframe(df, use_container_width=True, hide_index=True, height=min(400, len(rows_t)*36+40))
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:36px'></div>", unsafe_allow_html=True)

# ── Init ──────────────────────────────────────────────────────────────────────

if st.session_state.dados is None:
    with st.spinner("Carregando dados..."):
        st.session_state.dados = carregar_dados()
        st.session_state.ultima_atualizacao = datetime.now().strftime("%d/%m/%Y %H:%M")

# ── Roteamento ────────────────────────────────────────────────────────────────

if st.session_state.show_login:
    tela_login()
elif st.session_state.modo == "tv":
    modo_tv()
elif st.session_state.modo == "detalhe":
    modo_detalhe()
else:
    modo_painel()