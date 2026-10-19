import math
from io import BytesIO
from datetime import datetime

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# v3.0 FIXED: removed the custom appearance selector; use Streamlit's native top-right menu.

st.set_page_config(
    page_title="GridLab | Transformer Analyzer",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ---------------------- Neon engineering interface ----------------------
# Version 3 uses a fixed futuristic neon visual identity. Streamlit's native
# appearance options remain available from the top-right three-dot menu.
if "started" not in st.session_state:
    st.session_state["started"] = False
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "Overview"

THEMES = {
    "Neon": {
        "bg": "#070b16", "panel": "#0d1628", "panel2": "#111f37", "border": "#233c60",
        "text": "#f3f8ff", "body": "#c9d8ef", "muted": "#8fa8c9", "blue": "#7c8cff",
        "cyan": "#32f5e6", "header": "rgba(7,11,22,.94)", "sidebar": "#091225",
        "hero": "linear-gradient(115deg,#101e3d 0%,#0b2637 55%,#10152e 100%)", "input": "#101c31", "plot": "#0d1628",
        "grid": "#263c5a", "pill": "rgba(50,245,230,.10)", "shadow": "rgba(0,0,0,.28)"
    },
    "Light": {
        "bg": "#f4f7fc", "panel": "#ffffff", "panel2": "#edf4ff", "border": "#d9e4f2",
        "text": "#15213a", "body": "#34445e", "muted": "#667994", "blue": "#5b4bff",
        "cyan": "#008eaa", "header": "rgba(244,247,252,.96)", "sidebar": "#ffffff",
        "hero": "linear-gradient(115deg,#ffffff 0%,#eaf2ff 55%,#e6fbff 100%)", "input": "#ffffff", "plot": "#ffffff",
        "grid": "#d7e0ed", "pill": "#e3f8fa", "shadow": "rgba(16,24,40,.06)"
    }
}
T = THEMES["Neon"]
NEON = True
plt.rcParams.update({
    "figure.facecolor": T["plot"], "axes.facecolor": T["plot"],
    "axes.edgecolor": T["grid"], "axes.labelcolor": T["body"],
    "text.color": T["text"], "xtick.color": T["muted"], "ytick.color": T["muted"],
    "grid.color": T["grid"], "legend.labelcolor": T["body"]
})

st.markdown(f""" <style> @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'); :root {{ --bg:{T['bg']}; --panel:{T['panel']}; --panel2:{T['panel2']}; --border:{T['border']}; --text:{T['text']}; --body:{T['body']}; --muted:{T['muted']}; --blue:{T['blue']}; --cyan:{T['cyan']}; }} html, body, [class*="css"] {{ font-family: Inter, "Segoe UI", sans-serif; }} .stApp {{ background: radial-gradient(ellipse at 82% 2%, {('rgba(50,245,230,.12)' if NEON else 'rgba(91,75,255,.07)')}, transparent 28%), radial-gradient(ellipse at 5% 25%, {('rgba(91,75,255,.12)' if NEON else 'rgba(0,142,170,.05)')}, transparent 30%), var(--bg); color:var(--text); }} [data-testid="stHeader"] {{ background:{T['header']}; }} .block-container {{ max-width:1500px; padding-top:1.15rem; padding-bottom:3rem; }} h1,h2,h3 {{ color:var(--text) !important; letter-spacing:-.03em; }} h1 {{ font-size:2.1rem !important; font-weight:800 !important; }} h2 {{ font-size:1.42rem !important; font-weight:750 !important; }} h3 {{ font-size:1.06rem !important; font-weight:700 !important; }} p, label, li, [data-testid="stMarkdownContainer"] {{ color:var(--body); }} [data-testid="stCaptionContainer"] {{ color:var(--muted); }} [data-testid="stSidebar"] {{ background:linear-gradient(180deg,{T['sidebar']},var(--bg)); border-right:1px solid var(--border); }} [data-testid="stSidebar"] * {{ color:var(--body); }} [data-testid="stMetric"] {{ background:linear-gradient(145deg,var(--panel2),var(--panel)); border:1px solid var(--border); border-radius:17px; padding:17px 18px; box-shadow:0 8px 26px {T['shadow']}; min-height:112px; transition:transform .18s ease,border-color .18s ease; }} [data-testid="stMetric"]:hover {{ transform:translateY(-2px); border-color:var(--cyan); box-shadow:0 0 22px {('rgba(50,245,230,.10)' if NEON else 'rgba(91,75,255,.08)')}; }} [data-testid="stMetricLabel"] {{ color:var(--muted) !important; font-size:.82rem; }} [data-testid="stMetricValue"] {{ color:var(--cyan) !important; font-weight:800 !important; }} [data-testid="stMetricDelta"] {{ color:#18c79a !important; }} div[data-testid="stVerticalBlockBorderWrapper"] {{ background:var(--panel); border:1px solid var(--border); border-radius:17px; padding:1rem; box-shadow:0 5px 20px {T['shadow']}; }} .hero {{ background:{T['hero']}; border:1px solid var(--border); border-radius:22px; padding:27px 30px; margin-bottom:1.1rem; box-shadow:0 10px 34px {T['shadow']}; position:relative; overflow:hidden; }} .hero:after {{ content:""; position:absolute; right:-55px; top:-70px; width:220px; height:220px; border:1px solid {T['cyan']}; border-radius:50%; opacity:.14; box-shadow:0 0 0 24px rgba(50,245,230,.025),0 0 0 48px rgba(50,245,230,.02); pointer-events:none; }} .eyebrow {{ color:var(--cyan); font-size:.73rem; letter-spacing:.18em; font-weight:800; text-transform:uppercase; }} .hero-title {{ color:var(--text); font-size:2.15rem; line-height:1.13; font-weight:800; letter-spacing:-.045em; margin:.45rem 0 .6rem; }} .hero-sub {{ color:var(--muted); font-size:.96rem; max-width:900px; }} .pill {{ display:inline-block; padding:5px 10px; border-radius:999px; background:{T['pill']}; color:var(--cyan); border:1px solid var(--border); font-size:.75rem; font-weight:700; margin-right:5px; margin-top:8px; }} .landing {{ padding:3rem 1rem 2rem; }} .landing-title {{ font-size:clamp(2.4rem,6vw,4.8rem); line-height:1.02; font-weight:800; letter-spacing:-.06em; color:var(--text); margin:.6rem 0 1rem; }} .neon-word {{ color:var(--cyan); text-shadow:{('0 0 24px rgba(50,245,230,.25)' if NEON else 'none')}; }} .landing-copy {{ color:var(--muted); font-size:1.08rem; max-width:760px; line-height:1.75; }} .feature-card {{ height:100%; padding:1.1rem; border:1px solid var(--border); border-radius:16px; background:linear-gradient(145deg,var(--panel2),var(--panel)); }} .feature-num {{ color:var(--cyan); font-size:.75rem; font-weight:800; letter-spacing:.14em; }} div.stButton > button, div.stDownloadButton > button {{ border-radius:11px; font-weight:700; border:1px solid var(--border); min-height:2.7rem; transition:all .18s ease; }} div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] {{ background:linear-gradient(120deg,#655cff,#00bfc9); color:#fff !important; border-color:transparent; box-shadow:0 0 18px {('rgba(50,245,230,.13)' if NEON else 'rgba(91,75,255,.10)')}; }} div.stButton > button:hover, div.stDownloadButton > button:hover {{ border-color:var(--cyan); box-shadow:0 0 20px rgba(50,245,230,.15); }} input, textarea {{ background:var(--panel) !important; color:var(--text) !important; border-color:var(--border) !important; border-radius:10px !important; }} [data-baseweb="select"] > div {{ background:var(--panel); border-color:var(--border); border-radius:10px; }} [data-testid="stDataFrame"], [data-testid="stTable"] {{ border:1px solid var(--border); border-radius:12px; overflow:hidden; }} [data-testid="stExpander"] {{ background:var(--panel); border:1px solid var(--border); border-radius:13px; }} [data-testid="stAlert"] {{ border-radius:12px; }} hr {{ border-color:var(--border) !important; }} a {{ color:var(--cyan) !important; }} .small-muted {{ color:var(--muted); font-size:.84rem; }} </style> """, unsafe_allow_html=True)

# ---------------------- Calculations ----------------------
DEFAULTS = {
    "rating_a": 100.0, "load_a": 75.0, "pf_a": 0.90, "core_a": 300.0, "cu_a": 1200.0,
    "rating_b": 150.0, "load_b": 75.0, "pf_b": 0.90, "core_b": 420.0, "cu_b": 1800.0,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

def calculate(rating_kva, load_pct, pf, core_w, full_cu_w):
    load = load_pct / 100.0
    output_kw = rating_kva * load * pf
    copper_w = full_cu_w * load**2
    total_w = core_w + copper_w
    output_w = output_kw * 1000
    denom = output_w + total_w
    efficiency = (output_w / denom * 100) if denom > 0 else None
    max_load = math.sqrt(core_w / full_cu_w) * 100 if full_cu_w > 0 else None
    return {
        "rating_kva": rating_kva, "load_pct": load_pct, "pf": pf, "core_w": core_w,
        "full_cu_w": full_cu_w, "output_kw": output_kw, "copper_w": copper_w,
        "total_w": total_w, "total_kw": total_w / 1000,
        "efficiency_pct": efficiency, "max_load_pct": max_load,
        "input_kw": output_kw + total_w / 1000,
    }

def validate(values):
    errs = []
    if not math.isfinite(values["rating_kva"]) or values["rating_kva"] <= 0:
        errs.append("Rated capacity must be greater than 0 kVA.")
    if not math.isfinite(values["load_pct"]) or not 0 <= values["load_pct"] <= 200:
        errs.append("Load percentage must be between 0% and 200%.")
    if not math.isfinite(values["pf"]) or not 0 <= values["pf"] <= 1:
        errs.append("Power factor must be between 0 and 1.")
    if not math.isfinite(values["core_w"]) or values["core_w"] < 0:
        errs.append("Core loss cannot be negative.")
    if not math.isfinite(values["full_cu_w"]) or values["full_cu_w"] < 0:
        errs.append("Full-load copper loss cannot be negative.")
    return errs

def get_transformer(letter):
    suffix = letter.lower()
    return {
        "rating_kva": float(st.session_state[f"rating_{suffix}"]),
        "load_pct": float(st.session_state[f"load_{suffix}"]),
        "pf": float(st.session_state[f"pf_{suffix}"]),
        "core_w": float(st.session_state[f"core_{suffix}"]),
        "full_cu_w": float(st.session_state[f"cu_{suffix}"]),
    }

def as_results(values):
    errors = validate(values)
    return (None, errors) if errors else (calculate(**{
        "rating_kva": values["rating_kva"], "load_pct": values["load_pct"],
        "pf": values["pf"], "core_w": values["core_w"], "full_cu_w": values["full_cu_w"]
    }), [])

def make_sweep(values, loads):
    rows = []
    for load_pct in loads:
        row = calculate(values["rating_kva"], float(load_pct), values["pf"], values["core_w"], values["full_cu_w"])
        rows.append({"Load (%)": float(load_pct), "Output (kW)": row["output_kw"],
                     "Copper loss (W)": row["copper_w"], "Total loss (W)": row["total_w"],
                     "Efficiency (%)": row["efficiency_pct"]})
    return pd.DataFrame(rows)

def efficiency_plot(a, b, load_max):
    loads = np.linspace(1, load_max, 200)
    fig, ax = plt.subplots(figsize=(8, 4.1))
    for label, values in [("Transformer A", a), ("Transformer B", b)]:
        if values:
            eff = [calculate(values["rating_kva"], float(x), values["pf"], values["core_w"], values["full_cu_w"])["efficiency_pct"] for x in loads]
            ax.plot(loads, eff, linewidth=2.5, label=label)
            m = math.sqrt(values["core_w"] / values["full_cu_w"]) * 100 if values["full_cu_w"] > 0 else None
            if m is not None and 0 < m <= load_max:
                ax.axvline(m, linestyle=":", alpha=.55)
    ax.set_title("Efficiency vs. load", loc="left", fontweight="bold")
    ax.set_xlabel("Load (%)"); ax.set_ylabel("Efficiency (%)")
    ax.grid(True, alpha=.22); ax.legend(frameon=False)
    fig.tight_layout()
    return fig

def loss_plot(a, b):
    labels, core, copper = [], [], []
    for label, values in [("Transformer A", a), ("Transformer B", b)]:
        if values:
            p = calculate(values["rating_kva"], values["load_pct"], values["pf"], values["core_w"], values["full_cu_w"])
            labels.append(label); core.append(p["core_w"]); copper.append(p["copper_w"])
    fig, ax = plt.subplots(figsize=(7, 4.1))
    x = np.arange(len(labels))
    ax.bar(x, core, label="Core loss")
    ax.bar(x, copper, bottom=core, label="Copper loss")
    ax.set_xticks(x, labels); ax.set_ylabel("Loss (W)")
    ax.set_title("Loss breakdown at selected load", loc="left", fontweight="bold")
    ax.grid(axis="y", alpha=.22); ax.legend(frameon=False)
    fig.tight_layout()
    return fig

def pdf_report(report_rows, notes):
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
        buf = BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
        styles = getSampleStyleSheet()
        story = [Paragraph("Transformer Performance Analyzer", styles["Title"]),
                 Paragraph(f"Generated: {datetime.now().strftime('%d %b %Y, %H:%M')}", styles["Normal"]),
                 Spacer(1, 14), Paragraph("Calculated results from user-entered values", styles["Heading2"]), Spacer(1, 8)]
        data = [["Parameter", "Transformer A", "Transformer B"]]
        for key, label, fmt in [
            ("output_kw", "Output power (kW)", "{:.3f}"),
            ("copper_w", "Copper loss (W)", "{:.2f}"),
            ("total_w", "Total loss (W)", "{:.2f}"),
            ("efficiency_pct", "Efficiency (%)", "{:.3f}"),
            ("max_load_pct", "Theoretical max-efficiency load (%)", "{:.2f}"),
        ]:
            row = [label]
            for name in ["Transformer A", "Transformer B"]:
                val = report_rows.get(name, {}).get(key)
                row.append(fmt.format(val) if val is not None else "N/A")
            data.append(row)
        table = Table(data, colWidths=[245, 120, 120], repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1D4ED8")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("GRID", (0,0), (-1,-1), .4, colors.HexColor("#D0D5DD")),
            ("BACKGROUND", (0,1), (-1,-1), colors.white),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#F2F6FC")]),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 7), ("BOTTOMPADDING", (0,0), (-1,-1), 7),
        ]))
        story.append(table); story.append(Spacer(1, 16))
        story.append(Paragraph("Method and limitations", styles["Heading2"]))
        story.append(Paragraph(notes, styles["BodyText"]))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Formulas: Pout = rated kVA × load fraction × PF; copper loss = full-load copper loss × load fraction²; total loss = core loss + copper loss; efficiency = Pout / (Pout + total loss) × 100.", styles["BodyText"]))
        doc.build(story)
        return buf.getvalue()
    except ImportError:
        return None

