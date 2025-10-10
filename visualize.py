import matplotlib.pyplot as plt
import numpy as np
import os

def create_radar_chart(candidate_name, scores):
    # Set dark theme for matplotlib
    plt.style.use('dark_background')
    
    labels = ['Surface Fit', 'Depth Fit', 'Growth Potential', 'Cultural Fit']
    num_vars = len(labels)
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0E1117')  # Dark background
    ax.set_facecolor('#0E1117')
    
    # Remove extra margins
    plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
    
    values = [scores['surface_fit'], scores['depth_fit'], scores['growth_potential'], scores['cultural_fit']]
    values += values[:1]

    # Create gradient colors based on scores
    colors = []
    for score in values[:-1]:
        if score >= 70:
            colors.append('#4CAF50')  # Green for excellent
        elif score >= 50:
            colors.append('#FFC107')  # Yellow for good
        else:
            colors.append('#F44336')  # Red for poor
    
    # Plot the radar chart with gradient fill
    ax.fill(angles, values, color='#00D4FF', alpha=0.3)
    ax.plot(angles, values, color='#00D4FF', linewidth=3, marker='o', markersize=8, markerfacecolor='#FF6B6B', markeredgecolor='white', markeredgewidth=2)
    
    # Customize the chart
    ax.set_ylim(0, 100)
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, color='white', fontsize=12, fontweight='bold')
    
    # Add score labels
    for angle, value, label in zip(angles[:-1], values[:-1], labels):
        ax.text(angle, value + 10, f'{value}%', 
               horizontalalignment='center', 
               verticalalignment='center',
               fontsize=10, fontweight='bold', 
               color='#00D4FF',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='#1E1E1E', alpha=0.8))
    
    # Add grid lines
    ax.grid(True, color='#333333', alpha=0.7)
    ax.set_facecolor('#0E1117')
    
    # Title
    plt.title(f"MPRI Analysis: {candidate_name}", 
             color='white', fontsize=14, fontweight='bold', pad=10)
    
    # Save with tight layout to minimize whitespace
    os.makedirs("static", exist_ok=True)
    plt.tight_layout(pad=0.5)  # Minimize padding
    plt.savefig(f"static/{candidate_name.replace(' ', '_')}_radar_chart.png", 
                dpi=300, bbox_inches='tight', facecolor='#0E1117', edgecolor='none',
                pad_inches=0.1)  # Minimal padding around the figure
    plt.close()