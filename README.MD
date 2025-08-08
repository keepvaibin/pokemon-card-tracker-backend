# Pokémon Cards API

This README documents every available API endpoint, the authentication scheme, query filtering, pagination, and typical responses for this Flask + SQLAlchemy service.

---

## Quick Start

### Requirements

* Python 3.10+
* Flask + SQLAlchemy
* A database URL (SQLite by default)
* A Google OAuth **ID token** (from Google Sign-In) for every request

### Environment variables

* `DATABASE_URL` – defaults to `sqlite:///app.db` if unset.&#x20;
* `SECRET_KEY` – Flask secret (defaults to `dev` for local).&#x20;
* `GOOGLE_CLIENT_ID` – your Google OAuth Client ID (required for token verification).&#x20;

### App factory

The Flask app binds SQLAlchemy, registers routes, and (optionally) creates tables on start.&#x20;

---

## Authentication

All endpoints require a **Google OAuth ID token** in the `Authorization` header:

```
Authorization: Bearer <GOOGLE_ID_TOKEN>
```

Tokens are verified server-side using Google’s library and your `GOOGLE_CLIENT_ID`. Invalid or missing tokens return `401`. On success, the verified user info is stored on `g.user`. &#x20;

**401 errors**

* Missing/invalid header → `{"error":"Unauthorized"}`&#x20;
* Bad token → `{"error":"Invalid token"}`&#x20;

---

## Base URL & Versioning

* **Base URL:** (your deployment origin)
* **Versioning:** Not implemented (single version).

---

## Data Model (response shapes)

You will see two shapes of a card:

* **Basic** (list view, used by `GET /cards`) — includes IDs, key attributes, minimal set info, price snapshots, images.  &#x20;
* **Full** (detail view, used by `GET /cards/:id` and `/cards/bulk`) — includes abilities, attacks, weaknesses, resistances, legalities, full set, cardmarket and tcgplayer blocks.   &#x20;

> **Note:** Field names/structure follow the serializers in `routes.py`. If you add fields in the models/serializers, responses will grow accordingly.&#x20;

---

## Pagination

List endpoints use page/size parameters and compute `total_pages`.

* `page` (default `1`) and `page_size` (default `15`, max `100`). Invalid values return `400`.&#x20;
* Response includes: `page`, `page_size`, `total`, `total_pages`, and `cards`.&#x20;

---

## Filtering

### Equality filters (string/ID fields)

Pass as query params (exact match):

* `id`, `name`, `supertype`, `rarity`, `hp`, `level`, `number`, `setId`, `artist`.&#x20;

### Numeric comparison filters

Use suffixes on the keys below: `_<op>` where `<op>` ∈ `_gte`, `_lte`, `_gt`, `_lt`.

Supported numeric keys:

* `hp`, `averageSellPrice`, `trendPrice`, `lowPrice`, `normalMarket`, `holofoilMarket`, `reverseHolofoilMarket`.&#x20;

**Examples**

* `GET /cards?hp_gte=120&rarity=Rare`
* `GET /cards?trendPrice_lte=5.0`
* `GET /cards?normalMarket_gt=0.5&artist=Ken%20Sugimori`

Invalid numeric values return `400`.&#x20;

**Join behavior**
When any filter is supplied, the query left-joins `CardMarket`, `TcgPlayer`, and `TcgPlayerPrices` so price filters work, then applies the `AND` of all filters.&#x20;

---

## Endpoints

### 1) `GET /cards` — List cards (paginated + filters)

Returns a page of **basic** card objects. Supports pagination and the filters above. &#x20;

**Request**

```
GET /cards?page=1&page_size=20&hp_gte=100&rarity=Rare
Authorization: Bearer <GOOGLE_ID_TOKEN>
```

**Response (200)**

