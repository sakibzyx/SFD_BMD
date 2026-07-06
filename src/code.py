import os
import numpy as np
import plotly.graph_objects as go

# Output Folder
output_dir = r"D:\SFD_BMD\output"
os.makedirs(output_dir, exist_ok=True)

# Beam Data
span = 17          # Beam length (m)
A = 3              # Left support location (Pin)
B = 13             # Right support location (Roller)

# Point Loads: [location, Fx, Fy]
pointLoads = np.array([
    [6, 0, -90]
], dtype=float)

nPL = len(pointLoads)
# Generate X coordinates along the beam for calculation (dense sampling for smooth curves)
X = np.linspace(0, span, 1001)

# Calculate Reactions (Static Equilibrium)
# For a single point load (can be extended for multiple later):
# sum(M_A) = 0 => R_B * (B - A) + F_y * (x_p - A) = 0  (Note: F_y is negative)
xp = pointLoads[0, 0]
fy = pointLoads[0, 2]

# Reaction at B (Vertical)
vb = (-fy * (xp - A)) / (B - A)
# Reaction at A (Vertical)
va = -fy - vb
# Reaction at A (Horizontal)
ha = -pointLoads[0, 1]

reactions = [va, ha, vb]
PL_record = np.array([[va, vb]]) # Store for the function

# Loading Diagram
fig_load = go.Figure()

# Beam
fig_load.add_trace(
    go.Scatter(
        x=[0, span],
        y=[0, 0],
        mode="lines",
        line=dict(color="black", width=8),
        hoverinfo="skip",
        showlegend=False
    )
)

# Pin Support (A)
fig_load.add_trace(
    go.Scatter(
        x=[A],
        y=[-0.12],
        mode="markers+text",
        marker=dict(
            symbol="triangle-up",
            size=18,
            color="blue"
        ),
        text=["A"],
        textposition="bottom center",
        hoverinfo="skip",
        showlegend=False
    )
)

# Roller Support (B)
fig_load.add_trace(
    go.Scatter(
        x=[B],
        y=[-0.12],
        mode="markers+text",
        marker=dict(
            symbol="triangle-up",
            size=18,
            color="red"
        ),
        text=["B"],
        textposition="bottom center",
        hoverinfo="skip",
        showlegend=False
    )
)

# Point Loads
for load in pointLoads:
    xp_l = load[0]
    fy_l = load[2]

    fig_load.add_annotation(
        x=xp_l,
        y=0.05,
        ax=xp_l,
        ay=0.8,
        xref="x",
        yref="y",
        axref="x",
        ayref="y",
        showarrow=True,
        arrowhead=3,
        arrowsize=1.5,
        arrowwidth=3,
        arrowcolor="red"
    )

    fig_load.add_annotation(
        x=xp_l,
        y=0.95,
        text=f"{abs(fy_l):.0f} kN",
        showarrow=False,
        font=dict(size=14, color="red", family="Arial Black")
    )

# Beam End Labels
fig_load.add_annotation(x=0, y=-0.35, text="0 m", showarrow=False)
fig_load.add_annotation(x=span, y=-0.35, text=f"{span} m", showarrow=False)

fig_load.update_layout(
    title="Beam Loading Diagram",
    template="plotly_white",
    xaxis=dict(
        title="Distance (m)",
        range=[-1, span + 1],
        tickmode="array",
        tickvals=[0, A, pointLoads[0,0], B, span],
        ticktext=["0", str(A), str(int(pointLoads[0,0])), str(B), str(span)]
    ),
    yaxis=dict(
        visible=False,
        range=[-1, 2]
    ),
    margin=dict(l=40, r=40, t=60, b=40)
)

fig_load.show()
fig_load.write_html(os.path.join(output_dir, "Loading_Diagram.html"))

# Shear & Moment Function
def shear_moment_PL(n):
    xp = pointLoads[n, 0]
    fy = pointLoads[n, 2]

    va = PL_record[n, 0]
    vb = PL_record[n, 1]

    Shear = np.zeros(len(X))
    Moment = np.zeros(len(X))

    for i, x in enumerate(X):
        shear = 0
        moment = 0

        # Reaction at A
        if x >= A:
            shear += va
            moment += va * (x - A)

        # Point load
        if x >= xp:
            shear += fy
            moment += fy * (x - xp)

        # Reaction at B
        if x >= B:
            shear += vb
            moment += vb * (x - B)

        Shear[i] = shear
        Moment[i] = moment

    return Shear, Moment

# Initialize tracking lists
shearForce_list = []
bendingMoment_list = []

for n in range(nPL):
    Shear, Moment = shear_moment_PL(n)
    shearForce_list.append(Shear)
    bendingMoment_list.append(Moment)

# Convert lists to numpy arrays safely
shearForce = np.array(shearForce_list)
bendingMoment = np.array(bendingMoment_list)


# Results Printing
print(f"Vertical reaction at A   : {reactions[0]:.2f} kN")
print(f"Horizontal reaction at A : {reactions[1]:.2f} kN")
print(f"Vertical reaction at B   : {reactions[2]:.2f} kN")

# Total Shear & Moment
totalShear = np.sum(shearForce, axis=0)
totalMoment = np.sum(bendingMoment, axis=0)

# Plot Shear Diagram
fig1 = go.Figure()
fig1.add_trace(
    go.Scatter(
        x=X,
        y=totalShear,
        mode="lines",
        name="Shear Force",
        line=dict(color="green", width=3)
    )
)
fig1.update_layout(
    title="Shear Force Diagram",
    xaxis_title="Distance (m)",
    yaxis_title="Shear Force (kN)",
    xaxis=dict(range=[-1, span + 1]),
    template="plotly_white"
)
fig1.show()

# Plot Bending Moment Diagram
fig2 = go.Figure()
fig2.add_trace(
    go.Scatter(
        x=X,
        y=totalMoment,
        mode="lines",
        name="Bending Moment",
        line=dict(color="blue", width=3)
    )
)
fig2.update_layout(
    title="Bending Moment Diagram",
    xaxis_title="Distance (m)",
    yaxis_title="Moment (kN·m)",
    xaxis=dict(range=[-1, span + 1]),
    template="plotly_white"
)

fig1.write_html(os.path.join(output_dir, "SFD.html"))
fig2.write_html(os.path.join(output_dir, "BMD.html"))
fig2.show()