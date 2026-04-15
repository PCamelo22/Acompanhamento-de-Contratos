# ─────────────────────────────────────────────────────────────────────────────
# data.py — Acompanhamento de Contratos v2.0
# ─────────────────────────────────────────────────────────────────────────────

import io
import requests
import pandas as pd
from datetime import datetime, timedelta
from config import SHEET_URL, CORES, STATUS_VERDE, STATUS_AMARELO, MESES


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_num(v, decimals=0):
    if v is None:
        return "—"
    try:
        if pd.isna(v):
            return "—"
    except:
        pass
    try:
        return f"{float(v):,.{decimals}f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "—"

def fmt_mes(s):
    if not s or str(s) == "nan":
        return "—"
    s = str(s)[:7]
    try:
        y, m = s.split("-")
        return f"{MESES[int(m)-1]}/{y}"
    except:
        return s

def status_cor(pct):
    if pct >= STATUS_VERDE:
        return CORES["verde"]
    elif pct >= STATUS_AMARELO:
        return CORES["amarelo"]
    return CORES["vermelho"]

def status_label(pct):
    if pct >= STATUS_VERDE:
        return "✅ Dentro da meta"
    elif pct >= STATUS_AMARELO:
        return "⚠️ Atenção necessária"
    return "🔴 Abaixo da meta"

def status_emoji(pct):
    if pct >= STATUS_VERDE:
        return "✅"
    elif pct >= STATUS_AMARELO:
        return "⚠️"
    return "🔴"


# ── Leitura do Google Drive ───────────────────────────────────────────────────

def carregar_dados():
    r = requests.get(SHEET_URL, timeout=30)
    r.raise_for_status()

    xl = pd.ExcelFile(io.BytesIO(r.content))
    dados = {}

    for aba in xl.sheet_names:
        try:
            df = xl.parse(aba, header=None)
            if df.empty:
                continue

            hrow = None
            for i, row in df.iterrows():
                vals = [str(v).strip().lower() for v in row if pd.notna(v) and str(v).strip()]
                if any(v in ("mes", "mês", "entrega") for v in vals):
                    hrow = i
                    break

            if hrow is None:
                continue

            meta_contratual = None
            for i in range(hrow):
                row = df.iloc[i]
                for j in range(len(row)):
                    v = row.iloc[j]
                    if pd.notna(v) and "meta" in str(v).lower():
                        for k in range(j+1, len(row)):
                            rv = row.iloc[k]
                            if pd.notna(rv) and isinstance(rv, (int, float)) and rv > 0:
                                meta_contratual = float(rv)
                                break
                    if meta_contratual:
                        break
                if meta_contratual:
                    break

            headers = [str(v).strip() if pd.notna(v) else "" for v in df.iloc[hrow]]

            def find_col(*keywords):
                for kw in keywords:
                    for i, h in enumerate(headers):
                        if kw.lower() in h.lower():
                            return i
                return None

            c_ent      = find_col("entrega")
            c_mes      = find_col("mes", "mês")
            c_prod     = find_col("produto")
            c_producao = find_col("producao", "produção")
            c_meta     = find_col("meta_contratual", "meta contratual")

            if c_mes is None or c_producao is None:
                continue

            rows = []
            for i in range(hrow + 1, len(df)):
                row = df.iloc[i]
                mes_val  = row.iloc[c_mes]
                prod_val = row.iloc[c_producao]

                if pd.isna(mes_val) and pd.isna(prod_val):
                    continue

                mes_str = None
                if isinstance(mes_val, datetime):
                    mes_str = mes_val.strftime("%Y-%m-%d")
                elif isinstance(mes_val, str) and len(mes_val.strip()) >= 7:
                    mes_str = mes_val.strip()[:10]
                elif isinstance(mes_val, (int, float)) and not pd.isna(mes_val):
                    try:
                        d = datetime(1899, 12, 30) + timedelta(days=int(mes_val))
                        mes_str = d.strftime("%Y-%m-%d")
                    except:
                        pass

                if not mes_str:
                    continue

                producao = None
                if isinstance(prod_val, (int, float)) and not pd.isna(prod_val):
                    producao = float(prod_val)

                row_meta = None
                if c_meta is not None:
                    mv = row.iloc[c_meta]
                    if isinstance(mv, (int, float)) and not pd.isna(mv) and mv > 0:
                        row_meta = float(mv)
                if not row_meta:
                    row_meta = meta_contratual

                produto = "N/D"
                if c_prod is not None and pd.notna(row.iloc[c_prod]):
                    produto = str(row.iloc[c_prod]).strip()

                entrega = ""
                if c_ent is not None and pd.notna(row.iloc[c_ent]):
                    entrega = str(row.iloc[c_ent]).strip()

                if produto in ("N/D", "Produto", "nan", ""):
                    continue

                rows.append({
                    "entrega":  entrega,
                    "mes":      mes_str,
                    "produto":  produto,
                    "producao": producao,
                    "meta":     row_meta,
                })

            if rows:
                dados[aba] = rows

        except Exception:
            continue

    return dados