# ---------------------- Landing page and workspace navigation ----------------------
# No custom appearance dropdown: use Streamlit's native three-dot menu at top-right.
st.markdown("<div class='eyebrow'>GRIDLAB / TRANSFORMER INTELLIGENCE <span style='float:right;letter-spacing:.08em'>V 3.0</span></div>", unsafe_allow_html=True)

PAGES = ["Overview", "Performance Calculator", "Transformer Intelligence Lab", "Comparison Studio", "Load Analysis Lab", "Energy & Cost", "Reports", "Learn"]
if not st.session_state["started"]:
    # The first page is deliberately a clean landing page: no workspace sidebar.
    st.markdown(f""" <div class="landing"> <div class="pill">ENGINEERING ANALYTICS · V 3.0</div> <div class="landing-title">See beyond the<br><span class="neon-word">efficiency number.</span></div> <div class="landing-copy">A futuristic transformer performance workspace to explore losses, test operating scenarios, compare equipment, and turn calculations into practical engineering insight.</div> <div style="margin-top:1.2rem"><span class="pill">Loss intelligence</span><span class="pill">What-if scenarios</span><span class="pill">Energy economics</span><span class="pill">Explainable results</span></div> </div> """, unsafe_allow_html=True)
    a, b, c = st.columns(3)
    for col, num, title, desc in [
        (a, "01 / ANALYSE", "Performance engine", "Calculate efficiency, output power and loss components with transparent formulas."),
        (b, "02 / EXPLORE", "Scenario fingerprint", "See how the same transformer behaves as load and power factor change."),
        (c, "03 / DECIDE", "Engineering insights", "Get explainable observations, comparison results and estimated loss costs.")]:
        with col:
            st.markdown(f"<div class='feature-card'><div class='feature-num'>{num}</div><h3>{title}</h3><p>{desc}</p></div>", unsafe_allow_html=True)
    st.write("")
    go_left, go_btn, go_right = st.columns([1.5, 2, 1.5])
    with go_btn:
        if st.button("Launch Engineering Workspace →", type="primary", use_container_width=True):
            st.session_state["started"] = True
            st.session_state["active_page"] = "Overview"
            st.rerun()
    st.caption("Simulation and calculation only · No live transformer sensors are connected.")
    st.stop()

