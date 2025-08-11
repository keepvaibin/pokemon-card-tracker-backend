# Pokémon Cards API

A REST API for querying Pokémon TCG cards with filterable pricing snapshots and (optionally) time‑series price history. This README is **authoritative** to the current backend code and includes every supported filter (with examples), authentication, pagination, and all endpoints.

> TL;DR: Authentication is required on all routes (Google ID Token). PostgreSQL is required. TimescaleDB is optional but required for price history endpoints.

---

## Quick Start

### Requirements

- Python 3.10+
- Flask + SQLAlchemy
- **PostgreSQL** (required; uses `ARRAY` columns)
- (Optional) **TimescaleDB** if you want `/price/history` & `/price/latest`
- Google OAuth **Client ID** (for verifying ID tokens)

### Environment variables

- `DATABASE_URL` – PostgreSQL connection string (required)
- `GOOGLE_CLIENT_ID` – OAuth Client ID used to verify ID tokens (required)
- `SECRET_KEY` – Flask secret key (optional; default `dev`)
- `TIMESCALE_URL` – PostgreSQL/Timescale connection string (optional; required only for price history endpoints)

### Run

```bash
export DATABASE_URL=postgresql://...
export GOOGLE_CLIENT_ID=...apps.googleusercontent.com
export SECRET_KEY=dev
# optional
export TIMESCALE_URL=postgresql://...   # needed for /price/history and /price/latest

flask run
```

### Authentication

Every request **must** include a Google **ID token** in the `Authorization` header:

```
Authorization: Bearer <GOOGLE_ID_TOKEN>
```

Invalid or missing tokens return `401 Unauthorized`.

---

## Data Model (high level)

This API merges data from the following tables when needed:

- `Card` – core card fields (`id`, `name`, `supertype`, `rarity`, `hp` [string], `level` [string], `number` [string], `types[]`, `artist`, set linkage, images, etc.).
- `CardMarket` – snapshot pricing from Cardmarket (`averageSellPrice`, `trendPrice`, `lowPrice`).
- `TcgPlayer` & `TcgPlayerPrices` – TCGplayer price blocks; quick filters use **Market** fields (`normalMarket`, `holofoilMarket`, `reverseHolofoilMarket`).
- (Optional) `PriceHistory` – time‑series prices (cardId, time, averageSellPrice, source).

> Note: `hp`, `level`, and `number` are stored as **strings** in the DB. They support equality filtering only (no numeric comparisons) unless you extend the backend to cast them to integers.

### Response shapes

- **Basic card** (used by `GET /cards`): key identity fields, minimal set info, images, and the quick pricing snapshot (Cardmarket and TCGplayer markets).
- **Full card** (used by `GET /cards/:id` and `POST /cards/bulk`): basic card + abilities, attacks, weaknesses, resistances, full set block, and detailed pricing blocks.

---

## Pagination

All list endpoints include these parameters:

- `page` – default `1`
- `page_size` – default `15`, maximum `100`

Responses include: `page`, `page_size`, `total`, `total_pages`, and the data array.

---

## ✅ Filters (complete list)

The `/cards` endpoint supports **equality filters** and **numeric comparison filters**. All provided filters combine with **AND** semantics.

### Filters overview (cheat‑sheet)

| Parameter (query key) | Type    | Operators                               | Source table/column                  | Notes |
|---|---|---|---|---|
| `id`                  | string  | `=`                                      | `Card.id`                            | Exact match |
| `name`                | string  | `=`                                      | `Card.name`                          | Exact match |
| `supertype`           | string  | `=`                                      | `Card.supertype`                     | Exact match |
| `rarity`              | string  | `=`                                      | `Card.rarity`                        | Exact match |
| `hp`                  | string  | `=`                                      | `Card.hp`                            | **String equality only** |
| `level`               | string  | `=`                                      | `Card.level`                         | **String equality only** |
| `number`              | string  | `=`                                      | `Card.number`                        | **String equality only** |
| `setId`               | string  | `=`                                      | `Card.setId`                         | Exact match |
| `artist`              | string  | `=`                                      | `Card.artist`                        | Exact match |
| `averageSellPrice_*`  | number  | `_gte`, `_lte`, `_gt`, `_lt`             | `CardMarket.averageSellPrice`        | Numeric compare |
| `trendPrice_*`        | number  | `_gte`, `_lte`, `_gt`, `_lt`             | `CardMarket.trendPrice`              | Numeric compare |
| `lowPrice_*`          | number  | `_gte`, `_lte`, `_gt`, `_lt`             | `CardMarket.lowPrice`                | Numeric compare |
| `normalMarket_*`      | number  | `_gte`, `_lte`, `_gt`, `_lt`             | `TcgPlayerPrices.normalMarket`       | Numeric compare |
| `holofoilMarket_*`    | number  | `_gte`, `_lte`, `_gt`, `_lt`             | `TcgPlayerPrices.holofoilMarket`     | Numeric compare |
| `reverseHolofoilMarket_*` | number | `_gte`, `_lte`, `_gt`, `_lt`          | `TcgPlayerPrices.reverseHolofoilMarket` | Numeric compare |