```json
{
  "page": 1,
  "page_size": 20,
  "total": 1234,
  "total_pages": 62,
  "cards": [
    {
      "id": "swsh1-1",
      "name": "Bulbasaur",
      "supertype": "Pokémon",
      "subtypes": ["Basic"],
      "level": 5,
      "hp": 60,
      "types": ["Grass"],
      "rarity": "Common",
      "artist": "Mitsuhiro Arita",
      "number": "1",
      "nationalPokedexNumbers": [1],
      "retreatCost": ["Colorless"],
      "createdAt": "2024-01-01T00:00:00",
      "set": { "id": "swsh1", "name": "Sword & Shield", "series": "Sword & Shield" },
      "market": { "averageSellPrice": 0.25, "trendPrice": 0.21, "lowPrice": 0.02 },
      "tcgplayerPrices": { "normalMarket": 0.2, "holofoilMarket": null, "reverseHolofoilMarket": 0.5 },
      "images": { "small": "...", "large": "..." }
    }
  ]
}
```

(Field presence depends on data; see serializer.)&#x20;

**Errors**

* `400 Invalid pagination parameters` for bad `page`/`page_size`.&#x20;
* `400 Invalid numeric value for <key>` for bad numeric filters.&#x20;
* `401` on missing/invalid auth (see Authentication).

**cURL**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards?page=1&page_size=50&hp_gte=100&normalMarket_lte=1.0"
```

---

### 2) `GET /cards/filters` — Filter metadata (ranges & categories)

Provides precomputed **numeric ranges** and **distinct categorical values** to build UIs (sliders, dropdowns).&#x20;

**Ranges include**

* From `Card`: `hp`, `level`, `number`&#x20;
* From `CardMarket`: `averageSellPrice`, `trendPrice`, `lowPrice`&#x20;
* From `TcgPlayerPrices`: `normalLow`, `holofoilLow`, `reverseHolofoilLow`&#x20;

**Categories include**

* `artists`, `rarities`, `supertypes`, `types`, and `sets` (id, name). &#x20;

**Response (200)**

```json
{
  "ranges": {
    "hp": { "min": 30, "max": 340 },
    "level": { "min": 1, "max": 100 },
    "number": { "min": 1, "max": 300 },
    "averageSellPrice": { "min": 0.02, "max": 999.99 },
    "trendPrice": { "min": 0.01, "max": 999.99 },
    "lowPrice": { "min": 0.01, "max": 999.99 },
    "tcgplayer": {
      "normalLow": { "min": 0.01, "max": 999.99 },
      "holofoilLow": { "min": 0.01, "max": 999.99 },
      "reverseHolofoilLow": { "min": 0.01, "max": 999.99 }
    }
  },
  "categories": {
    "artists": ["..."],
    "rarities": ["..."],
    "supertypes": ["..."],
    "types": ["..."],
    "sets": [{ "id": "swsh1", "name": "Sword & Shield" }]
  }
}
```

**cURL**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards/filters"
```

---

### 3) `GET /cards/:id` — Card detail

Returns the **full** card object for a given `card_id`.

* `404` if not found.&#x20;

**cURL**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards/swsh1-1"
```

---

### 4) `POST /cards/bulk` — Batch fetch by IDs

Request body must include `ids` (array of strings). Returns the **full** objects for the found IDs and `count`. &#x20;

**Request**

```json
{
  "ids": ["swsh1-1", "swsh1-2", "xy7-54"]
}
```

**Response (200)**

```json
{
  "count": 3,
  "cards": [ { /* full card */ }, { /* full card */ }, { /* full card */ } ]
}
```

**Errors**

* Missing or non-list `ids` → `400` with message.&#x20;
* Empty/invalid strings after cleaning → `400`.&#x20;

**cURL**

```bash
curl -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"ids":["swsh1-1","swsh1-2"]}' \
     https://api.example.com/cards/bulk
