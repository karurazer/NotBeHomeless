# notBeHomeless

Async automation bot for student housing platforms in the Netherlands, exposed as a
**FastAPI** service. It logs in, caches the session, fetches and parses the current
housing offers, filters them by your criteria, lets you react to (sign up for) rooms
via a REST API, and can auto-sign matching rooms in the background.

The codebase is built to be **multi-platform**: generic domain models live in
`models/`, site-specific clients plug in under `websites/<site>/`, and each platform
is identified by the `Website` enum.

## Supported platforms

| Platform                                        | Status        |
|-------------------------------------------------|---------------|
| [Roomspot](https://www.roomspot.nl/) (Enschede) | ✅ Implemented |
| Kamernet                                        | 🚧 Planned    |
| Papirus                                         | 🚧 Planned    |

## Features

- 🌐 REST API (FastAPI) with interactive docs at `/docs`
- 🔐 Authentication with session/cookie persistence (re-login only when the token expires)
- 🏠 Fetching and parsing of the current housing offers (paginated)
- 🎯 Filtering by price, size, private kitchen/bathroom, furnished
- ✅ Adding / removing reactions to rooms, with truthful error reporting (404/409/502)
- 🤖 Background **auto-signer**: periodically signs rooms matching your filter
- 🧾 Structured `logging` (configurable level)
- 🔒 Personal data and secrets kept out of git

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
cp src/notbehomeless/websites/roomspot/data/hidden_filters.example.json \
   src/notbehomeless/websites/roomspot/data/hidden_filters.json
```

Then edit `hidden_filters.json` with your own profile values.

> `.env`, `hidden_filters.json` and `storage/` (session cookies) are listed in
> `.gitignore` — never commit them.

## Usage

Start the API server:

```bash
poetry run uvicorn notbehomeless.main:create_app --factory --reload
# or: poetry run python -m notbehomeless.main
```

Then open **http://127.0.0.1:8000/docs** for interactive Swagger docs.

On startup the app logs in to Roomspot (lifespan), keeps one shared aiohttp session,
and shuts down any running auto-signers on exit.

### Endpoints

| Method | Path                    | Description                                                        |
|--------|-------------------------|--------------------------------------------------------------------|
| GET    | `/health`               | Liveness probe                                                     |
| GET    | `/rooms`                | List rooms; filter via query (`max_price`, `min_size`, `kitchen`, `bathroom`, `furnished`) |
| POST   | `/rooms/{id}/react`     | React to a room; body `{"action": "add" \| "remove"}` → 200 / 404 / 409 / 502 |
| GET    | `/signers`              | List auto-signers and whether they are running                    |
| POST   | `/signers/roomspot`     | Start the Roomspot auto-signer (filter via query + `period_seconds`) |
| DELETE | `/signers/roomspot`     | Stop the Roomspot auto-signer                                      |

Examples:

```bash
# rooms under €800 with a private kitchen
curl "http://127.0.0.1:8000/rooms?max_price=800&kitchen=true"

# sign up for room 20361
curl -X POST http://127.0.0.1:8000/rooms/20361/react \
  -H "Content-Type: application/json" -d '{"action": "add"}'

# auto-sign matching rooms every 60 seconds
curl -X POST "http://127.0.0.1:8000/signers/roomspot?max_price=800&kitchen=true&period_seconds=60"
```

### Filtering in code

`RoomFilter` selects rooms (`-1` means "no limit"):

```python
from notbehomeless.models.room_filter import RoomFilter

room_filter = RoomFilter(max_price=800, min_size=15, kitchen=True)
matching = [r for r in rooms if room_filter.matches(r)]
```

## Logging

Logging is configured centrally in
[`config/logging_config.py`](src/notbehomeless/config/logging_config.py). Call
`setup_logging()` once at startup (the app lifespan already does); raise verbosity
with `setup_logging(logging.DEBUG)`. Library modules only obtain a logger via
`logging.getLogger(__name__)`.

## Project structure

```
src/notbehomeless/
├── main.py                # entry point: app factory, lifespan, uvicorn runner
├── api/                   # HTTP layer (FastAPI)
│   ├── routers/           #   /health, /rooms, /signers
│   ├── schemas/           #   Pydantic DTOs (RoomOut, ReactionRequest, ...)
│   └── dependencies.py    #   Depends() providers + Annotated aliases
├── models/                # domain: Room, Website, RoomFilter, AllocationType,
│                          #   BaseApi (per-site client contract), AppException
├── service/               # cross-site logic: RoomAutoSigner, AutoSignerManager
├── websites/              # one package per platform
│   └── roomspot/          #   api.py, service.py, authorizer, parser, reactor,
│       └── data/          #   request payload (git-ignored personal profile)
├── config/                # logging configuration
├── factory/               # FastAPI wiring (exception handlers)
├── utils/                 # cookies, JWT token, file loading, env config
└── storage/               # cached cookies (git-ignored)
```

Errors are reported through an `AppException` hierarchy (each exception carries its
HTTP `status_code` and the `Website` it belongs to) and mapped to JSON responses by a
single FastAPI exception handler.

## Roadmap

- [x] Roomspot client (auth, rooms, reactions)
- [x] REST API (FastAPI)
- [x] Auto-signer with start/stop endpoints
- [ ] Kamernet platform support
- [ ] Papirus platform support
- [ ] Shared platform service interface (dispatch by `Website`)
- [ ] Web frontend (Vue)
- [ ] Test coverage (`RoomFilter`, parsers, auto-signer)

## Security notes

- `.env`, `hidden_filters.json` and `storage/` (session cookies) are git-ignored — they
  contain credentials, personal data, and active sessions. Keep them local.
- Cookies are stored with `pickle`; only load cookie files you created yourself.
- The API has no authentication of its own — run it locally, do not expose it publicly.
