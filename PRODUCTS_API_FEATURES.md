# Products API - New Features Documentation

## Overview
Products API sekarang sudah mendukung:
- ✅ **Pagination Metadata** (total count, page info)
- ✅ **Sorting** (by name, stock, price, created_at, status)
- ✅ **Filtering** (by stock_status, price range, category, search)
- ✅ **Stock Status Indicator** (red/yellow/green)

Semua fitur tanpa perubahan tabel database.

---

## 1. Pagination with Metadata

### Response Format

GET all products sekarang mengembalikan response dengan format:

```json
{
  "data": [
    {
      "id": "...",
      "name": "Gaming Laptop",
      "price": 15000000,
      "stock": 5,
      "low_stock_threshold": 10,
      "stock_status": "yellow",
      ...
    }
  ],
  "metadata": {
    "total": 156,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 16
  }
}
```

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of records (after filtering) |
| `skip` | int | Number of records skipped |
| `limit` | int | Number of records per page |
| `page` | int | Current page number (1-indexed) |
| `total_pages` | int | Total number of pages |

### Example Usage

```bash
# Get page 1 (first 10 items)
GET /api/v1/products?skip=0&limit=10

# Get page 2
GET /api/v1/products?skip=10&limit=10

# Get page 3 with 20 items per page
GET /api/v1/products?skip=40&limit=20
```

---

## 2. Filtering Features

### Available Filters

| Parameter | Type | Description | Example Values |
|-----------|------|-------------|----------------|
| `search` | string | Search by product name (case-insensitive) | `laptop`, `gaming` |
| `category_id` | UUID | Filter by category | `550e8400-e29b-41d4-...` |
| `stock_status` | string | Filter by stock status | `red`, `yellow`, `green` |
| `min_price` | float | Minimum price (inclusive) | `100000`, `500000` |
| `max_price` | float | Maximum price (inclusive) | `2000000`, `5000000` |

### Filter Examples

#### Filter by Stock Status

**Get all out-of-stock products (red):**
```
GET /api/v1/products?stock_status=red
```

Returns only products where `stock == 0`

**Get all low-stock products (yellow):**
```
GET /api/v1/products?stock_status=yellow
```

Returns only products where `0 < stock <= low_stock_threshold`

**Get all healthy-stock products (green):**
```
GET /api/v1/products?stock_status=green
```

Returns only products where `stock > low_stock_threshold`

**Use case:** Inventory management - quickly find products that need restocking

#### Filter by Price Range

**Get products between Rp 1,000,000 and Rp 5,000,000:**
```
GET /api/v1/products?min_price=1000000&max_price=5000000
```

**Get products above Rp 10,000,000:**
```
GET /api/v1/products?min_price=10000000
```

**Get products below Rp 500,000:**
```
GET /api/v1/products?max_price=500000
```

**Use case:** Product catalog with price range slider

#### Combine Multiple Filters

**Low-stock products in specific price range:**
```
GET /api/v1/products?stock_status=yellow&min_price=100000&max_price=1000000
```

**Out-of-stock products in specific category:**
```
GET /api/v1/products?stock_status=red&category_id=xxx
```

**Search with price range:**
```
GET /api/v1/products?search=laptop&min_price=5000000&max_price=15000000
```

---

## 3. Sorting Feature

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort_by` | string | null | Field untuk sorting: `name`, `stock`, `price`, `created_at`, `status` |
| `order` | string | `asc` | Sort order: `asc` (ascending) atau `desc` (descending) |

**Note:** Saat `sort_by=status`:
- `order=asc`: Urutkan red → yellow → green (produk urgent dulu)
- `order=desc`: Urutkan green → yellow → red (produk sehat dulu)

### Examples

#### Sort by name (A-Z)
```
GET /api/v1/products?sort_by=name&order=asc
```

#### Sort by price (highest first)
```
GET /api/v1/products?sort_by=price&order=desc
```

#### Sort by stock (lowest first)
```
GET /api/v1/products?sort_by=stock&order=asc
```

#### Sort by created date (newest first)
```
GET /api/v1/products?sort_by=created_at&order=desc
```

#### Sort by stock status (urgent first: red → yellow → green)
```
GET /api/v1/products?sort_by=status&order=asc
```

**Use case:** Dashboard yang ingin menampilkan produk yang perlu restocking dulu

#### Sort by stock status (healthy first: green → yellow → red)
```
GET /api/v1/products?sort_by=status&order=desc
```

**Use case:** Report inventory yang menampilkan produk dengan stok sehat terlebih dahulu

#### Combine with search and filter
```
GET /api/v1/products?search=laptop&category_id=xxx&sort_by=price&order=asc
```

---

## 2. Stock Status Indicator

### Overview
Setiap product response sekarang include field `stock_status` yang computed secara otomatis berdasarkan stock level.

### Status Colors

| Status | Color | Condition | Meaning |
|--------|-------|-----------|---------|
| `red` | 🔴 | `stock == 0` | Out of stock |
| `yellow` | 🟡 | `0 < stock <= low_stock_threshold` | Low stock warning |
| `green` | 🟢 | `stock > low_stock_threshold` | Healthy stock |

### Response Example

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "Gaming Laptop",
  "description": "High performance laptop",
  "price": 15000000,
  "stock": 5,
  "low_stock_threshold": 10,
  "stock_status": "yellow",
  "image_url": "https://example.com/laptop.jpg",
  "category_id": "...",
  "creator": {
    "id": "...",
    "username": "admin",
    "email": "admin@example.com"
  },
  "category": {
    "id": "...",
    "name": "Electronics"
  },
  "created_at": "2025-01-15T10:00:00",
  "updated_at": "2025-01-15T10:00:00"
}
```

