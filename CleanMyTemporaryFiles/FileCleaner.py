import os
import time
from apscheduler.schedulers.background import BackgroundScheduler

LEAST_FILE_NUMBER = 0
CLEAN_RECORDS_FILENAME = '.file_to_clean'
MAX_FILE_EXIST_SECONDS = 7 * 24 * 60 * 60


def _determine_level(access_timetime):
    """
    根据文件的上一次的访问时间，将文件进行分类
    :param access_timetime: 文件的上一次的访问时间
    :return:  0 if day < MAX_FILE_EXIST_DAY else 1
    """
    seconds = round((time.time() - int(access_timetime)), 2)
    return 1 if seconds > MAX_FILE_EXIST_SECONDS else 0


def _mark_file_wait_clean(file_dir):
    file_names = os.listdir(file_dir)
    # 获取文件最新的访问时间 os.stat(file_path) 计算文件的最新访问时间。
    files_with_stat = [(a, _determine_level(os.stat(a).st_atime)) for a in ["{}/{}".format(file_dir, file_name) for file_name in file_names]]
    files_wait_clean = [file for file in files_with_stat if file[1]]
    # 将等级4的文件的名称写入.files_to_clean文件内，每次都直接覆盖
    with open("{}/{}".format(file_dir, CLEAN_RECORDS_FILENAME), 'w') as clean_file:
        for file in files_wait_clean:
            clean_file.write("{}\n".format(file[0]))
    global LEAST_FILE_NUMBER
    LEAST_FILE_NUMBER = len(files_wait_clean)


# 提示指定文件夹下的文件需要被删除了
def _notification(file_dir):
    # 如果没有文件超过最大时间，则不需要进行删除
    import applescript
    if LEAST_FILE_NUMBER == 0:
        do_noting_dialog = """display dialog "No files needed to delete，Good Luck." buttons {"Fine"} default button {"Fine"} """
        applescript.run(do_noting_dialog)
        return
    # 调用osascript脚本进行删除确认操作
    delete_file_dialog = 'display dialog "Going to delete over time files, Counts:' + str(LEAST_FILE_NUMBER) + \
                         '" buttons {"Don\'t Continue", "Continue","Check Files"} default button {"Check Files"} cancel button {"Don\'t Continue"}'
    res = applescript.run(delete_file_dialog)
    # 如果脚本运行失败，发送通知
    if res.code:
        error_running_osascript = 'display notification "Error happened when delete over time files, error message:{}"'.format(res.err)
        applescript.run(error_running_osascript)
        return
    # 脚本运行成功，并且确定删除文件
    if res.out == 'button returned:Continue':
        with open("{}/{}".format(file_dir, CLEAN_RECORDS_FILENAME), 'r') as clean_file:
            file_names = clean_file.readlines()
            success_delete_count = 0
            for file in file_names:
                move_file_to_trash = """
                tell application "Finder"
                    set delete_folder to POSIX file "{}"
                    move delete_folder to the trash
                end tell
                """.format(file.strip())
                delete_res = applescript.run(move_file_to_trash)
                if delete_res.code:
                    # 提示删除文件失败
                    alter_delete_notice = 'display notification "Error:{} happened when delete file:{}" please have a check'.format(delete_res.err, file.strip())
                    applescript.run(alter_delete_notice)
                    continue
                else:
                    success_delete_count += 1
            delete_success_notice = 'display notification "Delete files (Count:{}) Success"'.format(str(success_delete_count))
            applescript.run(delete_success_notice)
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
        applescript.run(check_files)
        _notification(file_dir)


def _clean_files(file_dir):
    _mark_file_wait_clean(file_dir)
    _notification(file_dir)


def _run_scheduler(file_dir):
    # 创建调度器
    schedule = BackgroundScheduler()
    schedule.start()
    # 每天早上10点开始统计过期的文件，并提示清理
    schedule.add_job(_clean_files, trigger='cron', hour="10", minute="30", args=[file_dir])
    # schedule.add_job(_clean_files, trigger='cron', second="*/10", args=[file_dir])
    return schedule


if __name__ == '__main__':
    work_dir = '/Users/zongzi/Desktop/temporary'
    sche = _run_scheduler(work_dir)
    try:
        while True:
            time.sleep(2)
    except(KeyboardInterrupt, SystemExit):
        sche.shutdown()
