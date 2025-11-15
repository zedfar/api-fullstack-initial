# Users API - Features Documentation

## Overview
Users API sekarang sudah mendukung:
- ✅ **Pagination Metadata** (total count, page info)
- ✅ **Sorting** (by username, email, full_name, created_at)
- ✅ **Enhanced Search** (username, email, full_name)

Semua fitur tanpa perubahan tabel database.

---

## 1. Pagination with Metadata

### Response Format

GET all users sekarang mengembalikan response dengan format:

```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "username": "johndoe",
      "email": "john@example.com",
      "full_name": "John Doe",
      "is_active": true,
      "role_id": "...",
      "role": {
        "id": "...",
        "name": "admin",
        "description": "Administrator role"
      },
      "created_at": "2025-01-15T10:00:00",
      "updated_at": "2025-01-15T10:00:00"
    }
  ],
  "metadata": {
    "total": 45,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 5
  }
}
```

### Metadata Fields

| Field | Type | Description |
|-------|------|-------------|
| `total` | int | Total number of users (after filtering) |
| `skip` | int | Number of records skipped |
| `limit` | int | Number of records per page |
| `page` | int | Current page number (1-indexed) |
| `total_pages` | int | Total number of pages |

### Example Usage

```bash
# Get page 1 (first 10 users)
GET /api/v1/users?skip=0&limit=10

# Get page 2
GET /api/v1/users?skip=10&limit=10

# Get page 3 with 20 users per page
GET /api/v1/users?skip=40&limit=20
```

---

## 2. Sorting Feature

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `sort_by` | string | null | Field untuk sorting: `username`, `email`, `full_name`, `created_at` |
| `order` | string | `asc` | Sort order: `asc` (ascending) atau `desc` (descending) |

### Examples

#### Sort by username (A-Z)
```
GET /api/v1/users?sort_by=username&order=asc
```

#### Sort by email (Z-A)
```
GET /api/v1/users?sort_by=email&order=desc
```

#### Sort by full name (A-Z)
```
GET /api/v1/users?sort_by=full_name&order=asc
```

#### Sort by created date (newest first)
```
GET /api/v1/users?sort_by=created_at&order=desc
```

**Use case:** Admin dashboard showing recently registered users

#### Sort by created date (oldest first)
```
GET /api/v1/users?sort_by=created_at&order=asc
```

**Use case:** View earliest registered users

---

## 3. Search Feature

### Enhanced Search

Search sekarang mencari di **3 fields**:
- `username`
- `email`
- `full_name`

### Query Parameter

| Parameter | Type | Description |
|-----------|------|-------------|
| `search` | string | Search term (case-insensitive) |

### Examples

#### Search by username
```
GET /api/v1/users?search=john
```

Finds: `johndoe`, `johnsmith`, `admin_john`

#### Search by email
```
GET /api/v1/users?search=gmail.com
```

Finds all users with Gmail addresses

#### Search by full name
```
GET /api/v1/users?search=doe
```

Finds: "John Doe", "Jane Doe", etc.

### Search Behavior

- **Case-insensitive**: `JOHN`, `john`, `JoHn` all match
- **Partial match**: `joh` matches `john`, `johnny`, `johndoe`
- **OR logic**: Searches across username, email, AND full_name
- Result includes `metadata.total` showing how many users match the search

---

## 4. Combined Usage Examples

### Example 1: Search and paginate
```
GET /api/v1/users?search=admin&skip=0&limit=10
```

Response:
```json
{
  "data": [
    { "username": "admin", "email": "admin@example.com", ... },
    { "username": "admin_user", "email": "admin@company.com", ... }
  ],
  "metadata": {
    "total": 15,    // 15 users match "admin"
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 2
  }
}
```

**Use case:** Admin panel user search with pagination

### Example 2: Sort users by registration date (page 2)
```
GET /api/v1/users?sort_by=created_at&order=desc&skip=10&limit=10
```

**Use case:** View recently registered users (second page)

### Example 3: Search and sort
```
GET /api/v1/users?search=example.com&sort_by=username&order=asc
```

**Use case:** Find all users from a specific domain, sorted alphabetically

### Example 4: Full-featured query
```
GET /api/v1/users?search=john&sort_by=created_at&order=desc&skip=0&limit=20
```

This will:
1. Search for "john" in username, email, or full_name
2. Sort by created date (newest first)
3. Return first 20 results
4. Include total count in metadata

---

## 5. Common Use Cases

### Use Case 1: User Management Dashboard

**Requirement:** Display all users with pagination and sorting

```bash
# Initial load - newest users first
GET /api/v1/users?sort_by=created_at&order=desc&skip=0&limit=20

# Next page
GET /api/v1/users?sort_by=created_at&order=desc&skip=20&limit=20
```

### Use Case 2: User Search

**Requirement:** Search for specific users

```bash
# Search by username
GET /api/v1/users?search=john&skip=0&limit=10

# Search by email domain
GET /api/v1/users?search=@company.com&skip=0&limit=10
```

### Use Case 3: User Directory (Alphabetical)

**Requirement:** Display all users alphabetically by name

```bash
GET /api/v1/users?sort_by=full_name&order=asc&skip=0&limit=50
```

### Use Case 4: Recent Registrations Report

**Requirement:** Show latest registered users

```bash
GET /api/v1/users?sort_by=created_at&order=desc&skip=0&limit=100
```

---

## 6. Technical Details

### No Database Changes
- ✅ No table modifications required
- ✅ No migrations needed
- ✅ All features use existing columns

