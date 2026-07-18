# matplotlib Chart Generation for Portfolio Reports

## Pattern

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 8), gridspec_kw={'height_ratios': [1, 1]})
fig.patch.set_facecolor('#1a1a2e')

for ax, title, data_items in [(ax1, "Portfolio", portfolio_items), (ax2, "Watchlist", watchlist_items)]:
    names = []
    changes = []
    colors = []
    for name, d in data_items:
        if "error" in d:
            continue
        names.append(name[:14])  # truncate long names
        changes.append(d["change_pct"])
        colors.append('#4ade80' if d["change_pct"] >= 0 else '#ef4444')

    bars = ax.barh(range(len(names)), changes, color=colors, height=0.6, edgecolor='white', linewidth=0.5)
    ax.set_yticks(range(len(names)))
    ax.set_yticklabels(names, fontsize=10, color='white')
    ax.axvline(0, color='white', linewidth=0.8, linestyle='-', alpha=0.3)
    ax.set_title(title, fontsize=13, color='white', fontweight='bold', pad=15)
    ax.set_facecolor('#16213e')
    ax.tick_params(colors='white', labelsize=9)
    for spine in ax.spines.values():
        spine.set_color('#333')

    # Value labels on bars
    for i, (bar, chg) in enumerate(zip(bars, changes)):
        lbl = f"{chg:+.2f}%"
        x_pos = bar.get_width() + 0.3 if chg >= 0 else bar.get_width() - 0.3
        ha = 'left' if chg >= 0 else 'right'
        ax.text(x_pos, bar.get_y() + bar.get_height()/2, lbl,
                ha=ha, va='center', fontsize=9, fontweight='bold',
                color='#4ade80' if chg >= 0 else '#ef4444')

plt.tight_layout(pad=3)
buf = io.BytesIO()
fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', facecolor=fig.get_facecolor())
plt.close(fig)
buf.seek(0)
```

## Key details

- **Dark theme**: `#1a1a2e` background, `#16213e` axis faces
- **Green/red bars**: `#4ade80` (up) / `#ef4444` (down)
- **White text**: `color='white'` on everything
- **No emojis in titles**: matplotlib's default font (DejaVu Sans) doesn't have emoji glyphs → `UserWarning: Glyph missing`. Use plain text titles like "Portfolio - Variation journaliere (%)"
- **BytesIO buffer**: keeps chart in memory — no temp file needed
- **Two subplots**: for portfolio + watchlist in one image
