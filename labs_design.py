# ----------------------------
# Imports
# ----------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import textwrap
from matplotlib.ticker import MultipleLocator, FuncFormatter

# ----------------------------
# Simulated example data
# ----------------------------
np.random.seed(42)

newlabels = [
    "This is a very long label for Group A that indicates what it is that is, really.",
    "Group B with detailed description",
    "A third group with another long name",
    "Group D - expanded name",
    "E Group (Special Category)",
    "F - Grouping explanation continues",
    "Seventh Group that has long label"
]

vals_levels = ["Category 1", "Category 2", "Category 3"]

df = pd.DataFrame({
    "newlable": np.repeat(newlabels, 3),
    "vals": np.tile(vals_levels, len(newlabels)),
    "anz": np.random.randint(20, 101, size=21)
})

# Calculate percentages
df["percent"] = df.groupby("newlable")["anz"].transform(lambda s: s / s.sum() * 100)

# Pivot for stacked bar plotting
df_pivot = df.pivot(index="newlable", columns="vals", values="percent").fillna(0)
df_pivot = df_pivot[vals_levels]  # ensure order

# Colors
colors = ["#4E79A7", "#F28E2B", "#E15759"]

# ----------------------------
# Plot
# ----------------------------
fig, axes = plt.subplots(len(df_pivot), 1, figsize=(10, 12), sharex=True)

if len(df_pivot) == 1:
    axes = [axes]

# tiny overlap to remove anti-alias seams between stacked segments
eps = 0.05  # in "percent points"; try 0.01–0.1 if needed for your backend/DPI

# Axis: smaller font + dark gray, 0.25 steps (on 0..1) => 25 steps (on 0..100)
tick_fontsize = 9
tick_color = "#666666"
major_step = 25  # 0, 25, 50, 75, 100

def pct_formatter(x, pos):
    # show clean percent labels
    return f"{x:.0f}"

for ax, (group, row) in zip(axes, df_pivot.iterrows()):
    left = 0.0

    for val, color in zip(vals_levels, colors):
        width = float(row[val])

        # Overlap segments slightly to avoid thin white seams (renderer artifacts)
        draw_width = width + (eps if width > 0 else 0)

        ax.barh(
            0,
            draw_width,
            left=left,
            color=color,
            height=0.8,
            edgecolor=color,   # same as facecolor to avoid contrasting outlines
            linewidth=0,
            antialiased=False  # key to removing "hairline" gaps on many backends
        )

        # Add percent label inside bar if wide enough
        if width > 3:
            ax.text(
                left + width / 2,
                0,
                f"{width:.1f}%",
                ha="center",
                va="center",
                color="white",
                fontweight="bold",
                fontsize=10
            )

        # IMPORTANT: advance by the true width (not draw_width) to keep sums correct
        left += width

    # Add facet label above bar
    wrapped_label = "\n".join(textwrap.wrap(group, width=100))
    ax.set_title(wrapped_label, loc="left", fontsize=11, fontweight="bold")

    ax.set_yticks([])      # remove y-axis ticks
    ax.set_xlim(0, 100)    # percent scale

    # 0.25 steps (0..1) mapped to percent axis
    ax.xaxis.set_major_locator(MultipleLocator(major_step))
    ax.xaxis.set_major_formatter(FuncFormatter(pct_formatter))

    # Make axis ticks/labels smaller and dark gray
    ax.tick_params(axis="x", which="major", labelsize=tick_fontsize, colors=tick_color)

    # Minimal style: remove spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(False)

    # Add light gridlines (optional)
    ax.set_axisbelow(True)
    ax.grid(axis="x", which="major", color="#E6E6E6", linewidth=0.5)

# Legend
fig.legend(
    vals_levels,
    loc="lower center",
    ncol=3,
    frameon=False,
    fontsize=11,
    bbox_to_anchor=(0.5, 0.01)
)

plt.tight_layout(rect=[0, 0.05, 1, 1])  # leave space for legend
plt.show()