> The `_*` suffix means **pick one of** `_gte`, `_lte`, `_gt`, or `_lt`. Example: `trendPrice_lte=5`.

---

## Filtering – details and examples

Below, each filter is explained with a working example. All examples include auth headers; replace `TOKEN` with a valid Google ID token.

> Base URL is assumed to be `http://localhost:5000` for curl examples.

### Equality filters (string exact matches)

- `id` – a specific card ID (e.g., `sv5-29`).  
  ```bash
  curl -s --location 'http://localhost:5000/cards?id=sv5-29' \
    --header 'Authorization: Bearer TOKEN'
  ```

- `name` – exact name match.  
  ```bash
  curl -s 'http://localhost:5000/cards?name=Pikachu' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `supertype` – e.g., `Pokémon`, `Trainer`, `Energy`.  
  ```bash
  curl -s 'http://localhost:5000/cards?supertype=Pokémon' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `rarity` – e.g., `Common`, `Rare`, `Rare Holo`.  
  ```bash
  curl -s 'http://localhost:5000/cards?rarity=Rare' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `hp` – **string** equality only (e.g., `"60"`, `"120"`).  
  ```bash
  curl -s 'http://localhost:5000/cards?hp=120' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `level` – **string** equality only.  
  ```bash
  curl -s 'http://localhost:5000/cards?level=5' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `number` – **string** equality only (the printed card number within the set).  
  ```bash
  curl -s 'http://localhost:5000/cards?number=1' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `setId` – the set identifier (e.g., `swsh1`).  
  ```bash
  curl -s 'http://localhost:5000/cards?setId=swsh1' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `artist` – the card artist’s exact name.  
  ```bash
  curl -s --get 'http://localhost:5000/cards' \
    --data-urlencode 'artist=Ken Sugimori' \
    -H 'Authorization: Bearer TOKEN'
  ```

> ⚠️ **Case-sensitivity** follows how values are stored in the DB. If you need case-insensitive or partial matching, extend the backend with `ilike`/`lower()` accordingly.

### Numeric comparison filters

Use one of the suffixes `_gte`, `_lte`, `_gt`, `_lt` with the **base key** shown below.

#### Cardmarket

- `averageSellPrice_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?averageSellPrice_gte=1.5' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `trendPrice_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?trendPrice_lte=5' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `lowPrice_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?lowPrice_gt=0.05' \
    -H 'Authorization: Bearer TOKEN'
  ```

#### TCGplayer (Market prices)

- `normalMarket_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?normalMarket_gte=0.25' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `holofoilMarket_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?holofoilMarket_lte=10' \
    -H 'Authorization: Bearer TOKEN'
  ```

- `reverseHolofoilMarket_*`  
  ```bash
  curl -s 'http://localhost:5000/cards?reverseHolofoilMarket_lt=2.5' \
    -H 'Authorization: Bearer TOKEN'
  ```

**Combination examples** (AND semantics):

```bash
# Rare cards in Sword & Shield base set with Cardmarket trend <= $5
curl -s 'http://localhost:5000/cards?setId=swsh1&rarity=Rare&trendPrice_lte=5' \
  -H 'Authorization: Bearer TOKEN'

# Artist + TCGplayer filter
curl -s --get 'http://localhost:5000/cards' \
  --data-urlencode 'artist=Ken Sugimori' \
  --data-urlencode 'normalMarket_gt=0.15' \
  -H 'Authorization: Bearer TOKEN'
```

> **Why no `hp_gte`?** `hp` is a string in the DB. Numeric comparisons on strings can cause DB errors. Use `hp=<value>` for exact string matches. If you want numeric HP filters, add a cast in the backend (see FAQ).

---

## Endpoints

### `GET /cards`

List cards (basic shape) with pagination and all filters described above.

**Query params:** `page`, `page_size`, any of the filters.  
**Errors:** `400` (invalid pagination or numeric value), `401` (unauthorized).

**Example**

```bash
curl -s 'http://localhost:5000/cards?page=2&page_size=25&rarity=Rare&trendPrice_lte=5' \
  -H 'Authorization: Bearer TOKEN'
