import json, os, logging


log = logging.getLogger(__name__)


def createDefaultConfig(config_path):
    log.info(f"Creating default config at {config_path}")
    with open(config_path, "w") as f:
        json.dump(
            {
                "host": "irc.freenode.net",
                "port": "6667",
                "ssl": False,
                "nick": "asirk",
                "user": "asirk",
                "unused": "*",
                "pass": "update_me",
                "mode": "+B",
                "owner": "your_nick",
                "channels": ["#asIrk"],
            },
            f,
            indent=2,
        )


def useUVloop():
    global uvloop
    if os.name != "nt":
        try:
            import uvloop, asyncio

            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except ImportError:
            log.warning(" Not using uvloop!")
