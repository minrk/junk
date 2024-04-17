import asyncio
import json
import logging
import os
import re
import secrets
import signal
from contextlib import asynccontextmanager
from pathlib import Path
from subprocess import Popen

import aiohttp
from playwright.async_api import async_playwright, expect

from jupyterhub.utils import exponential_backoff, url_path_join, wait_for_http_server

here = Path(__file__).parent.resolve()

hub_url = "http://127.0.0.1:8000"
hub_private_url = "http://127.0.0.1:8081"

api_token = secrets.token_urlsafe(16)

log = logging.getLogger(Path(__file__).name)


@asynccontextmanager
async def launch_hub():
    env = os.environ.copy()
    env["SERVICE_TOKEN"] = api_token
    log.info("Starting jupyterhub")
    p = Popen(
        [
            "jupyterhub",
        ],
        cwd=here,
        env=env,
    )
    with p:
        try:
            await wait_for_http_server(hub_private_url)
            await wait_for_http_server(hub_url)
            log.info(f"jupyterhub ready at {hub_url}")
            yield
        finally:
            log.info("Interrupting jupyterhub")
            p.send_signal(signal.SIGINT)
            for i in range(30):
                if p.poll() is None:
                    await asyncio.sleep(0.1)
            if p.poll() is None:
                log.info("Terminating jupyterhub")
                p.terminate()


async def api_request(session, path, body=None, method="GET"):
    """Make an API request to jupyterhub"""
    if body is not None:
        body = json.dumps(body)
    async with session.request(
        method,
        url_path_join(hub_url, "/hub/api", path),
        headers={"Authorization": f"Bearer {api_token}"},
    ) as response:
        response.raise_for_status()
        if 'json' in response.headers.get('Content-Type', ''):
            return await response.json()
        else:
            return None


async def wait_for_server(session, username, servername=""):
    async def _is_server_running():
        user_model = await api_request(
            session, f"/users/{username}?include_stopped_servers=1"
        )
        server = user_model["servers"][servername]
        return server["ready"]

    await exponential_backoff(
        _is_server_running,
        timeout=30,
        fail_message=f"server {username}/{servername} did not start",
    )


async def prepare_hub():
    # start two named servers
    async with aiohttp.ClientSession() as session:
        await api_request(session, "/users/admin/servers/stopped", method="POST")
        await api_request(session, "/users/admin/servers/started", method="POST")
        await api_request(session, "/users/user-123/servers/", method="POST")
        await wait_for_server(session, "admin", "stopped")
        await api_request(session, "/users/admin/servers/stopped", method="DELETE")
        await wait_for_server(session, "admin", "started")
        await wait_for_server(session, "user-123", "")


@asynccontextmanager
async def browser_page():
    async with async_playwright() as playwright:
        async with await playwright.firefox.launch() as browser:
            page = await browser.new_page()
            await page.set_viewport_size({"width": 1024, "height": 768})
            yield page


async def home_screenshots(page):
    await page.goto(hub_url + "/hub/home")
    await page.wait_for_load_state("load")
    await page.screenshot(path="home.png", full_page=True)

    # services dropdown
    dropdown = page.locator(".navbar-nav").locator(".dropdown")
    await dropdown.hover()
    await dropdown.click()
    await page.screenshot(path="home-services-dropdown.png", full_page=True)


async def token_screenshots(page):
    await page.goto(hub_url + "/hub/token")
    await page.wait_for_load_state("load")
    await page.screenshot(path="token.png", full_page=True)
    # request token
    request_btn = page.locator('//button[@type="submit"]')
    await request_btn.click()
    token_area = page.locator('#token-area')
    await expect(token_area).to_be_visible()
    await page.screenshot(path="token-requested.png", full_page=True)


async def admin_screenshots(page):
    await page.goto(hub_url + "/hub/admin#/?limit=10")
    await expect(page.get_by_role("table")).to_be_visible()
    await page.wait_for_load_state("load")
    await page.screenshot(path="admin.png", full_page=True)
    await page.locator('button[data-testid="admin-collapse-button"]').click()
    # wait for expand animation
    await asyncio.sleep(0.5)
    await page.screenshot(path="admin-expanded.png", full_page=True)
    await page.get_by_role("button", name="Add Users").click()
    await page.screenshot(path="admin-add-users.png", full_page=True)
    await page.go_back()
    await page.get_by_role("button", name="Manage Groups").click()
    await expect(page.get_by_role("button", name="New Group")).to_be_visible()
    await page.screenshot(path="admin-manage-groups.png", full_page=True)
    await page.get_by_role("button", name="New Group").click()
    await page.screenshot(path="admin-new-group.png", full_page=True)
    await page.go_back()
    await page.get_by_text("group-1").click()
    await page.screenshot(path="admin-edit-group.png", full_page=True)
    await page.go_back()


async def spawn_screenshots(page):
    await page.goto(hub_url + "/hub/spawn")
    await page.locator("#spawn-delay").fill("5")
    await page.screenshot(path="spawn-form.png", full_page=True)
    await page.locator('//input[@type="submit"]').click()
    await asyncio.sleep(2)
    await page.screenshot(path="spawn-progress.png", full_page=True)
    await page.locator("summary").click()
    await page.screenshot(path="spawn-progress-expanded.png", full_page=True)

    await page.goto(hub_url + "/user/user-123/")
    await expect(page).to_have_url(re.compile(".*/hub/api/oauth2/authorize.*"))
    await page.screenshot(path="authorize.png", full_page=True)


async def main():
    logging.basicConfig(level=logging.DEBUG)
    async with launch_hub(), browser_page() as page:
        await prepare_hub()
        await page.goto(hub_url + "/hub/login?next=/hub/home")
        await page.screenshot(path="login.png", full_page=True)
        # login
        await page.get_by_label("Username:").fill("admin")
        await page.get_by_label("Password:").fill("admin")
        await page.get_by_role("button", name="Sign in").click()

        await home_screenshots(page)
        await token_screenshots(page)
        await admin_screenshots(page)
        await spawn_screenshots(page)


def emit_compare(a, b):
    lines = []

    lines.append(f"| {a} | {b} |")
    lines.append("|---|---|")
    for png in sorted(Path(a).glob("*.png")):
        lines.append(f"| {png.name} <td colspan=2> |")
        lines.append(f"| ![{png}]({a}/{png.name}) | ![{png}]({b}/{png.name}) |")

    with Path("compare.md").open("w") as f:
        f.write("\n".join(lines))
        f.write("\n")


if __name__ == "__main__":
    # emit_compare("bs4", "bs5")
    asyncio.run(main())
