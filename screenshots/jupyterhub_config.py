import asyncio
import os
from pathlib import Path

from jupyterhub.spawner import SimpleLocalProcessSpawner

c = get_config()  # noqa
load_subconfig(str(Path(__file__).parents[1] / "jupyterhub_config.py"))  # noqa


class DemoSpawner(SimpleLocalProcessSpawner):
    delay = 0

    options_form = options_form = """
        <input name="form_input" class="form-control" placeholder="some input"></input>

        <label for="spawn-delay">Delay this many seconds before launching</label>
        <input name="delay" id="spawn-delay" type="number" default="0" class="form-control"></input>
    """

    def options_from_form(self, options_form):
        if "delay" in options_form:
            self.delay = float(options_form["delay"][0])
        else:
            self.delay = 0

    async def start(self):
        if self.delay:
            self.log.info(f"Sleeping for {self.delay}s")
            await asyncio.sleep(self.delay)
        return await super().start()

    async def progress(self):
        total_t = self.delay
        n = 10
        dt = total_t / n
        dx = 100 // n
        step = dx
        for step in range(dx, 100, dx):
            yield {
                "message": f"progress {step}%",
                "progress": step,
            }
            await asyncio.sleep(dt)


c.JupyterHub.spawner_class = DemoSpawner

c.JupyterHub.services = [
    {
        "name": "proxy",
        "url": "http://127.0.0.1:8000",
    },
    {
        "name": "screenshots",
        "api_token": os.environ.get("SERVICE_TOKEN", ""),
        "admin": True,
    },
]

c.JupyterHub.db_url = "sqlite:///:memory:"

c.Authenticator.allowed_users = {f"user-{i:03}" for i in range(200)}

c.JupyterHub.load_groups = {
    "group-1": ["user-000", "user-001"],
    "group-2": [],
}

c.JupyterHub.tornado_settings = {
    "slow_spawn_timeout": 0,
}
