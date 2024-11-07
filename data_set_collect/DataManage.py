import collections
import os

dirs = "./data"  # 存放数据的文件夹路径
process_time = 10


# 按页计算数据的熵值（实际上是熵值乘2的N次方，此处页面大小取4096b）
def entropy(data):
    e = 0
    # 使用collections.Counter计算每个元素的出现次数
    counter = collections.Counter(data)
    n = 12  # 页面字节数4096 = 2^12
    for count in counter.values():
        # 计算概率
        c_x = count
        # 计算熵值
        e += c_x * (n - c_x.bit_length() + 1)
    return e


if __name__ == "__main__":
    # 清空最终收集熵值的数据文件
    f = open("data.txt", "w")
    f.truncate()
    f.close()
    # 数据文件夹路径
    folder_path = './data'
    # 获取文件夹内所有项的列表
    items = os.listdir(folder_path)
    sectors = []  # 定义空列表存放已进行了熵值计算的扇区以避免重复计算

    # 从第三对文件开始遍历所有数据文件
    for file_cnt in range(2, int(len(items) / 2)):
        # 打开用于存储数据的文件
        fp = open(f"{dirs}/test{file_cnt}.txt", "r")
        fo = open(f"{dirs}/test{file_cnt}.bin", "rb")
        fn = open(f"{dirs}/test{file_cnt - 1}.txt", "r")
        fb = open(f"{dirs}/test{file_cnt - 2}.txt", "r")

        # 打开最终收集熵值的数据文件，并使用追加模式写入
        f = open("data.txt", "a")

        # 按行划分此前收集的数据文件
        outputs = fp.readlines()
        old_outputs = fn.readlines()
        oldest_outputs = fb.readlines()

        # 统计新进程的数据时，更新列表（不同进程间可以出现重复扇区）
        if file_cnt % process_time == 0:
            sectors = []

        cnt = 0  # 已读取的扇区数
        entropys_sum = 0  # 当前操作对应页面熵之和
        page_count = 0  # 当前操作对应页面数
        s = 0  # 用于存储当前页面熵之和
        sector_number = 0  # 扇区数量
        attributes = []  # 用于存储各字段
        sector = 0  # 起始扇区
        flag = 0  # 内部循环的标记
        # print(len(outputs))

        # 倒序（检测覆写情况）逐行对各字段进行拆分
        for output in reversed(outputs):
            # 初始化
            OWIO = 0  # 时间片内写入强度
            OWST = 0  # 时间片写入强度之比
            WAR = 0  # 是否读后写
            # CW = 0  # 写入覆盖率
            APE = 0  # 平均页面熵

            attributes = output.split()
            if attributes[6].find('R') != -1:
                continue

            # print(attributes)
            sector = int(attributes[7])  # 起始扇区
            entropys_sum = 0  # 页面熵之和
            page_count = 0  # 页面总数
            s = 0  # 当前页面熵
            sector_number = 0  # 扇区数量
            old_OWIO = 0  # 上上一秒对应写入强度，用于计算OWST
            # 起始扇区 + 偏移量形式
            if attributes[8] == '+':
                sector_number = int(attributes[9])  # 扇区数量
            # 起始扇区 / 结束扇区形式
            else:
                sector_number = int(attributes[9]) - int(attributes[7])

            # 结合数据文件{cnt - 2}计算上上秒写入强度
            for oldest_output in oldest_outputs:
                oldest_attributes = oldest_output.split()
                if oldest_attributes[3] >= attributes[3] and oldest_attributes[6].find('W') != -1:
                    old_OWIO += 1

            sector_list = [0] * sector_number  # 记录写入页面的读取情况，0表示未读取，1表示已读取
            # 结合数据文件{cnt - 1}计算各项指标
            for old_output in old_outputs:
                old_attributes = old_output.split()
                if old_attributes[3] >= attributes[3]:
                    old_sector = int(old_attributes[7])  # 起始扇区
                    # 起始扇区 + 偏移量形式
                    if old_attributes[8] == '+':
                        old_sector_number = int(old_attributes[9])  # 扇区数量
                    # 起始扇区 / 结束扇区形式
                    else:
                        old_sector_number = int(old_attributes[9]) - int(old_attributes[7])
                    # 判断读后写
                    if old_attributes[6].find('R') != -1:
                        if old_sector <= sector and old_sector + old_sector_number >= sector + sector_number:
                            WAR = 1
                        elif old_sector > sector and old_sector + old_sector_number < sector + sector_number:
                            sector_list[old_sector - sector:old_sector + old_sector_number - sector] = [
                                                                                                           1] * old_sector_number
                        elif old_sector <= sector and sector < old_sector + old_sector_number < sector + sector_number:
                            sector_list[:old_sector + old_sector_number - sector] = [1] * (
                                    old_sector + old_sector_number - sector)
                        elif old_sector + old_sector_number > sector + sector_number and sector < old_sector < sector + sector_number:
                            sector_list[old_sector - sector:] = [1] * (sector + sector_number - old_sector)
                    # 计算时间片写入强度
                    if old_attributes[6].find('W') != -1:
                        OWIO += 1
                else:
                    if old_attributes[6].find('W') != -1:
                        old_OWIO += 1

            # 结合数据文件{cnt}计算各项指标
            for new_output in outputs:
                new_attributes = new_output.split()
                if new_attributes[3] < attributes[3]:
                    new_sector = int(new_attributes[7])  # 起始扇区
                    # 起始扇区 + 偏移量形式
                    if new_attributes[8] == '+':
                        new_sector_number = int(new_attributes[9])  # 扇区数量
                    # 起始扇区 / 结束扇区形式
                    else:
                        new_sector_number = int(new_attributes[9]) - int(new_attributes[7])
                    # 判断读后写
                    if new_attributes[6].find('R') != -1:
                        if new_sector <= sector and new_sector + new_sector_number >= sector + sector_number:
                            WAR = 1
                        elif new_sector > sector and new_sector + new_sector_number < sector + sector_number:
                            sector_list[new_sector - sector:new_sector + new_sector_number - sector] = [
                                                                                                           1] * new_sector_number
                        elif new_sector <= sector and sector < new_sector + new_sector_number < sector + sector_number:
                            sector_list[:new_sector + new_sector_number - sector] = [1] * (
                                    new_sector + new_sector_number - sector)
                        elif new_sector + new_sector_number > sector + sector_number and sector < new_sector < sector + sector_number:
                            sector_list[new_sector - sector:] = [1] * (sector + sector_number - new_sector)
                    # 计算时间片写入强度
                    if new_attributes[6].find('W') != -1:
                        OWIO += 1

            if WAR != 1 and 0 not in sector_list:
                WAR = 1

            if old_OWIO != 0:
                OWST = OWIO / old_OWIO
            else:
                OWST = -1.0

            # 检查是否出现了覆写情况，即无法获取对应页面数据
            flag = 0
            for [begin, end] in sectors:
                if sector >= end or sector + sector_number <= begin:
                    continue
                flag = 1
                break
            sectors.append([sector, sector + sector_number])

            cnt = cnt + sector_number
            # 计算熵值
            if flag == 0:
                fo.seek(0 - cnt * 512, 2)
                # print("loc:", fo.tell())
                for i in range(0, sector_number, 8):
                    read = fo.read(4096)
                    s = entropy(read)
                    # print("s = ", s)
                    entropys_sum += s
                    page_count += 1
                    # print("entropys_sum / page_count = ", entropys_sum / page_count)
                APE = entropys_sum / page_count
            else:
                APE = -1.0

            # 更改时间戳
            m = ''
            index = 0
            for attribute in attributes:
                if index == 3:
                    m += str(float(attribute) % 1 + file_cnt) + '\t'
                else:
                    m += attribute + '\t'
                index += 1

            # 写入各项指标（用-1.0表示无法获取或计算的数据）
            f.write(m + str(OWIO) + '\t' + str(OWST) + '\t' + str(WAR) + '\t' + str(APE) + '\n')

        print(f'Data{file_cnt} finished!')
        fp.close()
        fo.close()
        f.close()