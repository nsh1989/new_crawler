# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from clients.main_mng import MainMng

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    mng1: MainMng
    try:
        mng1 = MainMng()
        mng1.run()
    except Exception as e:
        print(e)

    # print("mng2 : %d" % len(mng2.get_size_consumers()))
    # print("mng1 : %d" % len(mng1.get_size_consumers()))

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
