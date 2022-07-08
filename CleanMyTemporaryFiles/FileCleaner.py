import os
import time
import json
from apscheduler.schedulers.background import BackgroundScheduler

LEAST_FILE_NUMBER = 0
CLEAN_RECORDS_FILENAME = '.file_to_clean'


def _determine_level(access_timetime, max_seconds):
    """
    check if file is overtime
    :param access_timetime: 文件的上一次的访问时间
    :return:  0 if day < MAX_FILE_EXIST_DAY else 1
    """
    seconds = round((time.time() - int(access_timetime)), 2)
    return 1 if seconds > max_seconds else 0


def _mark_file_wait_clean(file_dir, max_seconds):
    file_names = os.listdir(file_dir)
    # 获取文件最新的访问时间 os.stat(file_path) 计算文件的最新访问时间。
    files_with_stat = [(a, _determine_level(os.stat(a).st_atime, max_seconds)) for a in ["{}/{}".format(file_dir, file_name) for file_name in file_names]]
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
        # nothing to delete return
        return
    # 调用osascript脚本进行删除确认操作
    delete_file_dialog = 'display dialog "Going to delete over time files at ' + file_dir + ', Counts:' + str(LEAST_FILE_NUMBER) + \
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
            delete_success_notice = 'display notification "Delete files at:{} (Count:{}) Success"'.format(file_dir, str(success_delete_count))
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
            end tell""".format(file_dir, CLEAN_RECORDS_FILENAME)
        applescript.run(check_files)
        _notification(file_dir)


def _clean_files(file_dir, max_seconds):
    _mark_file_wait_clean(file_dir, max_seconds)
    _notification(file_dir)


def _run_scheduler(schedule, config):
    # 创建调度器
    file_dir = config['dir']
    max_seconds = config['max_seconds']
    schedule.add_job(id=file_dir, func=_clean_files, trigger='cron', hour="14", minute="30", args=[file_dir, max_seconds])


def _load_config(config_file_name):
    with open(config_file_name, 'r') as config_file:
        data = json.load(config_file)
        return data


if __name__ == '__main__':
    configs = _load_config(".file_cleaner")
    if configs:
        sche = BackgroundScheduler()
        sche.start()
        try:
            for work_dir_config in configs['work_spaces']:
                _run_scheduler(sche, work_dir_config)
            while True:
                time.sleep(60)
        except(KeyboardInterrupt, SystemExit):
            sche.shutdown()
