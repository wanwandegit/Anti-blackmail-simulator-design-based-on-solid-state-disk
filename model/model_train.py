import pandas as pd
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt

# 假设数据文件名为 'data.txt'
data = pd.read_csv('data.txt', header=None, delimiter='\t')

# 指定特征列和标签列
features = data.iloc[:, -5:-1]
labels = data.iloc[:, -1]

# 划分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.3, random_state=42)

# 初始化并训练决策树模型
clf = DecisionTreeClassifier(random_state=42)
clf.fit(X_train, y_train)

# 预测并计算混淆矩阵
y_pred = clf.predict(X_test)
tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()

# 输出 TP, TN, FP, FN
print(f"True Positives (TP): {tp}")
print(f"True Negatives (TN): {tn}")
print(f"False Positives (FP): {fp}")
print(f"False Negatives (FN): {fn}")

# 计算并输出精确率和召回率
precision = tp / (tp + fp) if (tp + fp) > 0 else 0
recall = tp / (tp + fn) if (tp + fn) > 0 else 0
print(f"精确率 (Precision): {precision:.2f}")
print(f"召回率 (Recall): {recall:.2f}")

# 使用 matplotlib 可视化决策树
plt.figure(figsize=(15, 10))
plot_tree(clf, feature_names=['OWIO', 'OWST', 'WAR', 'APE'], class_names=['Non-Ransomware', 'Ransomware'], filled=True, rounded=True)
plt.title("Decision Tree Visualization")
plt.show()
