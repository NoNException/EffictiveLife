# all snippets tool


from pynput import keyboard
from pynput.keyboard import Key, Controller

result = []
using_keyboard = Controller()
replace_status = False


def _check_snippets():
    # 检查是否存在有可以匹配的列表
    match_str = "11"
    print("<<{}>>".format("".join(result)))
    if len(result) > 0 and "".join(result) == match_str:
        return len(match_str), "22\n"
    return None


def on_press(key):
    global result, replace_status

    if not hasattr(key, 'char') or not key.char or not key.char.strip():
        # 如果不是有值的按键，那么清空列表
        result = []
        return
    result.append(key.char)
    snippets = _check_snippets()
    if snippets:
        # 回退两格
        replace_status = True
        back_position = snippets[0]
        for i in range(back_position):
            using_keyboard.press(Key.backspace)
            using_keyboard.release(Key.backspace)
        for char in snippets[1]:
            using_keyboard.press(char)
            using_keyboard.release(char)
        result = []
        replace_status = False


if __name__ == "__main__":
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    while True:
        pass
