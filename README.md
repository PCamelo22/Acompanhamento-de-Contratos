# Acompanhamento de Contratos v2.0

Dashboard interativo para acompanhamento de contratos em tempo real.

## Estrutura

```
acompanhamento_v2/
├── app.py              — Aplicação principal Streamlit
├── config.py           — Configurações (URL, senha, cores, etc.)
├── data.py             — Leitura e processamento dos dados
├── graficos.py         — Gráficos Plotly
└── requirements.txt    — Dependências Python
```

## Instalação

```bash
pip install -r requirements.txt
```

## Executar localmente

```bash
streamlit run app.py
```

Acesse: http://localhost:8501

## Modos

- **Modo Painel** — Cards clicáveis com todos os órgãos
- **Modo TV (Apresentação)** — Grid 2x2, rotação automática a cada 30s — ideal para televisão
- **Modo Detalhe** — Gráficos completos de um órgão específico

## Atualizar dados

1. Atualize a planilha no Google Drive
2. No dashboard clique no botão 🔄
3. Digite a senha (padrão: `admin123`)
4. Os dados são atualizados automaticamente

> ⚠️ Troque a senha padrão em `config.py` antes de publicar!

## Publicar no Streamlit Cloud (acesso para todos)

1. Suba os arquivos no GitHub
2. Acesse [share.streamlit.io](https://share.streamlit.io)
3. Conecte o repositório
4. Pronto — qualquer pessoa com o link consegue visualizar

## Adicionar logo

1. Coloque o arquivo da logo em `assets/logo.png`
2. No `config.py` altere: `APP_LOGO = "assets/logo.png"`

## Novos órgãos

Novos órgãos são detectados **automaticamente** — basta adicionar a aba na planilha do Google Drive e clicar em 🔄 para atualizar.
