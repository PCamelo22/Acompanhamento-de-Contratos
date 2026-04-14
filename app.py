# ─────────────────────────────────────────────────────────────────────────────
# app.py — Acompanhamento de Contratos v2.0
# MF Inclusão · Criado por Pablo Camelo
# ─────────────────────────────────────────────────────────────────────────────

import time
import base64
import streamlit as st
from datetime import datetime
import pytz
from config import (
    APP_NOME, APP_VERSAO, APP_LOGO,
    ADMIN_SENHA, CORES,
    TV_COLS, TV_ROWS, TV_CARDS_POR_TELA, TV_ROTACAO_SEG, TV_CARD_VAZIO,
)
from data import carregar_dados, resumo_orgao, calcular, fmt_num, fmt_mes
from graficos import grafico_barras, grafico_rosca

st.set_page_config(
    page_title="Acompanhamento de Contratos · MF Inclusão",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

TZ      = pytz.timezone("America/Sao_Paulo")
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

# ── Logo base64 ───────────────────────────────────────────────────────────────
def get_logo_b64():
    try:
        with open("logo.png", "rb") as f:
            return base64.b64encode(f.read()).decode()
    except:
        return None

LOGO_B64 = get_logo_b64()

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

/* Grid animado */
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

/* ── Splash screen ── */
.splash {{
  position: fixed; inset: 0; z-index: 9999;
  background: {BG};
  display: flex; flex-direction: column;
  align-items: center; justify-content: center; gap: 20px;
  animation: splashFade 0.5s ease 2.5s forwards;
}}
@keyframes splashFade {{
  from {{ opacity: 1; pointer-events: all; }}
  to   {{ opacity: 0; pointer-events: none; }}
}}
.splash-logo {{
  width: 140px; height: 140px; border-radius: 24px;
  box-shadow: 0 0 60px rgba(59,130,246,.5), 0 0 120px rgba(59,130,246,.2);
  animation: logoGlow 2s ease-in-out infinite alternate;
}}
@keyframes logoGlow {{
  from {{ box-shadow: 0 0 40px rgba(59,130,246,.4); }}
  to   {{ box-shadow: 0 0 80px rgba(59,130,246,.8), 0 0 140px rgba(59,130,246,.3); }}
}}
.splash-title {{
  font-size: 28px; font-weight: 800; color: {TEXTO};
  letter-spacing: .04em; text-align: center;
  animation: fadeUp .8s ease .3s both;
}}
.splash-sub {{
  font-size: 16px; font-weight: 600; color: {ACCENT2};
  letter-spacing: .08em; text-align: center;
  animation: fadeUp .8s ease .5s both;
}}
.splash-credit {{
  font-family: DM Mono, monospace; font-size: 11px; color: {MUTED};
  letter-spacing: .1em; text-align: center;
  animation: fadeUp .8s ease .7s both;
  margin-top: 8px;
}}
.splash-bar {{
  width: 200px; height: 2px; background: rgba(59,130,246,.2);
  border-radius: 2px; overflow: hidden; margin-top: 4px;
  animation: fadeUp .8s ease .6s both;
}}
.splash-bar-fill {{
  height: 100%; background: linear-gradient(90deg, {ACCENT}, {VERDE});
  border-radius: 2px; animation: loadBar 2.5s ease forwards;
}}
@keyframes loadBar {{
  from {{ width: 0%; }}
  to   {{ width: 100%; }}
}}
@keyframes fadeUp {{
  from {{ opacity: 0; transform: translateY(16px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Glassmorphism */
.card-glass {{
  background: rgba(17,24,39,0.75);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2); border-radius: 16px;
  padding: 20px; margin-bottom: 6px; position: relative; overflow: hidden;
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
.neon-verde   {{ box-shadow: 0 0 12px rgba(16,185,129,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(16,185,129,.4) !important; }}
.neon-amarelo {{ box-shadow: 0 0 12px rgba(245,158,11,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(245,158,11,.4) !important; }}
.neon-vermelho {{ box-shadow: 0 0 12px rgba(239,68,68,.3), 0 8px 32px rgba(0,0,0,.4); border-color: rgba(239,68,68,.4) !important; animation: pulseRed 2s infinite; }}
@keyframes pulseRed {{
  0%,100% {{ box-shadow: 0 0 12px rgba(239,68,68,.3); }}
  50%     {{ box-shadow: 0 0 28px rgba(239,68,68,.6); }}
}}

/* Card TV fullscreen */
.card-tv-full {{
  background: rgba(17,24,39,0.85);
  backdrop-filter: blur(16px); border: 1px solid rgba(59,130,246,.25);
  border-radius: 20px; padding: 28px; position: relative; overflow: hidden;
  box-shadow: 0 8px 40px rgba(0,0,0,.5), inset 0 1px 0 rgba(255,255,255,.05);
}}
.card-tv-full::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, {ACCENT}, {BLUE}, transparent);
}}

/* Metric card */
.metric-card {{
  background: rgba(17,24,39,0.75); backdrop-filter: blur(12px);
  border: 1px solid rgba(59,130,246,0.2); border-radius: 14px;
  padding: 18px 20px; position: relative; overflow: hidden;
  box-shadow: 0 4px 20px rgba(0,0,0,.3), inset 0 1px 0 rgba(255,255,255,.04);
  display: flex; align-items: center; gap: 16px;
}}
.metric-card::before {{
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 2px;
  background: linear-gradient(90deg, {ACCENT}, transparent);
}}
.metric-icon {{ font-size: 32px; opacity: .85; flex-shrink: 0; }}
.metric-info {{ flex: 1; }}
.metric-label {{ font-family: DM Mono, monospace; font-size: 10px; color: {MUTED}; text-transform: uppercase; letter-spacing: .1em; margin-bottom: 4px; }}
.metric-value {{ font-size: 24px; font-weight: 800; line-height: 1; animation: countUp .6s ease; }}
.metric-unit  {{ font-size: 13px; font-weight: 400; color: {MUTED}; margin-left: 4px; }}
.metric-sub   {{ font-family: DM Mono, monospace; font-size: 10px; color: {MUTED}; margin-top: 4px; }}
.metric-trend {{ font-size: 12px; margin-top: 3px; }}
@keyframes countUp {{
  from {{ opacity: 0; transform: translateY(8px); }}
  to   {{ opacity: 1; transform: translateY(0); }}
}}

/* Banner status */
.status-banner {{
  border-radius: 14px; padding: 20px 28px; margin-bottom: 20px;
  text-align: center; position: relative; overflow: hidden;
  border: 1px solid rgba(59,130,246,.3);
  background: linear-gradient(135deg, rgba(17,24,39,.9), rgba(26,34,54,.9));
  backdrop-filter: blur(12px);
  box-shadow: 0 4px 24px rgba(0,0,0,.3);
}}
.status-banner-title {{ font-size: 22px; font-weight: 800; letter-spacing: .05em; text-transform: uppercase; margin-bottom: 4px; }}
.status-banner-sub   {{ font-family: DM Mono, monospace; font-size: 12px; color: {MUTED}; }}

/* Produto tag */
.produto-tag {{
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 14px; background: rgba(59,130,246,.1);
  border-left: 3px solid {ACCENT}; border-radius: 0 8px 8px 0;
  font-family: DM Mono, monospace; font-size: 11px; color: {ACCENT2};
  text-transform: uppercase; letter-spacing: .1em; margin-bottom: 16px;
}}

/* Linha do tempo */
.timeline-wrap {{
  background: rgba(17,24,39,.6); border: 1px solid rgba(59,130,246,.15);
  border-radius: 12px; padding: 16px 20px; margin-bottom: 20px;
}}
.timeline-bar  {{ height: 8px; background: rgba(31,46,74,.8); border-radius: 4px; overflow: hidden; margin: 8px 0; }}
.timeline-fill {{ height: 100%; border-radius: 4px; background: linear-gradient(90deg, {ACCENT}, {VERDE}); }}
.timeline-labels {{ display: flex; justify-content: space-between; font-family: DM Mono, monospace; font-size: 10px; color: {MUTED}; }}

/* Ticker */
.ticker-wrap {{
  position: fixed; bottom: 0; left: 0; right: 0;
  background: rgba(10,14,26,.95); backdrop-filter: blur(8px);
  border-top: 1px solid rgba(59,130,246,.2);
  padding: 5px 0; z-index: 100; overflow: hidden;
}}
.ticker-content {{
  display: inline-block; white-space: nowrap;
  animation: ticker 80s linear infinite;
  font-family: DM Mono, monospace; font-size: 11px; color: {MUTED};
}}
@keyframes ticker {{
  0%   {{ transform: translateX(100vw); }}
  100% {{ transform: translateX(-100%); }}
}}

/* Timer bar */
.timer-bar-bg {{ background: rgba(31,46,74,.8); border-radius: 2px; height: 3px; width: 100%; overflow: hidden; margin-top: 6px; }}

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

/* Selectbox */
.stSelectbox > div > div {{
  background: rgba(17,24,39,.8) !important;
  border-color: rgba(59,130,246,.25) !important;
  color: {TEXTO} !important; backdrop-filter: blur(8px) !important;
}}

/* Créditos rodapé */
.credito {{
  position: fixed; bottom: 28px; right: 16px;
  font-family: DM Mono, monospace; font-size: 10px;
  color: rgba(100,116,139,.4); z-index: 99;
  letter-spacing: .06em;
}}
</style>
""", unsafe_allow_html=True)

# ── Splash screen ─────────────────────────────────────────────────────────────
def splash():
    if LOGO_B64:
        logo_tag = f'<img src="data:image/png;base64,{LOGO_B64}" class="splash-logo">'
    else:
        logo_tag = f'<div class="splash-logo" style="background:linear-gradient(135deg,{BLUE},{ACCENT});display:flex;align-items:center;justify-content:center;font-size:48px;font-weight:800;color:#fff">MF</div>'

    st.markdown(f"""
    <div class="splash" id="splash">
      {logo_tag}
      <div class="splash-title">Acompanhamento de Contratos</div>
      <div class="splash-sub">MF Inclusão</div>
      <div class="splash-bar"><div class="splash-bar-fill"></div></div>
      <div class="splash-credit">Criado por Pablo Camelo</div>
    </div>
    """, unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
defaults = {
    "dados": None, "ultima_atualizacao": None,
    "modo": "painel", "orgao_ativo": None,
    "tv_pagina": 0, "tv_ultimo_tick": time.time(),
    "tv_produto_tick": {}, "tv_produto_idx": {},
    "autenticado": False, "show_login": False,
    "detalhe_origem": "painel", "splash_shown": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ───────────────────────────────────────────────────────────────────

def agora_br():
    return datetime.now(TZ)

def carregar():
    with st.spinner("Carregando dados..."):
        st.session_state.dados = carregar_dados()
        st.session_state.ultima_atualizacao = agora_br().strftime("%d/%m/%Y %H:%M")
    st.rerun()

def ir_para(modo, orgao=None, origem=None):
    st.session_state.modo = modo
    if orgao:   st.session_state.orgao_ativo    = orgao
    if origem:  st.session_state.detalhe_origem = origem
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
    if "digital"  in p: return "🗂️"
    if "tratamento" in p or "arquiv" in p: return "📦"
    if "livro"    in p or "scan"  in p: return "📚"
    if "imagem"   in p: return "🖼️"
    if "metro"    in p: return "📏"
    if "planta"   in p: return "🗺️"
    return "📄"

def icone_metrica(tipo, produto):
    p = produto.lower()
    digital = "digital" in p
    if tipo == "total":  return "🗂️" if digital else "📦"
    if tipo == "meta":   return "🎯"
    if tipo == "saldo":  return "⚖️"
    if tipo == "mensal": return "📅"
    return "📄"

def unidade(produto):
    p = produto.lower()
    if "metro"  in p: return "m/l"
    if "livro"  in p or "scan"  in p: return "livros"
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
    prod_rec = [r["producao"] for r in rows[-3:] if r["producao"]]
    if not prod_rec: return None
    media = sum(prod_rec) / len(prod_rec)
    if media <= 0: return None
    return int((meta - total) / media)

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
        for c in resumo_orgao(rows):
            parts.append(f"{c['emoji']} {orgao} ({c['produto'][:6]}): {c['pct']}%")
    return "  ·  ".join(parts) + "  ·  "

def build_card_html(orgao, calcs, css_class="card-glass"):
    pct_max = max((c["pct"] for c in calcs), default=0)
    neon    = neon_class(pct_max)
    prod_html = ""
    for c in calcs:
        pct = c["pct"]; cor = c["cor"]
        prod_html += (
            f'<div style="margin-top:10px">'
            f'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:4px">'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase;display:flex;align-items:center;gap:5px">'
            f'{icone_produto(c["produto"])} {c["produto"]}</div>'
            f'<div style="font-size:12px;font-weight:700;color:{cor}">{c["emoji"]} {pct}%</div>'
            f'</div>'
            f'<div style="background:rgba(31,46,74,.8);border-radius:6px;height:8px;overflow:hidden">'
            f'<div style="width:{min(100,pct)}%;background:{cor};height:100%;border-radius:6px;box-shadow:0 0 6px {cor}50"></div>'
            f'</div>'
            f'<div style="display:flex;justify-content:space-between;font-family:DM Mono,monospace;font-size:10px;color:{MUTED};margin-top:3px">'
            f'<span>{c["fmt_total"]}</span><span>Meta: {c["fmt_meta"]}</span>'
            f'</div></div>'
        )
    return (
        f'<div class="{css_class} {neon}">'
        f'<div style="font-size:17px;font-weight:800;margin-bottom:2px">{orgao}</div>'
        f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">{len(calcs)} produto(s)</div>'
        f'{prod_html}</div>'
    )

# ── Metric card ───────────────────────────────────────────────────────────────

def metric_card(label, value, unit="", sub=None, cor=None, icone="📄", trend_html=""):
    cor_v = cor or TEXTO
    sub_h   = f'<div class="metric-sub">{sub}</div>'   if sub        else ""
    trend_h = f'<div class="metric-trend">{trend_html}</div>' if trend_html else ""
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-icon">{icone}</div>'
        f'<div class="metric-info">'
        f'<div class="metric-label">{label}</div>'
        f'<div class="metric-value" style="color:{cor_v}">{value}<span class="metric-unit">{unit}</span></div>'
        f'{sub_h}{trend_h}</div></div>',
        unsafe_allow_html=True,
    )

# ── Header ────────────────────────────────────────────────────────────────────

def header(mostrar_nav=True):
    c1, c2, c3 = st.columns([2, 4, 3])
    with c1:
        if LOGO_B64:
            logo_html = (
                f'<div style="display:flex;align-items:center;gap:12px">'
                f'<img src="data:image/png;base64,{LOGO_B64}" style="width:44px;height:44px;border-radius:10px;'
                f'box-shadow:0 0 16px rgba(59,130,246,.4)">'
                f'<div>'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">MF Inclusão</div>'
                f'<div style="font-size:20px;font-weight:800">{APP_NOME}</div>'
                f'</div></div>'
            )
        else:
            logo_html = f'<div style="font-size:20px;font-weight:800">{APP_NOME}</div>'
        st.markdown(logo_html, unsafe_allow_html=True)

    with c2:
        if mostrar_nav:
            b1, b2, b3 = st.columns(3)
            with b1:
                if st.button("📊 Painel", key="btn_painel"): ir_para("painel")
            with b2:
                if st.button("📺 TV", key="btn_tv"): ir_para("tv")
            with b3:
                if st.button("🔄 Atualizar", key="btn_upd"):
                    if st.session_state.autenticado: carregar()
                    else: st.session_state.show_login = True; st.rerun()

    with c3:
        now = agora_br()
        st.markdown(
            f'<div style="text-align:right">'
            f'<div style="font-family:DM Mono,monospace;font-size:20px;font-weight:700;color:{TEXTO}">'
            f'{now.strftime("%H:%M:%S")}</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED}">'
            f'{now.strftime("%d/%m/%Y")} · Atualizado: {ts()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown(f"<hr style='border:none;border-top:1px solid rgba(59,130,246,.15);margin:14px 0 20px 0'>", unsafe_allow_html=True)

    # Crédito fixo no rodapé direito
    st.markdown(
        f'<div class="credito">Criado por Pablo Camelo · MF Inclusão</div>',
        unsafe_allow_html=True,
    )

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

    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-content">{ticker_text(dados)}</div></div>',
        unsafe_allow_html=True,
    )

# ── Modo TV ───────────────────────────────────────────────────────────────────

def modo_tv():
    dados = st.session_state.dados
    if not dados:
        st.warning("Sem dados.")
        if st.button("← Voltar"): ir_para("painel")
        return

    orgaos    = list(dados.keys())
    n_orgaos  = len(orgaos)
    agora     = time.time()

    # Rotação automática
    if agora - st.session_state.tv_ultimo_tick >= TV_ROTACAO_SEG:
        st.session_state.tv_pagina      = (st.session_state.tv_pagina + 1) % n_orgaos
        st.session_state.tv_ultimo_tick = agora

    idx_atual  = st.session_state.tv_pagina % n_orgaos
    orgao      = orgaos[idx_atual]
    calcs      = resumo_orgao(dados[orgao])
    elapsed    = agora - st.session_state.tv_ultimo_tick
    rest_pct   = max(0, (1 - elapsed / TV_ROTACAO_SEG)) * 100
    rest_seg   = max(0, int(TV_ROTACAO_SEG - elapsed))

    # ── Header TV ──
    c1, c2, c3 = st.columns([3, 4, 3])
    with c1:
        if LOGO_B64:
            st.markdown(
                f'<div style="display:flex;align-items:center;gap:10px">'
                f'<img src="data:image/png;base64,{LOGO_B64}" style="width:36px;height:36px;border-radius:8px;box-shadow:0 0 10px rgba(59,130,246,.4)">'
                f'<div>'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">Modo TV · MF Inclusão</div>'
                f'<div style="font-size:14px;font-weight:800">{APP_NOME}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
    with c2:
        st.markdown(
            f'<div style="text-align:center">'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">'
            f'Contrato {idx_atual+1} de {n_orgaos} · próximo em {rest_seg}s</div>'
            f'<div class="timer-bar-bg">'
            f'<div style="height:3px;background:{ACCENT};border-radius:2px;width:{rest_pct}%;box-shadow:0 0 6px {ACCENT}"></div>'
            f'</div></div>',
            unsafe_allow_html=True,
        )
    with c3:
        cs1, cs2, cs3 = st.columns(3)
        with cs1:
            if st.button("◀", key="tv_prev"):
                st.session_state.tv_pagina      = (idx_atual - 1) % n_orgaos
                st.session_state.tv_ultimo_tick = time.time()
                st.rerun()
        with cs2:
            if st.button("▶", key="tv_next"):
                st.session_state.tv_pagina      = (idx_atual + 1) % n_orgaos
                st.session_state.tv_ultimo_tick = time.time()
                st.rerun()
        with cs3:
            if st.button("✕", key="tv_sair"): ir_para("painel")

        # Menu suspenso
        sel = st.selectbox(
            "Contrato", ["— Ir para —"] + orgaos,
            key="tv_select", label_visibility="collapsed",
        )
        if sel != "— Ir para —":
            st.session_state.tv_pagina      = orgaos.index(sel)
            st.session_state.tv_ultimo_tick = time.time()
            st.rerun()

    st.markdown(f"<div style='border-top:1px solid rgba(59,130,246,.15);margin:10px 0 16px 0'></div>", unsafe_allow_html=True)

    # ── Card único fullscreen ──
    if not calcs:
        st.warning(f"Sem dados para {orgao}")
    else:
        # Alternância de produto a cada 10s
        key_idx  = f"tv_pidx_{orgao}"
        key_tick = f"tv_ptick_{orgao}"
        if key_idx  not in st.session_state: st.session_state[key_idx]  = 0
        if key_tick not in st.session_state: st.session_state[key_tick] = agora
        if agora - st.session_state[key_tick] >= 10:
            st.session_state[key_idx]  = (st.session_state[key_idx] + 1) % len(calcs)
            st.session_state[key_tick] = agora

        pidx = st.session_state[key_idx] % len(calcs)
        c    = calcs[pidx]
        cor  = c["cor"]
        pct  = c["pct"]
        neon = neon_class(pct)

        # Dots indicador de produto
        dots = "".join(
            f'<span style="display:inline-block;width:8px;height:8px;border-radius:50%;'
            f'background:{"#3b82f6" if i==pidx else "rgba(59,130,246,.2)"};margin:0 3px"></span>'
            for i in range(len(calcs))
        )

        st.markdown(f'<div class="card-tv-full {neon}">', unsafe_allow_html=True)

        # Cabeçalho do card
        hc1, hc2 = st.columns([3, 1])
        with hc1:
            st.markdown(
                f'<div style="margin-bottom:16px">'
                f'<div style="font-size:32px;font-weight:800;margin-bottom:4px">{orgao}</div>'
                f'<div style="display:flex;align-items:center;gap:10px">'
                f'<div style="font-family:DM Mono,monospace;font-size:12px;color:{MUTED};text-transform:uppercase">'
                f'{icone_produto(c["produto"])} {c["produto"]}</div>'
                f'<div>{dots}</div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
        with hc2:
            st.markdown(
                f'<div style="text-align:right">'
                f'<div style="font-size:48px;font-weight:800;color:{cor};'
                f'text-shadow:0 0 20px {cor}60;line-height:1">{pct}%</div>'
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{cor}">{c["status"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # 4 métricas
        m1, m2, m3, m4 = st.columns(4)
        with m1: metric_card("Total Produzido", c["fmt_total"], unidade(c["produto"]), f'{c["duracao"]} meses', icone=icone_metrica("total", c["produto"]))
        with m2: metric_card("Meta Contratual", c["fmt_meta"], unidade(c["produto"]), "(Total do Contrato)", icone=icone_metrica("meta", c["produto"]))
        with m3:
            sub3 = "✅ Meta batida!" if c["saldo"] and c["saldo"] <= 0 else "(Ainda Faltam)"
            metric_card("Saldo Remanescente", c["fmt_saldo"], unidade(c["produto"]), sub3, cor, icone=icone_metrica("saldo", c["produto"]))
        with m4: metric_card("Meta Mensal", c["fmt_meta_m"], unidade(c["produto"]), f'(Média em {c["duracao"]} meses)', icone=icone_metrica("mensal", c["produto"]))

        st.markdown("<div style='margin:12px 0'></div>", unsafe_allow_html=True)

        # Gráficos
        gc1, gc2 = st.columns([3, 1])
        with gc1:
            melhor = melhor_mes_idx(c["rows"])
            st.plotly_chart(grafico_barras(c, melhor_idx=melhor), use_container_width=True, config={"displayModeBar": False})
        with gc2:
            st.plotly_chart(grafico_rosca(c), use_container_width=True, config={"displayModeBar": False})

        st.markdown('</div>', unsafe_allow_html=True)

        if st.button(f"🔍 Ver detalhes de {orgao}", key=f"tv_det_{orgao}"):
            ir_para("detalhe", orgao, "tv")

    # Ticker
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-content">{ticker_text(dados)}</div></div>',
        unsafe_allow_html=True,
    )

    time.sleep(1)
    st.rerun()

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
            f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase">MF Inclusão · Acompanhamento de Contratos</div>'
            f'<div style="font-size:28px;font-weight:800">{orgao}</div>'
            f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED}">Última Atualização: {ts()}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    with c2:
        origem = st.session_state.detalhe_origem
        if st.button("📺 TV" if origem == "tv" else "← Painel", key="btn_voltar"):
            ir_para(origem)

    st.markdown(f"<div style='border-top:1px solid rgba(59,130,246,.15);margin-bottom:20px'></div>", unsafe_allow_html=True)

    rows_all  = dados[orgao]
    calcs_all = resumo_orgao(rows_all)

    for c_full in calcs_all:
        produto = c_full["produto"]
        cor     = c_full["cor"]
        pct_f   = c_full["pct"]
        neon    = neon_class(pct_f)
        uni     = unidade(produto)

        # Filtro de ano
        anos = ["Todos"] + [str(a) for a in anos_disponiveis(c_full["rows"])]
        col_tag, col_ano = st.columns([3, 1])
        with col_tag:
            st.markdown(f'<div class="produto-tag">{icone_produto(produto)} {produto}</div>', unsafe_allow_html=True)
        with col_ano:
            ano_sel = st.selectbox("Ano", anos, key=f"ano_{orgao}_{produto}", label_visibility="collapsed")

        rows_f = filtrar_por_ano(c_full["rows"], None if ano_sel == "Todos" else ano_sel)
        c      = c_full
        c_f    = calcular(rows_f, produto) if rows_f else c_full

        # Banner
        status_txt = "CONCLUÍDO ✅" if c["saldo"] and c["saldo"] <= 0 else ("ATENÇÃO ⚠️" if c["pct"] < 50 else "EM ANDAMENTO")
        periodo    = ""
        if c["rows"]:
            anos_l = [r["mes"][:4] for r in c["rows"] if r["mes"]]
            if anos_l: periodo = f"{min(anos_l)} - {max(anos_l)}"

        st.markdown(
            f'<div class="status-banner {neon}">'
            f'<div class="status-banner-title" style="color:{cor}">STATUS DO CONTRATO {orgao}: {status_txt}</div>'
            f'<div class="status-banner-sub">{produto} · {pct_f}% Concluído · Período: {periodo}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        # Linha do tempo
        if c["rows"]:
            n_preen   = sum(1 for r in c["rows"] if r["producao"] is not None)
            pct_tempo = round((n_preen / len(c["rows"])) * 100, 1)
            m_ini     = fmt_mes(c["rows"][0]["mes"])
            m_fim     = fmt_mes(c["rows"][-1]["mes"])
            st.markdown(
                f'<div class="timeline-wrap">'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};text-transform:uppercase;margin-bottom:6px">Linha do Tempo do Contrato</div>'
                f'<div class="timeline-labels"><span>{m_ini}</span>'
                f'<span style="color:{cor}">{n_preen} de {len(c["rows"])} entregas · {pct_tempo}%</span>'
                f'<span>{m_fim}</span></div>'
                f'<div class="timeline-bar"><div class="timeline-fill" style="width:{pct_tempo}%"></div></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Métricas
        trend_h = tendencia(c["rows"])
        prev    = previsao(c["total"], c["meta"], c["meta_mensal"], c["rows"])
        prev_txt = f"~{prev} meses p/ concluir" if prev else ""

        mc1, mc2, mc3, mc4 = st.columns(4)
        with mc1: metric_card(f"Total Produzido ({produto[:6]})", c["fmt_total"], uni, f'{c["duracao"]} meses de contrato', icone=icone_metrica("total", produto), trend_html=trend_h)
        with mc2: metric_card("Meta Contratual Total", c["fmt_meta"], uni, "(Total do Contrato)", icone=icone_metrica("meta", produto))
        with mc3:
            sub3 = "✅ Meta batida!" if c["saldo"] and c["saldo"] <= 0 else "(Ainda Faltam)"
            metric_card("Saldo Remanescente", c["fmt_saldo"], uni, sub3, cor, icone=icone_metrica("saldo", produto))
        with mc4: metric_card("Meta Mensal Média", c["fmt_meta_m"], uni, prev_txt or f'(Média em {c["duracao"]} meses)', icone=icone_metrica("mensal", produto))

        st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

        # Gráficos
        melhor = melhor_mes_idx(c_f["rows"] if c_f else [])
        gc1, gc2 = st.columns([3, 1])
        with gc1:
            st.markdown(
                f'<div style="background:rgba(17,24,39,.75);backdrop-filter:blur(12px);'
                f'border:1px solid rgba(59,130,246,.2);border-radius:14px;padding:18px;'
                f'box-shadow:0 4px 20px rgba(0,0,0,.3)">'
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};text-transform:uppercase;margin-bottom:2px">Histórico Mensal de Produção ({produto})</div>'
                f'<div style="font-family:DM Mono,monospace;font-size:10px;color:{MUTED};margin-bottom:10px">Período: {periodo}{" · " + ano_sel if ano_sel != "Todos" else ""}</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafico_barras(c_f if c_f else c, melhor_idx=melhor), use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)
        with gc2:
            st.markdown(
                f'<div style="background:rgba(17,24,39,.75);backdrop-filter:blur(12px);'
                f'border:1px solid rgba(59,130,246,.2);border-radius:14px;padding:18px;'
                f'box-shadow:0 4px 20px rgba(0,0,0,.3)">'
                f'<div style="font-family:DM Mono,monospace;font-size:11px;color:{MUTED};text-transform:uppercase;margin-bottom:10px">% da Meta Contratual</div>',
                unsafe_allow_html=True,
            )
            st.plotly_chart(grafico_rosca(c), use_container_width=True, config={"displayModeBar": False})
            st.markdown(f'<div style="text-align:center;font-size:14px;font-weight:700;color:{cor};margin-top:4px">{c["status"]}</div></div>', unsafe_allow_html=True)

        st.markdown("<div style='margin:16px 0'></div>", unsafe_allow_html=True)

        # Tabela
        import pandas as pd
        meta_m      = c_f["meta_mensal"] if c_f else 0
        meta_m      = meta_m or 0
        acum        = 0
        melhor_prod = max((r["producao"] or 0 for r in (c_f["rows"] if c_f else [])), default=0)
        rows_t      = []
        for r in (c_f["rows"] if c_f else []):
            acum  += r["producao"] or 0
            prod   = r["producao"]
            status = "✅ Atingiu" if prod and prod >= meta_m else ("— Pendente" if prod is None else "⚠️ Abaixo")
            badge  = "🏆 Melhor mês" if prod and prod == melhor_prod and melhor_prod > 0 else ""
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

    # Ticker
    st.markdown(
        f'<div class="ticker-wrap"><div class="ticker-content">{ticker_text(dados)}</div></div>',
        unsafe_allow_html=True,
    )

# ── Init ──────────────────────────────────────────────────────────────────────

# Splash na primeira carga
if not st.session_state.splash_shown:
    splash()
    st.session_state.splash_shown = True

if st.session_state.dados is None:
    with st.spinner("Carregando dados..."):
        st.session_state.dados = carregar_dados()
        st.session_state.ultima_atualizacao = agora_br().strftime("%d/%m/%Y %H:%M")

# ── Roteamento ────────────────────────────────────────────────────────────────
if st.session_state.show_login:
    tela_login()
elif st.session_state.modo == "tv":
    modo_tv()
elif st.session_state.modo == "detalhe":
    modo_detalhe()
else:
    modo_painel()