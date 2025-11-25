# Piekarnia – Application Documentation

## Overview

Piekarnia is a desktop application built with PySide6 and SQLAlchemy. It provides:

- A customer-facing interface for browsing bakery products, adding them to a cart, and purchasing them.
- A login/registration flow with support for regular users, guests, and admin users.
- An admin panel for managing users and reviewing their purchase history.
- A simple PDF report generator for sales data.

The main entry point is `app/main.py`, which initializes the database, creates default data (admin and guest users, sample products), and opens the login window.

## Installation

From the project root (`Piekarnia`):

1. Ensure you have Python installed.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

This installs PySide6, SQLAlchemy, bcrypt, reportlab, and optional alembic.

## Running the application

From the project root:

```bash
python -m app.main
```

On first run, this will:

- Create the SQLite database file `database.db` (if it doesn’t exist).
- Create and seed sample products.
- Create a default admin account and a guest account.
- Open the login window.

### Default accounts

- **Admin**: username `a`, password `a`
- **Guest**: virtual account used when choosing "Kontynuuj jako gość" in the login window.

## User flows

### Login

1. Run the application.
2. In the login window:
   - Enter your username and password, then click **"Zaloguj"**.
   - If credentials are valid, you will be logged in.
   - Admin users are taken directly to the admin panel; other users see the main shopping window.

If login fails, an error dialog is shown.

### Registration

1. From the login window, click **"Zarejestruj się"**.
2. In the registration window:
   - Fill in **Login**, **Email**, and **Hasło**.
   - Optionally provide a **Karta kredytowa** number (this can be left empty).
   - Confirm the password.
3. Click **"Zarejestruj"**.

The app enforces:

- Unique username.
- Unique, non-empty email.

On success, a message is shown and the registration window closes; you can then log in with the new credentials.

### Continue as guest

From the login window, click **"Kontynuuj jako gość"**. The app:

- Looks up or creates the `guest` user account.
- Opens the main window in guest mode.

Guest purchases are recorded to the `guest` user.

### Shopping and cart

Once logged in as a non-admin user, the **Main Window** provides:

- A product list on the left:
  - Each product shows an image, name, description placeholder, quantity selector, and **"Dodaj"** button.
- A cart on the right:
  - Displays selected products with quantities and line totals.
  - Includes a **"Kup wybrane"** button to checkout.

Flow:

1. Select quantities and click **"Dodaj"** next to products you want.
2. Review items in the cart on the right.
3. Click **"Kup wybrane"** to perform checkout.

### Payments

When checking out:

- If logged in as **guest** or the user has **no stored credit card**:
  - A **card payment window** appears asking for card number.
  - After entering a card number and confirming, the app:
    - Registers sales in the database (for the `guest` user or current user, depending on the path).
    - Clears the cart.

- If the logged-in user already has a credit card stored:
  - The app directly records `Sale` entries for the current user based on the cart contents.
  - Shows a confirmation and clears the cart.

## Admin panel

Admin functionality is accessed by logging in as the admin user.

The admin panel (`app/admin/users_window.py`) is split into two main parts:

- **User list (left side)**
  - Shows each user’s ID, username and role.
  - For each user you have buttons:
    - **"Usuń"** – delete the user.
    - **"Edytuj"** – change username and email.
    - **"Rola"** – change role between `user` and `admin`.
- **Purchase history (right side)**
  - After clicking a user on the left, you see all their sales: product name and quantity.
  - There is a button **"Eksportuj raport PDF"** which:
    - Asks where to save the file.
    - Uses `report_generator.generate_report` to create a PDF with that user’s sales.

All changes and reports use the shared database layer (`app/admin/admin_service.py` and `app/db/db_api.py`).

## Database structure (high level)

The SQLite database (`database.db`) is managed via SQLAlchemy ORM models in `app/db/models.py`:

- `User`: login information, hashed password, role, email, and optional credit card.
- `Product`: bakery items with name and price.
- `Sale`: links `User` and `Product` with a quantity and relationships back to both.

Database initialization and seeding are handled in `app/db/initialization.py`. A maintenance script in `docs/typczasowy.py` can reset the database file and recreate tables.

## Generating PDF sales reports

Sales reports are created in `app/reports/report_generator.py`.

### Built‑in way: from the admin panel

1. Log in as the admin user.
2. In the admin window, click a user on the left.
3. On the right, click **"Eksportuj raport PDF"**.
4. Choose where to save the file.

The app calls `generate_report(file_path, sales)` under the hood and creates a PDF with lines like:

- `<product.name> x <quantity> - <user.username>`

### Advanced: from the command line

You can also generate reports manually from the terminal.

**All sales in one report:**

```bash
python - << "PY"
from app.db.db_api import get_sales
from app.reports.report_generator import generate_report

sales = get_sales()
output_file = "sales_report.pdf"

generate_report(output_file, sales)
print(f"Generated sales report: {output_file}")
PY
```

**Single user report (by ID):**

```bash
python - << "PY"
from app.db.db_api import get_sales_by_user_id
from app.reports.report_generator import generate_report

user_id = 1  # change this to the desired user ID
sales = get_sales_by_user_id(user_id)
output_file = f"sales_report_user_{user_id}.pdf"

generate_report(output_file, sales)
print(f"Generated sales report for user {user_id}: {output_file}")
PY
```

## Where to extend next

- Add automated tests for the database and UI logic.
- Enhance reports (e.g. date ranges, totals per product, or CSV export alongside PDF).
- Expand product information (descriptions, categories, stock levels) and reflect these in the UI.
