# all snippets tool
import os
from pynput import keyboard
from pynput.keyboard import Key, Controller
import applescript

using_keyboard = Controller()
replace_status = False
all_snippets = []
input_stack = []
candidate_snippets = []


class Snippet(object):
    def __init__(self, name, content, description):
        self.name = name
        self.content = content
        self.description = description

    def match(self, match_str):
        return match_str == self.name

    def match_fuzzy(self, match_str):
        fuzzy_test = match_str in self.name
        prefix_test = "".join(self.name[0:len(match_str)]) == match_str
        return fuzzy_test and prefix_test


def _match_snippets():
    # 根据输入的字符查找候选snippet
    global candidate_snippets, input_stack
    search_range = candidate_snippets if len(candidate_snippets) > 0 else all_snippets
    search_str = "".join(input_stack)

    candidate_snippets = [s for s in search_range if s.match_fuzzy(search_str)]
    # 只匹配到一个代码片段，那么直接返回
    if len(candidate_snippets) == 0:
        input_stack = [search_str[-1]]
    if len(candidate_snippets) == 1 and candidate_snippets[0].name == search_str:
        input_stack = []
        return candidate_snippets[0]
    return None


def _get_focused_window():
    script_dir = os.path.dirname(__file__)
    res = applescript.run(os.path.join(script_dir, 'focus_window.scpt'))

    return res.out


def on_press(key):
    global replace_status, input_stack
    if replace_status or not hasattr(key, 'char') or not key.char or not key.char.strip():
        # 如果不是有值的按键，那么清空列表
        return
    input_stack.append(key.char)
    snippet = _match_snippets()
    if snippet:
        # 进入替换模式，暂时中止替换时输入的影响
        replace_status = True
        back_position = len(snippet.name)
        for i in range(back_position):
            using_keyboard.press(Key.backspace)
            using_keyboard.release(Key.backspace)
        using_keyboard.type(snippet.content)
        replace_status = False


if __name__ == "__main__":
    test_snippet = Snippet(name="test", content="i'm the best man.", description="test")
    test_snippet_1 = Snippet(name="11", content="i'm the best man_11.", description="test")
    all_snippets.append(test_snippet)
    all_snippets.append(test_snippet_1)
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while True:
        pass
