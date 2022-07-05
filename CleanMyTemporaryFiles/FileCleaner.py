# 文件更显分拣程序，将文件按照更显时间分类
import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

LEAST_FILE_NUMBER = 0
CLEAN_RECORDS_FILENAME = '.file_to_clean'


def _determine_level(access_timetime):
    """
    根据文件的上一次的访问时间，将文件进行分类
    :param access_timetime: 文件的上一次的访问时间
    :return: 0->3天内; 1->3-7天内; 2=>7~15天内; 4=>大于15天。
    """
    days = round((time.time() - int(access_timetime)) / 86400, 2)
    day_map = {0: [0, 3], 1: [3, 7], 2: [7, 15]}
    for (k, v) in day_map.items():
        if v[0] <= days < v[1]:
            return k
    return 3


def _mark_file_wait_clean(file_dir):
    file_names = os.listdir(file_dir)
    # 获取文件最新的访问时间 os.stat(file_path) 计算文件的最新访问时间。
    files_with_stat = [(a, _determine_level(os.stat(a).st_atime)) for a in ["{}/{}".format(file_dir, file_name) for file_name in file_names]]
    files_wait_clean = [file for file in files_with_stat if file[1] == 3 and file[0] not in [CLEAN_RECORDS_FILENAME]]
    # 将等级4的文件的名称写入.files_to_clean文件内，每次都直接覆盖
    with open("{}/{}".format(file_dir, CLEAN_RECORDS_FILENAME), 'w') as clean_file:
        for file in files_wait_clean:
            clean_file.write("{}\n".format(file[0]))
    global LEAST_FILE_NUMBER
    LEAST_FILE_NUMBER = len(files_wait_clean)


# 提示指定文件夹下的文件需要被删除了
def _notification_(file_dir):
    #  调用osascript脚本进行删除确认操作
    delete_file_dialog = 'display dialog "即将删除超过两周的文件,文件总数' + str(LEAST_FILE_NUMBER) + \
                         '" buttons {"Don\'t Continue", "Continue","Check Files"} default button {"Check Files"} cancel button {"Don\'t Continue"}'
    import applescript
    res = applescript.run(delete_file_dialog)
    # 如果脚本运行失败，发送通知
    if res.code:
        error_running_osascript = 'display notification "Error happened when delete over time files, error message:' + res.err + '"'
        applescript.run(error_running_osascript)
        return
    # 脚本运行成功，并且确定删除文件
    if res.out == 'button returned:Continue':
        with open("{}/{}".format(file_dir, CLEAN_RECORDS_FILENAME), 'r') as clean_file:
            file_names = clean_file.readlines()
            for file in file_names:
                os.remove("{}/{}".format(work_dir, file))
    if res.out == 'button returned:Check Files':
        # 检查文件，打开即将删除的文件列表
        check_files = \
            """
tell application "iTerm"
	activate
	create window with default profile
	tell first session of current tab of current window
        write text "cat {}/{}"
    end tell
end tell""".format(work_dir, CLEAN_RECORDS_FILENAME)
        res = applescript.run(check_files)


def _run_scheduler(file_dir):
    # 创建调度器
    schedule = BackgroundScheduler()
    schedule.start()
    # 每天0点开始统计过期的文件
    schedule.add_job(_mark_file_wait_clean, trigger='cron', hour=0, minute=0, second=0, args=[file_dir])
    # 每2个星期的星期1早上5点开始通知文件删除
    # schedule.add_job(_notification_, trigger='cron', hour=0, minute=0, seconds=0, args=[file_dir])


if __name__ == '__main__':
    work_dir = '/Users/zongzi/Desktop/temporary'
    _run_scheduler(work_dir)
    # _mark_file_wait_clean(work_dir)
    # _notification_(work_dir)
