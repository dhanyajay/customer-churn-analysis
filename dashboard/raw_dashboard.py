# ============================================================
#  CUSTOMER RETENTION — FULL EDA DASHBOARD
#  Single file · Plotly Dash · bob.csv + Retention.csv
#
#  HOW TO RUN:
#    1. Place bob.csv and Retention.csv in the SAME folder
#       as this file  (or adjust paths in load_retention /
#       load_bob below).
#    2. pip install dash dash-bootstrap-components plotly pandas numpy
#    3. python app.py
#    4. Open  http://127.0.0.1:8050  in your browser
# ============================================================

import os, warnings
warnings.filterwarnings("ignore")

import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
from dash import dcc, html, Input, Output, dash_table
import dash_bootstrap_components as dbc

# ────────────────────────────────────────────────────────────
# 1.  DATA LOADING
# ────────────────────────────────────────────────────────────

def _find(candidates):
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

def load_retention():
    p = _find(["Retention.csv", "retention.csv",
                "data/Retention.csv", "data/01_raw/Retention.csv",
                "../data/01_raw/Retention.csv"])
    if p is None:
        raise FileNotFoundError(
            "Retention.csv not found. Place it next to app.py.")
    return pd.read_csv(p, encoding="utf-8", encoding_errors="ignore")

def load_bob():
    p = _find(["bob.csv", "BOB.csv",
                "data/bob.csv", "data/01_raw/bob.csv",
                "../data/01_raw/bob.csv"])
    if p is None:
        return None
    return pd.read_csv(p, encoding="utf-8", encoding_errors="ignore")

ret = load_retention()
bob = load_bob()           # None if not found — dashboard still works

# ── Date parsing ─────────────────────────────────────────────
for col in ["Case Creation Date","Agreement End Date","Resolved Date",
            "Registered Date","Expected Pull Date",
            "Resolved Time","Registered Time"]:
    if col in ret.columns:
        ret[col] = pd.to_datetime(ret[col], errors="coerce", dayfirst=True)

if bob is not None:
    for col in ["agreement_start_date","agreement_end_date"]:
        if col in bob.columns:
            bob[col] = pd.to_datetime(bob[col], errors="coerce")

# ── Column type lists ─────────────────────────────────────────
def col_types(df):
    cat = df.select_dtypes(include="object").columns.tolist()
    num = df.select_dtypes(include="number").columns.tolist()
    dt  = [c for c in df.columns
           if pd.api.types.is_datetime64_any_dtype(df[c])]
    return cat, num, dt

ret_cat, ret_num, ret_dt = col_types(ret)
bob_cat, bob_num, bob_dt = col_types(bob) if bob is not None else ([],[],[])

# ────────────────────────────────────────────────────────────
# 2.  DESIGN TOKENS  (professional light theme)
# ────────────────────────────────────────────────────────────
NAVY   = "#1B2A4A"
BLUE   = "#2E6DA4"
BLUE2  = "#4A8FC4"
SKY    = "#D6E8F7"
ACCENT = "#E07B2A"
GREEN  = "#2E7D4F"
RED    = "#C0392B"
AMBER  = "#D4A017"
BG     = "#F4F6F9"
WHITE  = "#FFFFFF"
BORDER = "#D0D7E2"
MUTED  = "#6B7A8D"
LIGHT  = "#EBF0F7"

COLORWAY = [BLUE, GREEN, ACCENT, RED, AMBER, BLUE2, MUTED,
            "#7B5EA7","#1E8E9E","#C75B8A"]

PLOT_BASE = dict(
    paper_bgcolor=WHITE,
    plot_bgcolor=LIGHT,
    font=dict(family="'Source Sans Pro','Segoe UI',Arial,sans-serif",
              color=NAVY, size=11),
    colorway=COLORWAY,
    margin=dict(l=44, r=16, t=38, b=44),
    xaxis=dict(gridcolor=WHITE, linecolor=BORDER, zerolinecolor=BORDER),
    yaxis=dict(gridcolor=WHITE, linecolor=BORDER, zerolinecolor=BORDER),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=10)),
    hoverlabel=dict(bgcolor=NAVY, bordercolor=BLUE,
                    font=dict(color="white", size=11)),
    title=dict(font=dict(size=13, color=NAVY), x=0.02, xanchor="left"),
)

def atheme(fig, title=""):
    fig.update_layout(**PLOT_BASE)
    if title:
        fig.update_layout(title_text=title)
    return fig

def empty_fig(msg="No data available"):
    fig = go.Figure()
    fig.add_annotation(text=msg, x=0.5, y=0.5, showarrow=False,
                       font=dict(size=13, color=MUTED))
    return atheme(fig)

