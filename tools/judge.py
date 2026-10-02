#!/usr/bin/env python3
"""Сборка решений из tasks/<задача>.cpp и прогон тестов из tests/<задача>.

Запускается из Makefile, но можно и напрямую:
    python3 tools/judge.py a b c
    python3 tools/judge.py --build-only a
"""

import argparse
import os
import shlex
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TASKS_DIR = ROOT / "tasks"
TESTS_DIR = ROOT / "tests"

TASKS = {
    "a": "Первые треки",
    "b": "Обвал чартов",
    "c": "Поп vs хип-хоп",
    "d": "Хаос в плейлисте",
    "e": "Срез чарта",
    "f": "One Server to Rule Them All",
    "g": "One slot, or one opportunity...",
    "h": "Хедлайнеры",
    "i": "Пересортировка судного дня",
}

# Лимиты из условия: время в секундах и память в мегабайтах.
TIME_LIMIT = 1.0
MEMORY_LIMIT = {task: 256 for task in TASKS}
MEMORY_LIMIT["b"] = 64

# Через сколько секунд зависшее решение принудительно останавливается.
HARD_TIMEOUT = 10.0

USE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None


def paint(text, code):
    return f"\033[{code}m{text}\033[0m" if USE_COLOR else text


STATUS_COLOR = {"OK": "32", "WA": "31", "RE": "35", "TL": "33", "ML": "33", "CE": "31"}


def status_label(status):
    return paint(status, "1;" + STATUS_COLOR[status])


def shorten(text, limit=300):
    text = text.strip()
    if len(text) <= limit:
        return text
    return text[:limit] + f" ... (ещё {len(text) - limit} символов)"


# ---------------------------------------------------------------- сборка ---


def build(task, build_dir, cxx, cxxflags):
    """Компилирует tasks/<task>.cpp. Возвращает (бинарник, ошибка)."""
    source = TASKS_DIR / f"{task}.cpp"
    binary = build_dir / task
    stamp = build_dir / f"{task}.cmd"
    command = [
        *shlex.split(cxx), *shlex.split(cxxflags),
        os.path.relpath(source, ROOT), "-o", os.path.relpath(binary, ROOT),
    ]
    command_line = shlex.join(command)

    up_to_date = (
        binary.exists()
        and stamp.exists()
        and binary.stat().st_mtime >= source.stat().st_mtime
        and stamp.read_text() == command_line
    )
    if up_to_date:
        return binary, None

    build_dir.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
    if result.returncode != 0:
        return None, result.stderr or result.stdout
    stamp.write_text(command_line)
    if result.stderr.strip():
        print(result.stderr.rstrip(), file=sys.stderr)
    return binary, None


# ---------------------------------------------------------------- запуск ---


class Run:
    def __init__(self, stdout, stderr, exit_code, seconds, memory_mb, timed_out):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.seconds = seconds
        self.memory_mb = memory_mb
        self.timed_out = timed_out


def execute(binary, input_path):
    """Запускает бинарник на одном тесте, замеряет время и пиковую память."""
    with open(input_path, "rb") as stdin, tempfile.TemporaryFile() as stdout, \
            tempfile.TemporaryFile() as stderr:
        started = time.perf_counter()
        process = subprocess.Popen([str(binary)], stdin=stdin, stdout=stdout, stderr=stderr)
        timed_out = False
        memory_mb = None

        if hasattr(os, "wait4"):
            # wait4 отдаёт ресурсы конкретного процесса: процессорное время и пик памяти.
            while True:
                pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                if pid:
                    break
                if time.perf_counter() - started > HARD_TIMEOUT:
                    process.kill()
                    _, status, usage = os.wait4(process.pid, 0)
                    timed_out = True
                    break
                time.sleep(0.001)
            process.returncode = os.waitstatus_to_exitcode(status)
            seconds = usage.ru_utime + usage.ru_stime
            # ru_maxrss: на macOS в байтах, на Linux в килобайтах.
            rss_bytes = usage.ru_maxrss if sys.platform == "darwin" else usage.ru_maxrss * 1024
            memory_mb = rss_bytes / 1024 / 1024
        else:
            try:
                process.wait(timeout=HARD_TIMEOUT)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
                timed_out = True
            seconds = time.perf_counter() - started

        stdout.seek(0)
        stderr.seek(0)
        return Run(
            stdout.read().decode(errors="replace"),
            stderr.read().decode(errors="replace"),
            process.returncode,
            seconds,
            memory_mb,
            timed_out,
        )


def describe_exit(code):
    if code < 0:
        try:
            return f"программа упала: {signal.Signals(-code).name}"
        except ValueError:
            return f"программа упала: сигнал {-code}"
    return f"код возврата {code}"


# --------------------------------------------------------------- чекеры ---


def check_tokens(input_text, expected, actual):
    """Сравнение ответа по словам: лишние пробелы и переводы строк не важны."""
    if expected.split() == actual.split():
        return None
    return f"ожидалось: {shorten(expected)}\nполучено:  {shorten(actual) or '<пусто>'}"


