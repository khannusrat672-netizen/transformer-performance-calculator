import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math

st.set_page_config(
    page_title="Transformer Performance Analyzer",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Transformer Performance Analysis Calculator")
st.write(
    "Analyze transformer efficiency, losses, loading, "
    "and performance under different operating conditions."
)

st.sidebar.header("Transformer Parameters")

rating = st.sidebar.number_input(
    "Transformer Rating (kVA)",
    min_value=0.1,
    value=100.0,
    step=5.0
)

iron_loss = st.sidebar.number_input(
    "Iron/Core Loss (W)",
    min_value=0.0,
    value=500.0,
    step=50.0
)

copper_loss_full = st.sidebar.number_input(
    "Full-Load Copper Loss (W)",
    min_value=0.0,
    value=1000.0,
    step=50.0
)

load_percent = st.sidebar.slider(
    "Load Percentage (%)",
    min_value=0,
    max_value=100,
    value=75
)

power_factor = st.sidebar.slider(
    "Power Factor",
    min_value=0.1,
    max_value=1.0,
    value=0.8,
    step=0.05
)

load_fraction = load_percent / 100

output_power_kw = rating * load_fraction * power_factor

copper_loss = copper_loss_full * load_fraction**2

total_loss = iron_loss + copper_loss

output_power_w = output_power_kw * 1000

if output_power_w + total_loss > 0:
    efficiency = (
        output_power_w / (output_power_w + total_loss)
    ) * 100
else:
    efficiency = 0.0

if copper_loss_full > 0:
    max_efficiency_load = math.sqrt(
        iron_loss / copper_loss_full
    )
    max_efficiency_load = min(max_efficiency_load, 1.0)
else:
    max_efficiency_load = 1.0

st.subheader("📊 Performance Results")

col1, col2, col3, col4 = st.columns(4)

col1.metric("Output Power", f"{output_power_kw:.2f} kW")
col2.metric("Efficiency", f"{efficiency:.2f}%")
col3.metric("Total Losses", f"{total_loss:.2f} W")
col4.metric(
    "Load at Maximum Efficiency",
    f"{max_efficiency_load * 100:.1f}%"
)

st.divider()

st.subheader("🔌 Loss Breakdown")

loss_col1, loss_col2 = st.columns(2)

loss_col1.metric("Iron Loss", f"{iron_loss:.2f} W")
loss_col2.metric("Copper Loss", f"{copper_loss:.2f} W")

st.subheader("📈 Efficiency vs Load")

loads = np.linspace(1, 100, 100)
efficiencies = []

for load in loads:
    fraction = load / 100
    output_w = rating * fraction * power_factor * 1000
    copper_w = copper_loss_full * fraction**2
    losses_w = iron_loss + copper_w

    eff = output_w / (output_w + losses_w) * 100
    efficiencies.append(eff)

fig, ax = plt.subplots()

ax.plot(loads, efficiencies, label="Efficiency")
ax.set_xlabel("Load (%)")
ax.set_ylabel("Efficiency (%)")
ax.set_title("Transformer Efficiency Curve")
ax.grid(True)
ax.legend()

st.pyplot(fig)
plt.close(fig)

st.divider()

st.subheader("🧮 Calculation Details")

st.write(f"**Output Power:** {rating} × {load_fraction:.2f} × {power_factor}")
st.write(f"**Copper Loss:** {copper_loss_full} × {load_fraction:.2f}²")
st.write(f"**Total Loss:** Iron Loss + Copper Loss = {total_loss:.2f} W")
st.write(
    f"**Efficiency:** Output / (Output + Losses) × 100 "
    f"= {efficiency:.2f}%"
)

st.caption(
    "Educational tool: results use a simplified transformer model "
    "with constant core loss and copper loss proportional to load squared."
)