with st.sidebar:
    st.markdown("## ⚡ GRIDLAB")
    st.caption("TRANSFORMER INTELLIGENCE")
    st.markdown("---")
    page = st.radio("WORKSPACE", PAGES, index=PAGES.index(st.session_state["active_page"]), key="workspace_nav", label_visibility="collapsed")
    st.session_state["active_page"] = page
    st.markdown("---")
    if st.button("← Back to start", use_container_width=True):
        st.session_state["started"] = False
        st.rerun()
    st.caption("Steady-state estimates · SI units")
    st.caption("GRIDLAB · v3.0")

page = st.session_state["active_page"]
st.markdown(f""" <div class="hero"> <div class="eyebrow">GRIDLAB / TRANSFORMER INTELLIGENCE</div> <div class="hero-title">{page}</div> <div class="hero-sub">Explore transformer performance, inspect loss behaviour, and compare operating scenarios with transparent engineering calculations.</div> <div style="margin-top:14px"><span class="pill">Explainable analysis</span><span class="pill">SI units</span><span class="pill">Simulation workspace</span></div> </div> """, unsafe_allow_html=True)

raw_a, raw_b = get_transformer("A"), get_transformer("B")
res_a, err_a = as_results(raw_a)
res_b, err_b = as_results(raw_b)
valid_a = res_a is not None
valid_b = res_b is not None

