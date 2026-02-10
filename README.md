# Personal CLI Hub

Curated collection of personal CLI tools for everyday developer workflows.

## Installation

```bash
chmod +x cli_hub.py
alias cli-hub="python3 /path/to/cli_hub.py"
```

Or run directly:

```bash
python3 cli_hub.py <tool> [options]
```

## Available Tools

### system-info

Display detailed system information.

```bash
python3 cli_hub.py system-info
```

### password-gen

Generate secure random passwords.

```bash
python3 cli_hub.py password-gen                    # 16-char password
python3 cli_hub.py password-gen -l 32 -c 5         # 5 passwords, 32 chars each
python3 cli_hub.py password-gen --no-upper         # Exclude uppercase
python3 cli_hub.py password-gen --symbols           # Include special characters
```

### json-format

Format, minify, or validate JSON.

```bash
python3 cli_hub.py json-format '{"key": "value"}'
python3 cli_hub.py json-format '{"key":"value"}' --indent 4
python3 cli_hub.py json-format --minify < input.json
cat data.json | python3 cli_hub.py json-format --validate
```

### hash

Generate MD5, SHA1, SHA256, or SHA512 hashes.

```bash
python3 cli_hub.py hash --text "hello world"
python3 cli_hub.py hash --file somefile.txt
python3 cli_hub.py hash --text "hello" --algo sha256
python3 cli_hub.py hash --text "hello" --algo all
```

### text-stats

Analyze text statistics including word frequency.

```bash
python3 cli_hub.py text-stats "some text to analyze"
cat article.txt | python3 cli_hub.py text-stats
```

### find-large

Find large files in a directory tree.

```bash
python3 cli_hub.py find-large /home/user
python3 cli_hub.py find-large . -s 500        # Files >= 500 MB
python3 cli_hub.py find-large . -s 100 -d 3   # Max depth 3
```

### url

URL encode or decode strings.

```bash
python3 cli_hub.py url --encode "hello world & friends"
python3 cli_hub.py url --decode "hello%20world"
echo "some url" | python3 cli_hub.py url --encode
```

### todo

Simple todo list manager with JSON storage.

```bash
python3 cli_hub.py todo add "Fix the login bug"
python3 cli_hub.py todo add "Write unit tests"
python3 cli_hub.py todo list
python3 cli_hub.py todo done 1     # Mark todo #1 as complete
python3 cli_hub.py todo delete 2   # Delete todo #2
python3 cli_hub.py todo clear      # Clear all todos
```

Todos are stored in `~/.cli_hub_todos.json`.

### timer

Countdown timer with alarm.

```bash
python3 cli_hub.py timer -m 5          # 5 minutes
python3 cli_hub.py timer -m 1 -s 30    # 1 minute 30 seconds
```

### random-choice

Pick random items from a list.

```bash
python3 cli_hub.py random-choice pizza sushi burger
python3 cli_hub.py random-choice -n 2 pizza sushi burger tacos
printf "alpha\nbeta\ngamma\n" | python3 cli_hub.py random-choice -n 1
```

## Quick Reference

| Tool           | Command                     |
| -------------- | --------------------------- |
| System Info    | `cli-hub system-info`       |
| Password Gen   | `cli-hub password-gen`      |
| JSON Format    | `cli-hub json-format`       |
| Hash           | `cli-hub hash`              |
| Text Stats     | `cli-hub text-stats`        |
| Find Large     | `cli-hub find-large`        |
| URL Encode     | `cli-hub url`               |
| Todo Manager   | `cli-hub todo`              |
| Timer          | `cli-hub timer`             |
| Random Choice  | `cli-hub random-choice`     |

## License

MIT