```

---

### `GET /cards/filters`

Helper metadata for building filter UIs.

- **Ranges** (min/max):
  - Cardmarket: `averageSellPrice`, `trendPrice`, `lowPrice`
  - TCGplayer Prices: `normalLow`, `holofoilLow`, `reverseHolofoilLow`
  - Card (string ranges): `hp`, `level`, `number` (lexicographic)
- **Categories** (distinct values): `artists`, `rarities`, `supertypes`, `types[]`, `sets` (`{id,name}`)

**Example**

```bash
curl -s 'http://localhost:5000/cards/filters' \
  -H 'Authorization: Bearer TOKEN'
```

> Note: `hp`, `level`, `number` ranges are derived as strings; they are useful for UIs but not for numeric comparisons unless you cast in SQL.

---

### `GET /cards/:id`

Full card detail. Returns `404` if not found.

```bash
curl -s 'http://localhost:5000/cards/swsh1-1' \
  -H 'Authorization: Bearer TOKEN'
```

---

### `POST /cards/bulk`

Fetch multiple full cards by IDs.

**Body**
```json
{ "ids": ["swsh1-1", "xy7-54"] }
```

**Example**
```bash
curl -s -X POST 'http://localhost:5000/cards/bulk' \
  -H 'Authorization: Bearer TOKEN' \
  -H 'Content-Type: application/json' \
  --data '{"ids":["swsh1-1","xy7-54"]}'
```

**Errors:** `400` if `ids` missing/not an array/empty after cleaning; `401` unauthorized.

---

### `GET /cards/:id/price/history`  _(requires Timescale)_

Returns time‑series price entries from `PriceHistory` for a card ID.

**Query params**
- `from` – ISO 8601 timestamp (inclusive). Example: `2024-01-01T00:00:00Z`
- `to` – ISO 8601 timestamp (exclusive). Optional.
- `order` – `asc` (default) or `desc`
- `limit` – integer row cap (optional)

**Example**

```bash
curl -s 'http://localhost:5000/cards/swsh1-1/price/history?from=2024-01-01T00:00:00Z&order=desc&limit=200' \
  -H 'Authorization: Bearer TOKEN'
```

**Response**
```json
{
  "cardId": "swsh1-1",
  "count": 2,
  "history": [
    { "time": "2024-01-02T00:00:00+00:00", "averageSellPrice": 0.23, "source": "admin" },
    { "time": "2024-01-01T00:00:00+00:00", "averageSellPrice": 0.22, "source": "admin" }
  ]
}
```

---

### `GET /cards/:id/price/latest`  _(requires Timescale)_

Latest available timeseries point for a card.

**Example**
```bash
curl -s 'http://localhost:5000/cards/swsh1-1/price/latest' \
  -H 'Authorization: Bearer TOKEN'
```

**Response**
```json
{ "cardId": "swsh1-1", "time": "2024-01-02T00:00:00+00:00", "averageSellPrice": 0.23, "source": "admin" }
```
If none: `{ "cardId": "swsh1-1", "latest": null }`

---

## Sorting

_Not implemented._ Add `ORDER BY` in the `/cards` route if needed.

---

## Error codes

- `400 Bad Request` – invalid pagination, invalid numeric filter value, or malformed body
- `401 Unauthorized` – missing/invalid Google ID token
- `404 Not Found` – resource not found (e.g., card ID)

---

## FAQ / Notes

**Can I do `hp_gte=120`?**  
Not by default. `hp` is a **string** column. To enable numeric HP filtering, cast `Card.hp` to an integer in the query builder before applying comparison operators (and ensure non‑numeric values are handled).

**Are string filters case sensitive?**  
They follow DB storage. If you want case‑insensitive behavior, change `==` comparisons to `ilike` / `lower()` in the backend.

**Can I filter by arrays like `types[]`?**  
Not in this version. Add a custom filter that checks membership against the Postgres array (e.g., `Card.types.contains([...])`) if desired.

**How are multiple filters combined?**  
All with **AND** semantics.

**Why PostgreSQL only?**  
The models use Postgres `ARRAY` types and the price history feature expects Timescale/Postgres.

---

## Changelog (this README)

- Clarified Postgres requirement
- Documented **all** supported filters with examples
- Added the Timescale‑based endpoints
- Explicitly noted string vs numeric behavior for `hp`, `level`, `number`
- Kept other sections consistent with the existing project
