import multiprocessing
import threading

global_list = []


def modify_in_thread():
    global_list.append("Элемент добавит ПОТОК")


def modify_in_process():
    global_list.append("Элемент добавит ПРОЦЕСС")


if __name__ == "__main__":
    print("--- ТЕСТ 1: Работа с общей памятью в ПОТОКАХ ---")
    global_list.clear()
    t = threading.Thread(target=modify_in_thread)
    t.start()
    t.join()
    print(f"Список в родителе после завершения потока: {global_list}\n")

    print("--- ТЕСТ 2: Изоляция памяти в ПРОЦЕССАХ ---")
    global_list.clear()
    p = multiprocessing.Process(target=modify_in_process)
    p.start()
    p.join()
    print(f"Список в родителе после завершения процесса: {global_list}\n")