# ────────────────────────────────────────────────────────────
# 3.  UI HELPERS
# ────────────────────────────────────────────────────────────
CARD_STYLE = dict(
    backgroundColor=WHITE,
    border=f"1px solid {BORDER}",
    borderRadius="4px",
    boxShadow="0 1px 4px rgba(0,0,0,0.06)",
    marginBottom="14px",
)
HDR_STYLE = dict(
    backgroundColor=LIGHT,
    borderBottom=f"1px solid {BORDER}",
    padding="8px 14px",
    fontSize="11px", fontWeight="700",
    textTransform="uppercase", letterSpacing="0.5px",
    color=NAVY,
    fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
)

def card(hdr, *children):
    return html.Div([
        html.Div(hdr, style=HDR_STYLE),
        html.Div(list(children), style={"padding":"12px 14px"}),
    ], style=CARD_STYLE)

def kpi(value, label, color=BLUE):
    return html.Div([
        html.Div(str(value), style=dict(
            fontFamily="Georgia,'Times New Roman',serif",
            fontSize="28px", fontWeight="normal",
            color=color, lineHeight="1", marginBottom="4px")),
        html.Div(label, style=dict(
            fontSize="10px", color=MUTED,
            textTransform="uppercase", letterSpacing="0.4px",
            lineHeight="1.35")),
    ], style=dict(
        backgroundColor=WHITE,
        border=f"1px solid {BORDER}",
        borderLeft=f"4px solid {color}",
        borderRadius="4px",
        padding="10px 12px",
        marginBottom="8px",
    ))

DD = dict(fontSize="12px")          # common dropdown style

def graph(id_, h=230):
    return dcc.Graph(id=id_, config={"displayModeBar":False},
                     style={"height":f"{h}px"})

# ────────────────────────────────────────────────────────────
# 4.  KPIs
# ────────────────────────────────────────────────────────────
total_records  = len(ret)
missing_pct    = round(ret.isnull().mean().mean()*100, 1)
n_countries    = ret["Country"].nunique() if "Country" in ret.columns else "–"

open_cases = "–"
if "Resolution Status" in ret.columns:
    open_cases = int(ret["Resolution Status"].astype(str)
                     .str.upper().str.contains("OPEN").sum())

churn_pct = "–"
if "Pull Type" in ret.columns:
    pct = ret["Pull Type"].value_counts(normalize=True)*100
    churn_pct = f"{pct.get('Full', 0):.1f}%"

# ────────────────────────────────────────────────────────────
# 5.  APP INIT
# ────────────────────────────────────────────────────────────
app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        "https://fonts.googleapis.com/css2?family=Source+Sans+Pro:"
        "wght@300;400;600;700&display=swap",
    ],
    suppress_callback_exceptions=True,
)
server = app.server

GLOBAL_CSS = f"""
body{{background:{BG}!important;
     font-family:'Source Sans Pro','Segoe UI',Arial,sans-serif!important}}
.nav-tabs .nav-link{{color:{MUTED}!important;
    font-family:'Source Sans Pro','Segoe UI',Arial,sans-serif;
    font-size:12px;font-weight:600;text-transform:uppercase;
    letter-spacing:.4px;padding:10px 18px;
    border:none!important;border-bottom:2px solid transparent!important}}
.nav-tabs .nav-link.active{{color:{NAVY}!important;
    background:{WHITE}!important;border-bottom:2px solid {BLUE}!important}}
.nav-tabs{{border-bottom:1px solid {BORDER};background:{LIGHT}}}
::-webkit-scrollbar{{width:6px;height:6px}}
::-webkit-scrollbar-track{{background:{BG}}}
::-webkit-scrollbar-thumb{{background:{BORDER};border-radius:3px}}
"""

# ────────────────────────────────────────────────────────────
# 6.  LAYOUT
# ────────────────────────────────────────────────────────────
all_ret_cols = ret.columns.tolist()

