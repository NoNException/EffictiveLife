在我的桌面上有一个名为temporary的文件夹，里面有很多临时的文件，表格，别人发送给我的文件，下载的资料。
正常情况下这些文件都会被我归档到正确的文件夹下，但是仍然存在一些特殊的情况导致文件被长久的保留在这个文件夹下。
所以我决定编写一个定时脚本，将文件按照时间归类到2个时间等级的文件夹下。
- 两周之内
- 超过两周

并且在每天的下午2点半（运行时间目前不能自己定制），提示我对这几个文件的检查结果。如果我确认删除文件，这些文件就会被移动到废纸篓。

配置文件`.file_cleaner`格式：
```json
{
      "work_spaces":[
        {"dir":"/the/directory/you/want/to/be/cleaned","max_seconds":604880}
      ]
}
```
- `dir`表示，脚本即将运行的文件。
- `max_seconds`代表目录下文件存在的最大秒数。

运行脚本，在后台运行：
```shell 
nohub python FileCleaner.py & 
```
运行脚本之后，在程序第一次运行的时候，在你指定的文件夹下，会产生一个文件`.file_to_clean`，其中记录着，将要被删除的文件。

### tips:
本脚本只能在Mac OS的环境下运行。因为全部的交互过程都是通过`osascript`实现的。