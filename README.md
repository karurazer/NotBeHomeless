# notBeHomeless

Async automation bot for student housing platforms in the Netherlands. It logs in,
caches the session, fetches and parses the current housing offers, filters them by
your criteria, and can automatically react to (sign up for) matching rooms.

The codebase is built to be **multi-platform**: generic domain models live in
`models/`, site-specific clients plug in per platform, and each platform is identified
by the `Website` enum.


## Supported platforms

| Platform                                        | Status        |
|-------------------------------------------------|---------------|
| [Roomspot](https://www.roomspot.nl/) (Enschede) | ✅ Implemented |
| Kamernet                                        | 🚧 Planned    |
| Papirus                                         | 🚧 Planned    |

## Features

- 🏠 Fetching and parsing of the current housing offers
- 🎯 Filtering by price, size, private kitchen/bathroom, furnished, shared
- ✅ Adding / removing reactions to rooms

## Requirements

- Python **3.13+**
- [Poetry](https://python-poetry.org/)

## Installation

```bash
git clone https://github.com/karurazer/NotBeHomeless.git
cd notBeHomeless
poetry install
```

## Configuration

The app needs two things, both kept out of version control.

### 1. Credentials — `.env`

Copy the template and fill in your Roomspot login:

```bash
cp src/.env.example src/.env
```

```dotenv
ROOMSPOT_LOGIN=your-email@example.com
ROOMSPOT_PASSWORD=your-password
```

### 2. Search profile — `hidden_filters.json`

This file holds the request body sent to the Roomspot API: the search filters and
your `woningzoekende` (house-seeker) profile — age, household size, income, current
address, etc. It contains **personal data**, so the real file is git-ignored and only
a template is committed.

```bash
cp src/notbehomeless/roomspot/data/hidden_filters.example.json \
   src/notbehomeless/roomspot/data/hidden_filters.json
```

Then edit `hidden_filters.json` with your own profile values.

## Usage

Run the sample retrieval flow (fetch and log all matching rooms):

```bash
poetry run python -m notbehomeless.roomspot.api
```

The entry point in [`api.py`](src/notbehomeless/roomspot/api.py) calls `setup_logging()`
and runs `test_room_retrieval()`. Use the `RoomspotApi` class directly to build your
own flow:

```python
import aiohttp
from notbehomeless.roomspot.api import RoomspotApi
from notbehomeless.models.website import Website
from notbehomeless.utils.config import login_data
from notbehomeless.config.logging_config import setup_logging


async def main():
    setup_logging()
    async with aiohttp.ClientSession() as session:
        api = RoomspotApi()
        creds = login_data(Website.ROOMSPOT)
        await api.authorize(session, creds.login, creds.password)

        rooms = await api.get_rooms(session)
        for room in rooms:
            await api.perform_available_room_action(session, room)
```

### Filtering

Use `RoomFilter` to select rooms (`-1` means "no limit"):

```python
from notbehomeless.service.room_filter import RoomFilter

room_filter = RoomFilter(max_price=800, min_size=15, kitchen=True)
matching = [r for r in rooms if room_filter.matches(r)]
```

## Logging

Logging is configured centrally in
[`utils/logging_config.py`](src/notbehomeless/config/logging_config.py). Call
`setup_logging()` once at startup; raise verbosity with `setup_logging(logging.DEBUG)`.
Library modules only obtain a logger via `logging.getLogger(__name__)`.

## Project structure

```
src/notbehomeless/
├── models/            # domain models (Room, Website, AllocationType)
├── service/           # logic over models (filtering, auto-signing, status)
├── roomspot/          # Roomspot client (one package per platform;
│   ├── api.py         #   kamernet/ and papirus/ will follow the same layout)
│   ├── authorizer.py  # login + session validation
│   ├── room_parser.py # API JSON -> Room
│   ├── room_reactor.py# reactions + reaction data
│   └── data/          # request payload (git-ignored personal profile)
├── utils/             # cookies, JWT token, file loading, config, logging
└── storage/           # cached cookies (git-ignored)
```

## Roadmap

- [ ] Kamernet platform support
- [ ] Papirus platform support
- [ ] Shared platform interface (common `authorize` / `get_all_rooms` / reaction API)
- [ ] Auto-signer service (`RoomAutoSigner`) — react to filtered rooms automatically
- [ ] Test coverage (`RoomFilter`, parsers)