app.layout = html.Div([

    # ── HEADER ──────────────────────────────────────────────
    html.Div([
        html.Div([
            html.Div("CUSTOMER RETENTION PROJECT", style=dict(
                fontSize="10px", color="#A8BEDB",
                letterSpacing=".15em", marginBottom="3px", fontWeight="600")),
            html.H1("Retention & BOB — Raw Data EDA Dashboard", style=dict(
                fontFamily="Georgia,'Times New Roman',serif",
                fontSize="20px", fontWeight="normal",
                color=WHITE, margin="0 0 2px 0")),
            html.Div(
                "Pre-Analysis Overview · bob.csv & Retention.csv · "
                "Data Quality & Distribution Audit",
                style=dict(fontSize="11px", color="#A8BEDB", fontWeight="300")),
        ]),
        html.Div([
            html.Div(
                f"Retention rows: {total_records:,}  ·  "
                f"BOB rows: {len(bob):,}" if bob is not None
                else f"Retention rows: {total_records:,}",
                style=dict(fontSize="11px", color="#A8BEDB")),
            html.Div(
                f"Retention cols: {len(ret.columns)}  ·  "
                f"BOB cols: {len(bob.columns) if bob is not None else 0}",
                style=dict(fontSize="11px", color="#A8BEDB")),
        ], style={"textAlign":"right"}),
    ], style=dict(
        background=f"linear-gradient(135deg,{NAVY} 0%,#243358 100%)",
        borderBottom=f"3px solid {ACCENT}",
        padding="14px 28px",
        display="flex", justifyContent="space-between", alignItems="center",
    )),

    # ── BODY ────────────────────────────────────────────────
    dbc.Container([

        # KPI row
        dbc.Row([
            dbc.Col(kpi(f"{total_records:,}", "Total Records",       BLUE),  width=2),
            dbc.Col(kpi(f"{len(ret.columns)}","Retention Columns",   BLUE2), width=2),
            dbc.Col(kpi(f"{len(bob.columns) if bob is not None else 0}",
                        "BOB Columns", GREEN), width=2),
            dbc.Col(kpi(f"{missing_pct}%",  "Avg Missing %",        RED),   width=2),
            dbc.Col(kpi(str(n_countries),   "Countries",            AMBER), width=2),
            dbc.Col(kpi(str(open_cases),    "Open Risk Cases",      ACCENT),width=2),
        ], className="mt-3 mb-1"),

        # Tabs
        dbc.Tabs([

            # ══════════════════════════════════════
            # TAB 1 · OVERVIEW
            # ══════════════════════════════════════
            dbc.Tab(label="Overview", tab_id="tab-overview", children=[
                dbc.Row([
                    dbc.Col(card("Missing Values — Retention.csv",
                                 graph("g-missing-ret", 230)),
                            width=6, className="mt-3"),
                    dbc.Col(card("Column Type Distribution",
                                 graph("g-coltypes", 230)),
                            width=6, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Dataset Preview — Retention.csv (first 10 rows)",
                        dash_table.DataTable(
                            id="preview-table",
                            data=ret.head(10).astype(str).to_dict("records"),
                            columns=[{"name":c,"id":c} for c in ret.columns],
                            style_table={"overflowX":"auto"},
                            style_cell=dict(backgroundColor=WHITE,color=NAVY,
                                border=f"1px solid {BORDER}",
                                fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                                fontSize="11px",padding="6px 10px",
                                maxWidth="160px",overflow="hidden",
                                textOverflow="ellipsis",whiteSpace="nowrap"),
                            style_header=dict(backgroundColor=LIGHT,color=NAVY,
                                fontWeight="700",border=f"1px solid {BORDER}",
                                fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                                fontSize="10px",textTransform="uppercase",
                                letterSpacing="0.4px"),
                            style_data_conditional=[
                                {"if":{"row_index":"odd"},"backgroundColor":LIGHT}],
                            page_size=10,
                        )), width=12),
                ]),
                dbc.Row([
                    dbc.Col(card("Descriptive Statistics — Numeric Columns",
                        dash_table.DataTable(
                            id="stats-table",
                            data=(ret[ret_num].describe().round(3)
                                  .reset_index().rename(columns={"index":"Stat"})
                                  .to_dict("records")),
                            columns=[{"name":c,"id":c} for c in ["Stat"]+ret_num],
                            style_table={"overflowX":"auto"},
                            style_cell=dict(backgroundColor=WHITE,color=NAVY,
                                border=f"1px solid {BORDER}",
                                fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                                fontSize="11px",padding="6px 10px"),
                            style_header=dict(backgroundColor=LIGHT,color=NAVY,
                                fontWeight="700",border=f"1px solid {BORDER}",
                                fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                                fontSize="10px",textTransform="uppercase"),
                            style_data_conditional=[
                                {"if":{"row_index":"odd"},"backgroundColor":LIGHT}],
                        )), width=12),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 2 · STATUS & RISK
            # ══════════════════════════════════════
            dbc.Tab(label="Status & Risk", tab_id="tab-status", children=[
                dbc.Row([
                    dbc.Col(card("Current Status",    graph("g-cur-status")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Resolution Status", graph("g-res-status")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Pull Type",         graph("g-pull-type")),
                            width=4, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Case Type",   graph("g-case-type")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Risk Level",  graph("g-risk")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Case Origin", graph("g-case-origin")),
                            width=4, className="mt-3"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 3 · CUSTOMER SEGMENTS
            # ══════════════════════════════════════
            dbc.Tab(label="Customer Segments", tab_id="tab-seg", children=[
                dbc.Row([
                    dbc.Col(card("Cases by Branch",       graph("g-branch")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Company Size",          graph("g-compsize")),
                            width=4, className="mt-3"),
                    dbc.Col(card("Customer Tier",         graph("g-tier")),
                            width=4, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Company Size × Pull Type",     graph("g-size-pull",260)),
                            width=6, className="mt-3"),
                    dbc.Col(card("Branch × Resolution Status",   graph("g-branch-res",260)),
                            width=6, className="mt-3"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 4 · NUMERIC ANALYSIS
            # ══════════════════════════════════════
            dbc.Tab(label="Numeric Analysis", tab_id="tab-num", children=[
                dbc.Row([
                    dbc.Col(card("Select Numeric Column",
                        dcc.Dropdown(id="num-col-dd",
                            options=[{"label":c,"value":c} for c in ret_num],
                            value=ret_num[0] if ret_num else None,
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                    dbc.Col(card("Quick Statistics",
                        html.Div(id="num-stats",
                                 style={"fontSize":"12px","color":NAVY,
                                        "lineHeight":"1.9"})),
                            width=8, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Histogram", graph("num-hist",270)),
                            width=8, className="mt-3"),
                    dbc.Col(card("Box Plot",  graph("num-box",270)),
                            width=4, className="mt-3"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 5 · BIVARIATE EXPLORER
            # ══════════════════════════════════════
            dbc.Tab(label="Bivariate Explorer", tab_id="tab-bi", children=[
                dbc.Row([
                    dbc.Col(card("X-Axis",
                        dcc.Dropdown(id="bi-x",
                            options=[{"label":c,"value":c} for c in all_ret_cols],
                            value=ret_cat[0] if ret_cat else all_ret_cols[0],
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                    dbc.Col(card("Y-Axis",
                        dcc.Dropdown(id="bi-y",
                            options=[{"label":c,"value":c} for c in all_ret_cols],
                            value=ret_num[0] if ret_num else all_ret_cols[1],
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                    dbc.Col(card("Colour By (optional)",
                        dcc.Dropdown(id="bi-color",
                            options=([{"label":"None","value":"None"}] +
                                     [{"label":c,"value":c} for c in ret_cat]),
                            value="None",
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("", graph("bi-chart",360)), width=12, className="mt-2"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 6 · CORRELATION
            # ══════════════════════════════════════
            dbc.Tab(label="Correlation", tab_id="tab-corr", children=[
                dbc.Row([
                    dbc.Col(card("Pearson Correlation Matrix",
                                 graph("corr-heat",400)),
                            width=12, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Top Correlated Pairs — Scatter Plots",
                                 graph("corr-pairs",310)),
                            width=12, className="mt-2"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 7 · TIME TRENDS
            # ══════════════════════════════════════
            dbc.Tab(label="Time Trends", tab_id="tab-time", children=[
                dbc.Row([
                    dbc.Col(card("Date Column",
                        dcc.Dropdown(id="ts-date",
                            options=([{"label":c,"value":c} for c in ret_dt]
                                     if ret_dt else [{"label":"None","value":"none"}]),
                            value=ret_dt[0] if ret_dt else "none",
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                    dbc.Col(card("Numeric Metric",
                        dcc.Dropdown(id="ts-metric",
                            options=([{"label":c,"value":c} for c in ret_num]
                                     if ret_num else [{"label":"None","value":"none"}]),
                            value=ret_num[0] if ret_num else "none",
                            clearable=False, style=DD)),
                            width=4, className="mt-3"),
                    dbc.Col(card("Frequency",
                        dcc.Dropdown(id="ts-freq",
                            options=[{"label":"Daily","value":"D"},
                                     {"label":"Weekly","value":"W"},
                                     {"label":"Monthly","value":"ME"},
                                     {"label":"Quarterly","value":"QE"}],
                            value="ME", clearable=False, style=DD)),
                            width=4, className="mt-3"),
                ]),
                dbc.Row([
                    dbc.Col(card("Case Volume Over Time",  graph("ts-vol",250)),
                            width=6, className="mt-2"),
                    dbc.Col(card("Metric Average Over Time", graph("ts-met",250)),
                            width=6, className="mt-2"),
                ]),
                dbc.Row([
                    dbc.Col(card("Month × Year Heatmap", graph("ts-heat",250)),
                            width=12, className="mt-2"),
                ]),
            ]),

            # ══════════════════════════════════════
            # TAB 8 · BOB FILE
            # ══════════════════════════════════════
            dbc.Tab(label="BOB File", tab_id="tab-bob", children=[
                html.Div(id="bob-content", className="mt-3"),
            ]),

        ], id="tabs", active_tab="tab-overview", style={"marginTop":"12px"}),

    ], fluid=True, style={"maxWidth":"1440px","padding":"0 20px"}),

    # ── FOOTER ──────────────────────────────────────────────
    html.Div([
        html.Span("Pre-Analysis EDA Dashboard · Customer Retention Project · Confidential"),
        html.Span("Data: Retention.csv + bob.csv · Plotly Dash"),
    ], style=dict(backgroundColor=WHITE, borderTop=f"1px solid {BORDER}",
                  padding="7px 28px", display="flex",
                  justifyContent="space-between",
                  fontSize="10px", color=MUTED, marginTop="20px")),

], style={"backgroundColor":BG,"minHeight":"100vh"})


# ────────────────────────────────────────────────────────────
# 7.  CALLBACKS
# ────────────────────────────────────────────────────────────

# ── shared bar helper ─────────────────────────────────────────
def _bar(df, col, title="", top_n=15):
    if col not in df.columns:
        return empty_fig(f"'{col}' not found")
    vc = df[col].dropna().value_counts().head(top_n).reset_index()
    vc.columns = ["Cat","Count"]
    if vc.empty:
        return empty_fig("No data")
    fig = go.Figure(go.Bar(
        x=vc["Cat"], y=vc["Count"],
        marker_color=COLORWAY[:len(vc)],
        text=vc["Count"], textposition="outside",
    ))
    fig.update_layout(xaxis_tickangle=-30,
                      yaxis=dict(range=[0, vc["Count"].max()*1.25]))
    return atheme(fig, title)


# ── TAB 1: Overview ──────────────────────────────────────────
@app.callback(
    Output("g-missing-ret","figure"),
    Output("g-coltypes","figure"),
    Input("tabs","active_tab"),
)
def cb_overview(_):
    # Missing
    mis = (ret.isnull().mean()*100).round(1)
    mdf = mis[mis>0].sort_values(ascending=True).reset_index()
    mdf.columns = ["Field","Pct"]
    if mdf.empty:
        f_mis = empty_fig("No missing values ✓")
    else:
        cols = [RED if v>=50 else AMBER if v>=30 else BLUE for v in mdf["Pct"]]
        f_mis = go.Figure(go.Bar(
            y=mdf["Field"], x=mdf["Pct"], orientation="h",
            marker_color=cols,
            text=[f"{v}%" for v in mdf["Pct"]], textposition="outside"))
        f_mis.update_layout(xaxis_range=[0,115])
    atheme(f_mis, "Missing Values — Retention.csv")

    # Col types
    def tc(df, name):
        c = len(df.select_dtypes(include="object").columns)
        n = len(df.select_dtypes(include="number").columns)
        d = len([x for x in df.columns
                 if pd.api.types.is_datetime64_any_dtype(df[x])])
        return name, c, n, d

    rows = [tc(ret,"Retention.csv")]
    if bob is not None: rows.append(tc(bob,"bob.csv"))
    names = [r[0] for r in rows]
    f_ct = go.Figure()
    for vals,lbl,col in [([r[1] for r in rows],"Categorical",GREEN),
                          ([r[2] for r in rows],"Numeric",    BLUE),
                          ([r[3] for r in rows],"Date/Time",  ACCENT)]:
        f_ct.add_trace(go.Bar(name=lbl, x=names, y=vals,
                               marker_color=col, text=vals, textposition="inside"))
    f_ct.update_layout(barmode="stack",
                       legend=dict(orientation="h",y=-0.28))
    atheme(f_ct, "Column Type Distribution")
    return f_mis, f_ct


# ── TAB 2: Status & Risk ─────────────────────────────────────
@app.callback(
    Output("g-cur-status","figure"),
    Output("g-res-status","figure"),
    Output("g-pull-type","figure"),
    Output("g-case-type","figure"),
    Output("g-risk","figure"),
    Output("g-case-origin","figure"),
    Input("tabs","active_tab"),
)
def cb_status(_):
    return (
        _bar(ret,"Current Status",   "Current Status"),
        _bar(ret,"Resolution Status","Resolution Status"),
        _bar(ret,"Pull Type",        "Pull Type"),
        _bar(ret,"Case Type",        "Case Type"),
        _bar(ret,"Risk",             "Risk Level"),
        _bar(ret,"Case Origin",      "Case Origin"),
    )


# ── TAB 3: Customer Segments ─────────────────────────────────
@app.callback(
    Output("g-branch","figure"),
    Output("g-compsize","figure"),
    Output("g-tier","figure"),
    Output("g-size-pull","figure"),
    Output("g-branch-res","figure"),
    Input("tabs","active_tab"),
)
def cb_segments(_):
    f_br = _bar(ret,"Branch",       "Cases by Branch", top_n=20)
    f_cs = _bar(ret,"CompanySize",  "Company Size")
    f_ti = _bar(ret,"Customer Tier","Customer Tier")

    # Company size × Pull Type
    if "CompanySize" in ret.columns and "Pull Type" in ret.columns:
        tmp = (ret.dropna(subset=["CompanySize","Pull Type"])
                  .groupby(["CompanySize","Pull Type"])
                  .size().reset_index(name="Count"))
        f_sp = px.bar(tmp, x="CompanySize", y="Count",
                      color="Pull Type", barmode="group",
                      color_discrete_sequence=COLORWAY)
        atheme(f_sp,"Company Size × Pull Type")
    else:
        f_sp = empty_fig()

    # Branch × Resolution heatmap
    if "Branch" in ret.columns and "Resolution Status" in ret.columns:
        br  = ret["Branch"].value_counts().nlargest(12).index
        rs  = ret["Resolution Status"].value_counts().nlargest(6).index
        sub = ret[ret["Branch"].isin(br) & ret["Resolution Status"].isin(rs)]
        cross = pd.crosstab(sub["Branch"], sub["Resolution Status"])
        f_bh = px.imshow(cross, text_auto=True, aspect="auto",
                         color_continuous_scale=[[0,LIGHT],[0.5,BLUE2],[1,NAVY]])
        atheme(f_bh,"Branch × Resolution Status")
    else:
        f_bh = empty_fig()

    return f_br, f_cs, f_ti, f_sp, f_bh


# ── TAB 4: Numeric Analysis ──────────────────────────────────
@app.callback(
    Output("num-hist","figure"),
    Output("num-box","figure"),
    Output("num-stats","children"),
    Input("num-col-dd","value"),
)
def cb_numeric(col):
    if not col or col not in ret.columns:
        e = empty_fig()
        return e, e, "Select a column."
    s = ret[col].dropna()

    # Histogram
    fh = go.Figure(go.Histogram(
        x=s, nbinsx=35,
        marker_color=BLUE,
        marker_line=dict(color=WHITE,width=0.4),
        opacity=0.85, name=col))
    fh.add_vline(x=s.mean(), line_dash="dash", line_color=ACCENT,
                 annotation_text=f"Mean {s.mean():.2f}",
                 annotation_font_color=ACCENT, annotation_font_size=10)
    atheme(fh, f"Distribution — {col}")

    # Box
    fb = go.Figure(go.Box(
        y=s, name=col,
        marker_color=BLUE2, line_color=NAVY,
        boxmean="sd", fillcolor=SKY))
    atheme(fb, f"Box Plot — {col}")

    # Stats
    st = s.describe()
    stats = html.Div([
        html.Div([
            html.Span(f"{k}: ", style={"color":MUTED,"fontSize":"11px"}),
            html.Span(f"{v:,.3f}" if isinstance(v,float) else str(v),
                      style={"color":NAVY,"fontWeight":"600","fontSize":"11px"}),
        ], style={"display":"inline-block","marginRight":"18px","marginBottom":"4px"})
        for k,v in [("Count",int(st["count"])),("Min",st["min"]),
                    ("Max",st["max"]),("Mean",st["mean"]),
                    ("Median",st["50%"]),("Std",st["std"]),
                    ("Skew",float(s.skew())),("Kurt",float(s.kurtosis())),
                    ("Nulls",int(ret[col].isnull().sum()))]
    ])
    return fh, fb, stats


# ── TAB 5: Bivariate ─────────────────────────────────────────
@app.callback(
    Output("bi-chart","figure"),
    Input("bi-x","value"),
    Input("bi-y","value"),
    Input("bi-color","value"),
)
def cb_bivariate(x_col, y_col, color_col):
    if not x_col or not y_col or x_col == y_col:
        return empty_fig("Select two different features")
    ca = None if (not color_col or color_col=="None") else color_col
    try:
        if x_col in ret_num and y_col in ret_num:
            samp = ret.sample(min(2000,len(ret)),random_state=42)
            fig  = px.scatter(samp, x=x_col, y=y_col, color=ca,
                              opacity=0.65, trendline="ols",
                              color_discrete_sequence=COLORWAY)
            title = f"Scatter: {y_col} vs {x_col}"
        elif x_col in ret_cat and y_col in ret_num:
            top = ret[x_col].value_counts().nlargest(15).index
            fig = px.box(ret[ret[x_col].isin(top)], x=x_col, y=y_col,
                         color=ca, color_discrete_sequence=COLORWAY)
            fig.update_traces(marker_size=3)
            title = f"Box: {y_col} by {x_col}"
        elif x_col in ret_num and y_col in ret_cat:
            top = ret[y_col].value_counts().nlargest(15).index
            fig = px.violin(ret[ret[y_col].isin(top)], x=y_col, y=x_col,
                            box=True, color=ca,
                            color_discrete_sequence=COLORWAY)
            title = f"Violin: {x_col} by {y_col}"
        else:
            tx = ret[x_col].value_counts().nlargest(15).index
            ty = ret[y_col].value_counts().nlargest(15).index
            sub = ret[ret[x_col].isin(tx) & ret[y_col].isin(ty)]
            cross = pd.crosstab(sub[x_col], sub[y_col])
            fig = px.imshow(cross, text_auto=True, aspect="auto",
                            color_continuous_scale=[[0,LIGHT],[0.5,BLUE2],[1,NAVY]])
            title = f"Crosstab: {x_col} × {y_col}"
    except Exception as exc:
        return empty_fig(f"Cannot render: {exc}")
    return atheme(fig, title)


# ── TAB 6: Correlation ───────────────────────────────────────
@app.callback(
    Output("corr-heat","figure"),
    Output("corr-pairs","figure"),
    Input("tabs","active_tab"),
)
def cb_corr(_):
    if len(ret_num) < 2:
        e = empty_fig("Not enough numeric columns")
        return e, e
    corr = ret[ret_num].corr().round(3)
    fh = go.Figure(go.Heatmap(
        z=corr.values, x=corr.columns, y=corr.index,
        colorscale=[[0,RED],[0.5,LIGHT],[1,BLUE]],
        zmin=-1, zmax=1,
        text=corr.values.round(2), texttemplate="%{text}",
        textfont=dict(size=9),
        colorbar=dict(tickfont=dict(color=NAVY),len=0.9),
    ))
    fh.update_layout(xaxis_tickangle=-45,
                     height=max(300,len(ret_num)*42))
    atheme(fh, "Pearson Correlation Matrix")

    pairs = (corr.abs()
                 .where(np.triu(np.ones(corr.shape),k=1).astype(bool))
                 .stack().reset_index())
    pairs.columns = ["A","B","r"]
    pairs = pairs.sort_values("r",ascending=False).head(6)
    n = len(pairs)
    if n == 0:
        return fh, empty_fig("No numeric pairs")
    cp = min(3,n); rp = (n+cp-1)//cp
    fp = make_subplots(rows=rp, cols=cp,
                       subplot_titles=[f"{r['A']} × {r['B']} (r={r['r']:.2f})"
                                       for _,r in pairs.iterrows()])
    for idx,(_,row) in enumerate(pairs.iterrows()):
        ri,ci = divmod(idx,cp)
        samp = (ret[[row["A"],row["B"]]].dropna()
                .sample(min(500,len(ret)),random_state=42))
        fp.add_trace(
            go.Scatter(x=samp[row["A"]], y=samp[row["B"]],
                       mode="markers",
                       marker=dict(color=BLUE,size=4,opacity=0.55),
                       showlegend=False),
            row=ri+1, col=ci+1)
    fp.update_layout(height=280*rp, paper_bgcolor=WHITE,
                     plot_bgcolor=LIGHT,
                     font=dict(family="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                               color=NAVY,size=10),
                     margin=dict(l=40,r=16,t=40,b=40))
    return fh, fp


# ── TAB 7: Time Trends ───────────────────────────────────────
@app.callback(
    Output("ts-vol","figure"),
    Output("ts-met","figure"),
    Output("ts-heat","figure"),
    Input("ts-date","value"),
    Input("ts-metric","value"),
    Input("ts-freq","value"),
)
def cb_time(date_col, metric_col, freq):
    e = empty_fig("No date columns found")
    if not date_col or date_col=="none" or date_col not in ret_dt:
        return e, e, e
    tmp = ret[[date_col]].dropna()

    vol = tmp.resample(freq,on=date_col).size().reset_index(name="Count")
    fv = go.Figure(go.Scatter(
        x=vol[date_col], y=vol["Count"],
        mode="lines+markers",
        line=dict(color=BLUE,width=2),
        marker=dict(size=5,color=NAVY),
        fill="tozeroy", fillcolor=SKY))
    fv.update_layout(xaxis_title=date_col, yaxis_title="Cases")
    atheme(fv,"Case Volume Over Time")

    fm = go.Figure()
    if metric_col and metric_col!="none" and metric_col in ret_num:
        tmp2  = ret[[date_col,metric_col]].dropna()
        trend = tmp2.resample(freq,on=date_col)[metric_col].mean().reset_index()
        fm.add_trace(go.Scatter(
            x=trend[date_col], y=trend[metric_col],
            mode="lines+markers",
            line=dict(color=GREEN,width=2),
            marker=dict(size=5,color=GREEN),
            fill="tozeroy", fillcolor="#D4EEE0"))
        fm.update_layout(xaxis_title=date_col,
                         yaxis_title=f"Avg {metric_col}")
    atheme(fm, f"Metric: {metric_col}")

    fhm = empty_fig("Cannot build heatmap")
    try:
        t3 = ret[[date_col]].dropna().copy()
        t3["Year"]  = t3[date_col].dt.year
        t3["Month"] = t3[date_col].dt.month
        piv = t3.groupby(["Year","Month"]).size().unstack(fill_value=0)
        ml  = ["Jan","Feb","Mar","Apr","May","Jun",
               "Jul","Aug","Sep","Oct","Nov","Dec"]
        piv.columns = [ml[i-1] for i in piv.columns]
        fhm = go.Figure(go.Heatmap(
            z=piv.values, x=piv.columns,
            y=piv.index.astype(str),
            colorscale=[[0,LIGHT],[0.5,BLUE2],[1,NAVY]],
            text=piv.values, texttemplate="%{text}",
            textfont=dict(size=9),
            colorbar=dict(tickfont=dict(color=NAVY))))
        fhm.update_layout(xaxis_title="Month", yaxis_title="Year")
        atheme(fhm,"Case Count — Month × Year")
    except Exception:
        pass
    return fv, fm, fhm


# ── TAB 8: BOB File ──────────────────────────────────────────
@app.callback(
    Output("bob-content","children"),
    Input("tabs","active_tab"),
)
def cb_bob(_):
    if bob is None:
        return html.Div(
            "bob.csv not loaded. Place it in the same folder as app.py.",
            style={"color":RED,"padding":"20px","fontSize":"13px"})

    bm = (bob.isnull().mean()*100).round(1)
    bd = bm[bm>0].sort_values(ascending=True).reset_index()
    bd.columns = ["Field","Pct"]
    if bd.empty:
        fm = empty_fig("No missing values in bob.csv ✓")
    else:
        cols = [RED if v>=50 else AMBER if v>=30 else BLUE for v in bd["Pct"]]
        fm = go.Figure(go.Bar(
            y=bd["Field"], x=bd["Pct"], orientation="h",
            marker_color=cols,
            text=[f"{v}%" for v in bd["Pct"]], textposition="outside"))
        fm.update_layout(xaxis_range=[0,115])
    atheme(fm,"Missing Values — bob.csv")

    return [
        dbc.Row([
            dbc.Col(card("Missing Values — bob.csv",
                dcc.Graph(figure=fm,config={"displayModeBar":False},
                          style={"height":"220px"})), width=6),
            dbc.Col(card("Renewal Type",
                dcc.Graph(figure=_bar(bob,"renewal_type","Renewal Type"),
                          config={"displayModeBar":False},
                          style={"height":"220px"})), width=6),
        ]),
        dbc.Row([
            dbc.Col(card("Line of Business",
                dcc.Graph(figure=_bar(bob,"line_of_business","Line of Business"),
                          config={"displayModeBar":False},
                          style={"height":"220px"})), width=6),
            dbc.Col(card("System Status",
                dcc.Graph(figure=_bar(bob,"system_status","System Status"),
                          config={"displayModeBar":False},
                          style={"height":"220px"})), width=6),
        ]),
        dbc.Row([
            dbc.Col(card("BOB File Preview — First 10 Rows",
                dash_table.DataTable(
                    data=bob.head(10).astype(str).to_dict("records"),
                    columns=[{"name":c,"id":c} for c in bob.columns],
                    style_table={"overflowX":"auto"},
                    style_cell=dict(backgroundColor=WHITE,color=NAVY,
                        border=f"1px solid {BORDER}",
                        fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                        fontSize="11px",padding="6px 10px",
                        maxWidth="160px",overflow="hidden",
                        textOverflow="ellipsis",whiteSpace="nowrap"),
                    style_header=dict(backgroundColor=LIGHT,color=NAVY,
                        fontWeight="700",border=f"1px solid {BORDER}",
                        fontFamily="'Source Sans Pro','Segoe UI',Arial,sans-serif",
                        fontSize="10px",textTransform="uppercase"),
                    style_data_conditional=[
                        {"if":{"row_index":"odd"},"backgroundColor":LIGHT}],
                    page_size=10,
                )), width=12),
        ]),
    ]


# ────────────────────────────────────────────────────────────
# 8.  RUN
# ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8050)
