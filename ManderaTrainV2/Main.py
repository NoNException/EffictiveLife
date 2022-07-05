import random
import time

from prompt_toolkit import prompt, print_formatted_text


# 获取一个词
def get_center_world():
    file = open("words.csv", 'r')
    lines = file.readlines()
    random_line = random.randint(0, len(lines) - 1)
    contents = lines[random_line].split(",")
    file.close()
    return int(contents[0]), contents[1], int(contents[2])


# 保存结果
def save_worlds(result_words: list, type_word: int, main_word_index):
    file = open("words.csv", 'r')
    contents = file.readlines()
    contents_length = len(contents)
    file.close()
    file = open("words.csv", "a")
    for (index_, new_word) in enumerate(result_words):
        file.write("\n{},{},{},{}".format(contents_length + index_, new_word, type_word, main_word_index))
    file.close()


def records_log(record_word, costs):
    file = open("./records.csv", "a")
    file.write("\n{},{}s".format(record_word, costs))
    file.close()


if __name__ == '__main__':
    (index, word, attrs) = get_center_world()
    words_dic = ["具象", "抽象"]
    attr_char = words_dic[attrs]
    words_dic.remove(attr_char)
    print_formatted_text("中心词:{}, 词性:{}".format(word, attr_char))
    start_time = time.time()
    result = []
    for i in range(0, 8):
        worlds = prompt("第{}个{}词:".format(i + 1, words_dic[0]))
        result.append(worlds)
    time_costs = round(time.time() - start_time, 2)
    print("耗时:{}s".format(time_costs, 2))
    print(result)
    save_worlds(result, abs(attrs - 1), index)
    records_log(word, time_costs)
