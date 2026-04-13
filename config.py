# ─────────────────────────────────────────────────────────────────────────────
# config.py — Acompanhamento de Contratos v2.0
# ─────────────────────────────────────────────────────────────────────────────

APP_NOME    = "Acompanhamento de Contratos"
APP_VERSAO  = "2.0"
APP_LOGO    = None   # Caminho para logo: "assets/logo.png" — adicione futuramente

# ── Google Drive ──────────────────────────────────────────────────────────────
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTqZcTuHX-3-_sIIjg5F3HPvQHyeoMuVJoWcdAPwBvC7O3sLEtK76_cvWat3_nVqQ/pub?output=xlsx"

# ── Autenticação ──────────────────────────────────────────────────────────────
# Troque a senha abaixo antes de publicar!
ADMIN_SENHA = "admin123"

# ── Apresentação (Modo TV) ────────────────────────────────────────────────────
TV_COLS            = 2          # colunas no grid
TV_ROWS            = 2          # linhas no grid
TV_CARDS_POR_TELA  = TV_COLS * TV_ROWS   # 4 por tela
TV_ROTACAO_SEG     = 30         # segundos entre telas
TV_CARD_VAZIO      = "Em breve" # texto dos cards vazios na última tela

# ── Thresholds de status (%) ──────────────────────────────────────────────────
STATUS_VERDE   = 80
STATUS_AMARELO = 50

# ── Cores ─────────────────────────────────────────────────────────────────────
CORES = {
    "bg":       "#0a0e1a",
    "surface":  "#111827",
    "surface2": "#1a2236",
    "border":   "#1f2e4a",
    "blue":     "#1F4E79",
    "accent":   "#3b82f6",
    "accent2":  "#60a5fa",
    "verde":    "#10b981",
    "amarelo":  "#f59e0b",
    "vermelho": "#ef4444",
    "texto":    "#e2e8f0",
    "muted":    "#64748b",
}

# ── Meses em português ────────────────────────────────────────────────────────
MESES = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"]