def check_headliners(input_text, expected, actual):
    """Задача H: подходит любой минимальный набор хедлайнеров."""
    numbers = list(map(int, input_text.split()))
    n = numbers[0]
    points = [(numbers[1 + 2 * i], numbers[2 + 2 * i]) for i in range(n)]

    # Точки, которые никто не перекрывает строго: правая верхняя «лесенка».
    order = sorted(set(points), key=lambda p: (-p[0], -p[1]))
    frontier = set()
    best_y = None
    for x, y in order:
        if best_y is None or y > best_y:
            frontier.add((x, y))
            best_y = y

    tokens = actual.split()
    try:
        values = list(map(int, tokens))
    except ValueError:
        return f"в выводе не только числа: {shorten(actual)}"
    if not values:
        return "пустой вывод"
    count, chosen = values[0], values[1:]
    if count != len(frontier):
        return f"размер набора {count}, а минимальный размер {len(frontier)}"
    if len(chosen) != count:
        return f"объявлено {count} номеров, выведено {len(chosen)}"
    covered = set()
    for index in chosen:
        if not 1 <= index <= n:
            return f"номер {index} вне диапазона 1..{n}"
        point = points[index - 1]
        if point not in frontier:
            return f"трек {index} {point} перекрывается другим треком, он лишний"
        if point in covered:
            return f"трек {index} {point} дублирует уже выбранный"
        covered.add(point)
    return None


CHECKERS = {"h": check_headliners}


# ---------------------------------------------------------------- прогон ---


def judge_task(task, binary, limits):
    tests = sorted(
        (TESTS_DIR / task).glob("*.in"),
        key=lambda p: (len(p.stem), p.stem),
    )
    checker = CHECKERS.get(task, check_tokens)
    passed = 0
    verdicts = []

    for input_path in tests:
        answer_path = input_path.with_suffix(".out")
        if not answer_path.exists():
            print(f"  {input_path.stem:<6} нет файла {answer_path.name}, тест пропущен")
            continue

        run = execute(binary, input_path)
        problem = None
        if run.timed_out:
            status, problem = "TL", f"остановлено через {HARD_TIMEOUT:.0f} с"
        elif run.exit_code != 0:
            status, problem = "RE", describe_exit(run.exit_code)
            if run.stderr.strip():
                problem += "\n" + shorten(run.stderr, 600)
        else:
            problem = checker(input_path.read_text(), answer_path.read_text(), run.stdout)
            status = "WA" if problem else "OK"
            if status == "OK" and limits:
                if run.seconds > TIME_LIMIT:
                    status = "TL"
                    problem = f"лимит {TIME_LIMIT:.0f} с"
                elif run.memory_mb is not None and run.memory_mb > MEMORY_LIMIT[task]:
                    status = "ML"
                    problem = f"лимит {MEMORY_LIMIT[task]} МБ"

        memory = f"{run.memory_mb:6.1f} МБ" if run.memory_mb is not None else ""
        print(f"  {input_path.stem:<6} {status_label(status)}  {run.seconds:6.3f} с  {memory}")
        if problem:
            print("         " + problem.replace("\n", "\n         "))
        verdicts.append(status)
        passed += status == "OK"

    return passed, len(verdicts), verdicts


def main():
    parser = argparse.ArgumentParser(description="Сборка и проверка решений лабы.")
    parser.add_argument("tasks", nargs="*", default=list(TASKS), help="буквы задач, по умолчанию все")
    parser.add_argument("--build-dir", default=str(ROOT / "build"))
    parser.add_argument("--build-only", action="store_true", help="только собрать")
    parser.add_argument("--no-limits", action="store_true", help="не проверять время и память")
    args = parser.parse_args()

    cxx = os.environ.get("CXX", "c++")
    cxxflags = os.environ.get("CXXFLAGS", "-std=c++20 -O2 -Wall -Wextra")
    build_dir = Path(args.build_dir)

    unknown = [t for t in args.tasks if t not in TASKS]
    if unknown:
        parser.error(f"нет такой задачи: {', '.join(unknown)}. Есть: {' '.join(TASKS)}")

    summary = []
    for task in args.tasks:
        binary, error = build(task, build_dir, cxx, cxxflags)
        if args.build_only:
            if error:
                print(error.rstrip(), file=sys.stderr)
                return 1
            continue

        print(paint(f"{task.upper()}. {TASKS[task]}", "1"))
        if error:
            print(f"  {status_label('CE')}  ошибка компиляции")
            print("    " + error.rstrip().replace("\n", "\n    "))
            summary.append((task, 0, 0, "CE"))
        else:
            passed, total, verdicts = judge_task(task, binary, not args.no_limits)
            worst = next((v for v in verdicts if v != "OK"), "OK")
            summary.append((task, passed, total, worst))
        print()

    if args.build_only:
        return 0

    if len(summary) > 1:
        print(paint("Итого", "1"))
        for task, passed, total, worst in summary:
            print(f"  {task.upper()}  {status_label(worst)}  {passed}/{total}  {TASKS[task]}")
        solved = sum(1 for *_, worst in summary if worst == "OK")
        print(f"\n  Проходят все тесты: {solved} из {len(summary)}")

    return 0 if all(worst == "OK" for *_, worst in summary) else 1


if __name__ == "__main__":
    sys.exit(main())
