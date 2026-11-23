# Project 6: Brevet Times REST API (DockerRestAPI)

**Author:** Milo Reynolds
**Email:** miloreyn@uoregon.edu

A three-part Docker Compose app built on the ACP brevet control-time calculator from Projects 4 and 5.

1. **Calculator** (Flask, Ajax, MongoDB): enter controls, Submit stores them in MongoDB, Display shows what was stored.
2. **REST API** (Flask): exposes the stored open and close times as JSON or CSV.
3. **Consumer** (PHP, separate container): a web page that reads the API and lets you pick which list to show and how many rows (`top`).

## Running

Requires Docker with the Compose plugin.

```
docker compose up --build
```

| Part | URL |
|---|---|
| Consumer web page | http://localhost:5000 |
| REST API | http://localhost:5001 |
| Calculator | http://localhost:5002 |

Open the calculator, enter some controls and press **Submit** first. The API reads from the same MongoDB database, so it has nothing to return until data has been submitted. Submitting again replaces the previously stored controls.

## API

| Path | Returns |
|---|---|
| `/listAll`, `/listAll/json` | open and close times, JSON |
| `/listAll/csv` | open and close times, CSV |
| `/listOpenOnly`, `/listOpenOnly/json` | open times only, JSON |
| `/listOpenOnly/csv` | open times only, CSV |
| `/listCloseOnly`, `/listCloseOnly/json` | close times only, JSON |
| `/listCloseOnly/csv` | close times only, CSV |

JSON is the default representation. Each JSON entry is an object such as `{"open": "...", "close": "..."}`. CSV output has a header line (`open,close`, `open` or `close`) followed by one line per control.

### Top k

Add `?top=k` to any URL to get only the first k entries, in ascending order. For example `/listAll/csv?top=3` returns the three earliest controls.

- `listAll` and `listOpenOnly` are ordered by open time; `listCloseOnly` is ordered by close time. So `top=k` on `listCloseOnly` returns the k earliest closing times.
- Times are stored as ISO 8601 strings with the same UTC offset, so sorting them as strings gives chronological order.
- `top=k` returns exactly k entries (or fewer if fewer exist).

### Decisions

- A `top` that is not a whole number, or is less than 1, returns HTTP 400.
- If the database is empty, the JSON endpoints return `[]` and the CSV endpoints return only the header line.

## Consumer

The PHP page runs in its own container and reaches the API over the Compose network at `http://laptop-service`. It has a drop-down to choose all, open only or close only, and a `top` box. If the API rejects the request (for example `top=0`), the page shows an error message.

## Tests

The calculator tests live in `brevets/` and run with `pynose` (a maintained fork of nose):

```
cd DockerRestAPI/brevets
nosetests
```

They cover the open and close time calculations and the input validation used by Submit.

## Configuration

Calculator settings come from `brevets/app.ini` (committed, with a placeholder secret key) and optionally `brevets/credentials.ini` (not committed). The submitted `credentials.ini` contains `author` and `repo` under `[DEFAULT]`.

## Layout

```
DockerRestAPI/
  docker-compose.yml
  brevets/    calculator (Flask + Ajax + MongoDB), tests
  laptop/     REST API (Flask)
  website/    consumer (PHP)
```
