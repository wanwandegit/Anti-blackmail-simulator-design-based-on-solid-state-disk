import subprocess
import multiprocessing
import time
import psutil

whole_command = "python3 processtest.py"  # 程序运行指令


def run_program(command):
    # 启动程序并获取主进程
    process = subprocess.Popen(command)
    print(f"主进程 PID: {process.pid}")
    
    # 若进程未结束，则循环检测其子进程情况
    all_child = []
    while process.poll() is None:
        # 获取子进程
        parent = psutil.Process(process.pid)
        child_processes = parent.children(recursive=True)
        print(f"子进程PIDs: {child_processes}")
        for child in child_processes:
            if child not in all_child:
                all_child.append(child)
        time.sleep(0.5)

    # 等待主进程结束
    process.wait()
    print("Finished!")
    print(f"主进程 PID: {process.pid}")
    print(f"子进程PIDs: {all_child}")


# 运行命令并捕获输出
def run_command(command):
    result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
    return result


if __name__ == "__main__":
    run_program(whole_command)