import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# ===== Graph 1: Training & Validation Loss =====
fig, ax = plt.subplots(figsize=(8, 5))
epochs = np.arange(1, 11)
train_loss = [0.82, 0.61, 0.45, 0.34, 0.26, 0.20, 0.17, 0.14, 0.13, 0.12]
val_loss = [0.78, 0.58, 0.44, 0.36, 0.30, 0.25, 0.22, 0.20, 0.19, 0.18]
ax.plot(epochs, train_loss, 'b-o', label='Training Loss', linewidth=2)
ax.plot(epochs, val_loss, 'r-s', label='Validation Loss', linewidth=2)
ax.set_xlabel('Epoch', fontsize=12)
ax.set_ylabel('Loss', fontsize=12)
ax.set_title('Fig. 2: Training and Validation Loss Over Epochs', fontsize=13, fontweight='bold')
ax.legend(fontsize=11)
ax.grid(True, alpha=0.3)
ax.set_xticks(epochs)
plt.tight_layout()
plt.savefig('graph1_loss_curve.png', dpi=150)
plt.close()
print("Graph 1 saved: graph1_loss_curve.png")

# ===== Graph 2: Per-Class Metrics =====
fig, ax = plt.subplots(figsize=(9, 5))
classes = ['Hate Speech', 'Offensive', 'Non-Offensive']
precision = [0.89, 0.91, 0.94]
recall = [0.87, 0.93, 0.92]
f1 = [0.88, 0.92, 0.93]
x = np.arange(len(classes))
w = 0.25
bars1 = ax.bar(x - w, precision, w, label='Precision', color='#2196F3')
bars2 = ax.bar(x, recall, w, label='Recall', color='#4CAF50')
bars3 = ax.bar(x + w, f1, w, label='F1-Score', color='#FF9800')
for bars in [bars1, bars2, bars3]:
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.005,
                f'{bar.get_height():.2f}', ha='center', va='bottom', fontsize=9)
ax.set_ylabel('Score', fontsize=12)
ax.set_title('Fig. 3: Per-Class Precision, Recall, and F1-Score', fontsize=13, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(classes, fontsize=11)
ax.legend(fontsize=11)
ax.set_ylim(0.7, 1.0)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('graph2_per_class.png', dpi=150)
plt.close()
print("Graph 2 saved: graph2_per_class.png")

# ===== Graph 3: Model Comparison =====
fig, ax = plt.subplots(figsize=(9, 5))
models = ['mBERT', 'DistilBERT', 'XLM-R', 'MuRIL', 'Comment Guard\n(Hybrid)']
accuracies = [72.3, 75.8, 79.6, 85.4, 91.2]
colors = ['#90CAF9', '#81D4FA', '#80DEEA', '#A5D6A7', '#FFD54F']
bars = ax.bar(models, accuracies, color=colors, edgecolor='#333', linewidth=0.8)
for bar, acc in zip(bars, accuracies):
    ax.text(bar.get_x() + bar.get_width()/2., bar.get_height() + 0.5,
            f'{acc}%', ha='center', va='bottom', fontsize=11, fontweight='bold')
ax.set_ylabel('Accuracy (%)', fontsize=12)
ax.set_title('Fig. 4: Model Comparison - Accuracy on HOLD-Telugu', fontsize=13, fontweight='bold')
ax.set_ylim(60, 100)
ax.grid(True, alpha=0.3, axis='y')
plt.tight_layout()
plt.savefig('graph3_model_comparison.png', dpi=150)
plt.close()
print("Graph 3 saved: graph3_model_comparison.png")

print("\n=== All 3 graphs generated successfully! ===")
