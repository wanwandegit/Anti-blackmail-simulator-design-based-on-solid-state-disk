import subprocess
import time
import time as import_time
import os
import asyncio
import aiofiles

dirs = "./data"  # 存放数据的文件夹路径
device = '/dev/sda'  # 要监控的设备
device_number = '8,0'  # 设备号
time = '10'  # 单个blktrace进程的检测时间（单位为秒）
process_number = 3  # 总进程数
not_null_file = []  # 非空文件序号


# 删除目录下所有文件
def delete_files(directory):
    file_list = os.listdir(directory)
    for file in file_list:
        file_path = os.path.join(directory, file)
        if os.path.isfile(file_path):
            os.remove(file_path)


# 将收集到的数据写入文件
async def write_task(cnt, blkparse_output):
    now_time = import_time.time()
    print(f"write_task: 开启第{cnt}个异步任务，总耗时：", now_time - start_time)

    # 使用 aiofiles 打开硬盘文件
    async with aiofiles.open(device, 'rb') as f:
        # 读取blkparse输出，按行划分
        outputs = blkparse_output.split('\n')
        current_time = -1  # 当前时间戳（秒）

        for output in outputs:
            attributes = output.split()
            # 判断是否是有效的IO操作信息
            if len(attributes) == 11 and attributes[0] == device_number and attributes[7].isdigit() and \
            attributes[5] == 'C' and (attributes[6].find('R') != -1 or attributes[6].find('W') != -1):
                # 提取时间戳（以秒为单位）
                timestamp = float(attributes[3])  # blkparse中的时间戳
                elapsed_time = int(timestamp)  # 转换为整秒

                # 如果当前时间戳和上一个时间戳不同，创建新文件
                if elapsed_time != current_time:
                    current_time = elapsed_time
                    file_num = cnt * int(time) + elapsed_time
                    not_null_file.append(file_num)
                    # 创建新的文件
                    fp = await aiofiles.open(f"./data/test{file_num}.txt", "w")
                    fo = await aiofiles.open(f"./data/test{file_num}.bin", "wb")

                # 记录读取操作的信息
                if attributes[6].find('R') != -1:
                    await fp.write(output + '\n')
                
                # 记录写入操作的信息
                if attributes[6].find('W') != -1:
                    await fp.write(output + '\n')
                    # 读取数据
                    sector = int(attributes[7])  # 起始扇区
                    if attributes[8] == '+':
                        sector_number = int(attributes[9])  # 扇区数量
                    else:
                        sector_number = int(attributes[9]) - int(attributes[7])
                    await f.seek(sector * 512)
                    read = await f.read(512 * sector_number)
                    await fo.write(read)

                # 关闭文件在结束时
                if elapsed_time != current_time:  # 上一个时间戳改变时关闭文件
                    await fp.close()
                    await fo.close()

    now_time = import_time.time()
    print(f"write_task: 结束第{cnt}个异步任务，总耗时：", now_time - start_time)


