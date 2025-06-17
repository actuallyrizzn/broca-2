# CLI-Test Plugin

> **Status:** Proof-of-concept / placeholder  
> **Location:** `broca2/plugins/cli_test/`

The *CLI-Test Plugin* is a **very small stub** designed to exercise the Broca 2 plugin lifecycle during unit-testing and CI pipelines.  It purposefully contains just the bare minimum required interface implementation so that developers can:

* Verify that the `PluginManager` can *discover, load, start and stop* a plugin.
* Provide a sandbox for experimenting with the plugin API *without* depending on third-party services (Telegram, Slack, …).
* Serve as a template for writing new plugins.

Because the file at [`plugins/cli_test/plugin.py`](../plugins/cli_test/plugin.py) is currently empty you are encouraged to copy it and fill in logic relevant to your development workflow.

---

## Why keep an "empty" plugin?
1. **API Regression Checks** – CI can attempt to import and instantiate all plugins; if the core `Plugin` base-class signature changes, this plugin will fail fast.
2. **Documentation & On-boarding** – New contributors immediately have a minimal example to look at.
3. **Scaffolding** – Acts as a starting point for quick experiments (`git checkout -b my-new-plugin` and you're ready).

---

## Suggested Implementation Skeleton
```python
from runtime.core.plugin import Plugin

class CLITestPlugin(Plugin):
    """A minimal no-op plugin used for testing."""

    async def start(self) -> None:
        print("CLITestPlugin started")

    async def stop(self) -> None:
        print("CLITestPlugin stopped")

    def get_name(self) -> str:
        return "cli_test"

    def get_platform(self) -> str:
        return "cli"

    def get_message_handler(self):
        # This plugin does not process external messages
        return lambda *args, **kwargs: None
```
Save the file, run Broca, and you should see the start/stop printouts in the log.

---

## Configuration
No external configuration is required.  All settings are hard-coded because the plugin does *nothing* by design.

---

## Extending the Plugin
If you want to turn this stub into a real in-terminal chat plugin, you could:
1. Implement a readline loop to capture user input.
2. Send captured messages into the Broca queue with `add_to_queue()` like other plugins.
3. Print agent responses to the console.

Until then, the plugin remains a lightweight canary to safeguard Broca's extensibility points.