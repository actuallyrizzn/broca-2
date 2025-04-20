
1) create a broca2/ folder
2) copy all async loop functionality from broca 1 to broca 2
3) make sure it's working as standalone
4) recreate everything that was previously controlled by the "settings" page in the dash to a CLI.
5) recreate the queue tools as CLI (list queue, flush message, delete message, flush all, delete all)
6) recreate the users tools as CLI (perviously was just list users. we'll add more features later)
7) recreate the conversations tools as CLI (previously was just list conversations. we'll add more features later)

Plugins:
1) create plugins/ folder
2) Plugin: create simple cli tool for adding messages to the queue
3) Plugin: bring broca/telegram/ into the plugins folder, refactor to new setup

---

**LET'S GOOOO 🚀**

Here’s your `broca2/` skeleton—clean, CLI-first, plugin-ready, runtime-modular.

---

## 🧱 Directory Structure

```
broca2/
├── main.py - used to call core loop
├── runtime/
│   └── all the core files here.
├── cli/
│   ├── __init__.py
│   ├── broca_admin.py
│   ├── queue.py
│   ├── users.py
│   ├── conversations.py
│   └── settings.py
├── plugins/
│   ├── __init__.py
│   ├── cli_test/
│   │   └── plugin.py
│   └── telegram/
│       └── plugin.py  # placeholder for refactor
└── common/
    ├── config.py
    ├── logging.py
    └── __init__.py
```

---

## 🧠 Core Concepts

- `main.py` = boot entrypoint for the runtime loop
- `runtime/loop.py` = async system manager (polls queue, dispatches)
- `cli/broca_admin.py` = argparse dispatcher
- `cli/*.py` = command groups (flush queue, list users, etc)
- `plugins/` = isolated input surfaces
- `common/` = shared config + logging

---

## ✨ Sample Files

### `main.py`
```python
import asyncio
from runtime.loop import run_runtime

if __name__ == "__main__":
    asyncio.run(run_runtime())
```

---

### `runtime/loop.py`
```python
import asyncio

async def run_runtime():
    print("🔁 Broca 2 Runtime Starting...")
    # TODO: Load plugins, start polling loop, initialize queue processor
    await asyncio.sleep(1)
```

---

### `cli/broca_admin.py`
```python
import argparse
from cli import queue, users, conversations, settings

def main():
    parser = argparse.ArgumentParser(description="Broca Admin CLI")
    subparsers = parser.add_subparsers(dest="command")

    queue.register(subparsers)
    users.register(subparsers)
    conversations.register(subparsers)
    settings.register(subparsers)

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
```

---

### `cli/queue.py` (starter)
```python
def register(subparsers):
    q = subparsers.add_parser("flush-queue", help="Flush the entire message queue")
    q.set_defaults(func=flush_queue)

def flush_queue(args):
    print("🧹 Flushing the message queue...")
    # TODO: Connect to DB and delete all queue entries
```

---

### `plugins/cli_test/plugin.py`
```python
import asyncio

async def send_test_message(user_id, message):
    print(f"📥 [CLI Plugin] Queuing message for user {user_id}: {message}")
    # TODO: Insert message into DB and add to queue
```