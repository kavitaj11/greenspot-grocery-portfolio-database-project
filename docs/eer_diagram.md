# EER Diagram - Greenspot Grocer Database
## Visual Database Schema Documentation

---

## ASCII EER Diagram (Detailed)

```
╔═══════════════════════════════════════════════════════════════════════════════════╗
║                           GREENSPOT GROCER DATABASE SCHEMA                        ║
║                          Extended Entity-Relationship Diagram                     ║
╚═══════════════════════════════════════════════════════════════════════════════════╝

┌─────────────────────────────┐
│     PRODUCT_CATEGORIES      │
├─────────────────────────────┤
│ 🔑 category_id INT(11) PK   │ ◄──┐
│   category_name VARCHAR(50) │    │
│   description TEXT          │    │ 1:M
│   created_at TIMESTAMP      │    │
└─────────────────────────────┘    │
                                   │
┌─────────────────────────────┐    │  ┌─────────────────────────────┐
│          VENDORS            │    │  │         PRODUCTS            │
├─────────────────────────────┤    │  ├─────────────────────────────┤
│ 🔑 vendor_id INT(11) PK     │ ◄──┼──┤ 🔑 product_id INT(11) PK    │
│   vendor_name VARCHAR(100)  │    │  │   product_name VARCHAR(100) │
│   address TEXT              │    │  │ 🔗 category_id INT(11) FK   │ ──┘
│   city VARCHAR(50)          │    │  │   unit_of_measure VARCHAR(20)│
│   state VARCHAR(20)         │    │  │   location_code VARCHAR(10) │
│   zip_code VARCHAR(10)      │ 1:M│  │ 🔗 primary_vendor_id INT FK │ ──┘
│   phone VARCHAR(20)         │    │  │   created_at TIMESTAMP      │
│   email VARCHAR(100)        │    │  │   updated_at TIMESTAMP      │
│   created_at TIMESTAMP      │    │  └─────────────────────────────┘
└─────────────────────────────┘    │                 │
           │                       │                 │ 1:1
           │                       │                 ▼
           │                       │  ┌─────────────────────────────┐
           │ 1:M                   │  │         INVENTORY           │
           │                       │  ├─────────────────────────────┤
           │                       │  │ 🔑 inventory_id INT(11) PK  │
           │                       │  │ 🔗 product_id INT(11) FK UQ │ ◄─┘
           │                       │  │   quantity_on_hand INT      │
           │                       │  │   reorder_level INT         │
           │                       │  │   max_stock_level INT       │
           │                       │  │   last_updated TIMESTAMP    │
           │                       │  └─────────────────────────────┘
           │                       │
           │                       │
           ▼                       │
┌─────────────────────────────┐    │
│     PURCHASE_ORDERS         │    │
├─────────────────────────────┤    │
│ 🔑 purchase_id INT(11) PK   │    │
│ 🔗 product_id INT(11) FK    │ ───┼─────────────────┐
│ 🔗 vendor_id INT(11) FK     │ ◄──┘                 │
│   quantity_ordered INT      │                      │ M:1
│   unit_cost DECIMAL(10,2)   │                      │
│   total_cost DECIMAL(10,2)  │ GENERATED            │
│   purchase_date DATE        │                      │
│   received_date DATE        │                      │
│   status ENUM(...)          │                      │
│   notes TEXT                │                      │
│   created_at TIMESTAMP      │                      │
└─────────────────────────────┘                      │
                                                     │
                                                     │
┌─────────────────────────────┐               ┌─────┴───────────────────────┐
│        CUSTOMERS            │               │    SALES_TRANSACTIONS       │
├─────────────────────────────┤               ├─────────────────────────────┤
│ 🔑 customer_id INT(11) PK   │ ◄─────────────┤ 🔑 transaction_id INT(11) PK│
│   first_name VARCHAR(50)    │          1:M  │ 🔗 product_id INT(11) FK    │ ◄─┘
│   last_name VARCHAR(50)     │               │ 🔗 customer_id INT(11) FK   │
│   email VARCHAR(100)        │               │   quantity_sold INT         │
│   phone VARCHAR(20)         │               │   unit_price DECIMAL(10,2)  │
│   address TEXT              │               │   total_amount DECIMAL(10,2)│ GENERATED
│   city VARCHAR(50)          │               │   sale_date DATE            │
│   state VARCHAR(20)         │               │   transaction_time TIME     │
│   zip_code VARCHAR(10)      │               │   payment_method ENUM(...)  │
│   registration_date DATE    │               │   created_at TIMESTAMP      │
│   created_at TIMESTAMP      │               └─────────────────────────────┘
└─────────────────────────────┘                            │
                                                           │ M:1
                                                           │
                                  ┌────────────────────────┘
                                  │
                    ┌─────────────▼───────────────┐
                    │         PRODUCTS            │
                    │      (Reference Only)       │
                    └─────────────────────────────┘

╔═══════════════════════════════════════════════════════════════════════════════════╗
║                                    LEGEND                                         ║
╠═══════════════════════════════════════════════════════════════════════════════════╣
║ 🔑 PK = Primary Key          🔗 FK = Foreign Key         UQ = Unique Constraint   ║
║ 1:1 = One-to-One            1:M = One-to-Many           M:1 = Many-to-One        ║
║ GENERATED = Computed Column  ENUM = Enumeration Values                           ║
╚═══════════════════════════════════════════════════════════════════════════════════╝
```

