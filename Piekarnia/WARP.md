# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Environment and dependencies

- Python desktop application built with **PySide6** and **SQLAlchemy**.
- Local SQLite database stored in `database.db` at the project root.
- Python dependencies are listed in `requirements.txt` (PySide6, SQLAlchemy, bcrypt, reportlab, optional alembic).

To install dependencies:

```bash
pip install -r requirements.txt
```

## Common commands

All commands assume the working directory is the project root (`Piekarnia`).

- **Run the application** (starts the Qt GUI, initializes DB and sample data if needed):

  ```bash
  python -m app.main
  ```

- **Reset/recreate the database schema** (drops existing `database.db` and recreates tables):

  ```bash
  python docs/typczasowy.py
  ```

- **Initialize tables and seed sample data without resetting the DB file** (this also happens automatically when running the app):

  ```bash
  python -c "from app.main import main; main()"
  ```

> Note: There is currently **no dedicated test suite or linting configuration** in this repository, so there are no standard commands for running tests or linters yet.

## High-level architecture

### Entry point and application bootstrap

- **`app/main.py`** is the GUI entry point:
  - Calls `init_db()`, `init_sample_data()`, `create_default_admin()`, `create_guest_user()` from `app.db.initialization`.
  - Changes the working directory to the `app/` folder so that resource paths (e.g. `ui/resources/style.qss`) resolve correctly.
  - Creates a `QApplication`, applies the global stylesheet from `app/ui/resources/style.qss`, and opens `LoginWindow` from `app.ui.login_window`.

- The project root contains `database.db`, which is the SQLite file used via SQLAlchemy.

### Configuration and database layer

- **`app/config.py`** defines `DATABASE_URL`, currently pointing to the SQLite file one level above the `app` folder.
- **`app/db/database.py`**:
  - Builds the SQLAlchemy `engine` from `DATABASE_URL`.
  - Exposes `SessionLocal` (session factory) used by higher-level data access modules.
  - Provides a simple `init_db()` helper to create all tables.
- **`app/db/models.py`** defines the ORM models on a shared `Base`:
  - `User`: login (`username`), bcrypt `password_hash` (stored as `LargeBinary`), `role` (e.g. `user`, `admin`, `guest`), unique `email`, optional `credit_card`.
  - `Product`: basic catalog item with `name` and `price`.
  - `Sale`: links a `User` to a `Product` with `quantity`, and sets up relationships back to both.
- **`app/db/db_api.py`** is the main data-access façade over `SessionLocal` and the models:
  - User queries and creation (`get_user_by_username`, `get_user_by_email`, `create_user`, `get_all_users`).
  - Product CRUD (`get_all_products`, `add_product`, `get_product_by_id`, `update_product`, `delete_product`).
  - Sales creation and retrieval (`add_sale`, `get_sales`, `get_sales_by_user_id`), with `joinedload` to eagerly fetch `Sale.product` for reporting/UIs.
- **`app/db/initialization.py`** contains DB bootstrapping logic:
  - `init_db()` creates tables.
  - `init_sample_data()` seeds a default set of bakery products if none exist.
  - `create_default_admin()` ensures an admin user with login `a` exists.
  - `create_guest_user()` ensures a `guest` account exists for guest checkout flows.
- **`docs/typczasowy.py`** is a maintenance script that deletes `database.db` (if present) and recreates tables via `Base.metadata.create_all(bind=engine)`.

### Authentication and user management

- **`app/auth/auth_utils.py`**:
  - Wraps `bcrypt` for password hashing (`hash_password`) and verification (`verify_password`).
  - Provides a low-level `login_user(username, password)` that checks credentials using `db_api.get_user_by_username`.
- **`app/auth/auth_service.py`** builds on `auth_utils` and `db_api` to provide higher-level flows:
  - `login_user(username, password)` returns a `User` ORM object on success or `None` on failure.
  - `register_user(username, password, email, credit_card)` validates uniqueness of username and email, enforces a non-empty email, hashes the password, and persists a new `User`.
