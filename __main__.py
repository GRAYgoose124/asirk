import logging
import asyncio
import bot


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def main():
    loop = asyncio.get_event_loop()

    config = {
            'host': b'irc.foonetic.net', 'port': b'6697', 'ssl': True,
            'nick': 'Duckborg', 'pass': 'fxcva',
            'ident': '', 'user': 'Duckborg',
            'mode': '+B', 'unused': '*',
            'owner': 'graygoose124', 'owner_email': '',
            'channels': ['#testgrounds']
    }

    asirk = bot.Irk(loop, config)

    asirk.start()

    loop.run_until_complete(asirk.client_completed)


if __name__ == '__main__':
    main()



