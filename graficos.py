# ─────────────────────────────────────────────────────────────────────────────
# graficos.py — Acompanhamento de Contratos v2.0
# ─────────────────────────────────────────────────────────────────────────────

import plotly.graph_objects as go
from config import CORES


LAYOUT_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color=CORES["texto"]),
)


def grafico_barras(calc, melhor_idx=-1):
    rows   = calc["rows"]
    labels = [str(r["mes"])[:7] for r in rows]
    prod   = [r["producao"] or 0 for r in rows]
    meta_m = calc["meta_mensal"] or 0

    # Cores das barras — destaque no melhor mês
    cores = []
    for i, p in enumerate(prod):
        if i == melhor_idx:
            cores.append("#f59e0b")  # dourado para melhor mês
        elif p >= meta_m:
            cores.append(CORES["verde"])
        else:
            cores.append(CORES["accent"])

    # Bordas — destaque no melhor mês
    border_colors = ["#f59e0b" if i == melhor_idx else "rgba(0,0,0,0)" for i in range(len(prod))]
    border_widths = [3 if i == melhor_idx else 0 for i in range(len(prod))]

    # Texto customizado para hover
    hover = []
    for i, (l, p) in enumerate(zip(labels, prod)):
        badge = " 🏆 Melhor mês!" if i == melhor_idx else ""
        hover.append(f"<b>{l}</b><br>Produção: {p:,.2f}<br>Meta: {meta_m:,.2f}{badge}<extra></extra>")

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=labels, y=prod,
        name="Produção",
        marker_color=cores,
        marker_line_color=border_colors,
        marker_line_width=border_widths,
        hovertemplate=hover,
        marker=dict(
            color=cores,
            line=dict(color=border_colors, width=border_widths),
            opacity=0.9,
        )
    ))

    fig.add_trace(go.Scatter(
        x=labels, y=[meta_m] * len(labels),
        name="Meta Mensal", mode="lines",
        line=dict(color=CORES["amarelo"], width=2, dash="dash"),
        hovertemplate="Meta Mensal: %{y:,.2f}<extra></extra>",
    ))

    fig.update_layout(
        **LAYOUT_BASE,
        height=280,
        margin=dict(l=10, r=10, t=30, b=10),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            font=dict(size=11, color=CORES["muted"]),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(
            tickfont=dict(size=10, color=CORES["muted"]),
            gridcolor="rgba(31,46,74,.4)",
            linecolor="rgba(31,46,74,.4)",
            tickangle=-45,
        ),
        yaxis=dict(
            tickfont=dict(size=10, color=CORES["muted"]),
            gridcolor="rgba(31,46,74,.4)",
            linecolor="rgba(31,46,74,.4)",
        ),
        bargap=0.3,
        hoverlabel=dict(
            bgcolor="rgba(17,24,39,.95)",
            bordercolor=CORES["border"],
            font=dict(size=12, color=CORES["texto"]),
        ),
    )
    return fig


def grafico_rosca(calc):
    pct = calc["pct"]
    cor = calc["cor"]
    produto = calc.get("produto", "")

    label_centro = "CONCLUÍDO" if "digital" in produto.lower() else "ATINGIDO"

    fig = go.Figure(go.Pie(
        values=[pct, max(0, 100 - pct)],
        hole=0.72,
        marker_colors=[cor, "rgba(31,46,74,.6)"],
        textinfo="none", hoverinfo="skip", showlegend=False,
        marker=dict(line=dict(color="rgba(0,0,0,0)", width=0)),
    ))

    fig.add_annotation(
        text=f"<b>{pct}%</b>", x=0.5, y=0.58,
        font=dict(size=30, color=cor, family="DM Sans, sans-serif"),
        showarrow=False,
    )
    fig.add_annotation(
        text=label_centro, x=0.5, y=0.38,
        font=dict(size=10, color=CORES["muted"], family="DM Mono, sans-serif"),
        showarrow=False,
    )

    fig.update_layout(
        **LAYOUT_BASE,
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
    )
    return fig