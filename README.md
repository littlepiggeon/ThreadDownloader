# ThreadDownloader 多线程下载器

## English 英语

Thread downloader,let the downloading faster.  
I only developed CLI program.  
If you want,you can build the source code by Cython,Pyinstaller or others.  
I downloaded a ISO file with this.I just use **64 threads**,and it takes just **10 minutes**.
This Program only works on Windows.I will try to let it can use on Linux and Mac.

## Chinese Simpled 简体中文

多线程下载器，让下载更快。  
我只开发了命令行版本。
我使用这个下载了一个ISO文件，只是开了**64个**线程，只花了**10分钟**。  
这个程序只能在Windows上使用，我会试着让它可以在Linux和Mac上运行的。

### 用法

在[Releases](https://github.com/littlepiggeon/releases/latest)上下载downloader.exe，再使用命令行运行。
常用参数：  
-U,--URL 下载链接  
-d,--dir 保存目录  
-t,--thread-count 线程数（通常十几到几十个，如果对多线程下载没有概念的话不要超过一百个）