# Database_Course_Design


## 1. 环境搭建

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

## 2. 实际运行

> 特别提醒，在实际运行前，需要修改`config.ini`文件中的数据库配置（如：user、password、host、port等信息），否则无法连接数据库。

1. 确保MySQL能连接成功。如果在下面运行的时候，显示MySQL没连接，那可以打开 系统->服务->MYSQL80，右键点击MYSQL80，然后选择`启动`，等待服务启动完成。

2. 在mysql命令行，运行`./sql`文件夹下的三个mysql脚本，创建数据库、表、数据。

```
mysql -u root -p
source 换成你的实际路径/Database_Course_Design/sql/create_table.sql
source 换成你的实际路径/Database_Course_Design/sql/create_trigger.sql
source 换成你的实际路径/Database_Course_Design/sql/insert_test_data.sql
```

> 也可以在 MySQL workbench中运行，那就不需要写命令了，直接点击即可
> 注意：建表的命令必须是最先执行

3. 运行`main.py`文件，即可看到整个医药销售管理系统。

> 如果无法运行，可以查看`logs`文件夹下的日志文件，排查错误。