```

---

## Response Field Reference (selected)

### Basic card object (from `GET /cards`)

* Core: `id`, `name`, `supertype`, `subtypes`, `level`, `hp`, `types`, `rarity`, `artist`, `number`, `nationalPokedexNumbers`, `retreatCost`, `createdAt`.&#x20;
* Set (minimal): `id`, `name`, `series`.&#x20;
* Market snapshot: `averageSellPrice`, `trendPrice`, `lowPrice`.&#x20;
* TCGPlayer quick prices: `normalMarket`, `holofoilMarket`, `reverseHolofoilMarket`.&#x20;
* Images: `small`, `large`.&#x20;

### Full card object (from `GET /cards/:id` and `/cards/bulk`)

* Everything above **plus**: evolves, rules, flavorText, full set block (logo, symbol, printedTotal, total, ptcgoCode, releaseDate, updatedAt, legalities), abilities, attacks, weaknesses, resistances, legalities, images, full `cardmarket` (many price stats), full `tcgplayer` (nested prices).   &#x20;

---

## Error Model

* `400` — invalid pagination or numeric filter input; invalid bulk payload (see above).  &#x20;
* `401` — missing or invalid token (see Authentication).&#x20;
* `404` — card not found for `GET /cards/:id`.&#x20;

---

## Sorting

* **Not implemented.** Results are whatever the DB returns given filters/pagination.

---

## Rate Limiting & Caching

* **Not implemented** in the provided code. Add reverse proxy (e.g., Cloudflare) or Flask middleware if needed.

---

## CORS

* **Not configured** in the provided code. If you are calling this from a browser app on a different origin, add Flask-CORS.

---

## Running Locally

Typical pattern:

```bash
export GOOGLE_CLIENT_ID="your.apps.googleusercontent.com"
export FLASK_APP="yourpackage:create_app"
export FLASK_ENV=development
flask run
```

Tables are auto-created in app context for local dev. (Remove or gate in production.)&#x20;

---

## Example Flows

### Web client (Google Sign-In)

1. Obtain a **Google ID token** in the browser (Google Identity Services).
2. Call API endpoints with `Authorization: Bearer <ID_TOKEN>`. &#x20;

### Building a filters UI

* Call `GET /cards/filters` to populate sliders (`hp`, price ranges) and dropdowns (`artists`, `rarities`, `types`, `sets`). Then query `GET /cards` with equality + numeric suffix filters to narrow results.  &#x20;

---

## Security Notes

* Only **Google ID tokens** issued by `accounts.google.com` are accepted. Issuer is verified.&#x20;
* Keep `SECRET_KEY` and `GOOGLE_CLIENT_ID` secret. Use secure production values. &#x20;

---

## Change Log / Extensibility

* New fields: extend serializers in `routes.py`.&#x20;
* New filters: add to `allowed_filters` or `allowed_numeric_filters` and ensure joins include target tables.  &#x20;

---

## Glossary of Price Fields (selected)

* **Cardmarket**: `averageSellPrice`, `trendPrice`, `lowPrice`, `lowPriceExPlus`, `avg1/7/30`, `reverseHolo*` variants, etc.&#x20;
* **TCGPlayer**: Prices for `normal`, `holofoil`, `reverseHolofoil` tiers: `Low`, `Mid`, `High`, `Market`, `DirectLow`.&#x20;

---

## FAQ

**Q: Can I search by partial name?**
A: Not in the current code (only exact equality on `name`). Consider adding `ilike` for substring search to `GET /cards`.

**Q: Can I sort results?**
A: Not yet; add `order_by` support in the list endpoint.

**Q: Do I need separate OAuth for server-to-server?**
A: As written, the API expects a Google **ID** token (user sign-in). For service-to-service, you could accept and verify Google service account **JWTs** with a different verifier.

---

## Handy cURL Cheatsheet

* List rare cards with HP ≥ 120, 50 per page:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards?rarity=Rare&hp_gte=120&page_size=50"
```

* Get price-capped search (trend ≤ \$5):

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards?trendPrice_lte=5"
```

* Fetch detail for a single card:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.example.com/cards/swsh1-1"
```

* Bulk by IDs:

```bash
curl -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"ids":["swsh1-1","xy7-54"]}' \
  https://api.example.com/cards/bulk
```
