import os
import shutil

import pytest
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from config.markets import MARKETS, auth_file, credentials
from igv.pages.betsson import BetssonSite
from igv.report import Checks, Evidence, record, slug

load_dotenv()


def pytest_addoption(parser):
    parser.addoption("--market", action="store", default=os.getenv("MARKET"), choices=list(MARKETS), help="betsson-com | betsson-pe")

def _context_kwargs(m):
    return dict(
        locale=m.locale, 
        timezone_id=m.timezone, 
        geolocation=m.geolocation,
        permissions=["geolocation"], 
        viewport={"width": 1366, "height": 768},
        extra_http_headers={
            "x-obg-trusted-traffic": "1",
            "x-obg-country-code": "ES",
            "x-obg-origin": "ES",
            "x-obg-internal": "1"
        }
    )
@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, f"rep_{rep.when}", rep)


@pytest.fixture(scope="session")
def market(request):
    mid = request.config.getoption("--market")
    if not mid:
        pytest.fail("Pass --market betsson-com|betsson-pe (or set MARKET)")
    return MARKETS[mid]


@pytest.fixture(scope="session")
def browser():
    proxy = os.getenv("BETSSON_PE_PROXY") if os.getenv("MARKET") == "betsson-pe" else None
    with sync_playwright() as p:
        b = p.chromium.launch(headless=os.getenv("HEADED") != "1",
                              args=["--autoplay-policy=no-user-gesture-required"],
                              proxy={"server": proxy} if proxy else None)
        yield b
        b.close()


def _context_kwargs(m):
    return dict(locale=m.locale, timezone_id=m.timezone, geolocation=m.geolocation,
                permissions=["geolocation"], viewport={"width": 1366, "height": 768})


def _auth_state(browser, m, kind: str) -> str:
    """Log in once per account in a context with NO video/trace, so credentials never reach artifacts."""
    path = auth_file(m, kind)
    if os.path.exists(path):
        return path
    user, pw = credentials(m, kind)
    if not user or not pw:
        pytest.fail(f"No '{kind}' credentials configured for {m.id} (see .env.example)")
    os.makedirs(".auth", exist_ok=True)
    ctx = browser.new_context(**_context_kwargs(m))
    page = ctx.new_page()
    site = BetssonSite(page, m)
    site.open()
    site.login(user, pw)
    ctx.storage_state(path=path)
    ctx.close()
    return path


@pytest.fixture
def scenario_name(request):
    mk = request.node.get_closest_marker("scenario")
    return mk.args[0] if mk else request.node.name


@pytest.fixture
def player(request, browser, market, scenario_name):
    mk = request.node.get_closest_marker("account")
    kind = mk.args[0] if mk else "funded"
    state = _auth_state(browser, market, kind)
    vdir = f"results/evidence/{market.id}/{slug(scenario_name)}/video-tmp"
    ctx = browser.new_context(storage_state=state, record_video_dir=vdir,
                              record_video_size={"width": 1366, "height": 768}, **_context_kwargs(market))
    page = ctx.new_page()
    yield page
    video = page.video
    ctx.close()
    if video:
        shutil.move(video.path(), f"results/evidence/{market.id}/{slug(scenario_name)}/video.webm")
    shutil.rmtree(vdir, ignore_errors=True)


@pytest.fixture
def evidence(market, scenario_name):
    return Evidence(market.id, scenario_name)


@pytest.fixture
def checks(request, market, scenario_name):
    c = Checks(scenario_name, market.id)
    yield c
    rep = getattr(request.node, "rep_call", None)
    record(scenario_name, market.id, "pass" if rep and rep.passed else "fail", "Test run result",
           f"outcome={rep.outcome if rep else 'not run'}")
