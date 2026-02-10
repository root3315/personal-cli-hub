#!/usr/bin/env python3
"""Personal CLI Hub - Curated collection of CLI tools for everyday developer workflows."""

import argparse
import hashlib
import json
import os
import platform
import random
import re
import secrets
import shutil
import string
import subprocess
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional


def tool_system_info(args):
    """Display detailed system information."""
    print("=" * 60)
    print(" System Information")
    print("=" * 60)
    print(f"  OS       : {platform.system()} {platform.release()}")
    print(f"  Node     : {platform.node()}")
    print(f"  Machine  : {platform.machine()}")
    print(f"  Python   : {platform.python_version()}")
    print(f"  Arch     : {platform.architecture()[0]}")
    print(f"  CPUs     : {os.cpu_count()}")
    print(f"  User     : {os.environ.get('USER', 'unknown')}")
    print(f"  Shell    : {os.environ.get('SHELL', 'unknown')}")
    print(f"  CWD      : {os.getcwd()}")

    try:
        total = shutil.disk_usage("/").total
        free = shutil.disk_usage("/").free
        used = total - free
        print(f"  Disk Used: {used // (1024**3)} GB / {total // (1024**3)} GB")
    except Exception:
        print("  Disk Used: N/A")

    mem_info = Path("/proc/meminfo")
    if mem_info.exists():
        lines = mem_info.read_text().splitlines()[:3]
        for line in lines:
            key, val = line.split(":", 1)
            print(f"  {key.strip():<9}: {val.strip()}")
    print("=" * 60)


def tool_password_generator(args):
    """Generate secure random passwords."""
    length = args.length
    count = args.count
    use_upper = args.no_upper is False
    use_lower = args.no_lower is False
    use_digits = args.no_digits is False
    use_symbols = args.symbols

    charset = ""
    if use_upper:
        charset += string.ascii_uppercase
    if use_lower:
        charset += string.ascii_lowercase
    if use_digits:
        charset += string.digits
    if use_symbols:
        charset += "!@#$%^&*()_+-=[]{}|;:,.<>?"

    if not charset:
        print("Error: at least one character set must be selected.", file=sys.stderr)
        sys.exit(1)

    for _ in range(count):
        password = "".join(secrets.choice(charset) for _ in range(length))
        print(password)


def tool_json_format(args):
    """Format or validate JSON data."""
    input_data = args.input

    if input_data is None and not sys.stdin.isatty():
        input_data = sys.stdin.read()

    if input_data is None:
        print("Error: no JSON input provided.", file=sys.stderr)
        sys.exit(1)

    try:
        parsed = json.loads(input_data)
        if args.minify:
            print(json.dumps(parsed, separators=(",", ":")))
        else:
            indent = args.indent if args.indent else 2
            print(json.dumps(parsed, indent=indent, ensure_ascii=False))
        if args.validate:
            print("Valid JSON.", file=sys.stderr)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        sys.exit(1)


