WeiMonitor （威守护）使用说明书

简介
WeiMonitor（威守护）是一款通用守护程序，旨在监控指定的Windows进程，并根据配置文件自动化执行预定命令，以确保指定的Windows进程能够持续运行。该软件可最小化到系统托盘，并提供便捷的用户界面供用户填写和维护配置。

特性
根据INI文件配置自动运行
最小化至托盘，方便监控
每月弹出主界面，提供配置更新
定期监控指定的exe进程
自定义扫描间隔时间
自动启动指定程序并记录日志
按月生成的日志文件，易于追溯

系统要求
操作系统：Windows 7 或更高版本

![截图](https://github.com/user-attachments/assets/d0ef8743-a2f0-43bc-ae40-837abda10bf8)


安装与设置
下载：从官方网站或其他受信任的资源下载 WeiMonitor 安装包。
安装：按照安装向导进行步骤，完成安装。
配置INI文件
在程序首次运行时，若存在名为 config.ini 的文件，程序将自动读取并应用配置。以下是 config.ini 文件的示例结构：

[DEFAULT]
process=bt4560.exe
scan_interval=3
wait_time=20
command=D:\Program\bt4560v2.1\bt4560.exe


配置项说明
process：要监控的进程名称（例如 bt4560.exe）。
scan_interval：两次扫描之间的间隔时间（以秒为单位）。
wait_time：当进程启动后，程序休眠的时间（以秒为单位）。
command：启动进程时执行的命令行（包括该程序完整路径）。

您可根据实际需求修改该文件，并将其放置在 WeiMonitor 可执行文件的同一目录下。


使用方式
部署程序：将程序压缩包解压到D盘某文件夹下。或者C盘具有执行和写入权限的文件夹下。把WeiMonitor.exe的快捷方式拖动到桌面。

自动启动（win10、win11）：
按下 Win + R 组合键，打开运行对话框。
输入 shell:startup，然后按 Enter。这将打开当前用户的启动文件夹。通常路径为：
C:\Users\<你的用户名>\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup
把WeiMonitor.exe的快捷方式拖动到startup文件夹内。
WeiMonitor.exe将在你每次登录 Windows 时自动运行。

启动程序：双击 WeiMonitor 图标，程序将读取配置并最小化到系统托盘。
监控过程：程序将根据配置文件中的设置，定时检查指定的进程：
如果检测到指定进程存在，程序会继续间隔扫描。
如果未检测到指定进程，将执行启动命令，并在启动后休眠60秒以等待程序加载，随后继续扫描。
日志记录：所有操作将会记录在位于程序目录下的日志文件中，文件名格式为 log_YYYY-MM.txt。
用户界面
每月，程序将自动弹出主界面，用户可以在界面上修改INI配置，例如扫描间隔和启动命令。

日志文件
除定时扫描正常的日志信息外，所有自动化操作均会记录到日志文件中，便于用户追溯启动命令的执行时间和次数。日志文件按月生成，格式为 log_YYYY-MM.txt。
示例日志内容
2024-10-24 21:33:06 - 配置已保存
2024-10-24 21:33:06 - 监控已启动
2024-10-24 21:33:06 - 进程 FlashFXP.exe 未运行，正在启动...
2024-10-24 21:33:06 - 已启动进程: D:\Program\FlashFXP\FlashFXP.exe
2024-10-24 21:33:06 - 进程已启动，休眠 30 秒...
2024-10-24 21:34:26 - 监控已停止
2024-10-24 21:34:26 - 配置已保存

常见问题及解决方案
Q1: 如何更改扫描间隔时间？
方法1：直接在程序界面修改。
方法2：打开 config.ini 文件，找到 scan_interval 属性，然后修改为所需的时间（以秒为单位），保存后重新启动程序。

Q2: 程序没有检测到指定的进程，该怎么办？
确保在 config.ini 文件中指定的启动命令是正确的完整路径及文件名。如果仍有问题，请检查任务管理器确认该进程的名称是否与配置一致。

Q3: 日志文件在哪里可以找到？
日志文件位于 WeiMonitor 的安装目录的log文件夹下，文件名格式为 log_YYYY-MM.txt。

Q4:无法通过 exe 路径启动怎么办？
由于部分电脑权限问题，直接指定 exe 路径可能会无法启动。此时可以将监控的 exe 程序建立
一个快捷方式，通常把快捷方式放桌面上。
![第4页-2](https://github.com/user-attachments/assets/2cdee81c-3777-400f-ba56-29537ab6f97e)

然后在威守护中，设定桌面快捷方式路径为启动命令。
例如：
command=D:\Users\lin.wei3\Desktop\bt4560.lnk


支持与反馈
如果您在使用 WeiMonitor 的过程中遇到任何问题，或有建议，请通过以下方式联系我们：

邮箱：wwip@qq.com
感谢您使用 WeiMonitor（威守护），愿它能够为您提供帮助与便利！