### Performance Notes
- All sorting done at **database level** (efficient, no client-side processing)
- Total count query is optimized and runs **before** eager loading relationships
- Pagination with `skip`/`limit` prevents loading entire dataset
- Search uses SQL `ILIKE` for case-insensitive partial matching
- Indexes on `username`, `email`, and `created_at` columns improve query performance

### Pagination Implementation
- Total count calculated using `COUNT(*)` query (efficient)
- Total count respects search filter
- Page calculation: `page = (skip / limit) + 1`
- Total pages: `ceil(total / limit)`
- Works correctly with all sorting and filtering options

### Search Implementation

Search uses SQL OR condition across 3 fields:

```sql
WHERE
  username ILIKE '%search_term%' OR
  email ILIKE '%search_term%' OR
  full_name ILIKE '%search_term%'
```

### Sorting Implementation

Sort columns mapped to database columns:

| sort_by value | Database Column |
|---------------|-----------------|
| `username` | `users.username` |
| `email` | `users.email` |
| `full_name` | `users.full_name` |
| `created_at` | `users.created_at` |

---

## 7. API Endpoints Summary

### GET /api/v1/users

**Query Parameters:**

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `skip` | int | No | 0 | Number of records to skip |
| `limit` | int | No | 10 | Number of records per page (max: 100) |
| `search` | string | No | null | Search term |
| `sort_by` | string | No | null | Sort field: username, email, full_name, created_at |
| `order` | string | No | asc | Sort order: asc or desc |

**Response:** `PaginatedUserResponse`

```json
{
  "data": [UserResponse],
  "metadata": {
    "total": int,
    "skip": int,
    "limit": int,
    "page": int,
    "total_pages": int
  }
}
```

**Authentication:** Required (Bearer token)

---

## 8. Frontend Implementation Example

### React Example

```javascript
import { useState, useEffect } from 'react';

function UserList() {
  const [users, setUsers] = useState([]);
  const [metadata, setMetadata] = useState(null);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [sortBy, setSortBy] = useState('created_at');
  const [order, setOrder] = useState('desc');
  const pageSize = 20;

  useEffect(() => {
    fetchUsers();
  }, [page, search, sortBy, order]);

  const fetchUsers = async () => {
    const skip = (page - 1) * pageSize;
    const params = new URLSearchParams({
      skip,
      limit: pageSize,
      sort_by: sortBy,
      order
    });

    if (search) {
      params.append('search', search);
    }

    const response = await fetch(
      `/api/v1/users?${params}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    );

    const { data, metadata } = await response.json();
    setUsers(data);
    setMetadata(metadata);
  };

  return (
    <div>
      {/* Search */}
      <input
        type="text"
        placeholder="Search users..."
        value={search}
        onChange={(e) => {
          setSearch(e.target.value);
          setPage(1); // Reset to page 1 on search
        }}
      />

      {/* Sort controls */}
      <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
        <option value="username">Username</option>
        <option value="email">Email</option>
        <option value="full_name">Full Name</option>
        <option value="created_at">Registration Date</option>
      </select>

      <select value={order} onChange={(e) => setOrder(e.target.value)}>
        <option value="asc">Ascending</option>
        <option value="desc">Descending</option>
      </select>

      {/* User table */}
      <table>
        <thead>
          <tr>
            <th>Username</th>
            <th>Email</th>
            <th>Full Name</th>
            <th>Role</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {users.map(user => (
            <tr key={user.id}>
              <td>{user.username}</td>
              <td>{user.email}</td>
              <td>{user.full_name}</td>
              <td>{user.role?.name}</td>
              <td>{user.is_active ? 'Active' : 'Inactive'}</td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* Pagination */}
      {metadata && (
        <div>
          <p>
            Showing {metadata.skip + 1} - {Math.min(metadata.skip + metadata.limit, metadata.total)}
            of {metadata.total} users
          </p>

          <button
            disabled={page === 1}
            onClick={() => setPage(page - 1)}
          >
            Previous
          </button>

          <span>Page {metadata.page} of {metadata.total_pages}</span>

          <button
            disabled={page === metadata.total_pages}
            onClick={() => setPage(page + 1)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}
```

---

## 9. Error Handling

### Invalid Query Parameters

```bash
# limit > 100 (exceeds max)
GET /api/v1/users?limit=200
```

**Response:** `422 Unprocessable Entity`

```json
{
  "detail": [
    {
      "loc": ["query", "limit"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

### Invalid sort_by Field

```bash
GET /api/v1/users?sort_by=invalid_field
```

**Response:** Query executes but `sort_by` is ignored (no error)

---

## 10. Migration from Old API

### Old Response Format
```json
[
  { "id": "...", "username": "john", ... },
  { "id": "...", "username": "jane", ... }
]
```

### New Response Format
```json
{
  "data": [
    { "id": "...", "username": "john", ... },
    { "id": "...", "username": "jane", ... }
  ],
  "metadata": {
    "total": 45,
    "skip": 0,
    "limit": 10,
    "page": 1,
    "total_pages": 5
  }
}
```

### Migration Guide

**Before:**
```javascript
const users = await response.json();
users.forEach(user => { /* ... */ });
```

**After:**
```javascript
const { data, metadata } = await response.json();
data.forEach(user => { /* ... */ });

// Now you can also use metadata for pagination
console.log(`Total users: ${metadata.total}`);
console.log(`Page ${metadata.page} of ${metadata.total_pages}`);
```

---

## Questions?

For issues or feature requests, contact the development team.
