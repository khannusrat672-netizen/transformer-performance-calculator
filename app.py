import math
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Transformer Performance Analysis Calculator",
    page_icon="⚡",
    layout="wide",
)



# ---------- Premium dark engineering dashboard ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
:root {
  --bg:#080d18; --panel:#101a2b; --panel2:#142239; --border:#273b58;
  --text:#eef5ff; --muted:#9db0cb; --blue:#54a6ff; --cyan:#35d6e8;
}
html, body, [class*="css"] { font-family: Inter, "Segoe UI", sans-serif; }
.stApp {
  background: radial-gradient(ellipse at 78% 0%, rgba(28,105,180,.18), transparent 34%), var(--bg);
  color: var(--text);
}
[data-testid="stHeader"] { background: rgba(8,13,24,.94); }
.block-container { max-width: 1500px; padding-top: 1.7rem; padding-bottom: 3rem; }
h1,h2,h3 { color: #f2f7ff !important; letter-spacing: -.035em; }
h1 { font-size: 2.15rem !important; font-weight: 800 !important; }
h2 { font-size: 1.45rem !important; font-weight: 750 !important; }
h3 { font-weight: 700 !important; }
p, label { color: #d3deef; }
[data-testid="stCaptionContainer"] { color: var(--muted); }
[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#0e192b 0%,#091220 100%);
  border-right: 1px solid var(--border);
}
[data-testid="stSidebar"] * { color: #dce8fa; }
[data-testid="stMetric"] {
  background: linear-gradient(145deg,rgba(21,36,59,.98),rgba(13,23,39,.98));
  border: 1px solid #2a405f; border-radius: 17px; padding: 18px 19px;
  box-shadow: 0 9px 28px rgba(0,0,0,.18); min-height: 116px;
  transition: transform .18s ease,border-color .18s ease;
}
[data-testid="stMetric"]:hover { transform: translateY(-2px); border-color:#398fe8; }
[data-testid="stMetricLabel"] { color:#a4b6d0 !important; font-size:.83rem; }
[data-testid="stMetricValue"] { color:var(--blue) !important; font-weight:800 !important; }
[data-testid="stMetricDelta"] { color:#55dfb0 !important; }
div[data-testid="stVerticalBlockBorderWrapper"] {
  background: rgba(16,26,43,.72); border:1px solid var(--border);
  border-radius:18px; padding:1rem;
}
.hero {
  background:linear-gradient(115deg,rgba(20,45,77,.98),rgba(13,26,44,.96));
  border:1px solid #2c4a70; border-radius:22px; padding:25px 28px;
  margin-bottom:1.1rem; box-shadow:0 14px 38px rgba(0,0,0,.18);
}
.kicker { color:#58d7eb; font-size:.73rem; font-weight:800; letter-spacing:.17em; text-transform:uppercase; }
.hero-title { color:#f5f8ff; font-size:2rem; font-weight:800; letter-spacing:-.045em; margin:.35rem 0 .45rem; }
.hero-sub { color:#b7c9e2; font-size:.96rem; margin:0; }
.pill {
  display:inline-block; background:rgba(53,214,232,.1); color:#74e5ef;
  border:1px solid rgba(53,214,232,.32); border-radius:999px;
  padding:5px 10px; font-size:.75rem; font-weight:700; margin-top:12px;
}
.stButton > button {
  background:linear-gradient(135deg,#1677ff,#00aeca); color:white !important;
  border:1px solid transparent; border-radius:11px; font-weight:700;
  padding:.55rem 1rem; transition:all .2s ease;
}
.stButton > button:hover { box-shadow:0 0 22px rgba(49,130,246,.28); border-color:#55b6ff; }
input, textarea {
  background:#111d30 !important; color:#eff6ff !important;
  border-color:#314765 !important; border-radius:10px !important;
}
[data-baseweb="select"] > div { background:#111d30; border-color:#314765; border-radius:10px; }
hr { border-color:#293b55 !important; }
[data-testid="stDataFrame"] { border:1px solid #2a3d59; border-radius:13px; overflow:hidden; }
[data-testid="stExpander"] {
  background:#101a2b; border:1px solid #293c58; border-radius:13px;
}
[data-testid="stAlert"] { border-radius:12px; }
a { color:#6bb5ff !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚡ GRIDLAB")
    st.caption("TRANSFORMER ANALYTICS")
    st.markdown("---")
    st.markdown("**WORKSPACE**")
    st.markdown("▰  Performance overview")
    st.markdown("▰  Transformer comparison")
    st.markdown("▰  Loss analysis")
    st.markdown("▰  Load sweep")
    st.markdown("---")
    st.markdown("**MODEL STATUS**")
    st.success("Calculation engine ready")
    st.caption("Steady-state estimate • SI units")
    st.markdown("---")
    st.caption("Transformer Performance Analyzer · v1.0")


DEFAULTS = {
    "rating_a_kva": 100.0,
    "load_a_pct": 75.0,
    "pf_a": 0.90,
    "core_a_w": 300.0,
    "copper_a_w": 1200.0,
    "rating_b_kva": 150.0,
    "load_b_pct": 75.0,
    "pf_b": 0.90,
    "core_b_w": 420.0,
    "copper_b_w": 1800.0,
}

LOAD_LEVELS_PCT = np.arange(0, 201, 25, dtype=float)
PLOT_LOAD_LEVELS_PCT = np.linspace(0, 200, 201)


def calculate_performance(
    rating_kva: float,
    load_fraction: float,
    power_factor: float,
    core_loss_w: float,
    full_load_copper_loss_w: float,
) -> dict[str, Any]:
    """Calculate transformer output, losses, efficiency, and optimum load."""
    output_kw = rating_kva * load_fraction * power_factor
    output_w = output_kw * 1000
    copper_loss_w = full_load_copper_loss_w * load_fraction**2
    total_loss_w = core_loss_w + copper_loss_w
    denominator_w = output_w + total_loss_w

    efficiency_pct = (
        (output_w / denominator_w) * 100 if denominator_w > 0 else None
    )

    if full_load_copper_loss_w > 0:
        max_efficiency_load_pct = (
            math.sqrt(core_loss_w / full_load_copper_loss_w) * 100
        )
        max_efficiency_note = None
    elif core_loss_w == 0:
        max_efficiency_load_pct = None
        max_efficiency_note = "Not defined when both losses are zero"
    else:
        max_efficiency_load_pct = None
        max_efficiency_note = "No finite optimum when copper loss is zero"

    return {
        "output_kw": output_kw,
        "output_w": output_w,
        "copper_loss_w": copper_loss_w,
        "core_loss_w": core_loss_w,
        "total_loss_w": total_loss_w,
        "efficiency_pct": efficiency_pct,
        "max_efficiency_load_pct": max_efficiency_load_pct,
        "max_efficiency_note": max_efficiency_note,
    }


def validate_transformer_inputs(values: dict[str, float]) -> list[str]:
    """Return user-readable input errors before any calculations are shown."""
    errors: list[str] = []

    if not math.isfinite(values["rating_kva"]) or values["rating_kva"] <= 0:
        errors.append("Transformer rating must be greater than 0 kVA.")
    if (
        not math.isfinite(values["load_pct"])
        or values["load_pct"] < 0
        or values["load_pct"] > 200
    ):
        errors.append("Load percentage must be between 0% and 200%.")
    if (
        not math.isfinite(values["power_factor"])
        or values["power_factor"] < 0
        or values["power_factor"] > 1
    ):
        errors.append("Power factor must be between 0 and 1.")
    if (
        not math.isfinite(values["core_loss_w"])
        or values["core_loss_w"] < 0
    ):
        errors.append("Core loss must be zero or greater.")
    if (
        not math.isfinite(values["full_load_copper_loss_w"])
        or values["full_load_copper_loss_w"] < 0
    ):
        errors.append("Full-load copper loss must be zero or greater.")

    return errors


def efficiency_at_load(
    transformer: dict[str, float], load_fraction: float
) -> float:
    performance = calculate_performance(
        rating_kva=transformer["rating_kva"],
        load_fraction=load_fraction,
        power_factor=transformer["power_factor"],
        core_loss_w=transformer["core_loss_w"],
        full_load_copper_loss_w=transformer["full_load_copper_loss_w"],
    )
    efficiency_pct = performance["efficiency_pct"]
    return float(efficiency_pct) if efficiency_pct is not None else np.nan


for input_key, default_value in DEFAULTS.items():
    if input_key not in st.session_state:
        st.session_state[input_key] = default_value


st.markdown(
    """
    <section class="hero">
      <div class="kicker">POWER SYSTEMS / ANALYTICS</div>
      <div class="hero-title">Transformer Performance Analyzer</div>
      <p class="hero-sub">Model operating performance, compare losses, and identify efficient loading conditions.</p>
      <span class="pill">● CALCULATION ENGINE ONLINE</span>
    </section>
    """,
    unsafe_allow_html=True,
)

if st.button("Reset to default values", type="secondary"):
    for input_key, default_value in DEFAULTS.items():
        st.session_state[input_key] = default_value
    st.rerun()


def render_transformer_inputs(
    column: Any, transformer_label: str, key_suffix: str
) -> dict[str, float]:
    with column:
        st.subheader(transformer_label)
        st.caption("Enter nameplate rating and loss-test values.")
        rating_kva = st.number_input(
            "Transformer rating (kVA)",
            min_value=0.0,
            max_value=200_000.0,
            step=1.0,
            key=f"rating_{key_suffix}_kva",
            help="Use the transformer's rated apparent power.",
        )
        load_pct = st.number_input(
            "Load percentage (%)",
            min_value=0.0,
            max_value=200.0,
            step=1.0,
            key=f"load_{key_suffix}_pct",
            help="Values above 100% represent overload operation.",
        )
        power_factor = st.number_input(
            "Power factor",
            min_value=0.0,
            max_value=1.0,
            step=0.01,
            format="%.2f",
            key=f"pf_{key_suffix}",
            help="Real power factor, from 0 to 1.",
        )
        core_loss_w = st.number_input(
            "Iron / core losses (W)",
            min_value=0.0,
            max_value=10_000_000.0,
            step=10.0,
            key=f"core_{key_suffix}_w",
            help="Approximately constant no-load loss.",
        )
        full_load_copper_loss_w = st.number_input(
            "Full-load copper losses (W)",
            min_value=0.0,
            max_value=10_000_000.0,
            step=10.0,
            key=f"copper_{key_suffix}_w",
            help="Load-dependent winding loss at rated current.",
        )

    return {
        "rating_kva": float(rating_kva),
        "load_pct": float(load_pct),
        "power_factor": float(power_factor),
        "core_loss_w": float(core_loss_w),
        "full_load_copper_loss_w": float(full_load_copper_loss_w),
    }


st.subheader("Operating inputs")
input_columns = st.columns(2, gap="large")
transformer_inputs = {
    "Transformer A": render_transformer_inputs(
        input_columns[0], "Transformer A", "a"
    ),
    "Transformer B": render_transformer_inputs(
        input_columns[1], "Transformer B", "b"
    ),
}

valid_transformers: dict[str, dict[str, float]] = {}
for transformer_name, values in transformer_inputs.items():
    validation_values = {
        "rating_kva": values["rating_kva"],
        "load_pct": values["load_pct"],
        "power_factor": values["power_factor"],
        "core_loss_w": values["core_loss_w"],
        "full_load_copper_loss_w": values["full_load_copper_loss_w"],
    }
    errors = validate_transformer_inputs(validation_values)
    if errors:
        st.error(
            f"{transformer_name}: " + " ".join(errors),
            icon="⚠️",
        )
    else:
        valid_transformers[transformer_name] = values


if valid_transformers:
    performance_by_transformer: dict[str, dict[str, Any]] = {}
    for transformer_name, values in valid_transformers.items():
        performance_by_transformer[transformer_name] = calculate_performance(
            rating_kva=values["rating_kva"],
            load_fraction=values["load_pct"] / 100,
            power_factor=values["power_factor"],
            core_loss_w=values["core_loss_w"],
            full_load_copper_loss_w=values["full_load_copper_loss_w"],
        )

    st.subheader("Current operating point")
    for transformer_name, performance in performance_by_transformer.items():
        st.markdown(f"**{transformer_name}**")
        metric_columns = st.columns(5)
        max_load_value = performance["max_efficiency_load_pct"]
        max_load_display = (
            f"{max_load_value:,.1f}%"
            if max_load_value is not None
            else performance["max_efficiency_note"]
        )
        efficiency_value = performance["efficiency_pct"]
        efficiency_display = (
            f"{efficiency_value:,.2f}%"
            if efficiency_value is not None
            else "Not defined"
        )

        metric_columns[0].metric(
            "Output power", f"{performance['output_kw']:,.2f} kW"
        )
        metric_columns[1].metric(
            "Copper losses", f"{performance['copper_loss_w']:,.1f} W"
        )
        metric_columns[2].metric(
            "Total losses", f"{performance['total_loss_w']:,.1f} W"
        )
        metric_columns[3].metric("Efficiency", efficiency_display)
        metric_columns[4].metric("Maximum-efficiency load", max_load_display)

        if performance["max_efficiency_note"]:
            st.caption(performance["max_efficiency_note"] + ".")

    st.subheader("Efficiency versus load")
    plt.rcParams.update({
        "figure.facecolor": "#101a2b",
        "axes.facecolor": "#101a2b",
        "axes.edgecolor": "#526783",
        "axes.labelcolor": "#c8d8ed",
        "xtick.color": "#a9bbd3",
        "ytick.color": "#a9bbd3",
        "text.color": "#edf4ff",
        "grid.color": "#344963",
        "legend.facecolor": "#142239",
        "legend.edgecolor": "#314765",
    })
    efficiency_figure, efficiency_axes = plt.subplots(figsize=(10, 5))
    line_colors = {
        "Transformer A": "#54a6ff",
        "Transformer B": "#35d6e8",
    }

    for transformer_name, values in valid_transformers.items():
        efficiencies = [
            efficiency_at_load(values, load_pct / 100)
            for load_pct in PLOT_LOAD_LEVELS_PCT
        ]
        color = line_colors[transformer_name]
        efficiency_axes.plot(
            PLOT_LOAD_LEVELS_PCT,
            efficiencies,
            label=transformer_name,
            linewidth=2.5,
            color=color,
        )
        current_performance = performance_by_transformer[transformer_name]
        current_efficiency = current_performance["efficiency_pct"]
        if current_efficiency is not None:
            efficiency_axes.scatter(
                [values["load_pct"]],
                [current_efficiency],
                color=color,
                edgecolor="white",
                linewidth=1.2,
                s=70,
                zorder=3,
            )

        max_load = current_performance["max_efficiency_load_pct"]
        if max_load is not None and 0 <= max_load <= 200:
            efficiency_axes.axvline(
                max_load,
                color=color,
                linestyle=":",
                linewidth=1,
                alpha=0.7,
            )

    efficiency_axes.set_xlim(0, 200)
    efficiency_axes.set_ylim(0, 102)
    efficiency_axes.set_xlabel("Load (%)")
    efficiency_axes.set_ylabel("Efficiency (%)")
    efficiency_axes.set_title("Efficiency across the operating range")
    efficiency_axes.grid(True, linestyle="--", alpha=0.3)
    efficiency_axes.legend()
    efficiency_figure.tight_layout()
    st.pyplot(efficiency_figure, clear_figure=True)
    plt.close(efficiency_figure)
    st.caption(
        "Dots mark each transformer's selected operating point. Dotted "
        "vertical lines show the theoretical maximum-efficiency load when "
        "a finite value exists."
    )

    st.subheader("Loss breakdown at the selected load")
    loss_figure, loss_axes = plt.subplots(figsize=(8, 4.5))
    transformer_names = list(valid_transformers.keys())
    positions = np.arange(len(transformer_names), dtype=float)
    bar_width = 0.34
    core_losses = [
        performance_by_transformer[name]["core_loss_w"]
        for name in transformer_names
    ]
    copper_losses = [
        performance_by_transformer[name]["copper_loss_w"]
        for name in transformer_names
    ]
    loss_axes.bar(
        positions - bar_width / 2,
        core_losses,
        width=bar_width,
        label="Iron / core loss",
        color="#54a6ff",
    )
    loss_axes.bar(
        positions + bar_width / 2,
        copper_losses,
        width=bar_width,
        label="Copper loss at selected load",
        color="#35d6e8",
    )
    loss_axes.set_xticks(positions, transformer_names)
    loss_axes.set_ylabel("Losses (W)")
    loss_axes.set_title("Core and load-dependent copper losses")
    loss_axes.grid(axis="y", linestyle="--", alpha=0.3)
    loss_axes.legend()
    loss_figure.tight_layout()
    st.pyplot(loss_figure, clear_figure=True)
    plt.close(loss_figure)

    st.subheader("Performance at different load levels")
    sweep_rows: list[dict[str, Any]] = []
    for load_pct in LOAD_LEVELS_PCT:
        row: dict[str, Any] = {"Load level (%)": int(load_pct)}
        for transformer_name, values in valid_transformers.items():
            performance = calculate_performance(
                rating_kva=values["rating_kva"],
                load_fraction=float(load_pct) / 100,
                power_factor=values["power_factor"],
                core_loss_w=values["core_loss_w"],
                full_load_copper_loss_w=values["full_load_copper_loss_w"],
            )
            row[f"{transformer_name} output (kW)"] = performance["output_kw"]
            row[f"{transformer_name} efficiency (%)"] = (
                performance["efficiency_pct"]
            )
        sweep_rows.append(row)

    sweep_table = pd.DataFrame(sweep_rows)
    st.dataframe(
        sweep_table,
        width="stretch",
        hide_index=True,
        column_config={
            "Load level (%)": st.column_config.NumberColumn(
                "Load level", format="%d%%"
            ),
            **{
                column_name: st.column_config.NumberColumn(
                    column_name,
                    format="%.2f",
                )
                for column_name in sweep_table.columns
                if column_name != "Load level (%)"
            },
        },
    )
else:
    st.warning("Enter a valid transformer rating to view calculated results.")


with st.expander("Formulas and engineering notes"):
    st.markdown(
        r"""
**Load fraction**

\[
L = \frac{\text{Load percentage}}{100}
\]

**Real output power**

\[
P_{\text{out}}(\mathrm{kW}) =
S_{\text{rated}}(\mathrm{kVA}) \times L \times \mathrm{PF}
\]

**Copper loss at the selected load**

\[
P_{\text{cu}}(\mathrm{W}) =
P_{\text{cu,FL}} \times L^2
\]

**Total losses and efficiency**

\[
P_{\text{loss}} = P_{\text{core}} + P_{\text{cu}}
\]

\[
\eta(\%) =
\frac{P_{\text{out}}(\mathrm{W})}
{P_{\text{out}}(\mathrm{W}) + P_{\text{loss}}(\mathrm{W})}
\times 100
\]

Output power is converted from kW to W before calculating efficiency.
Core loss is treated as constant; copper loss varies with the square of
load. The theoretical maximum-efficiency load occurs when core and copper
losses are equal:

\[
L_{\max\eta} =
\sqrt{\frac{P_{\text{core}}}{P_{\text{cu,FL}}}}
\]

If both losses are zero, efficiency is 100% at any positive real output,
while efficiency at zero output and the maximum-efficiency load are
undefined. If full-load copper loss is zero but core loss is positive,
there is no finite maximum-efficiency load under this simplified model.
"""
    )

st.caption(
    "Engineering estimates assume sinusoidal steady-state operation and "
    "the loss values supplied by the user. Results do not include auxiliary "
    "or temperature-correction losses."
)
