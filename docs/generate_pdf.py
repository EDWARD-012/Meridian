"""Generate Final Plan + Design PDF for E-Commerce DBMS project."""
from fpdf import FPDF
from pathlib import Path

OUTPUT = Path(__file__).parent / "ECommerce_DBMS_Final_Plan.pdf"


class PlanPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(80, 80, 80)
        self.cell(0, 8, "E-Commerce DBMS | Django + MySQL (Cloud) + Vercel", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title: str):
        self.ln(4)
        self.set_font("Helvetica", "B", 14)
        self.set_text_color(20, 60, 120)
        self.cell(0, 10, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(20, 60, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(6)

    def sub_title(self, title: str):
        self.ln(2)
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(40, 40, 40)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(2)

    def body_text(self, text: str):
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bullet_list(self, items: list[str]):
        self.set_x(self.l_margin)
        self.set_font("Helvetica", "", 10)
        self.set_text_color(30, 30, 30)
        for item in items:
            self.set_x(self.l_margin)
            self.multi_cell(0, 5.5, f"- {item}")
        self.ln(2)

    def table(self, headers: list[str], rows: list[list[str]], col_widths: list[int] | None = None):
        if col_widths is None:
            w = 190 / len(headers)
            col_widths = [w] * len(headers)
        self.set_font("Helvetica", "B", 9)
        self.set_fill_color(230, 240, 250)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8)
        fill = False
        for row in rows:
            if self.get_y() > 260:
                self.add_page()
            self.set_fill_color(248, 248, 248) if fill else self.set_fill_color(255, 255, 255)
            max_h = 7
            for i, cell in enumerate(row):
                x, y = self.get_x(), self.get_y()
                self.multi_cell(col_widths[i], 5, cell, border=0)
                max_h = max(max_h, self.get_y() - y)
                self.set_xy(x + col_widths[i], y)
            self.set_xy(10, self.get_y() + max_h - 5)
            y_start = self.get_y() - max_h + 5
            for i, cell in enumerate(row):
                self.rect(10 + sum(col_widths[:i]), y_start, col_widths[i], max_h)
            self.ln(max_h)
            fill = not fill
        self.set_x(self.l_margin)
        self.ln(4)


def draw_er_diagram(pdf: PlanPDF):
    pdf.section_title("Design 1: Database ER Schema")
    pdf.body_text(
        "Relational schema for Product Catalog, Cart, Orders, and Payment Tracking. "
        "All tables use InnoDB engine with foreign keys and indexes for viva demonstration."
    )

    entities = [
        ("USER", "id PK, username UK, email UK, password_hash, phone, created_at"),
        ("ADDRESS", "id PK, user_id FK->USER, line1, city, state, pincode, is_default"),
        ("CATEGORY", "id PK, name UK, description"),
        ("PRODUCT", "id PK, category_id FK, name, description, price, stock_qty, image_url, is_active"),
        ("CART", "id PK, user_id FK->USER, updated_at"),
        ("CART_ITEM", "id PK, cart_id FK, product_id FK, quantity (UNIQUE cart+product)"),
        ("ORDER", "id PK, user_id FK, address_id FK, total_amount, status, order_date"),
        ("ORDER_ITEM", "id PK, order_id FK, product_id FK, quantity, unit_price, subtotal"),
        ("PAYMENT", "id PK, order_id FK UK, method, amount, status, transaction_id, paid_at"),
    ]
    pdf.table(["Entity", "Attributes"], [[e, a] for e, a in entities], [35, 155])

    pdf.sub_title("Relationships")
    pdf.bullet_list([
        "USER 1---M CART, ORDER, ADDRESS",
        "CATEGORY 1---M PRODUCT",
        "CART 1---M CART_ITEM ---M 1 PRODUCT",
        "ORDER 1---M ORDER_ITEM ---M 1 PRODUCT",
        "ORDER 1---1 PAYMENT",
        "ORDER_ITEM.unit_price = price snapshot at order time",
    ])

    pdf.sub_title("ER Diagram (Visual)")
    pdf.set_font("Courier", "", 7)
    pdf.set_text_color(20, 20, 20)
    diagram = """
    +----------+       +----------+       +-----------+
    | CATEGORY |1-----M| PRODUCT  |M-----1| CART_ITEM |
    +----------+       +----+-----+       +-----+-----+
                          |                      |
                          |M                     |M
                          |                      |
                     +----+-----+          +-----+-----+
                     |ORDER_ITEM|          |   CART    |
                     +----+-----+          +-----+-----+
                          |M                      |1
                          |                       |
                          |1                 +----+----+
                     +----+-----+            |  USER   |
                     |  ORDER   |M-----------+----+----+
                     +----+-----+                 |1
                          |1                       |M
                          |                   +-----+-----+
                     +----+-----+             |  ADDRESS  |
                     | PAYMENT  |             +-----------+
                     +----------+
    """
    pdf.multi_cell(0, 3.5, diagram.strip())
    pdf.ln(4)


def draw_architecture(pdf: PlanPDF):
    pdf.add_page()
    pdf.section_title("Design 2: System Architecture")
    pdf.sub_title("Production (Vercel + Cloud MySQL)")
    pdf.set_font("Courier", "", 8)
    arch = """
    [ Browser / Mobile ]
            |
            v HTTPS
    +---------------------------+
    |      VERCEL PLATFORM      |
    |  CDN (Static CSS/JS/IMG)  |
    |  Django Vercel Function   |
    |  (WSGI - Gunicorn-like)   |
    +-------------+-------------+
                  |
                  | mysqlclient / PyMySQL
                  | SSL connection
                  v
    +---------------------------+
    |   CLOUD MYSQL (TiDB /     |
    |   Railway / Aiven)        |
    |   Tables + Views +        |
    |   Triggers + Procedures   |
    +---------------------------+

    External: Cloudinary (product images)
    Env Vars: DB_HOST, DB_USER, DB_PASS, DB_NAME, SECRET_KEY
    """
    pdf.multi_cell(0, 4, arch.strip())
    pdf.ln(4)

    pdf.sub_title("Local Development")
    pdf.set_font("Courier", "", 8)
    local = """
    [ Browser ] --> python manage.py runserver --> MySQL localhost:3306
    Same Django code | Different DB_HOST in .env
    """
    pdf.multi_cell(0, 4, local.strip())
    pdf.ln(4)

    pdf.sub_title("Order Placement Flow (Transaction)")
    pdf.set_font("Helvetica", "", 10)
    pdf.bullet_list([
        "1. User clicks Checkout -> POST /orders/place/",
        "2. Django @transaction.atomic block starts",
        "3. Validate cart items and stock quantities",
        "4. INSERT into ORDER and ORDER_ITEM tables",
        "5. UPDATE PRODUCT stock (or trigger fires)",
        "6. INSERT PAYMENT record (status = pending)",
        "7. Clear CART_ITEM rows",
        "8. COMMIT - all or nothing (ROLLBACK on error)",
    ])


def build_pdf():
    pdf = PlanPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(20, 60, 120)
    pdf.cell(0, 12, "E-Commerce Database System", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 14)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 10, "Final Project Plan", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, "Stack: Django + MySQL (Cloud) + Vercel", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(8)

    pdf.section_title("1. Project Overview")
    pdf.body_text(
        "College DBMS project: Online shopping backend with Product Catalog, Cart System, "
        "Order Placement, and Payment Tracking. Full-stack web app using Django (Python), "
        "MySQL database connected via Django ORM and raw SQL, deployed on Vercel with "
        "cloud-hosted MySQL for production."
    )

    pdf.section_title("2. Tech Stack")
    pdf.table(
        ["Layer", "Technology", "Purpose"],
        [
            ["Backend", "Django 5.x", "MVT framework, ORM, Admin, Auth"],
            ["Database", "MySQL 8 (Cloud)", "Relational DB - joins, triggers, views"],
            ["DB Driver", "mysqlclient", "Python-MySQL connection"],
            ["Frontend", "Django Templates + Bootstrap 5", "Server-rendered UI"],
            ["Auth", "Django built-in User model", "Login, sessions, permissions"],
            ["Images", "Cloudinary", "Product images (Vercel has no local disk)"],
            ["Config", "python-decouple / .env", "Secrets not in Git"],
            ["Deploy App", "Vercel", "Serverless Django + CDN static files"],
            ["Deploy DB", "TiDB Serverless / Railway", "Free-tier cloud MySQL"],
        ],
        [30, 55, 105],
    )

    pdf.section_title("3. Why This Stack Works")
    pdf.bullet_list([
        "Vercel officially supports Django (zero-config, detects manage.py).",
        "Same Django code runs locally and on Vercel - only DB_HOST changes.",
        "Local MySQL for dev; Cloud MySQL for production (laptop DB not reachable from Vercel).",
        "Django ORM for CRUD plus raw SQL files for viva (views, triggers, procedures).",
        "Django Admin gives free product/order management for demo.",
    ])

    pdf.section_title("4. Django Project Structure")
    pdf.set_font("Courier", "", 8)
    structure = """
ecommerce_dbms/
|-- manage.py
|-- requirements.txt
|-- .env.example          (template - never commit .env)
|-- pyproject.toml          (optional Vercel config)
|-- config/                 settings, urls, wsgi
|-- accounts/               User profile, register, login
|-- catalog/                Category, Product models + views
|-- cart/                   Cart, CartItem
|-- orders/                 Order, OrderItem, Payment
|-- sql_scripts/            schema.sql, views.sql, triggers.sql
|-- templates/              base.html, product list, cart, checkout
|-- static/                 CSS, Bootstrap
"""
    pdf.multi_cell(0, 4, structure.strip())
    pdf.ln(4)

    pdf.add_page()
    pdf.section_title("5. Database Tables (Detailed)")
    pdf.table(
        ["Table", "Key Columns", "Notes"],
        [
            ["user (auth_user)", "id, username, email", "Django built-in + Profile extend"],
            ["category", "id, name", "Electronics, Clothing, etc."],
            ["product", "id, category_id, price, stock", "INDEX on category_id"],
            ["cart", "id, user_id", "One cart per logged-in user"],
            ["cart_item", "cart_id, product_id, qty", "UNIQUE(cart_id, product_id)"],
            ["order", "id, user_id, total, status", "status: pending/confirmed/shipped/delivered"],
            ["order_item", "order_id, product_id, unit_price", "Price snapshot at order time"],
            ["payment", "order_id, amount, status", "status: pending/success/failed/refunded"],
            ["address", "user_id, line1, city, pincode", "Shipping address"],
        ],
        [28, 72, 90],
    )

    draw_er_diagram(pdf)
    draw_architecture(pdf)

    pdf.add_page()
    pdf.section_title("6. Feature Implementation Map")
    pdf.table(
        ["Feature", "Django App", "Key Models / Views", "SQL Concept"],
        [
            ["Product Catalog", "catalog", "Category, Product, ListView", "SELECT + JOIN"],
            ["Cart System", "cart", "Cart, CartItem, add/remove", "INSERT/UPDATE/DELETE"],
            ["Order Placement", "orders", "place_order view", "TRANSACTION"],
            ["Payment Tracking", "orders", "Payment model", "FK + status enum"],
            ["Admin Panel", "Django Admin", "All models registered", "CRUD demo"],
            ["Reports (Viva)", "sql_scripts", "Raw SQL views", "VIEW, GROUP BY"],
        ],
        [35, 25, 65, 65],
    )

    pdf.section_title("7. Environment Variables")
    pdf.set_font("Courier", "", 8)
    env = """
# Local (.env)
SECRET_KEY=your-secret-key
DEBUG=True
DB_ENGINE=django.db.backends.mysql
DB_NAME=ecommerce_db
DB_USER=root
DB_PASSWORD=yourpassword
DB_HOST=127.0.0.1
DB_PORT=3306
CLOUDINARY_URL=cloudinary://...

# Vercel Dashboard (Production)
SECRET_KEY=<strong-random-key>
DEBUG=False
DB_HOST=<cloud-mysql-host>
DB_USER=<cloud-user>
DB_PASSWORD=<cloud-password>
DB_NAME=ecommerce_db
DB_PORT=3306
ALLOWED_HOSTS=.vercel.app
"""
    pdf.multi_cell(0, 4, env.strip())
    pdf.ln(4)

    pdf.section_title("8. Phase-wise Timeline (6 Weeks)")
    pdf.table(
        ["Week", "Tasks", "Deliverable"],
        [
            ["1", "Django setup, MySQL connect, User auth", "Login/Register working"],
            ["2", "Category + Product CRUD, Admin seed data", "Product catalog live"],
            ["3", "Cart add/remove/update quantity", "Cart system complete"],
            ["4", "Checkout, Order + Payment, transactions", "Order placement working"],
            ["5", "SQL views, triggers, indexes, report page", "DBMS viva material"],
            ["6", "Cloud MySQL + Vercel deploy, testing, report", "Live demo URL"],
        ],
        [15, 95, 80],
    )

    pdf.section_title("9. Deployment Steps")
    pdf.bullet_list([
        "Step 1: Push code to GitHub (.env in .gitignore).",
        "Step 2: Create TiDB Serverless or Railway MySQL instance.",
        "Step 3: Run sql_scripts/schema.sql on cloud DB.",
        "Step 4: Import repo on vercel.com - auto-detects Django.",
        "Step 5: Add all env vars in Vercel Project Settings.",
        "Step 6: Deploy -> run migrations via Vercel CLI or local against cloud DB.",
        "Step 7: Create superuser, load seed products, test live URL.",
    ])

    pdf.section_title("10. Vercel Limitations (Know Before Demo)")
    pdf.bullet_list([
        "Cold start: first request may take 1-2 seconds.",
        "No local MEDIA_ROOT - use Cloudinary for uploads.",
        "No Celery/background jobs on Vercel.",
        "Function timeout: ~10s (Hobby) / ~60s (Pro).",
        "SQLite must NOT be used in production on Vercel.",
    ])

    pdf.section_title("11. Viva / Report Checklist")
    pdf.bullet_list([
        "ER Diagram + Architecture Diagram (this PDF + designs.html).",
        "CREATE TABLE script with PK, FK, constraints.",
        "At least 1 VIEW (e.g. sales by category).",
        "At least 1 TRIGGER (e.g. reduce stock on order).",
        "TRANSACTION demo during order placement.",
        "EXPLAIN on indexed vs non-indexed query.",
        "Screenshots: Admin, Catalog, Cart, Order, Payment status.",
        "Live Vercel URL in report.",
    ])

    pdf.section_title("12. Team Role Suggestion (Optional)")
    pdf.table(
        ["Member", "Responsibility"],
        [
            ["Member 1", "Database schema, SQL scripts, ER diagram"],
            ["Member 2", "Django models, migrations, Admin"],
            ["Member 3", "Views, Templates, Bootstrap UI"],
            ["Member 4", "Cart + Order logic, transactions, deployment"],
        ],
        [35, 155],
    )

    pdf.ln(6)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.multi_cell(
        0, 5,
        "Also open docs/designs.html in browser and use Ctrl+P -> Save as PDF for high-quality visual diagrams.",
    )

    pdf.output(str(OUTPUT))
    print(f"PDF generated: {OUTPUT}")


if __name__ == "__main__":
    build_pdf()
