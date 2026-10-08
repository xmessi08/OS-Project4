import concurrent.futures
import multiprocessing
import os
import statistics
import threading
import time
import urllib.request

FILE_NAME = "numbers.txt"
NUM_COUNT = 10_000_000


def generate_numbers_file():
    if not os.path.exists(FILE_NAME) or os.path.getsize(FILE_NAME) < 1000000:
        print(f"Генерация {FILE_NAME} ({NUM_COUNT} чисел)...")
        with open(FILE_NAME, "w") as f:
            for i in range(1, NUM_COUNT + 1):
                f.write(f"{i}\n")
        print("Файл успешно создан.")


URLS = ["https://httpbin.org/delay/0.5"] * 20


def load_data():
    with open(FILE_NAME, "r") as f:
        return [int(line) for line in f if line.strip()]


def cpu_single_thread(data):
    return sum(data)


def cpu_multi_threads(data, num_threads=4):
    chunk_size = len(data) // num_threads
    chunks = [
        data[i * chunk_size : (i + 1) * chunk_size] for i in range(num_threads)
    ]
    results = [0] * num_threads

    def worker(idx, chunk):
        results[idx] = sum(chunk)

    threads = []
    for i in range(num_threads):
        t = threading.Thread(target=worker, args=(i, chunks[i]))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    return sum(results)


def _sum_chunk(chunk):
    return sum(chunk)


def cpu_multi_processes(data, num_processes=4):
    chunk_size = len(data) // num_processes
    chunks = [
        data[i * chunk_size : (i + 1) * chunk_size]
        for i in range(num_processes)
    ]

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(_sum_chunk, chunks)
    return sum(results)


def fetch_url(url):
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            return len(response.read())
    except Exception:
        return 0


def io_sequential(urls):
    return [fetch_url(u) for u in urls]


def io_thread_pool(urls, max_workers=4):
    with concurrent.futures.ThreadPoolExecutor(
        max_workers=max_workers
    ) as executor:
        return list(executor.map(fetch_url, urls))


def io_process_pool(urls, max_workers=4):
    with concurrent.futures.ProcessPoolExecutor(
        max_workers=max_workers
    ) as executor:
        return list(executor.map(fetch_url, urls))


def run_benchmark(func, *args, runs=3):
    times = []
    for _ in range(runs):
        start = time.perf_counter()
        func(*args)
        times.append(time.perf_counter() - start)
    return statistics.median(times)


if __name__ == "__main__":
    generate_numbers_file()
    print("Загрузка данных в RAM...")
    data = load_data()
    print("Данные загружены. Начинаем замеры...\n")

    t_cpu_single = run_benchmark(cpu_single_thread, data)
    t_cpu_threads = run_benchmark(cpu_multi_threads, data)
    t_cpu_procs = run_benchmark(cpu_multi_processes, data)

    t_io_seq = run_benchmark(io_sequential, URLS)
    t_io_threads = run_benchmark(io_thread_pool, URLS)
    t_io_procs = run_benchmark(io_process_pool, URLS)

    nproc = os.cpu_count()
    print("=" * 70)
    print(f" РЕЗУЛЬТАТЫ ЭКСПЕРИМЕНТА (Число ядер процессора nproc: {nproc})")
    print("=" * 70)
    print(f"{'Тип задачи':<18} | {'Метод выполнения':<26} | {'Медиана (сек)':<12}")
    print("-" * 70)
    print(f"{'CPU-bound':<18} | {'1 поток (Single)':<26} | {t_cpu_single:.4f}")
    print(f"{'(Сумма 10 млн)':<18} | {'4 потока (threading)':<26} | {t_cpu_threads:.4f}")
    print(f"{'':<18} | {'4 процесса (multiprocessing)':<26} | {t_cpu_procs:.4f}")
    print("-" * 70)
    print(f"{'I/O-bound':<18} | {'Последовательно':<26} | {t_io_seq:.4f}")
    print(f"{'(20 URL)':<18} | {'ThreadPoolExecutor (4)':<26} | {t_io_threads:.4f}")
    print(f"{'':<18} | {'ProcessPoolExecutor (4)':<26} | {t_io_procs:.4f}")
    print("=" * 70)