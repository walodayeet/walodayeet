from __future__ import annotations

import os
import re
from pathlib import Path

import requests

README = Path(__file__).resolve().parents[1] / 'README.md'
START = '<!-- HABITICA:START -->'
END = '<!-- HABITICA:END -->'
API = 'https://habitica.com/api/v3/user'


def fetch_user() -> dict:
    user_id = os.environ['HABITICA_USER_ID']
    token = os.environ['HABITICA_API_TOKEN']
    headers = {
        'x-api-user': user_id,
        'x-api-key': token,
        'content-type': 'application/json',
    }
    response = requests.get(API, headers=headers, timeout=20)
    response.raise_for_status()
    payload = response.json()['data']
    stats = payload.get('stats', {})
    items = payload.get('items', {})
    current_pet = items.get('currentPet', 'none')
    current_mount = items.get('currentMount', 'none')
    return {
        'level': stats.get('lvl', 'unknown'),
        'class': stats.get('class', 'unknown'),
        'gold': round(float(stats.get('gp', 0)), 2),
        'pet': current_pet,
        'mount': current_mount,
    }


def build_block(user: dict) -> str:
    return '\n'.join([
        START,
        f"- Level: {user['level']}",
        f"- Class: {user['class']}",
        f"- Gold: {user['gold']}",
        f"- Pet: {user['pet']}",
        f"- Mount: {user['mount']}",
        '- Focus: consistency, study, infrastructure',
        END,
    ])


def update_readme(block: str) -> None:
    text = README.read_text(encoding='utf-8')
    pattern = re.compile(re.escape(START) + r'.*?' + re.escape(END), re.S)
    updated = pattern.sub(block, text)
    README.write_text(updated, encoding='utf-8')


def main() -> None:
    user = fetch_user()
    block = build_block(user)
    update_readme(block)
    print('README Habitica block updated.')


if __name__ == '__main__':
    main()