### Use Cases

#### 1. Display stock status in UI
```javascript
// Frontend example
const getStockColor = (status) => {
  switch(status) {
    case 'red': return '#EF4444'; // Red
    case 'yellow': return '#F59E0B'; // Yellow
    case 'green': return '#10B981'; // Green
  }
};
```

#### 2. Filter products by stock status
```javascript
// Client-side filtering
const lowStockProducts = products.filter(p => p.stock_status === 'yellow' || p.stock_status === 'red');
const outOfStockProducts = products.filter(p => p.stock_status === 'red');
```

#### 3. Dashboard alerts
```javascript
// Show alerts for low/out of stock
const needsAttention = products.filter(p => p.stock_status !== 'green');
if (needsAttention.length > 0) {
  alert(`${needsAttention.length} products need restocking!`);
}
```

---

## 4. Combined Usage Examples

### Example 1: Get products that need attention (sorted by urgency) with pagination
```
GET /api/v1/products?sort_by=status&order=asc&skip=0&limit=20
```

Response:
```json
{
  "data": [
    { "name": "Product A", "stock": 0, "stock_status": "red", ... },
    { "name": "Product B", "stock": 3, "stock_status": "yellow", ... },
    ...
  ],
  "metadata": {
    "total": 156,
    "skip": 0,
    "limit": 20,
    "page": 1,
    "total_pages": 8
  }
}
```

This is perfect for inventory management dashboards!

### Example 2: Get products by category sorted by price (page 2)
```
GET /api/v1/products?category_id=xxx&sort_by=price&order=asc&skip=10&limit=10
```

### Example 3: Search with pagination
```
GET /api/v1/products?search=laptop&skip=0&limit=10
```

Response includes `metadata.total` showing how many products match "laptop".

### Example 4: Full-featured query
```
GET /api/v1/products?search=gaming&category_id=xxx&sort_by=price&order=desc&skip=20&limit=10
```

This will:
1. Search for "gaming" in product names
2. Filter by category
3. Sort by price (highest first)
4. Return page 3 (skip 20, limit 10)
5. Include total count in metadata

---

## 5. Technical Details

### No Database Changes
- ✅ No table modifications required
- ✅ No migrations needed
- ✅ `stock_status` is computed at response time using Pydantic's `@computed_field`
- ✅ Sorting (including `sort_by=status`) uses SQLAlchemy's `order_by()` and `case()` expressions at database level
- ✅ Status sorting uses SQL CASE statement to compute priority from `stock` and `low_stock_threshold` columns

### How Status Sorting Works

Status sorting menggunakan SQL `CASE` expression yang mengubah stock status menjadi priority number:

```sql
CASE
  WHEN stock = 0 THEN 0              -- red (most urgent)
  WHEN stock <= low_stock_threshold THEN 1  -- yellow
  ELSE 2                              -- green (least urgent)
END
```

**Example Data:**

| Product | Stock | Threshold | Status | Priority |
|---------|-------|-----------|--------|----------|
| Laptop A | 0 | 10 | red | 0 |
| Mouse B | 5 | 10 | yellow | 1 |
| Keyboard C | 3 | 10 | yellow | 1 |
| Monitor D | 20 | 10 | green | 2 |

**Sorting Results:**

- `sort_by=status&order=asc`: Laptop A (red) → Mouse B (yellow) → Keyboard C (yellow) → Monitor D (green)
- `sort_by=status&order=desc`: Monitor D (green) → Mouse B (yellow) → Keyboard C (yellow) → Laptop A (red)

### Performance Notes
- All sorting (including status) is done at **database level** (efficient, no client-side processing)
- `stock_status` in response is computed per product (minimal overhead)
- Total count query is optimized and runs **before** eager loading relationships
- Pagination with `skip`/`limit` prevents loading entire dataset
- Indexes on `stock` and `low_stock_threshold` columns can improve status sorting performance

### Pagination Implementation
- Total count calculated using `COUNT(*)` query (efficient)
- Total count respects all filters (search, category_id)
- Page calculation: `page = (skip / limit) + 1`
- Total pages: `ceil(total / limit)`
- Works correctly with all sorting and filtering options

### Customization
To change stock thresholds, update `low_stock_threshold` field per product:

```json
PUT /api/v1/products/{product_id}
{
  "low_stock_threshold": 20
}
```

Now products with `stock <= 20` will show yellow status.

---

## Questions?

For issues or feature requests, contact the development team.