def transformer_form(letter, title):
    suffix = letter.lower()
    st.markdown(f"### {title}")
    c1, c2 = st.columns(2)
    with c1:
        st.number_input("Rated capacity (kVA)", min_value=0.1, max_value=100000.0, step=10.0, key=f"rating_{suffix}")
        st.number_input("Load (%)", min_value=0.0, max_value=200.0, step=5.0, key=f"load_{suffix}")
        st.number_input("Power factor", min_value=0.0, max_value=1.0, step=0.05, format="%.2f", key=f"pf_{suffix}")
    with c2:
        st.number_input("Core loss (W)", min_value=0.0, max_value=10000000.0, step=50.0, key=f"core_{suffix}")
        st.number_input("Full-load copper loss (W)", min_value=0.0, max_value=10000000.0, step=100.0, key=f"cu_{suffix}")

def show_metrics(result, prefix):
    c1, c2, c3, c4 = st.columns(4)
    c1.metric(f"{prefix} output power", f'{result["output_kw"]:.3f} kW')
    c2.metric(f"{prefix} total losses", f'{result["total_kw"]:.3f} kW')
    c3.metric(f"{prefix} efficiency", f'{result["efficiency_pct"]:.3f}%' if result["efficiency_pct"] is not None else "N/A")
    c4.metric(f"{prefix} max-efficiency load", f'{result["max_load_pct"]:.1f}%' if result["max_load_pct"] is not None else "N/A")

