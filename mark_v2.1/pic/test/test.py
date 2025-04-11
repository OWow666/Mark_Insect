import cv2
import numpy as np

# 读取图像
image = cv2.imread('G3_R.jpg')

# 转换为灰度图
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 高斯模糊
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# 边缘检测
edges = cv2.Canny(blurred, 50, 150)

# 寻找轮廓
contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# 筛选轮廓（根据面积）
min_area = 1000  # 根据实际情况调整
filtered_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]

# 创建掩码
mask = np.zeros_like(gray)
cv2.drawContours(mask, filtered_contours, -1, (255), thickness=cv2.FILLED)

# 分割昆虫
segmented = cv2.bitwise_and(image, image, mask=mask)

# 保存结果
cv2.imwrite('segmented_insect.jpg', segmented)