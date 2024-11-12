# 超星学习通自动化完成任务点（GUI版）

## 1. 本项目是 [超星学习通自动化完成任务点](https://github.com/Samueli924/chaoxing) 的扩展版，增加了图形界面（GUI）支持，使用 Tkinter 库进行界面设计。
## 2. 感谢 [Samueli924](https://github.com/Samueli924) 作者提供的开源代码。

---

# 使用说明

## 一、脚本运行

1. **克隆或下载项目到本地**
   
2. **安装依赖**

   运行以下命令来安装所需的 Python 库：

   ```bash
   pip install -r requirements.txt
   ```

3. **启动程序**

   运行以下命令启动程序：

   ```bash
   python main.py
   ```

---

## 二、脚本自动化运行

1. **启动 `main.py`**

   ![启动界面](./docs/image1.png)

1. **登录并获取课程ID**

   - 成功启动程序后，您将看到如下界面。
   - 在登录界面输入账号和密码，成功登录后获取课程ID：
  
   ![登录界面](./docs/image2.png)

2. **启动 `app.py`**

   ![配置界面](./docs/image3.png)

3. **填写账号信息、课程ID和次数**

   - 在界面中输入账号、密码、课程ID、次数。
   - "次数"表示同时打开多个窗口的数量（默认为1，推荐设置为10）。
   - 点击 **启动** 按钮即可开始自动化任务。
  
   ![设置界面](./docs/image4.png)

4. **注意事项**

   - 为了防止账号被发现异常，自动化程序默认每30秒启动一个窗口，您可以根据自己的情况在 `app.py` 中调整启动间隔。
   - 下次运行时，无需上面这些繁琐的步骤，直接启动 `app.py` 即可。程序会自动读取上次的配置，无需重新输入账号、密码和课程ID。
   - 如果需要更换课程，只需点击 **重置** 按钮，重新配置课程ID。


## 三、exe 可执行文件运行

1. **下载 exe 文件**

   从最新的 [Releases](https://github.com/cxfjh/ChaoXingGUI/releases) 页面下载 `ChaoXingGUI.7z` 文件，然后解压。

2. **运行 exe 文件**

   - 双击运行 `main.exe` 文件，拿到课程ID后。
   - 然后双击运行 `app.exe` 文件，按照上面的步骤填写账号、密码、课程ID、次数，点击启动即可。


# 免责声明
## 本代码遵循 [GPL-3.0](https://www.gnu.org/licenses/gpl-3.0.html) 协议，任何人不得将本代码用于商业用途。