if page == "Overview":
    st.subheader("Performance snapshot")
    if not valid_a and not valid_b:
        st.warning("Enter valid transformer values in the Performance Calculator to begin.")
    else:
        cols = st.columns(4)
        if valid_a:
            cols[0].metric("Transformer A efficiency", f'{res_a["efficiency_pct"]:.2f}%')
            cols[1].metric("Transformer A total losses", f'{res_a["total_kw"]:.3f} kW')
        if valid_b:
            cols[2].metric("Transformer B efficiency", f'{res_b["efficiency_pct"]:.2f}%')
            cols[3].metric("Transformer B total losses", f'{res_b["total_kw"]:.3f} kW')
        left, right = st.columns([1.35, 1])
        with left:
            st.markdown("#### Efficiency profile")
            fig = efficiency_plot(raw_a if valid_a else None, raw_b if valid_b else None, 200)
            st.pyplot(fig, use_container_width=True); plt.close(fig)
        with right:
            st.markdown("#### Loss breakdown")
            fig = loss_plot(raw_a if valid_a else None, raw_b if valid_b else None)
            st.pyplot(fig, use_container_width=True); plt.close(fig)
        st.info("Tip: use the Performance Calculator page to change input parameters. All pages use the same values.")
    st.markdown("#### Workspace")
    cards = st.columns(3)
    for col, title, desc in [
        (cards[0], "01 · Calculate", "Edit ratings, load, power factor and losses."),
        (cards[1], "02 · Compare", "Compare performance indicators side by side."),
        (cards[2], "03 · Export", "Download a results table or a report."),
    ]:
        with col:
            with st.container(border=True):
                st.markdown(f"**{title}**")
                st.caption(desc)