def tool_hash(args):
    """Generate hashes for strings or files."""
    if args.file:
        file_path = Path(args.file)
        if not file_path.exists():
            print(f"Error: file '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
        data = file_path.read_bytes()
        label = f"File: {args.file}"
    else:
        data = args.text.encode("utf-8")
        label = f"Text: {args.text}"

    print(f"{label}")
    print("-" * 40)

    if args.algo in ("all", None):
        algorithms = ["md5", "sha1", "sha256", "sha512"]
    else:
        algorithms = [args.algo]

    for algo in algorithms:
        try:
            h = hashlib.new(algo)
            h.update(data)
            print(f"  {algo.upper():<8}: {h.hexdigest()}")
        except ValueError:
            print(f"  {algo:<8}: unsupported", file=sys.stderr)


def tool_text_stats(args):
    """Display statistics for text input."""
    text = args.input
    if text is None and not sys.stdin.isatty():
        text = sys.stdin.read()
    if text is None:
        print("Error: no text input provided.", file=sys.stderr)
        sys.exit(1)

    lines = text.splitlines()
    words = text.split()
    no_spaces = text.replace(" ", "").replace("\t", "").replace("\n", "")

    print(f"  Lines       : {len(lines)}")
    print(f"  Words       : {len(words)}")
    print(f"  Characters  : {len(text)}")
    print(f"  Characters (no spaces): {len(no_spaces)}")
    print(f"  Paragraphs  : {sum(1 for l in lines if l.strip()) if lines else 0}")

    freq = {}
    for word in words:
        w = word.lower().strip(".,!?;:\"'()[]{}")
        freq[w] = freq.get(w, 0) + 1
    top_words = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    if top_words:
        print("\n  Top words:")
        for word, count in top_words:
            bar = "#" * count
            print(f"    {word:<20} {count:>5}  {bar}")


def tool_find_large_files(args):
    """Find large files in a directory tree."""
    target = Path(args.directory)
    if not target.exists():
        print(f"Error: directory '{args.directory}' not found.", file=sys.stderr)
        sys.exit(1)

    threshold = args.size_mb * 1024 * 1024
    results = []

    for root, dirs, files in os.walk(target):
        if args.max_depth is not None:
            depth = Path(root).relative_to(target).parts.__len__()
            if depth >= args.max_depth:
                dirs.clear()
        for fname in files:
            fpath = Path(root) / fname
            try:
                size = fpath.stat().st_size
                if size >= threshold:
                    results.append((fpath, size))
            except (PermissionError, OSError):
                continue

    results.sort(key=lambda x: x[1], reverse=True)

    print(f"Files >= {args.size_mb} MB in {target}:")
    print("-" * 60)
    if not results:
        print("  No files found.")
        return

    for fpath, size in results:
        size_mb = size / (1024 * 1024)
        print(f"  {size_mb:>8.2f} MB  {fpath}")
    print(f"\nTotal: {len(results)} file(s)")


def tool_url_encode_decode(args):
    """URL encode or decode strings."""
    text = args.text
    if text is None and not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    if text is None:
        print("Error: no input provided.", file=sys.stderr)
        sys.exit(1)

    if args.encode:
        from urllib.parse import quote
        result = quote(text, safe="")
    elif args.decode:
        from urllib.parse import unquote
        result = unquote(text)
    else:
        print("Error: specify --encode or --decode.", file=sys.stderr)
        sys.exit(1)

    print(result)


def tool_todo_manager(args):
    """Simple CLI todo list manager stored in a JSON file."""
    todo_file = Path(os.environ.get("HOME", ".")) / ".cli_hub_todos.json"

    def load_todos():
        if todo_file.exists():
            return json.loads(todo_file.read_text())
        return []

    def save_todos(todos):
        todo_file.write_text(json.dumps(todos, indent=2))

    action = args.action

    if action == "add":
        todos = load_todos()
        todo_id = max([t["id"] for t in todos], default=0) + 1
        todos.append({
            "id": todo_id,
            "text": args.task,
            "done": False,
            "created": datetime.now().isoformat()
        })
        save_todos(todos)
        print(f"Added todo #{todo_id}: {args.task}")

    elif action == "list":
        todos = load_todos()
        if not todos:
            print("No todos.")
            return
        for t in todos:
            status = "[x]" if t["done"] else "[ ]"
            print(f"  {status} #{t['id']}  {t['text']}")

    elif action == "done":
        todos = load_todos()
        for t in todos:
            if t["id"] == args.task_id:
                t["done"] = True
                save_todos(todos)
                print(f"Completed todo #{t['id']}: {t['text']}")
                return
        print(f"Todo #{args.task_id} not found.", file=sys.stderr)
        sys.exit(1)

    elif action == "delete":
        todos = load_todos()
        new_todos = [t for t in todos if t["id"] != args.task_id]
        if len(new_todos) == len(todos):
            print(f"Todo #{args.task_id} not found.", file=sys.stderr)
            sys.exit(1)
        save_todos(new_todos)
        print(f"Deleted todo #{args.task_id}")

    elif action == "clear":
        save_todos([])
        print("Cleared all todos.")


def tool_timer(args):
    """Simple countdown timer."""
    minutes = args.minutes
    seconds = args.seconds
    total_seconds = minutes * 60 + seconds

    if total_seconds <= 0:
        print("Error: timer must be greater than 0.", file=sys.stderr)
        sys.exit(1)

    print(f"Timer set for {minutes}m {seconds}s")
    start = time.time()

    try:
        while True:
            elapsed = time.time() - start
            remaining = total_seconds - elapsed
            if remaining <= 0:
                break
            mins, secs = divmod(int(remaining), 60)
            print(f"\r  {mins:02d}:{secs:02d} remaining", end="", flush=True)
            time.sleep(1)
    except KeyboardInterrupt:
        elapsed = time.time() - start
        print(f"\nTimer interrupted after {int(elapsed)}s")
        return

    remaining_time = total_seconds - (time.time() - start)
    if remaining_time <= 1:
        print(f"\r  00:00 remaining")
        print("\n  Time's up!")
        if platform.system() != "Windows":
            print("\a", end="", flush=True)


def tool_random_choice(args):
    """Pick random choice from a list."""
    choices = args.choices
    if not choices and not sys.stdin.isatty():
        stdin_data = sys.stdin.read().strip()
        if stdin_data:
            choices = stdin_data.split("\n")
    if not choices:
        print("Error: provide choices as arguments or piped input.", file=sys.stderr)
        sys.exit(1)

    picks = min(args.count, len(choices))
    selected = random.sample(choices, picks)
    for i, choice in enumerate(selected, 1):
        print(f"  {i}. {choice}")


def build_parser():
    parser = argparse.ArgumentParser(
        prog="cli-hub",
        description="Personal CLI Hub - Developer tools for everyday workflows"
    )
    subparsers = parser.add_subparsers(dest="tool", help="Available tools")

    # system-info
    p_sys = subparsers.add_parser("system-info", help="Display system information")
    p_sys.set_defaults(func=tool_system_info)

    # password-gen
    p_pw = subparsers.add_parser("password-gen", help="Generate secure passwords")
    p_pw.add_argument("-l", "--length", type=int, default=16, help="Password length")
    p_pw.add_argument("-c", "--count", type=int, default=1, help="Number of passwords")
    p_pw.add_argument("--no-upper", action="store_true")
    p_pw.add_argument("--no-lower", action="store_true")
    p_pw.add_argument("--no-digits", action="store_true")
    p_pw.add_argument("--symbols", action="store_true", help="Include symbols")
    p_pw.set_defaults(func=tool_password_generator)

    # json-format
    p_json = subparsers.add_parser("json-format", help="Format or validate JSON")
    p_json.add_argument("input", nargs="?", help="JSON string or pipe from stdin")
    p_json.add_argument("--minify", action="store_true")
    p_json.add_argument("--indent", type=int, default=None)
    p_json.add_argument("--validate", action="store_true")
    p_json.set_defaults(func=tool_json_format)

    # hash
    p_hash = subparsers.add_parser("hash", help="Generate hashes")
    p_hash.add_argument("--text", help="Text to hash")
    p_hash.add_argument("--file", help="File to hash")
    p_hash.add_argument("--algo", choices=["md5", "sha1", "sha256", "sha512", "all"], default=None)
    p_hash.set_defaults(func=tool_hash)

    # text-stats
    p_txt = subparsers.add_parser("text-stats", help="Analyze text statistics")
    p_txt.add_argument("input", nargs="?", help="Text input or pipe from stdin")
    p_txt.set_defaults(func=tool_text_stats)

    # find-large
    p_large = subparsers.add_parser("find-large", help="Find large files in directory")
    p_large.add_argument("directory", nargs="?", default=".", help="Directory to scan")
    p_large.add_argument("-s", "--size-mb", type=float, default=100, help="Size threshold in MB")
    p_large.add_argument("-d", "--max-depth", type=int, default=None)
    p_large.set_defaults(func=tool_find_large_files)

    # url-encode
    p_url = subparsers.add_parser("url", help="URL encode/decode")
    p_url.add_argument("text", nargs="?", help="Text to process")
    p_url.add_argument("--encode", action="store_true")
    p_url.add_argument("--decode", action="store_true")
    p_url.set_defaults(func=tool_url_encode_decode)

    # todo
    p_todo = subparsers.add_parser("todo", help="Todo list manager")
    p_todo.add_argument("action", choices=["add", "list", "done", "delete", "clear"])
    p_todo.add_argument("task", nargs="?", help="Task text (for add)")
    p_todo.add_argument("task_id", nargs="?", type=int, help="Task ID (for done/delete)")
    p_todo.set_defaults(func=tool_todo_manager)

    # timer
    p_timer = subparsers.add_parser("timer", help="Countdown timer")
    p_timer.add_argument("-m", "--minutes", type=int, default=0)
    p_timer.add_argument("-s", "--seconds", type=int, default=0)
    p_timer.set_defaults(func=tool_timer)

    # random-choice
    p_choice = subparsers.add_parser("random-choice", help="Pick random items")
    p_choice.add_argument("choices", nargs="*", help="Options to choose from")
    p_choice.add_argument("-n", "--count", type=int, default=1, help="Number of picks")
    p_choice.set_defaults(func=tool_random_choice)

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(1)

    try:
        args.func(args)
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
