import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
from aip import AipImageClassify
import threading
import base64

# ========== 请替换成你自己的信息 ==========
APP_ID = '122664654'
API_KEY = 'x5qdr1pnGYhlQCmk7FTTWk58'
SECRET_KEY = 'q9eIWAI17QMHwJnESEqYGybkgZNM4EZS'
STUDENT_ID = '202335020644'  # 改成你的学号
STUDENT_NAME = '谢书云'  # 改成你的姓名


# =======================================

class BaiduImageRecognizer:
    def __init__(self, root):
        self.root = root
        self.root.title(f"智能图像识别系统 - {STUDENT_NAME}({STUDENT_ID})")
        self.root.geometry("700x600")

        # 初始化百度AI客户端
        self.client = AipImageClassify(APP_ID, API_KEY, SECRET_KEY)

        # 当前图片路径
        self.current_image_path = None

        self.setup_ui()

    def setup_ui(self):
        # 标题区域 - 显示学号姓名
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x')
        title_frame.pack_propagate(False)

        title_label = tk.Label(title_frame,
                               text=f"智能图像识别系统\n{STUDENT_NAME}  {STUDENT_ID}",
                               font=('微软雅黑', 16, 'bold'),
                               fg='white', bg='#2c3e50')
        title_label.pack(expand=True)

        # 图片显示区域
        self.image_label = tk.Label(self.root, text="暂无图片",
                                    bg='#ecf0f1', width=80, height=15,
                                    relief='solid')
        self.image_label.pack(pady=20, padx=20)

        # 按钮区域
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        self.select_btn = tk.Button(btn_frame, text="选择图片",
                                    command=self.select_image,
                                    font=('微软雅黑', 12), bg='#3498db', fg='white',
                                    width=12, height=1)
        self.select_btn.pack(side='left', padx=10)

        self.recognize_btn = tk.Button(btn_frame, text="开始识别",
                                       command=self.recognize_image,
                                       font=('微软雅黑', 12), bg='#27ae60', fg='white',
                                       width=12, height=1, state='disabled')
        self.recognize_btn.pack(side='left', padx=10)

        # 识别结果区域
        result_frame = tk.LabelFrame(self.root, text="识别结果", font=('微软雅黑', 12))
        result_frame.pack(fill='both', expand=True, padx=20, pady=10)

        self.result_text = tk.Text(result_frame, font=('微软雅黑', 11), height=8)
        self.result_text.pack(fill='both', expand=True, padx=10, pady=10)

        # 进度条
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')

        # 状态栏
        self.status_label = tk.Label(self.root, text="就绪", bd=1, relief='sunken', anchor='w')
        self.status_label.pack(side='bottom', fill='x')

    def select_image(self):
        file_path = filedialog.askopenfilename(
            title="选择图片",
            filetypes=[("图片文件", "*.jpg *.jpeg *.png *.bmp")]
        )
        if file_path:
            self.current_image_path = file_path
            # 显示图片
            img = Image.open(file_path)
            # 缩放图片以适应显示区域
            img.thumbnail((400, 300))
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text='')
            self.image_label.image = photo
            self.recognize_btn.config(state='normal')
            self.status_label.config(text=f"已选择: {file_path.split('/')[-1]}")
            # 清空上次结果
            self.result_text.delete(1.0, tk.END)

    def recognize_image(self):
        if not self.current_image_path:
            return

        # 禁用按钮，显示进度
        self.select_btn.config(state='disabled')
        self.recognize_btn.config(state='disabled')
        self.progress.pack(pady=5)
        self.progress.start()
        self.status_label.config(text="正在识别中，请稍候...")

        # 在新线程中执行识别，避免界面卡死
        thread = threading.Thread(target=self._do_recognition)
        thread.start()

    def _do_recognition(self):
        try:
            # 读取图片
            with open(self.current_image_path, 'rb') as f:
                image_data = f.read()

            # 调用百度API
            result = self.client.advancedGeneral(image_data)

            # 更新UI（需要在主线程中执行）
            self.root.after(0, self._show_result, result)

        except Exception as e:
            self.root.after(0, self._show_error, str(e))

    def _show_result(self, result):
        self.progress.stop()
        self.progress.pack_forget()
        self.select_btn.config(state='normal')
        self.recognize_btn.config(state='normal')

        # 解析结果
        if 'error_code' in result:
            self.result_text.insert(tk.END, f"识别失败: {result.get('error_msg', '未知错误')}")
            self.status_label.config(text="识别失败")
            return

        self.result_text.insert(tk.END, "=" * 40 + "\n")
        self.result_text.insert(tk.END, f"识别结果（共{result.get('result_num', 0)}个）:\n\n")

        for idx, item in enumerate(result.get('result', []), 1):
            keyword = item.get('keyword', '未知')
            score = item.get('score', 0)
            self.result_text.insert(tk.END, f"{idx}. {keyword}\n")
            self.result_text.insert(tk.END, f"   置信度: {score:.2%}\n\n")

        self.result_text.insert(tk.END, "=" * 40)
        self.status_label.config(text="识别完成")

    def _show_error(self, error_msg):
        self.progress.stop()
        self.progress.pack_forget()
        self.select_btn.config(state='normal')
        self.recognize_btn.config(state='normal')
        messagebox.showerror("错误", f"识别出错: {error_msg}")
        self.status_label.config(text="识别出错")


if __name__ == '__main__':
    root = tk.Tk()
    app = BaiduImageRecognizer(root)
    root.mainloop()