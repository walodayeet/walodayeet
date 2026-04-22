from __future__ import annotations

import os
import re
from pathlib import Path

import requests

README = Path(__file__).resolve().parents[1] / 'README.md'
START = '<!-- HABITICA:START -->'
END = '<!-- HABITICA:END -->'
USER_API = 'https://habitica.com/api/v3/user'
DAILIES_API = 'https://habitica.com/api/v3/tasks/user?type=dailys'


def get_headers() -> dict[str, str]:
    headers = {
        'x-api-user': os.environ['HABITICA_USER_ID'],
        'x-api-key': os.environ['HABITICA_API_TOKEN'],
        'content-type': 'application/json',
    }
    client = os.environ.get('HABITICA_CLIENT')
    if client:
        headers['x-client'] = client
    return headers


def fetch_level_and_remaining_dailies() -> dict[str, int]:
    headers = get_headers()

    user_response = requests.get(USER_API, headers=headers, timeout=20)
    user_response.raise_for_status()
    user_payload = user_response.json()['data']
    level = int(user_payload.get('stats', {}).get('lvl', 0))

    dailies_response = requests.get(DAILIES_API, headers=headers, timeout=20)
    dailies_response.raise_for_status()
    dailies = dailies_response.json().get('data', [])

    remaining = sum(
        1
        for task in dailies
        if task.get('isDue') and not task.get('completed', False)
    )

    return {
        'level': level,
        'remaining_daily_tasks': remaining,
    }


def build_block(data: dict[str, int]) -> str:
    return '\n'.join([
        START,
        f"- Level: {data['level']}",
        f"- Remaining daily tasks: {data['remaining_daily_tasks']}",
        END,
    ])


def update_readme(block: str) -> None:
    text = README.read_text(encoding='utf-8')
    pattern = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
    updated = pattern.sub(block, text)
    README.write_text(updated, encoding='utf-8')


def main() -> None:
    data = fetch_level_and_remaining_dailies()
    update_readme(build_block(data))
    print('README Habitica block updated.')


if __name__ == '__main__':
    main()
