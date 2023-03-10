# 这是一个示例 Python 脚本。

# 按 Shift+F10 执行或将其替换为您的代码。
# 按 双击 Shift 在所有地方搜索类、文件、工具窗口、操作和设置。


def print_hi(name):
    # 在下面的代码行中使用断点来调试脚本。
    print(f'Hi, {name}')  # 按 Ctrl+F8 切换断点。
    print('1'+'2')


# 按间距中的绿色按钮以运行脚本。
if __name__ == '__main__':
    ip2ip_str = '192.168.1.250-192.168.2.5'

    ipx = ip2ip_str.split('-')

    ip2num = lambda x: sum([256 ** i * int(j) for i, j in enumerate(x.split('.')[::-1])])

    num2ip = lambda x: '.'.join([str(x // (256 ** i) % 256) for i in range(3, -1, -1)])

    a = [num2ip(i) for i in range(ip2num(ipx[0]), ip2num(ipx[1]) + 1) if
         not ((i + 1) % 256 == 0 or (i) % 256 == 0)]

    print(a)
    print('1' + '2')

# 访问 https://www.jetbrains.com/help/pycharm/ 获取 PyCharm 帮助
