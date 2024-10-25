import sys
import os
import time
import psutil
import subprocess
import tkinter as tk
from tkinter import messagebox
import threading
import pystray
from PIL import Image
from pystray import MenuItem as item
import datetime
import re

def get_version_from_file():
    try:
        if getattr(sys, 'frozen', False):
            application_path = sys._MEIPASS
        else:
            application_path = os.path.dirname(os.path.abspath(__file__))
        
        version_file = os.path.join(application_path, 'version_info.txt')
        
        with open(version_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用正则表达式查找版本信息
        match = re.search(r'prodvers=\((.*?)\)', content) or re.search(r"StringStruct\(u'FileVersion', u'(.*?)'\)", content)
        
        if match:
            version = match.group(1)
            if ',' in version:  # 如果是 tuple 格式
                return '.'.join(version.replace(' ', '').split(','))
            return version  # 如果已经是字符串格式
    except Exception as e:
        print(f"读取版本信息时发生错误: {str(e)}")
    
    return "未知版本"  # 如果没有找到版本信息或发生错误

VERSION = get_version_from_file()

def resource_path(relative_path):
    """ 获取资源的绝对路径 """
    try:
        # PyInstaller 创建临时文件夹并将路径存储在 _MEIPASS 中
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class ProcessMonitor:
    @staticmethod
    def resource_path(relative_path):
        """ 获取资源的绝对路径 """
        try:
            # PyInstaller 创建临时文件夹 _MEIxxxxxx 并将资源存储其中
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def __init__(self, master):
        self.master = master
        master.title(f"威守护 - v{VERSION}")
        print(f"初始化程序，版本: {VERSION}")  # 添加这行来验证版本
        master.geometry("400x400")  # 调整窗口大小以适应日志区域
        master.protocol("WM_DELETE_WINDOW", self.on_closing)

        # 添加这一行
        self.log_line_count = 0

        # 设置窗口图标和任务栏图标
        icon_path = resource_path("icon.ico")
        if os.path.exists(icon_path):
            master.iconbitmap(icon_path)
        else:
            print(f"警告：图标文件未找到: {icon_path}")

        self.create_widgets()
        self.is_monitoring = False
        self.monitor_thread = None
        self.create_tray_icon()

        # 初始化输入框
        self.txt_process.insert(0, '')
        # self.txt_user.insert(0, '')  # 注释掉这一行
        self.txt_scan_interval.insert(0, '5')
        self.txt_wait_time.insert(0, '30')
        self.txt_command.insert(0, '')

        if os.path.exists('config.ini'):
            if self.load_config():
                self.auto_start_monitoring()
        else:
            print("配置文件不存在，使用默认值")

        self.show_window()

    def create_widgets(self):
        # 创建一个框架来容纳所有控件
        frame = tk.Frame(self.master, padx=10, pady=10)
        frame.grid(row=0, column=0, sticky="nsew")

        # 用户名 (注释掉，但保留代)
        # tk.Label(frame, text="用户名:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        # self.txt_user = tk.Entry(frame, width=30)
        # self.txt_user.grid(row=0, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        # 进程名
        tk.Label(frame, text="进程名:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.txt_process = tk.Entry(frame, width=30)
        self.txt_process.grid(row=1, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        # 扫描间隔
        tk.Label(frame, text="扫描间隔(秒):").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.txt_scan_interval = tk.Entry(frame, width=10)
        self.txt_scan_interval.grid(row=2, column=1, sticky="w", padx=5, pady=5)

        # 启动命令
        tk.Label(frame, text="启动命令:").grid(row=3, column=0, sticky="e", padx=5, pady=5)
        self.txt_command = tk.Entry(frame, width=40)
        self.txt_command.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=5)

        # 拉起后休眠时长
        tk.Label(frame, text="拉起后休眠时长(秒):").grid(row=4, column=0, sticky="e", padx=5, pady=5)
        self.txt_wait_time = tk.Entry(frame, width=10)
        self.txt_wait_time.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        # 按钮
        button_frame = tk.Frame(frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=10)

        self.btn_start = tk.Button(button_frame, text="开始监控", command=self.start_monitoring, width=10)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_stop = tk.Button(button_frame, text="停止监控", command=self.stop_monitoring, state=tk.DISABLED, width=10)
        self.btn_stop.grid(row=0, column=1, padx=5)

        # 配置网格权重，使其能够适应窗口大小变化
        self.master.grid_rowconfigure(0, weight=1)
        self.master.grid_columnconfigure(0, weight=1)
        for i in range(6):
            frame.grid_rowconfigure(i, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        # 添加日志显示区域
        self.log_text = tk.Text(self.master, height=10, width=50, state='disabled')
        self.log_text.grid(row=6, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

        # 添加滚动条
        scrollbar = tk.Scrollbar(self.master, command=self.log_text.yview)
        scrollbar.grid(row=6, column=3, sticky='nsew')
        self.log_text['yscrollcommand'] = scrollbar.set

        # 配置行和列的权重，使日志区域可以随窗口调整大小
        self.master.grid_rowconfigure(6, weight=1)
        self.master.grid_columnconfigure(0, weight=1)

    def load_config(self):
        try:
            with open('config.ini', 'r', encoding='utf-8') as f:
                config = dict(line.strip().split('=', 1) for line in f if '=' in line)
            
            self.txt_process.delete(0, tk.END)
            self.txt_process.insert(0, config.get('process', ''))
            
            # self.txt_user.delete(0, tk.END)
            # self.txt_user.insert(0, config.get('user', ''))
            
            self.txt_scan_interval.delete(0, tk.END)
            self.txt_scan_interval.insert(0, config.get('scan_interval', '5'))
            
            self.txt_wait_time.delete(0, tk.END)
            self.txt_wait_time.insert(0, config.get('wait_time', '30'))
            
            self.txt_command.delete(0, tk.END)
            self.txt_command.insert(0, config.get('command', ''))
            
            print("配置已加载")
            return True
        except FileNotFoundError:
            print("配置文件不存在，使用默认值")
            self.txt_scan_interval.insert(0, '5')
            self.txt_wait_time.insert(0, '30')
            return False
        except Exception as e:
            print(f"加载配置时发生错误: {str(e)}")
            self.txt_scan_interval.insert(0, '5')
            self.txt_wait_time.insert(0, '30')
            return False

    def save_config(self):
        try:
            with open('config.ini', 'w', encoding='utf-8') as f:
                f.write(f"process={self.txt_process.get()}\n")
                f.write(f"scan_interval={self.txt_scan_interval.get()}\n")
                f.write(f"wait_time={self.txt_wait_time.get()}\n")
                f.write(f"command={self.txt_command.get()}\n")
            self.log("配置已保存")
            return True
        except Exception as e:
            self.log(f"保存配置时发生错误: {str(e)}")
            return False

    def is_process_running(self):
        process_name = self.txt_process.get().lower()
        
        for proc in psutil.process_iter(['name']):
            try:
                if proc.name().lower() == process_name:
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def start_process(self):
        command = self.txt_command.get()
        if not command:
            self.log("错误：未指定启动命令")
            return

        try:
            # 如果命令路径包含空格，需要用引号括起来
            if ' ' in command and not (command.startswith('"') and command.endswith('"')):
                command = f'"{command}"'
            subprocess.Popen(command, shell=True)
            self.log(f"已启动进程: {command}")
        except Exception as e:
            self.log(f"启动进程时发生错误: {str(e)}")

    def check_process(self):
        while self.is_monitoring:
            try:
                if not self.is_process_running():
                    self.log(f"进程 {self.txt_process.get()} 未运行，正在启动...")
                    self.start_process()
                    
                    # 获取休眠时长并休眠
                    wait_time = int(self.txt_wait_time.get())
                    self.log(f"进程已启动，休眠 {wait_time} 秒...")
                    time.sleep(wait_time)
                else:
                    self.log(f"进程 {self.txt_process.get()} 正在运行。", save_to_file=False)
            except Exception as e:
                self.log(f"发生错误: {str(e)}")
            
            # 获取扫描间隔并休眠
            scan_interval = int(self.txt_scan_interval.get())
            time.sleep(scan_interval)

    def create_tray_icon(self):
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                application_path = os.path.dirname(os.path.abspath(__file__))
            
            icon_path = os.path.join(application_path, 'icon.ico')
            print(f"尝试加载图标: {icon_path}")
            
            if not os.path.exists(icon_path):
                print(f"警告：图标文件未找到: {icon_path}")
                image = self.create_default_icon()
            else:
                image = Image.open(icon_path)

            menu = (pystray.MenuItem('显示', self.show_window),
                    pystray.MenuItem('退出', self.quit_app))
            self.icon = pystray.Icon("name", image, "威守护", menu)
            self.icon_thread = threading.Thread(target=self.icon.run)
            self.icon_thread.start()
        except Exception as e:
            print(f"创建系统托盘图标时发生错误: {str(e)}")
            self.icon = None

    def create_default_icon(self):
        image = Image.new('RGB', (64, 64), color = (73, 109, 137))
        return image

    def setup(self, icon):
        icon.visible = True
        icon.on_click = self.on_tray_click

    def on_tray_click(self, icon, button):
        if button == pystray.MouseButton.LEFT:
            self.show_window()

    def show_window(self):
        self.master.deiconify()  # 显示主窗口
        self.master.lift()  # 将窗口提升到顶层
        self.master.focus_force()  # 强制获取焦点

    def hide_window(self):
        self.master.withdraw()
        if self.icon:
            self.icon.visible = True

    def on_closing(self):
        if self.is_monitoring:
            result = messagebox.askyesno("确认", "是否要关闭程序？", 
                                         detail="选择'是'关闭程序，选择'否'最小化到系统盘。")
            if result:
                self.safe_quit()
            else:
                self.hide_window()
        else:
            if messagebox.askokcancel("退出", "确定要退出程序吗？"):
                self.safe_quit()
            else:
                self.hide_window()

    def safe_quit(self):
        self.master.after(0, self.quit_program)

    def quit_program(self):
        self.stop_monitoring()  # 停止监控
        self.flush_logs_to_file()  # 确保所有日志都被保
        if self.icon:
            self.icon.stop()  # 停止系统托盘图标
        self.master.after(100, self._destroy_window)  # 使用 after 方法在主线程中调用销毁窗口

    def _destroy_window(self):
        self.master.quit()
        self.master.destroy()
        os._exit(0)  # 强制退出程序

    def start_monitoring(self):
        if not self.is_monitoring:
            self.save_config()
            self.is_monitoring = True
            self.monitor_thread = threading.Thread(target=self.check_process)
            self.monitor_thread.start()
            self.btn_start.config(state=tk.DISABLED)
            self.btn_stop.config(state=tk.NORMAL)
            self.log("监控已启动")
            self.hide_window()  # 添加这行来隐藏窗口

    def stop_monitoring(self):
        if self.is_monitoring:
            self.is_monitoring = False
            if self.monitor_thread:
                self.monitor_thread.join(timeout=10)
            self.btn_start.config(state=tk.NORMAL)
            self.btn_stop.config(state=tk.DISABLED)
            self.log("监控已停止")
            # 保存配置
            self.save_config()

    def validate_inputs(self):
        if not all([self.txt_process.get(), self.txt_start_command.get()]):
            messagebox.showerror("验证错误", "请填写进程名和启动命令。")
            return False

        try:
            scan_interval = int(self.txt_scan_interval.get())
            if scan_interval <= 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("验证错误", "扫描间隔必须是大于0的整数。")
            return False

        try:
            wait_time = int(self.txt_wait_time.get())
            if wait_time < 0:
                raise ValueError()
        except ValueError:
            messagebox.showerror("验证错误", "等待时间必需是非负整数。")
            return False

        return True

    def auto_start_monitoring(self):
        self.start_monitoring()
        self.master.after(2000, self.hide_window)  # 延迟2000毫秒后最小化窗口

    def log(self, message, save_to_file=True):
        def update_log():
            self.log_text.config(state='normal')
            
            # 检查是否需要清空界面日志
            if self.log_line_count >= 100:  # 将 10 改为 100
                self.log_text.delete('1.0', tk.END)
                self.log_line_count = 0
                self.log_text.insert(tk.END, "日志已清空\n")
                self.log_line_count += 1

            self.log_text.insert(tk.END, f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
            self.log_line_count += 1

        # 在主线程中更新界面
        self.master.after(0, update_log)

        # 保存日志到文件
        if save_to_file and not self.is_process_running_message(message):
            self.write_log_to_file(message)

    def write_log_to_file(self, message):
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        current_month = datetime.datetime.now().strftime("%Y-%m")
        log_file = os.path.join(log_dir, f"log_{current_month}.txt")
        
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - {message}\n")

    def flush_logs_to_file(self):
        self.log_text.config(state='normal')
        logs = self.log_text.get('1.0', tk.END).split('\n')
        self.log_text.config(state='disabled')

        for log in logs:
            if log and not self.is_process_running_message(log):
                # 从日志条目中提取时间戳和消息
                parts = log.split(' - ', 1)
                if len(parts) == 2:
                    timestamp, message = parts
                    self.write_log_to_file(message)

    def is_process_running_message(self, message):
        process_name = self.txt_process.get().lower()
        return f"进程 {process_name} 正在运行" in message.lower()

    def quit_app(self):
        if self.icon:
            self.icon.stop()
        self.master.quit()

if __name__ == '__main__':
    root = tk.Tk()
    app = ProcessMonitor(root)
    root.mainloop()