elif page == "Performance Calculator":
    st.markdown("Edit the values below. The results recalculate automatically.")
    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            transformer_form("A", "Transformer A")
    with right:
        with st.container(border=True):
            transformer_form("B", "Transformer B")
    st.markdown("### Calculated results")
    if err_a:
        for e in err_a: st.error("Transformer A: " + e)
    if err_b:
        for e in err_b: st.error("Transformer B: " + e)
    if valid_a:
        show_metrics(res_a, "A")
    if valid_b:
        show_metrics(res_b, "B")
    with st.expander("Show formulas and worked calculations"):
        st.latex(r"P_{out}(kW)=S_{rated}(kVA)\\times L\\times PF")
        st.latex(r"P_{cu}(W)=P_{cu,FL}\\times L^2")
        st.latex(r"P_{loss}=P_{core}+P_{cu}")
        st.latex(r"\\eta(\\%)=\\frac{P_{out}(W)}{P_{out}(W)+P_{loss}(W)}\\times100")
        if valid_a:
            st.markdown("**Transformer A worked values**")
            st.write(f'Load fraction = {raw_a["load_pct"]:.1f}/100 = {raw_a["load_pct"]/100:.3f}')
            st.write(f'Output power = {raw_a["rating_kva"]:.2f} × {raw_a["load_pct"]/100:.3f} × {raw_a["pf"]:.2f} = {res_a["output_kw"]:.3f} kW')
            st.write(f'Copper loss = {raw_a["full_cu_w"]:.2f} × ({raw_a["load_pct"]/100:.3f})² = {res_a["copper_w"]:.2f} W')
            st.write(f'Total losses = {raw_a["core_w"]:.2f} + {res_a["copper_w"]:.2f} = {res_a["total_w"]:.2f} W')
            st.write(f'Efficiency = {res_a["efficiency_pct"]:.3f}%' if res_a["efficiency_pct"] is not None else "Efficiency is undefined at zero output and zero loss.")

elif page == "Transformer Intelligence Lab":
    st.subheader("Transformer operating fingerprint")
    st.caption("A scenario-based analysis that turns a single set of transformer parameters into a load-and-power-factor performance map. This is a model-based estimate, not live condition monitoring.")
    if valid_a:
        # Load profile scenarios use transformer A as the reference unit.
        base = raw_a
        lcol, pfcol = st.columns(2)
        with lcol:
            load_points = st.multiselect("Load points to inspect (%)", [25, 40, 50, 60, 75, 80, 90, 100, 110, 125], default=[25, 50, 75, 100])
        with pfcol:
            pf_points = st.multiselect("Power factors to compare", [0.70, 0.80, 0.85, 0.90, 0.95, 1.00], default=[0.80, 0.90, 1.00], format_func=lambda x: f"{x:.2f}")
        rows = []
        for lp in load_points:
            for pfv in pf_points:
                q = calculate(base["rating_kva"], float(lp), float(pfv), base["core_w"], base["full_cu_w"])
                rows.append({"Load (%)": lp, "Power factor": pfv, "Output (kW)": q["output_kw"], "Copper loss (W)": q["copper_w"], "Total loss (W)": q["total_w"], "Efficiency (%)": q["efficiency_pct"]})
        if rows:
            df_fp = pd.DataFrame(rows)
            best = df_fp.loc[df_fp["Efficiency (%)"].idxmax()]
            m1, m2, m3 = st.columns(3)
            m1.metric("Best tested efficiency", f"{best['Efficiency (%)']:.3f}%")
            m2.metric("Scenario load", f"{best['Load (%)']:.0f}%")
            m3.metric("Scenario power factor", f"{best['Power factor']:.2f}")
            st.dataframe(df_fp, use_container_width=True, hide_index=True)
            fig, ax = plt.subplots(figsize=(9, 4.2))
            for pfv in sorted(df_fp["Power factor"].unique()):
                subset = df_fp[df_fp["Power factor"] == pfv].sort_values("Load (%)")
                ax.plot(subset["Load (%)"], subset["Efficiency (%)"], marker="o", linewidth=2.2, label=f"PF {pfv:.2f}")
            ax.set_title("Operating fingerprint · efficiency across scenarios", loc="left", fontweight="bold")
            ax.set_xlabel("Load (%)"); ax.set_ylabel("Efficiency (%)"); ax.grid(True, alpha=.22); ax.legend(frameon=False)
            fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close(fig)
            # Explainable rule-based observations, not a machine-learning diagnosis.
            current = res_a
            insights = []
            if current["max_load_pct"] is not None:
                insights.append(f"The simplified loss model predicts maximum efficiency near {current['max_load_pct']:.1f}% load, where core loss equals copper loss.")
            if current["copper_w"] > current["core_w"]:
                insights.append("At the selected operating point, copper loss exceeds core loss. Load-dependent winding loss is the larger of these two modeled components.")
            else:
                insights.append("At the selected operating point, core loss is at least as large as copper loss. Fixed losses are a substantial part of the modeled loss total at this load.")
            if current["load_pct"] > 100:
                insights.append("The selected load exceeds nameplate rating. Treat this as a mathematical scenario, not a safe operating recommendation.")
            st.markdown("#### Explainable engineering observations")
            for insight in insights:
                st.info(insight)
            st.caption("The 'best tested efficiency' is only the best among selected scenarios; it is not a universal optimum. Real transformer limits require nameplate, thermal, insulation and manufacturer data.")
        else:
            st.info("Select at least one load point and one power factor to generate the operating fingerprint.")
    else:
        st.warning("Enter valid Transformer A inputs in the Performance Calculator first.")

