import matplotlib.pyplot as plt
import numpy as np

# Hardcoded data from your experiments
experiments = [
    {"players": 100000,   "rules": 100, "c_time": 0.0855, "python_time": 0.7848, "numba_time": 0.6088, "fast_c_time":0.0055},
    {"players": 1000000,  "rules": 150, "c_time": 0.9861, "python_time": 11.3552, "numba_time": 9.6022, "fast_c_time": 0.0332},
    {"players": 1000000,  "rules": 150, "c_time": 0.9861, "python_time": 10.9832, "numba_time": 9.6022, "fast_c_time": 0.0332},
    {"players": 1000000,  "rules": 150, "c_time": 0.9861, "python_time":  10.9832, "numba_time": 9.6022, "fast_c_time": 0.0410},
     {"players": 10000000, "rules": 150, "c_time": 14.5382, "python_time": 119.456, "numba_time": 98.022, "fast_c_time": 0.922},
]

# Extracting lists for plotting
x_labels = [f"{e['players']//1000}K Players\n{e['rules']} Rules" for e in experiments]

c_times = [e["c_time"] for e in experiments]
python_times = [e["python_time"] for e in experiments]
numba_times = [e["numba_time"] for e in experiments]
fast_c_times = [e["fast_c_time"] for e in experiments]

# Set up figure and log scale (to handle massive differences)
fig, ax = plt.subplots(figsize=(12, 7))

# Line plots
if any(c_times):
    ax.plot(x_labels, c_times, marker='o', label='Original C Batch', linestyle='--', color='seagreen')
if any(fast_c_times):
    ax.plot(x_labels, fast_c_times, marker='s', label='Optimized Fast C Batch', linestyle='-', color='forestgreen')
if any(python_times):
    ax.plot(x_labels, python_times, marker='^', label='Ordinary Python', linestyle='--', color='darkorange')
if any(numba_times):
    ax.plot(x_labels, numba_times, marker='D', label='Numba Python', linestyle='-', color='royalblue')

# Log scale for y-axis to make tiny and huge times comparable
ax.set_yscale('log')
ax.set_ylabel('Time (seconds) - Log Scale')
ax.set_title('Offer Evaluation Performance Across Experiments')
ax.legend()

# Adding text annotations (time in seconds) directly on the points
def add_labels(times, offset=5):
    for i, time in enumerate(times):
        if time is not None:
            ax.annotate(f"{time:.2f}s", (i, time), textcoords="offset points", xytext=(0, offset), ha='center', fontsize=9)

add_labels(c_times)
add_labels(fast_c_times, offset=-15)
add_labels(python_times)
add_labels(numba_times)

# Final tweaks
plt.grid(True, which="both", linestyle="--", linewidth=0.5)
plt.xticks(rotation=0)
plt.tight_layout()

# Save and show
plt.savefig("experiment_performance_comparison.png")
plt.show()
