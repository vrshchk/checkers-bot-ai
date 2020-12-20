import asyncio
import logging
import aiohttp
import searcher
from game import Game


class QqBot:
    def __init__(self, loop):
        self._api_url = 'http://localhost:8081'
        self._session = aiohttp.ClientSession()
        self._game = Game()
        self._loop = loop
        self._last_moves = []
        self._time = 3

    async def _prepare_player(self):
        async with self._session.post(
                f'{self._api_url}/game',
                params={'team_name': "Qq"}
        ) as resp:
            res = (await resp.json())['data']
            self._player = {
                'color': res['color'],
                'token': res['token']
            }

    async def _make_move(self, move):
        json = {'move': move}
        headers = {'Authorization': f'Token {self._player["token"]}'}
        async with self._session.post(
                f'{self._api_url}/move',
                json=json,
                headers=headers
        ) as resp:
            resp = (await resp.json())['data']
            logging.info(f'Qq made move {move}, response: {resp}')

    async def _get_game(self):
        async with self._session.get(f'{self._api_url}/game') as resp:
            return (await resp.json())['data']

    async def _play_game(self):
        current_game_progress = await self._get_game()
        is_finished = current_game_progress['is_finished']
        is_started = current_game_progress['is_started']

        while is_started and not is_finished:
            if current_game_progress['last_move'] is not None and not self._last_moves == \
                                                                      current_game_progress['last_move']['last_moves']:
                self._game.move(current_game_progress['last_move']['last_moves'][-1])
                self._last_moves = current_game_progress['last_move']['last_moves']

            if current_game_progress['whose_turn'] == self._player['color']:
                async with self._session.get(f'http://localhost:8081/game') as resp:
                    curr_state = await resp.json()
                move = searcher.find_move(self._game, self._time)
                await self._make_move(move)

            current_game_progress = await self._get_game()
            is_finished = current_game_progress['is_finished']
            is_started = current_game_progress['is_started']

    async def start(self):
        logging.info('Qq was initialized')
        await self._prepare_player()
        await asyncio.sleep(1)
        await self._play_game()
        logging.info('Game finished')
        last_game_progress = await self._get_game()
        logging.info(str(last_game_progress))
        await self._session.close()


async def init():
    loop = asyncio.get_event_loop()
    player = QqBot(loop)
    await player.start()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init())