elif page == "Comparison Studio":
    st.subheader("Side-by-side performance")
    if valid_a and valid_b:
        show_metrics(res_a, "A"); show_metrics(res_b, "B")
        rows = []
        for key, label, unit in [
            ("rating_kva","Rated capacity","kVA"), ("load_pct","Operating load","%"),
            ("pf","Power factor",""), ("output_kw","Output power","kW"),
            ("core_w","Core losses","W"), ("copper_w","Copper losses at selected load","W"),
            ("total_w","Total losses","W"), ("efficiency_pct","Efficiency","%"),
        ]:
            va, vb = res_a.get(key), res_b.get(key)
            diff = (vb-va) if va is not None and vb is not None else None
            rows.append({"Parameter":label, "Transformer A":va, "Transformer B":vb, "B − A":diff, "Unit":unit})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        fig = efficiency_plot(raw_a, raw_b, 200)
        st.pyplot(fig, use_container_width=True); plt.close(fig)
        st.caption("Comparison is based on the selected inputs; a larger transformer is not automatically better for every duty.")
    else:
        st.warning("Please enter valid inputs for both transformers on the Performance Calculator page.")

elif page == "Load Analysis Lab":
    st.subheader("Explore performance across loading conditions")
    max_load = st.slider("Maximum load to display (%)", min_value=50, max_value=200, value=150, step=10)
    selected_load = st.slider("Inspect a specific load (%)", min_value=0, max_value=200, value=int(raw_a["load_pct"]), step=5)
    loads = np.linspace(0, max_load, int(max_load / 5) + 1)
    chosen = []
    if valid_a: chosen.append(("Transformer A", raw_a))
    if valid_b: chosen.append(("Transformer B", raw_b))
    if chosen:
        rows = []
        for name, v in chosen:
            p = calculate(v["rating_kva"], selected_load, v["pf"], v["core_w"], v["full_cu_w"])
            rows.append({"Transformer":name, "Load (%)":selected_load, "Output (kW)":p["output_kw"],
                         "Copper loss (W)":p["copper_w"], "Total loss (W)":p["total_w"], "Efficiency (%)":p["efficiency_pct"]})
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        fig, ax = plt.subplots(figsize=(9, 4.3))
        for name, v in chosen:
            sweep = make_sweep(v, loads)
            ax.plot(sweep["Load (%)"], sweep["Copper loss (W)"], linewidth=2.4, label=f"{name} copper loss")
        ax.set_title("Copper loss vs. load", loc="left", fontweight="bold")
        ax.set_xlabel("Load (%)"); ax.set_ylabel("Copper loss (W)"); ax.grid(True, alpha=.22); ax.legend(frameon=False)
        fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close(fig)
        fig = efficiency_plot(raw_a if valid_a else None, raw_b if valid_b else None, max_load)
        st.pyplot(fig, use_container_width=True); plt.close(fig)
        st.caption("The model extrapolates the square-law copper-loss relationship up to 200% load for exploration. This is not a recommendation to overload a transformer.")

