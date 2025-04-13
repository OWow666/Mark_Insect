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
current_rectangles = []
saved_rectangles = []
current_image = None
image_index = 0
window_width = 1920
window_height = 1080
scale_factor = 1.0
original_image = None
crop_count = 1
new_img = True


def on_mouse(event, x, y, flags, param):
    global is_drawing, start_point, end_point, current_image, current_rectangles

    if event == cv2.EVENT_LBUTTONDOWN:

        is_drawing = True
        start_point = (int(x / scale_factor), int(y / scale_factor))
    elif event == cv2.EVENT_MOUSEMOVE:

        if is_drawing:
            temp_img = current_image.copy()

            for rect in saved_rectangles:
                cv2.rectangle(temp_img, (int(rect[0] * scale_factor), int(rect[1] * scale_factor)),
                              (int(rect[2] * scale_factor), int(rect[3] * scale_factor)), (0, 0, 255), 2)

            scaled_x, scaled_y = int(x / scale_factor), int(y / scale_factor)
            cv2.rectangle(temp_img, (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor)),
                          (x, y), (0, 255, 0), 2)
            cv2.imshow("Image", temp_img)
    elif event == cv2.EVENT_LBUTTONUP:

        is_drawing = False
        end_point = (int(x / scale_factor), int(y / scale_factor))
        current_rectangles.append((start_point[0], start_point[1], end_point[0], end_point[1]))

        temp_img = current_image.copy()

        for rect in saved_rectangles:
            cv2.rectangle(temp_img, (int(rect[0] * scale_factor), int(rect[1] * scale_factor)),
                          (int(rect[2] * scale_factor), int(rect[3] * scale_factor)), (0, 0, 255), 2)

        cv2.rectangle(temp_img, (int(start_point[0] * scale_factor), int(start_point[1] * scale_factor)),
                      (x, y), (0, 255, 0), 2)
        cv2.imshow("Image", temp_img)


def get_insect_name():
    root = tk.Tk()
    root.withdraw()
    insect_name = simpledialog.askstring("输入", "请输入昆虫的名字:", parent=root)
    root.destroy()
    return insect_name


def save_cropped_rectangles(image, rectangles, image_name, output_dir="output"):
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
        group_number = "1"
    # print(rectangles)
    judge_input = False
    for i, (x1, y1, x2, y2) in enumerate(rectangles):
        if i == len(rectangles) - 1:
            judge_input = True
        # print(rectangles)
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)

        if x2 > x1 and y2 > y1 :
            cropped = image[y1:y2, x1:x2]

            if judge_input:
                insect_name = get_insect_name()
                if insect_name:
                    output_path = os.path.join(output_dir, f"G{group_number}_{insect_name}.png")
                else:
                    global crop_count
                    output_path = os.path.join(output_dir, f"G{group_number}_crop_{crop_count}.png")
                    crop_count += 1

            # cv2.imwrite(output_path, cropped)
                cv2.imencode('.jpg', cropped)[1].tofile(output_path)
                print(f"已保存: {output_path}")

            saved_rectangles.append((x1, y1, x2, y2))
            judge_input = False


def adjust_window_size(image):
    global window_width, window_height, scale_factor
    h, w = image.shape[:2]
    if w > window_width or h > window_height:
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

    image_folder = "pic"
    image_paths_ori = glob.glob(os.path.join(image_folder, "G*_*.jpeg")) + glob.glob(os.path.join(image_folder, "G*_*.jpg"))
    image_paths = sorted(image_paths_ori, key=lambda x: int(os.path.basename(x).split('_')[0][1:]))
    # image_paths.reverse()

    if not image_paths:
        print("未找到图片文件，请检查文件夹路径。")
        return

    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)

    # Init
    cv2.namedWindow("Image", cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Image", window_width, window_height)
    cv2.setMouseCallback("Image", on_mouse)

    while image_index < len(image_paths):
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
        window_width = 1920
        window_height = 1080
        scale_factor = 1.0

        adjust_window_size(original_image)

        h, w = original_image.shape[:2]
        current_image = cv2.resize(original_image, (int(w * scale_factor), int(h * scale_factor)))

        cv2.imshow("Image", current_image)

        while True:
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):  # 按 'q' 切换
                # save_cropped_rectangles(original_image, current_rectangles, image_path, output_dir)
                # print(0)
                image_index += 1
                break
            elif key == ord('s'):  # 按 's' 保存
                save_cropped_rectangles(original_image, current_rectangles, image_path, output_dir)
                # print(1)
        print(f"已保存所有标注区域：{image_path}")

    cv2.destroyAllWindows()
    print("所有图片处理完成。")


if __name__ == "__main__":
    main()