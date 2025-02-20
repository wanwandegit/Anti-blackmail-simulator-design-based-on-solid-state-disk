import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import glob
import os
import matplotlib.pyplot as plt

# 文件夹路径（替换为你的文件夹路径）
folder_path = 'data/ransomware_data'

# 读取文件夹下所有.txt文件并合并
all_files = glob.glob(os.path.join(folder_path, '*.txt'))
data_list = [pd.read_csv(file, header=None, delimiter='\t') for file in all_files]
data = pd.concat(data_list, ignore_index=True)

# 指定特征列和标签列
features = data.iloc[:, -5:-1]
labels = data.iloc[:, -1]

# 过滤掉四项指标中有任一值为 -1.0 的数据
filtered_data = data[(features != -1.0).all(axis=1)]

# 更新特征列和标签列
features = filtered_data.iloc[:, -5:-1]
labels = filtered_data.iloc[:, -1]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

# 初始化并训练随机森林模型
clf = RandomForestClassifier(random_state=42)
clf.fit(X_train, y_train)

# 获取测试集的预测概率
y_probs = clf.predict_proba(X_test)[:, 1]  # 取正类的概率

# 创建结果存储列表
results = []

# 循环遍历阈值从0.1到0.9
for threshold in [i / 10 for i in range(1, 10)]:
    # 根据当前阈值生成预测标签
    y_pred = (y_probs >= threshold).astype(int)

    # 计算混淆矩阵并提取指标
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

    # 打印结果到控制台
    print(f"Threshold: {threshold:.1f}")
    print(f"True Positives (TP): {tp}")
    print(f"True Negatives (TN): {tn}")
    print(f"False Positives (FP): {fp}")
    print(f"False Negatives (FN): {fn}")
    print(f"精确率 (Precision): {precision:.2f}")
    print(f"召回率 (Recall): {recall:.2f}")
    print(f"F1分数 (F1 Score): {f1_score:.2f}\n")

    # 将结果存储到列表
    results.append({
        "Threshold": threshold,
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Precision": precision,
        "Recall": recall,
        "F1 Score": f1_score
    })

# 将结果保存到CSV文件
results_df = pd.DataFrame(results)
results_df.to_csv('threshold_metrics.csv', index=False)
print("结果已保存到 threshold_metrics.csv")

# 可视化数据
thresholds = results_df["Threshold"]
precision = results_df["Precision"]
recall = results_df["Recall"]
f1_score = results_df["F1 Score"]

plt.figure(figsize=(10, 6))
plt.plot(thresholds, precision, marker='o', label='Precision', color='blue')
plt.plot(thresholds, recall, marker='o', label='Recall', color='green')
plt.plot(thresholds, f1_score, marker='o', label='F1 Score', color='red')

# 设置坐标轴范围
plt.xlim(0, 1)  # X轴从0到1
plt.ylim(0, 1)  # Y轴从0到1

# 添加标题和标签
plt.title("Precision, Recall, and F1 Score vs Threshold", fontsize=14)
plt.xlabel("Threshold", fontsize=12)
plt.ylabel("Score", fontsize=12)
plt.xticks(thresholds)

# 设置图例位置为右下角
plt.legend(loc='lower right')
plt.grid()

# 保存图表
plt.savefig("threshold_metrics_plot.png")
plt.show()