elif page == "Energy & Cost":
    st.subheader("Estimate the cost of transformer losses")
    c1, c2, c3 = st.columns(3)
    hours_day = c1.number_input("Operating hours per day", min_value=0.0, max_value=24.0, value=24.0, step=1.0)
    days_year = c2.number_input("Operating days per year", min_value=0, max_value=366, value=365, step=1)
    tariff = c3.number_input("Electricity tariff (₹/kWh)", min_value=0.0, max_value=100000.0, value=8.0, step=0.5)
    selected = st.selectbox("Transformer to analyse", ["Transformer A", "Transformer B"])
    r = res_a if selected == "Transformer A" else res_b
    if r:
        annual_hours = hours_day * days_year
        annual_kwh = r["total_kw"] * annual_hours
        annual_cost = annual_kwh * tariff
        a, b, c = st.columns(3)
        a.metric("Estimated loss energy / year", f"{annual_kwh:,.1f} kWh")
        b.metric("Estimated loss cost / year", f"₹{annual_cost:,.2f}")
        c.metric("Operating hours / year", f"{annual_hours:,.0f} h")
        st.info("Estimate assumes the selected operating load and calculated losses remain constant for all entered operating hours. Real annual cost varies with load profile, voltage, temperature, tariff structure and auxiliary losses.")
        st.markdown("#### Cost sensitivity")
        tariffs = np.linspace(0, max(1, tariff * 2), 30)
        fig, ax = plt.subplots(figsize=(8, 3.8))
        ax.plot(tariffs, r["total_kw"] * annual_hours * tariffs, linewidth=2.5)
        ax.axvline(tariff, linestyle=":", alpha=.65)
        ax.set_xlabel("Electricity tariff (₹/kWh)"); ax.set_ylabel("Estimated annual loss cost (₹)")
        ax.set_title("Annual loss cost vs. electricity tariff", loc="left", fontweight="bold")
        ax.grid(True, alpha=.22); fig.tight_layout(); st.pyplot(fig, use_container_width=True); plt.close(fig)

elif page == "Reports":
    st.subheader("Export your current analysis")
    report_results = {}
    if valid_a: report_results["Transformer A"] = res_a
    if valid_b: report_results["Transformer B"] = res_b
    if not report_results:
        st.warning("Enter valid transformer values first.")
    else:
        rows = []
        for name, r in report_results.items():
            rows.append({"Transformer":name, "Rating (kVA)":r["rating_kva"], "Load (%)":r["load_pct"],
                         "Power factor":r["pf"], "Output (kW)":r["output_kw"], "Core loss (W)":r["core_w"],
                         "Copper loss (W)":r["copper_w"], "Total loss (W)":r["total_w"],
                         "Efficiency (%)":r["efficiency_pct"], "Max-efficiency load (%)":r["max_load_pct"]})
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.download_button("Download results as CSV", data=df.to_csv(index=False).encode("utf-8"),
                           file_name="transformer_performance_results.csv", mime="text/csv", type="primary")
        pdf = pdf_report(report_results, "This report uses user-entered values and a simplified steady-state loss model. It is for education and preliminary analysis only; it is not a physical test report or certified engineering assessment.")
        if pdf:
            st.download_button("Download summary as PDF", data=pdf, file_name="transformer_performance_report.pdf", mime="application/pdf")
        else:
            st.warning("PDF export requires the reportlab package. Add reportlab to requirements.txt and redeploy.")
        st.caption("Reports show calculated estimates, not measured data.")

elif page == "Learn":
    st.subheader("Transformer concepts")
    with st.expander("1. What is transformer efficiency?", expanded=True):
        st.write("Efficiency is the ratio of useful real output power to input real power, expressed as a percentage. In this simplified model, input power equals output power plus the estimated core and copper losses.")
        st.latex(r"\\eta=\\frac{P_{out}}{P_{out}+P_{loss}}\\times100")
    with st.expander("2. Core losses"):
        st.write("Core losses mainly comprise hysteresis and eddy-current losses. They are treated as approximately constant when supply voltage and frequency remain constant.")
    with st.expander("3. Copper losses"):
        st.write("Winding copper losses follow I²R. Under the simplified model, current scales with load, so copper loss scales with the square of load fraction.")
        st.latex(r"P_{cu}=P_{cu,FL}L^2")
    with st.expander("4. Maximum-efficiency condition"):
        st.write("For the simplified loss model, maximum efficiency occurs when core loss equals copper loss.")
        st.latex(r"L_{max\\eta}=\\sqrt{\\frac{P_{core}}{P_{cu,FL}}}")
    with st.expander("5. Units"):
        st.write("kVA is apparent power; kW is real power; W is power or loss; kWh is energy. Power factor is a dimensionless value between 0 and 1.")
    st.warning("Educational tool: validate calculations against textbook examples, manufacturer data or laboratory measurements before any real engineering decision.")

st.markdown("---")
st.markdown('<div class="small-muted">GRIDLAB · Transformer Performance Analyzer v3.0 · Model-based estimates; not live monitoring.</div>', unsafe_allow_html=True)