# ── Cálculos por produto ──────────────────────────────────────────────────────

def calcular(rows, produto):
    """Retorna métricas calculadas para um produto de um órgão.
    
    Status baseado no ÚLTIMO mês com produção vs meta mensal recalculada.
    Meta mensal é dinâmica: saldo restante redistribuído nos meses sem produção.
    """
    filtered = [r for r in rows if r["produto"].strip() == produto]
    if not filtered:
        return None

    meta    = next((r["meta"] for r in filtered if r["meta"]), None)
    duracao = len(filtered)
    total   = sum(r["producao"] or 0 for r in filtered)
    saldo   = meta - total if meta else None
    pct     = round((total / meta) * 100, 1) if meta else 0

    # ── Meta mensal recalculada dinamicamente ──────────────────────────────
    # Saldo restante redistribuído nos meses sem produção a cada mês
    metas_mensais = []
    saldo_acum = meta or 0
    for i, r in enumerate(filtered):
        meses_restantes = len(filtered) - i
        meta_mes = saldo_acum / meses_restantes if meses_restantes > 0 else 0
        metas_mensais.append(round(meta_mes, 2))
        if r["producao"] is not None:
            saldo_acum = max(0, saldo_acum - r["producao"])

    # Meta mensal atual = meta do próximo mês sem produção
    meta_m = None
    for i, r in enumerate(filtered):
        if r["producao"] is None:
            meta_m = metas_mensais[i]
            break
    if meta_m is None:
        meta_m = metas_mensais[-1] if metas_mensais else (meta / duracao if meta and duracao > 0 else None)

    # ── Status baseado no ÚLTIMO mês com produção ──────────────────────────
    ultimo_com_prod = None
    for i in range(len(filtered) - 1, -1, -1):
        if filtered[i]["producao"] is not None:
            ultimo_com_prod = (filtered[i]["producao"], metas_mensais[i])
            break

    if ultimo_com_prod:
        prod_ult, meta_ult = ultimo_com_prod
        pct_mes       = (prod_ult / meta_ult * 100) if meta_ult > 0 else 0
        cor_status    = status_cor(pct_mes)
        label_status  = status_label(pct_mes)
        emoji_status  = status_emoji(pct_mes)
    else:
        cor_status    = status_cor(0)
        label_status  = status_label(0)
        emoji_status  = status_emoji(0)

    # Adiciona meta recalculada em cada row para o gráfico de barras
    rows_com_meta = []
    for i, r in enumerate(filtered):
        row_copy = dict(r)
        row_copy["meta_mensal_calc"] = metas_mensais[i]
        rows_com_meta.append(row_copy)

    return {
        "produto":        produto,
        "rows":           rows_com_meta,
        "meta":           meta,
        "duracao":        duracao,
        "meta_mensal":    meta_m,
        "metas_mensais":  metas_mensais,
        "total":          total,
        "saldo":          saldo,
        "pct":            pct,
        "cor":            cor_status,
        "status":         label_status,
        "emoji":          emoji_status,
        "fmt_total":      fmt_num(total, 2),
        "fmt_meta":       fmt_num(meta),
        "fmt_saldo":      fmt_num(abs(saldo) if saldo else None),
        "fmt_meta_m":     fmt_num(meta_m, 2),
        "fmt_mes_rows":   [(fmt_mes(r["mes"]), r["producao"], r["entrega"]) for r in filtered],
    }


def resumo_orgao(rows):
    """Retorna lista de cálculos por produto para um órgão.
    Mantém a ordem original da planilha.
    """
    produtos = list(dict.fromkeys(r["produto"].strip() for r in rows))
    return [c for c in (calcular(rows, p) for p in produtos) if c]