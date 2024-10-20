import subprocess
import time
import time as import_time
import os
import asyncio

dirs = "./data"  # 存放数据的文件夹路径
device = '/dev/sda'  # 要监控的设备
device_number = '8,0'  # 设备号
time = '1'  # 单个blktrace进程的检测时间（单位为秒）
process_number = 10  # 总进程数


# 将收集到的数据写入文件
async def write_task(cnt, blkparse_output):
    PID = 0  # 进程号
    sector = 0  # 起始扇区

    # 打开用于存储数据的文件并清空之前的数据
    fp = open(f"./data/test{cnt}.txt", "w")
    fo = open(f"./data/test{cnt}.bin", "wb")
    fp.truncate()
    fo.truncate()
    # 打开硬盘文件
    f = open(device, 'rb')

    # 读取blkparse输出，按行划分
    outputs = blkparse_output.stdout.split('\n')

    # 逐行对各字段进行拆分
    for output in outputs:
        attributes = output.split()
        # 记录读取操作的信息
        if len(attributes) == 11 and attributes[0] == device_number and attributes[7].isdigit() and attributes[
            5] == 'C' and attributes[6].find('R') != -1:
            # print(attributes)
            PID = int(attributes[4])  # 进程号
            sector = int(attributes[7])  # 起始扇区
            sector_number = 0
            fp.write(output + '\n')

            # 起始扇区 + 偏移量形式
            if attributes[8] == '+':
                sector_number = int(attributes[9])  # 扇区数量
            # 起始扇区 / 结束扇区形式
            else:
                sector_number = int(attributes[9]) - int(attributes[7])

        # 提取需计算熵值的扇区
        if len(attributes) == 11 and attributes[0] == device_number and attributes[7].isdigit() and attributes[
            5] == 'C' and attributes[6].find('W') != -1:
            # print(attributes)
            PID = int(attributes[4])  # 进程号
            sector = int(attributes[7])  # 起始扇区
            sector_number = 0
            fp.write(output + '\n')

            # 起始扇区 + 偏移量形式
            if attributes[8] == '+':
                sector_number = int(attributes[9])  # 扇区数量
            # 起始扇区 / 结束扇区形式
            else:
                sector_number = int(attributes[9]) - int(attributes[7])

            # 定位到起始扇区（起始页）
            f.seek(sector * 512)
            read = f.read(512 * sector_number)
            fo.write(read)

    fp.close()
    fo.close()
    f.close()


# io信息收集
async def collect():
    tasks = []  # 异步任务列表
    # 循环运行blktrace工具来捕获设备的IO操作
    for cnt in range(0, process_number):
        now_time = import_time.time()
        print(f"开启第{cnt}个循环，总耗时：", now_time - start_time)
        # 启动blktrace
        blktrace_output = subprocess.run(f'blktrace -d {device} -w {time}', shell=True, check=True, capture_output=True,
                                         text=True)
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程得到blktrace_output，总耗时：", now_time - start_time)

        # 解析blktrace数据文件并获取输出
        blkparse_output = subprocess.run(f'blkparse -i sda -d sda.blktrace.bin', shell=True, check=True,
                                         capture_output=True, text=True)
        now_time = import_time.time()
        print(f"第{cnt}个blktrace进程得到blkparse_output，总耗时：", now_time - start_time)

        # 开启异步任务
        task = asyncio.create_task(write_task(cnt, blkparse_output))
        tasks.append(task)
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
    await asyncio.gather(*tasks)


if __name__ == "__main__":
    if not os.path.exists(dirs):
        os.makedirs(dirs)

    write_count = [0, 0, 0]  # 记录最近3个进程中的写入次数（最后一项对应当前进程）
    read_sectors = []  # 用于传递上一秒的读取情况

    start_time = import_time.time()  # 记录循环总时间以判断数据空窗期长短

    # 循环开启blktrace收集数据
    asyncio.run(collect())

    end_time = import_time.time()
    print("收集完成，总耗时：", end_time - start_time)