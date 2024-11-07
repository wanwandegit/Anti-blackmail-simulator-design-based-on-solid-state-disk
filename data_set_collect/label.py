blackmail_PID = []  # 勒索程序对应PID，根据PIDtest的输出进行设置


if __name__ == "__main__":
    f = open("data.txt", "r")
    fp = open("data_with_label.txt", "w")
    fp.truncate()
    outputs = f.readlines()
    for output in outputs:
        attributes = output.split()
        if attributes[4] in blackmail_PID:
            fp.write(output[:-1] + '\t1\n')
        else:
            fp.write(output[:-1] + '\t0\n')
    print("Finished!")
    f.close()
    fp.close()