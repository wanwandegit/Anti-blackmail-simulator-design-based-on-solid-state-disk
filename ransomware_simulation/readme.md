如果出现目录下明明有可执行文件，也执行了chmod 命令
却提示找不到文件，“No such file or directory”
可能是因为这是32位的程序，在64位的Ubuntu中运行需要提前安装32位的库。

首先添加i32架构，然后更新镜像源，再安装就可以了，指令如下：

`sudo dpkg --add-architecture i386`

`sudo apt-get update`

`sudo apt-get install libc6:i386 libncurses5:i386 libstdc++6:i386 -y`

`sudo apt install lib32z1 -y`