- **`app/admin/admin_service.py`** exposes admin-only operations on users:
  - Retrieval of all users, deletion, in-place editing of username/email with uniqueness checks, and role changes.

### UI layers (PySide6)

The UI is split between a login/registration flow, the main customer-facing window, and an admin panel.

- **`app/ui/login_window.py`** (`LoginWindow`):
  - Entry UI after app bootstrap.
  - Uses `auth_service.login_user` to authenticate and, on success, opens `MainWindow` with the authenticated `User`.
  - Provides navigation to `RegistrationWindow` and a "continue as guest" flow using the `guest` user from the DB.

- **`app/ui/registration_window.py`** (`RegistrationWindow`):
  - Collects username, email, optional credit card, and password + confirmation.
  - Validates required fields and calls `auth_service.register_user`; on success, informs the user and closes.

- **`app/ui/main_window.py`** (`MainWindow`):
  - Central window shown after login/guest selection.
  - Behavior splits on `user.role`:
    - For `admin`, immediately delegates to the admin panel (`UsersWindow` from `app.admin.users_window`) and closes itself.
    - For non-admin users, builds the main shopping UI:
      - Top menu with logout and username display.
      - Left panel: scrollable list of products built from `db_api.get_all_products()`; each entry shows an image (`ui/resources/250.png`), name, description placeholder, quantity selector, and "Add" button.
      - Right panel: cart list, dynamically updated when products are added.
  - Checkout behavior (`checkout` method):
    - If the user is `guest` or has no persisted credit card, opens `CardPaymentWindow` (from `app.ui.card_payment_window`) and uses a callback to either register `Sale` records for the `guest` user or update the in-memory user credit card.
    - If the user already has a credit card set, aggregates cart items by product and writes `Sale` entries directly via `db_api.add_sale`.

- **`app/ui/card_payment_window.py`** (`CardPaymentWindow`):
  - Simple dialog prompting for a credit card number; on confirmation, executes a callback provided by the caller (e.g., to register sales or persist card data) and closes.

- **`app/ui/products_window.py`** and **`app/ui/sales_window.py`**:
  - Auxiliary windows for listing products and registering a simple sale for a given user, using the same `db_api` helpers.

- **`app/ui/dialogs.py`**:
  - Small wrapper around `QMessageBox` for standardized info/error dialogs.

- **Resources** under `app/ui/resources/`:
  - `style.qss` contains the Qt stylesheet loaded globally in `main.py`.
  - `250.png` is the product image reused in the product list UI.

### Admin panel

- **`app/admin/users_window.py`** (`UsersWindow`):
  - Main admin GUI shown when an admin logs in.
  - Left panel: list of users built from `admin_service.get_all_users()`, where each row embeds controls to delete, edit, or change the role for that user.
  - Right panel: purchase history (`Sale` records) for the selected user, populated via `db_api.get_sales_by_user_id` and the `Sale.product` relationship.
  - Uses modal dialogs (`EditUserDialog`, `RoleDialog`) to edit user attributes and roles, which delegate back to `admin_service` functions.

### Reporting

- **`app/reports/report_generator.py`**:
  - Provides `generate_report(filename, sales)` which renders a simple PDF report using reportlab, listing each sale as `product x quantity - username`.
  - Intended to be used by UIs or scripts that fetch sales via `db_api.get_sales()` or `get_sales_by_user_id()` and then pass them into this helper.

## Notes for future automation

- Many flows (login, registration, cart/checkout, admin user management) are tightly coupled to the ORM models and `db_api` helpers; when modifying database schemas, verify corresponding UI logic and initialization functions in `app/db/initialization.py`.
- The working directory assumptions in `app/main.py` (changing to the `app` directory) are important for locating resources and the SQLite DB; be cautious when introducing new entry points or CLI scripts that need access to the same assets.
