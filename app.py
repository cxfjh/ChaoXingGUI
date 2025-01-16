import os
import re
import sys
import time
import ctypes
from threading import Thread
from tkinter import messagebox, Tk, Frame, Button, ttk


# 定义全局变量
filePath = "./log/disposition.txt"
idFilePath = "./log/course.txt"
errorPath = './log/error.txt'


# 查询ID
def queryId():
    try: 
        if os.path.exists("./log"):
            for file in os.listdir("./log"): os.remove(os.path.join("./log", file))
        Thread(target=opens).start()
    except: pass


# 从文件中提取账号信息。
def extractInfoFromFile():
    try: 
        if not os.path.exists(filePath): return
        with open(filePath, 'r', encoding='utf-8') as file: content = file.read()
        entryAccount.insert(0, re.search(r'账号：(\d+)', content).group(1))  
        entryPassword.insert(0, re.search(r'密码：(.+)', content).group(1))
        entryId.insert(0, re.search(r'ID：(.+)', content).group(1))
    except: pass


# 打开App.exe
def opens(): 
    if getattr(sys, 'frozen', False): exePath = os.path.join(sys._MEIPASS, 'dist', 'main.exe') 
    else: exePath = os.path.join(os.path.dirname(__file__), 'dist', 'main.exe')
    ctypes.windll.shell32.ShellExecuteW(None, "open", exePath, None, None, 1)


# 启动小助手
def startApp(index):
    for _ in range(index):
        Thread(target=opens).start()
        time.sleep(3)
        if os.path.exists(errorPath):
            with open(errorPath, "r", encoding="utf-8") as file: messagebox.showerror("错误", file.read())
            os.remove(errorPath)
            return
        time.sleep(27)


# 提交数据
def submitData():
    try:
        # 判断文件是否存在，不存在则创建
        dirName = os.path.dirname(filePath) 
        if not os.path.exists(dirName): os.makedirs(dirName) 

        # 获取输入数据
        account = entryAccount.get()
        password = entryPassword.get()
        userId = entryId.get()
        count = entryCount.get() or 1
        
        # 将数据写入文件
        if account and password and userId: 
            with open(filePath, "w", encoding="utf-8") as file:
                file.write(f"账号：{account}\n")
                file.write(f"密码：{password}\n")
                file.write(f"ID：{userId}\n")

        messagebox.showinfo("提示", "信息注入程序成功！")
        Thread(target=startApp, args=(int(count),)).start() # 启动线程启动小助手
    except: messagebox.showerror("错误", "信息注入程序失败！")


# 重置程序
def resetApp():
    try:
        if os.path.exists("./log"):
            for file in os.listdir("./log"): os.remove(os.path.join("./log", file))
        messagebox.showinfo("提示", "重置成功！")
    except: messagebox.showerror("错误", "重置失败！")


# 创建主窗口
root = Tk()
root.title("刷课小助手")
root.geometry("350x280")
root.resizable(False, False)
root.attributes("-topmost", True)
root.option_add("*Font", "楷体 15")

# 处理图标路径
if getattr(sys, 'frozen', False): iconPath = os.path.join(sys._MEIPASS, 'dist', 'icon.ico')
else: iconPath = os.path.join(os.path.dirname(__file__), 'dist', 'icon.ico')
root.iconbitmap(iconPath)

# 创建框架以实现左右布局
frame = Frame(root)
frame.pack(padx=0, pady=30)

# 姓名标签和输入框
labelAccount = ttk.Label(frame, text="账号:")
labelAccount.grid(row=0, column=0, padx=5, pady=5, sticky="e")
entryAccount = ttk.Entry(frame)
entryAccount.grid(row=0, column=1, padx=5, pady=5)

# 年龄标签和输入框
labelPassword = ttk.Label(frame, text="密码:")
labelPassword.grid(row=1, column=0, padx=5, pady=5, sticky="e")
entryPassword = ttk.Entry(frame)
entryPassword.grid(row=1, column=1, padx=5, pady=5)

# 身份证号标签和输入框
labelId = ttk.Label(frame, text="课ID:")
labelId.grid(row=2, column=0, padx=5, pady=5, sticky="e")
entryId = ttk.Entry(frame)
entryId.grid(row=2, column=1, padx=5, pady=5)

# 身份证号标签和输入框
labelCount = ttk.Label(frame, text="次数:")
labelCount.grid(row=3, column=0, padx=5, pady=5, sticky="e")
entryCount = ttk.Entry(frame)
entryCount.grid(row=3, column=1, padx=5, pady=5)

# 启动按钮
submitButton = Button(root, text="启动", width=5, height=4, command=submitData)
submitButton.pack(side="left", padx=28, pady=(0, 35)) 

# 查询ID
idButton = Button(root, text="查ID", width=5, height=4, command=queryId)
idButton.pack(side="left", padx=28, pady=(0, 35)) 

# 重置按钮
resetButton = Button(root, text="重置", width=5, height=4, command=resetApp)
resetButton.pack(side="left", padx=28, pady=(0, 35)) 

# 底部版本信息右下角,设置字体黑色
labelVersion = ttk.Label(root, text="v1.0.0", foreground="gray", font=("楷体", 10))
labelVersion.place(relx=1.0, rely=1.0, anchor='se', x=-5, y=-5)

# 从文件中提取账号信息
extractInfoFromFile()

# 运行主循环
root.mainloop()