---

## Relationship Matrix

| Parent Table | Child Table | Relationship Type | Foreign Key | Constraint |
|-------------|-------------|------------------|-------------|------------|
| **PRODUCT_CATEGORIES** | PRODUCTS | 1:M | category_id | CASCADE |
| **VENDORS** | PRODUCTS | 1:M | primary_vendor_id | SET NULL |
| **PRODUCTS** | INVENTORY | 1:1 | product_id | CASCADE + UNIQUE |
| **PRODUCTS** | PURCHASE_ORDERS | 1:M | product_id | CASCADE |
| **VENDORS** | PURCHASE_ORDERS | 1:M | vendor_id | CASCADE |
| **PRODUCTS** | SALES_TRANSACTIONS | 1:M | product_id | CASCADE |
| **CUSTOMERS** | SALES_TRANSACTIONS | 1:M | customer_id | SET NULL |

---

## Entity Specifications

### Primary Entities (Strong Entities)
1. **PRODUCT_CATEGORIES** - Independent category master
2. **VENDORS** - Independent vendor master  
3. **CUSTOMERS** - Independent customer master

### Dependent Entities (Weak/Associative Entities)
4. **PRODUCTS** - Depends on CATEGORIES and VENDORS
5. **INVENTORY** - Depends on PRODUCTS (1:1 relationship)
6. **PURCHASE_ORDERS** - Transaction entity linking PRODUCTS ↔ VENDORS
7. **SALES_TRANSACTIONS** - Transaction entity linking PRODUCTS ↔ CUSTOMERS

---

## Data Flow Visualization

```
RAW CSV DATA
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                  ETL TRANSFORMATION                         │
├─────────────────────────────────────────────────────────────┤
│ 1. Parse vendor addresses → VENDORS table                  │
│ 2. Extract categories → PRODUCT_CATEGORIES table           │
│ 3. Normalize products → PRODUCTS table                     │
│ 4. Generate customer records → CUSTOMERS table             │
│ 5. Create inventory snapshots → INVENTORY table            │
│ 6. Split purchase transactions → PURCHASE_ORDERS table     │
│ 7. Split sales transactions → SALES_TRANSACTIONS table     │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│              NORMALIZED DATABASE                            │
├─────────────────────────────────────────────────────────────┤
│ ✅ 3rd Normal Form (3NF) compliance                        │
│ ✅ ACID transaction properties                              │
│ ✅ Referential integrity enforced                          │
│ ✅ Business rules implemented as constraints               │
│ ✅ Optimized for OLTP and OLAP workloads                  │
└─────────────────────────────────────────────────────────────┘
```

---

## Database Statistics (After Implementation)

| Table | Records | Relationships | Indexes | Constraints |
|-------|---------|---------------|---------|-------------|
| **product_categories** | 4 | Parent to 13 products | 2 | PK, UNIQUE |
| **vendors** | 8 | Parent to 13 products, 15 orders | 2 | PK |
| **products** | 13 | Central hub entity | 4 | PK, 2 FKs |
| **customers** | 10 | Parent to 13 transactions | 2 | PK |
| **inventory** | 13 | 1:1 with products | 3 | PK, FK, UNIQUE |
| **purchase_orders** | 15 | Links products ↔ vendors | 4 | PK, 2 FKs |
| **sales_transactions** | 13 | Links products ↔ customers | 4 | PK, 2 FKs |
| **TOTAL** | **76** | **7 relationships** | **21** | **14** |

This EER diagram demonstrates a properly normalized database design that eliminates the data anomalies present in the original flat-file structure while maintaining all business relationships and supporting complex analytical queries.