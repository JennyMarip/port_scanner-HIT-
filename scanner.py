import sys
import threading

from PyQt5.QtCore import QThread
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5 import uic

import inspect

import ctypes


def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""

    tid = ctypes.c_long(tid)

    if not inspect.isclass(exctype):
        exctype = type(exctype)

    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))

    if res == 0:

        raise ValueError("invalid thread id")

    elif res != 1:

        # """if it returns a number greater than one, you're in trouble,

        # and you should call it again with exc=NULL to revert the effect"""

        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)

        raise SystemError("PyThreadState_SetAsyncExc failed")


def stop_thread(thread):
    _async_raise(thread.ident, SystemExit)
# 判断字符串是否是合法的ip地址
def is_valid_ip(s):
    lists = s.split('.')
    if len(lists) != 4:
        return 'no'
    for i in range(4):
        if not lists[i].isdigit():
            return 'no'
        if int(lists[i]) not in range(0, 256):
            return 'no'
    return 'yes'


def is_valid_ip_input(ip1, ip2):
    if is_valid_ip(ip1) == 'no' or is_valid_ip(ip2) == 'no':
        return False
    list1 = ip1.split('.')
    list2 = ip2.split('.')
    for i in range(4):
        if int(list2[i]) > int(list1[i]):
            break
        elif int(list2[i]) == int(list1[i]):
            continue
        else:
            return False
    return True


def is_valid_port_input(port1, port2):
    if not port1.isdigit() or not port2.isdigit():
        return False
    if not int(port1) in range(1, 65536) or not int(port2) in range(1, 65536):
        return False
    if int(port1) > int(port2):
        return False
    return True


def is_valid_num_input(thread_num):
    if not thread_num.isdigit():
        return False
    if int(thread_num) < 1:
        return False
    return True


def get_ip_addresses(ip1, ip2):
    ipx = []
    ipx.append(ip1)
    ipx.append(ip2)

    ip2num = lambda x: sum([256 ** i * int(j) for i, j in enumerate(x.split('.')[::-1])])

    num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])

    a = [num2ip(i) for i in range(ip2num(ipx[0]), ip2num(ipx[1]) + 1) if
         not ((i + 1) % 256 == 0 or (i) % 256 == 0)]
    return a


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.open_num = 0

    def init_ui(self):
        self.ui = uic.loadUi("./lab1.ui")
        self.ip1_line = self.ui.lineEdit
        self.ip2_line = self.ui.lineEdit_2
        self.port1_line = self.ui.lineEdit_3
        self.port2_line = self.ui.lineEdit_4
        self.num_line = self.ui.lineEdit_5
        self.start_btn = self.ui.pushButton
        self.end_btn = self.ui.pushButton_2
        self.browser = self.ui.textBrowser
        # 获取界面中的控件
        self.start_btn.clicked.connect(self.start_scan)  # 关联start_scan函数
        self.end_btn.clicked.connect(self.end_scan)  # 关联end_scan函数

    def start_scan(self):
        self.scan_thread = threading.Thread(target=self.run)
        self.scan_thread.start()

    def task(self, task_list):
        import socket
        for sock in task_list:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(0.05)
                s.connect((sock[0], sock[1]))
                self.browser.append('ip地址' + sock[0] + ',端口号:' + str(sock[1]) + ' 端口开启')
                self.open_num += 1
            except Exception as e:
                self.browser.append('ip地址' + sock[0] + ',端口号:' + str(sock[1]) + ' 端口关闭')
        self.lock.acquire()
        self.complete_num += 1
        self.lock.release()

    def run(self):
        self.browser.append('=====================================')
        ip1 = self.ip1_line.text()
        ip2 = self.ip2_line.text()
        port1 = self.port1_line.text()
        port2 = self.port2_line.text()
        thread_num = self.num_line.text()
        is_valid = True
        if not is_valid_ip_input(ip1, ip2):
            print(self.browser)
            self.browser.append('不是合法的ip地址范围设置!')
            is_valid = False
        if not is_valid_port_input(port1, port2):
            self.browser.append('不是合法的端口范围设置!')
            is_valid = False
        if not is_valid_num_input(thread_num):
            self.browser.append('不是合法的线程数设置!')
            is_valid = False
        if is_valid:
            # 输入全部有效的话开始进行扫描
            self.sock_combine = []  # ip + 端口号的组合
            port_list = []  # 端口号范围中的所有端口号
            for i in range(int(port1), int(port2) + 1):
                port_list.append(i)
            ip_list = get_ip_addresses(ip1, ip2)  # 给定ip地址范围的所有ip地址
            for ip in ip_list:
                for port in port_list:
                    self.sock_combine.append([ip, port])
            total_sock_num = len(ip_list) * len(port_list)
            task_num = []  # 每个线程被分配的任务数
            for i in range(int(thread_num)):
                task_num.append(0)
            temp_num = total_sock_num
            for i in range(int(thread_num)):
                temp = int(temp_num / (int(thread_num) - i))
                temp_num -= temp
                task_num[i] = temp
            index = 0
            self.thread_list = []
            self.complete_num = 0
            self.lock = threading.Lock()
            for i in range(int(thread_num)):
                task_list = self.sock_combine[index:index + task_num[i]]
                index += task_num[i]
                t = threading.Thread(target=self.task, args=(task_list,))
                self.thread_list.append(t)
            for t in self.thread_list:
                t.setDaemon(True)
                t.start()
            for t in self.thread_list:
                t.join()
            while True:
                if self.complete_num == int(thread_num):
                    self.browser.append('扫描结束, 共有 ' + str(self.open_num) + ' 个端口开放')
                    break

    def end_scan(self):
        stop_thread(self.scan_thread)
        for t in self.thread_list:
            stop_thread(t)
        # 结束扫描的操作
        self.browser.append('扫描被终止')

    def clear_gui(self):
        self.ip2_line.clear()
        self.ip1_line.clear()
        self.port1_line.clear()
        self.port2_line.clear()
        self.num_line.clear()
        self.browser.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = MyWindow()
    w.ui.show()
    app.exec()
