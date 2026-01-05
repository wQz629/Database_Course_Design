# Database_Course_Design

数据库期末大作业

## 环境搭建

1. 创建虚拟环境

```
python -m venv venv
```

2. 激活虚拟环境

- Windows(POWERSHELL)

```
.\venv\Scripts\Activate.ps1
```

- Windows(CMD)

```
.\venv\Scripts\activate.bat
```

- Linux/MacOS

```
source venv/bin/activate
```

> 如果在PowerShell中显示字符无法识别，那么可以换用CMD命令行。或者在PowerShell中以管理员身份运行，并执行以下命令：`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`，即可解决PowerShell字符无法识别的问题。

3. 安装依赖包

```
pip install -r requirements.txt
```

4. 代码检测

4.1 在命令行中运行以下代码，能够成功输出 `Hello, world!`，那么说明环境搭建成功。

```
python -c "import PyQt6; import pymysql; print('库安装成功，可以开始写代码了！')"
```

4.2 尝试运行 `test_gui.py`文件，能够成功打开PyQt6空窗口，那么说明环境搭建成功。

5. Qt Designer 在 `.\venv\Lib\site-packages\qt6_applications\Qt\bin\designer.exe `
