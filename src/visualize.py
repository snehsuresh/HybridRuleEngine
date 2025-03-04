# import pandas as pd
# import matplotlib.pyplot as plt


# def plot_offer_distribution(results, plot_file):
#     df = pd.DataFrame(results)
#     offer_counts = df["offer"].value_counts()

#     plt.figure(figsize=(10, 6))
#     offer_counts.plot(kind="bar", color="skyblue")
#     plt.title("Offer Distribution")
#     plt.xlabel("Offer")
#     plt.ylabel("Number of Players")
#     plt.grid(axis="y", linestyle="--", alpha=0.7)
#     plt.tight_layout()
#     plt.savefig(plot_file)
#     plt.show()


# def save_metrics(filepath, c_duration, py_duration, num_players, rules):
#     data = {
#         "Metric": [
#             "C Duration (s)",
#             "Python Duration (s)",
#             "Number of Players",
#             "Number of Rules",
#         ],
#         "Value": [c_duration, py_duration, num_players, len(rules)],
#     }
#     df = pd.DataFrame(data)
#     df.to_csv(filepath, index=False)
#     print(f"Saved evaluation metrics to {filepath}")
