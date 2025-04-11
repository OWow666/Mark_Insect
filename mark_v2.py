from time import sleep

import cv2
import os
import glob
import re
import tkinter as tk
from tkinter import simpledialog

# 全局变量
is_drawing = False
start_point = (0, 0)
end_point = (0, 0)
current_rectangles = []  # 当前图片的矩形列表
saved_rectangles = []  # 已保存的矩形列表
current_image = None
image_index = 0
window_width = 1920  # 默认窗口宽度
window_height = 1080  # 默认窗口高度
scale_factor = 1.0  # 缩放比例
original_image = None  # 原始图片
crop_count = 1  # 未输入名字的裁剪区域计数
new_img = True


def on_mouse(event, x, y, flags, param):
    """
    鼠标回调函数，用于处理鼠标事件。
    """
    global is_drawing, start_point, end_point, current_image, current_rectangles

    if event == cv2.EVENT_LBUTTONDOWN:
        # 鼠标左键按下，开始绘制矩形
        is_drawing = True
        start_point = (int(x / scale_factor), int(y / scale_factor))
    elif event == cv2.EVENT_MOUSEMOVE:
        # 鼠标移动，如果正在绘制，则动态显示矩形
        if is_drawing:
            temp_img = current_image.copy()
            # 绘制已保存的矩形
            for rect in saved_rectangles:
                cv2.rectangle(temp_img, (int(rect[0] * scale_factor), int(rect[1] * scale_factor)),
                              (int(rect[2] * scale_factor), int(rect[3] * scale_factor)), (0, 0, 255), 2)
            # 绘制当前矩形
            scaled_x, scaled_y = int(x / scale_factor), int(y / scale_factor)
            cv2.rectangle(temp_img, (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor)),
                          (x, y), (0, 255, 0), 2)
            cv2.imshow("Image", temp_img)
    elif event == cv2.EVENT_LBUTTONUP:
        # 鼠标左键释放，完成矩形绘制
        is_drawing = False
        end_point = (int(x / scale_factor), int(y / scale_factor))
        current_rectangles.append((start_point[0], start_point[1], end_point[0], end_point[1]))
        # 在当前图片上绘制矩形
        temp_img = current_image.copy()
        # 绘制已保存的矩形
        for rect in saved_rectangles:
            cv2.rectangle(temp_img, (int(rect[0] * scale_factor), int(rect[1] * scale_factor)),
                          (int(rect[2] * scale_factor), int(rect[3] * scale_factor)), (0, 0, 255), 2)
        # 绘制当前矩形
        cv2.rectangle(temp_img, (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor)),
                      (x, y), (0, 255, 0), 2)
        cv2.imshow("Image", temp_img)


def get_insect_name():
    """
    弹出输入对话框获取昆虫的名字。
    """
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    insect_name = simpledialog.askstring("输入", "请输入昆虫的名字:", parent=root)
    root.destroy()
    return insect_name


def save_cropped_rectangles(image, rectangles, image_name, output_dir="output"):
    """
    保存裁剪后的矩形区域，并要求用户输入昆虫的名字。
    """
    import os
    os.makedirs(output_dir, exist_ok=True)

    global new_img, saved_rectangles
    if new_img:
        new_img = False
        saved_rectangles = []

    # 提取组号
    match = re.search(r'G(\d+)_', image_name)
    if match:
        group_number = match.group(1)
    else:
        group_number = "1"  # 默认组号
    # print(rectangles)
    judge_input = False
    for i, (x1, y1, x2, y2) in enumerate(rectangles):
        if i == len(rectangles) - 1:
            judge_input = True
        # 确保坐标有效
        # print(rectangles)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)

        # 裁剪矩形区域
        if x2 > x1 and y2 > y1 :  # 确保裁剪区域有效
            cropped = image[y1:y2, x1:x2]

            # 获取昆虫名字
            if judge_input:
                insect_name = get_insect_name()
                if insect_name:
                # 生成保存路径
                    output_path = os.path.join(output_dir, f"G{group_number}_{insect_name}.png")
                else:
                # 未输入名字，使用默认命名规则
                    global crop_count
                    output_path = os.path.join(output_dir, f"G{group_number}_crop_{crop_count}.png")
                    crop_count += 1  # 增加未输入名字的计数

            # cv2.imwrite(output_path, cropped)
                cv2.imencode('.jpg', cropped)[1].tofile(output_path)
                print(f"已保存: {output_path}")

            # 将当前矩形添加到已保存的矩形列表
            saved_rectangles.append((x1, y1, x2, y2))
            judge_input = False


def adjust_window_size(image):
    """
    调整窗口大小以适应图片。
    """
    global window_width, window_height, scale_factor
    h, w = image.shape[:2]
    if w > window_width or h > window_height:
        # 计算缩放比例
        scale_width = window_width / w
        scale_height = window_height / h
        scale_factor = min(scale_width, scale_height)
        window_width = int(w * scale_factor)
        window_height = int(h * scale_factor)
        cv2.resizeWindow("Image", window_width, window_height)
    else:
        scale_factor = 1.0


def main():
    global current_image, image_index, current_rectangles, window_width, window_height, original_image, scale_factor, saved_rectangles, crop_count, new_img

    # 获取图片列表（假设图片在当前目录下的 "images" 文件夹中）
    image_folder = "pic"  # 替换为你的图片文件夹路径
    image_paths_ori = glob.glob(os.path.join(image_folder, "G*_*.JPEG"))
    image_paths = sorted(image_paths_ori, key=lambda x: int(os.path.basename(x).split('_')[0][1:]))

    if not image_paths:
        print("未找到图片文件，请检查文件夹路径。")
        return

    # 创建输出目录
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # 初始化
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)  # 允许调整窗口大小
    cv2.resizeWindow("Image", window_width, window_height)
    cv2.setMouseCallback("Image", on_mouse)

    while image_index < len(image_paths):
        # 加载当前图片
        image_path = image_paths[image_index]
        original_image = cv2.imread(image_path)
        if original_image is None:
            print(f"无法加载图片: {image_path}")
            image_index += 1
            continue

        # 重置
        current_rectangles = []
        saved_rectangles = []
        new_img = True
        window_width = 1920  # 默认窗口宽度
        window_height = 1080  # 默认窗口高度
        scale_factor = 1.0  # 缩放比例

        # 调整窗口大小以适应图片
        adjust_window_size(original_image)

        # 缩放图片以适应窗口
        h, w = original_image.shape[:2]
        current_image = cv2.resize(original_image, (int(w * scale_factor), int(h * scale_factor)))

        # 显示图片
        cv2.imshow("Image", current_image)

        # 等待用户操作
        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 按 'q' 切换到下一张图片
                # save_cropped_rectangles(original_image, current_rectangles, image_path, output_dir)
                # print(0)
                image_index += 1
                break
            elif key == ord('s'):  # 按 's' 保存当前图片的标注结果
                save_cropped_rectangles(original_image, current_rectangles, image_path, output_dir)
                # print(1)
        print(f"已保存所有标注区域：{image_path}")

    # 退出
    cv2.destroyAllWindows()
    print("所有图片处理完成。")


if __name__ == "__main__":
    main()