# # 将收集到的数据写入文件
# async def write_task(cnt, blkparse_output):
#     now_time = import_time.time()
#     print(f"write_task:开启第{cnt}个异步任务，总耗时：", now_time - start_time)
#     PID = 0  # 进程号
#     sector = 0  # 起始扇区
# 
#     # 使用 aiofiles 打开数据文件和硬盘文件
#     async with aiofiles.open(f"./data/test{cnt}.txt", "w") as fp, \
#             aiofiles.open(f"./data/test{cnt}.bin", "wb") as fo, \
#             aiofiles.open(device, 'rb') as f:
# 
#         # 读取blkparse输出，按行划分
#         outputs = blkparse_output.split('\n')
# 
#         # 逐行对各字段进行拆分
#         for output in outputs:
#             attributes = output.split()
#             # 记录读取操作的信息
#             if len(attributes) == 11 and attributes[0] == device_number and attributes[7].isdigit() and attributes[
#                 5] == 'C' and attributes[6].find('R') != -1:
#                 # print(attributes)
#                 PID = int(attributes[4])  # 进程号
#                 sector = int(attributes[7])  # 起始扇区
#                 sector_number = 0
#                 await fp.write(output + '\n')
# 
#                 # 起始扇区 + 偏移量形式
#                 if attributes[8] == '+':
#                     sector_number = int(attributes[9])  # 扇区数量
#                 # 起始扇区 / 结束扇区形式
#                 else:
#                     sector_number = int(attributes[9]) - int(attributes[7])
# 
#             # 提取需计算熵值的扇区
#             if len(attributes) == 11 and attributes[0] == device_number and attributes[7].isdigit() and attributes[
#                 5] == 'C' and attributes[6].find('W') != -1:
#                 # print(attributes)
#                 PID = int(attributes[4])  # 进程号
#                 sector = int(attributes[7])  # 起始扇区
#                 sector_number = 0
#                 await fp.write(output + '\n')
# 
#                 # 起始扇区 + 偏移量形式
#                 if attributes[8] == '+':
#                     sector_number = int(attributes[9])  # 扇区数量
#                 # 起始扇区 / 结束扇区形式
#                 else:
#                     sector_number = int(attributes[9]) - int(attributes[7])
# 
#                 # 定位到起始扇区（起始页）
#                 await f.seek(sector * 512)
#                 read = await f.read(512 * sector_number)
#                 await fo.write(read)
# 
#     now_time = import_time.time()
#     print(f"write_task:结束第{cnt}个异步任务，总耗时：", now_time - start_time)


# io信息收集
async def collect():
    tasks = []  # 异步任务列表
    # 循环运行blktrace工具来捕获设备的IO操作
    for cnt in range(0, process_number):
        now_time = import_time.time()
        print(f"开启第{cnt}个循环，总耗时：", now_time - start_time)

        # 启动 blktrace作为异步子进程
        blktrace_process = await asyncio.create_subprocess_shell(
            f'blktrace -d {device} -w {time}',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        #blktrace_output = subprocess.run(f'blktrace -d {device} -w {time}', shell=True, check=True, capture_output=True,
        #                                 text=True)
        
        # 等待 blktrace 进程完成
        await blktrace_process.communicate()
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程得到blktrace_output，总耗时：", now_time - start_time)

        # 解析blktrace数据文件并获取输出
        blkparse_process = await asyncio.create_subprocess_shell(
            f'blkparse -i sda -d sda.blktrace.bin',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        #blkparse_output = subprocess.run(f'blkparse -i sda -d sda.blktrace.bin', shell=True, check=True,
        #                                 capture_output=True, text=True)

        # 异步读取 blkparse 输出
        stdout, stderr = await blkparse_process.communicate()
        if stderr:
            print(f"blkparse 错误: {stderr.decode().strip()}")
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程得到blkparse_output，总耗时：", now_time - start_time)
        
        # 开启异步任务
        tasks = asyncio.create_task(write_task(cnt, stdout.decode()))
        await asyncio.sleep(0)  # 让事件循环有机会执行已创建的任务
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程开启异步任务，总耗时：", now_time - start_time)

        # 将生成的sda等文件删除
        folder_path = os.getcwd()
        afiles = os.listdir(folder_path)
        for afile in afiles:
            if afile.startswith("sda"):
                file_path = os.path.join(folder_path, afile)
                os.remove(file_path)
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程完成，总耗时：", now_time - start_time)

    now_time = import_time.time()
    print("blktrace收集完成，总耗时：", now_time - start_time)
    # 等待所有任务完成
    await asyncio.gather(*[tasks])


if __name__ == "__main__":
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    else:
        delete_files(dirs)
        
    delete_files(dirs)

    write_count = [0, 0, 0]  # 记录最近3个进程中的写入次数（最后一项对应当前进程）
    read_sectors = []  # 用于传递上一秒的读取情况

    start_time = import_time.time()  # 记录循环总时间以判断数据空窗期长短

    # 循环开启blktrace收集数据
    asyncio.run(collect())
    
    print("非空数据文件序号：", not_null_file)
    for i in range(0, int(time) * process_number):
        if i not in not_null_file:
            fp = open(f"./data/test{i}.txt", "w")
            fo = open(f"./data/test{i}.bin", "wb")
            fp.close()
            fo.close()

    end_time = import_time.time()
    print("收集完成，总耗时：", end_time - start_time)
