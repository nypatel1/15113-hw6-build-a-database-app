#!/usr/bin/env python3

import sqlite3
import os
import sys
from contextlib import contextmanager
from datetime import datetime, date
from typing import Optional

DB_FILE = "finance.db"

PRESET_CATEGORIES = [
    "Food & Dining",
    "Rent / Housing",
    "Utilities",
    "Transportation",
    "Entertainment",
    "Subscriptions",
    "Healthcare",
    "Shopping",
    "Education",
    "Travel",
    "Salary",
    "Freelance",
    "Investments",
    "Gifts",
    "Other",
]

PAYMENT_METHODS = [
    "Cash",
    "Credit Card",
    "Debit Card",
    "Bank Transfer",
    "Mobile Payment",
    "Cryptocurrency",
    "Other",
]

# ─── Terminal colours ──────────────────────────────────────────────────────────

GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

def c(text, color): return f"{color}{text}{RESET}"
def bold(text):     return c(text, BOLD)
def green(text):    return c(text, GREEN)
def red(text):      return c(text, RED)
def yellow(text):   return c(text, YELLOW)
def cyan(text):     return c(text, CYAN)
def dim(text):      return c(text, DIM)


# ─── Database setup ────────────────────────────────────────────────────────────

@contextmanager
def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id             INTEGER PRIMARY KEY AUTOINCREMENT,
                description    TEXT    NOT NULL,
                amount         REAL    NOT NULL CHECK(amount > 0),
                category       TEXT    NOT NULL,
                type           TEXT    NOT NULL CHECK(type IN ('income', 'expense')),
                date           TEXT    NOT NULL,
                payment_method TEXT,
                notes          TEXT
            );
        """)


# ─── UI helpers ───────────────────────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def separator(char="─", width=60):
    print(dim(char * width))


def header(title: str):
    print()
    separator("═")
    print(bold(cyan(f"  {title}")))
    separator("═")
    print()


def pause():
    input(dim("\n  Press Enter to continue…"))


def confirm(prompt: str) -> bool:
    ans = input(f"\n  {yellow('⚠')}  {prompt} [{green('y')}/{red('n')}]: ").strip().lower()
    return ans in ("y", "yes")


def pick_from_list(items: list, prompt: str, allow_custom=False) -> str:
    """Display a numbered list and return the chosen string value."""
    print()
    for i, item in enumerate(items, 1):
        print(f"    {dim(str(i).rjust(2))}.  {item}")
    if allow_custom:
        print(f"    {dim(str(len(items)+1).rjust(2))}.  {cyan('Custom…')}")
    print()
    while True:
        raw = input(f"  {prompt}: ").strip()
        if not raw:
            continue
        try:
            idx = int(raw) - 1
            if allow_custom and idx == len(items):
                val = input("  Enter custom value: ").strip()
                if val:
                    return val
                continue
            if 0 <= idx < len(items):
                return items[idx]
        except ValueError:
            # Accept freeform text too
            return raw
        print(red("  Invalid choice, try again."))


def pick_type() -> str:
    print(f"\n    1.  {green('income')}")
    print(f"    2.  {red('expense')}")
    while True:
        raw = input("\n  Type [1/2]: ").strip()
        if raw == "1": return "income"
        if raw == "2": return "expense"
        print(red("  Please enter 1 or 2."))


def parse_date(raw: str) -> Optional[str]:
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return None


def ask_date(prompt: str, default: str = "") -> str:
    hint = f" [{dim(default)}]" if default else ""
    while True:
        raw = input(f"  {prompt}{hint} (YYYY-MM-DD): ").strip()
        if not raw and default:
            return default
        parsed = parse_date(raw)
        if parsed:
            return parsed
        print(red("  Invalid date. Use YYYY-MM-DD."))


def fmt_amount(amount: float, typ: str) -> str:
    s = f"${amount:,.2f}"
    return green(s) if typ == "income" else red(s)


def fmt_type(typ: str) -> str:
    return green("income") if typ == "income" else red("expense")


# ─── Print transactions table ─────────────────────────────────────────────────

COLUMNS = ["id", "date", "type", "category", "description", "amount", "payment_method", "notes"]
COL_WIDTHS = [5, 12, 9, 18, 28, 11, 16, 20]

def _trunc(s: str, n: int) -> str:
    s = str(s) if s is not None else ""
    return s if len(s) <= n else s[:n-1] + "…"


def print_transactions(rows, show_running=True):
    if not rows:
        print(dim("  No transactions found."))
        return

    # header row
    header_parts = []
    for col, w in zip(COLUMNS, COL_WIDTHS):
        header_parts.append(bold(col.upper().replace("_", " ").ljust(w)))
    print("  " + "  ".join(header_parts))
    separator(width=sum(COL_WIDTHS) + len(COLUMNS)*2 + 2)

    running = 0.0
    for row in rows:
        typ = row["type"]
        amt = row["amount"]
        running += amt if typ == "income" else -amt

        parts = []
        for col, w in zip(COLUMNS, COL_WIDTHS):
            val = row[col]
            if col == "amount":
                cell = _trunc(f"${val:,.2f}", w).rjust(w)
                cell = green(cell) if typ == "income" else red(cell)
            elif col == "type":
                cell = fmt_type(str(val)).ljust(w + (len(fmt_type(str(val))) - len(str(val))))
                # pad to visual width
                cell = fmt_type(str(val))
                cell = cell + " " * max(0, w - len(str(val)))
            else:
                cell = _trunc(str(val) if val is not None else "", w).ljust(w)
            parts.append(cell)
        print("  " + "  ".join(parts))

    if show_running:
        separator(width=sum(COL_WIDTHS) + len(COLUMNS)*2 + 2)
        color = green if running >= 0 else red
        print(f"\n  {bold('Running balance:')}  {color(f'${running:,.2f}')}\n")


# ─── CRUD Operations ──────────────────────────────────────────────────────────

def add_transaction():
    header("Add Transaction")

    description = ""
    while not description:
        description = input("  Description: ").strip()
        if not description:
            print(red("  Description cannot be empty."))

    while True:
        raw = input("  Amount (e.g. 49.99): $").strip()
        try:
            amount = float(raw)
            if amount <= 0:
                print(red("  Amount must be greater than 0."))
                continue
            break
        except ValueError:
            print(red("  Please enter a valid number."))

    print(f"\n  {bold('Category')} — choose one:")
    category = pick_from_list(PRESET_CATEGORIES, "Category number", allow_custom=True)

    print(f"\n  {bold('Type')}:")
    typ = pick_type()

    today = date.today().strftime("%Y-%m-%d")
    txn_date = ask_date("Date", default=today)

    print(f"\n  {bold('Payment method')} (optional, Enter to skip):")
    for i, m in enumerate(PAYMENT_METHODS, 1):
        print(f"    {dim(str(i).rjust(2))}.  {m}")
    raw_pm = input("\n  Payment method [Enter to skip]: ").strip()
    payment_method = None
    if raw_pm:
        try:
            idx = int(raw_pm) - 1
            if 0 <= idx < len(PAYMENT_METHODS):
                payment_method = PAYMENT_METHODS[idx]
            else:
                payment_method = raw_pm
        except ValueError:
            payment_method = raw_pm

    notes = input("  Notes (optional): ").strip() or None

    with get_connection() as conn:
        conn.execute(
            """INSERT INTO transactions
               (description, amount, category, type, date, payment_method, notes)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (description, amount, category, typ, txn_date, payment_method, notes),
        )

    print(green(f"\n  ✓  Transaction added successfully!"))
    pause()


def view_transactions():
    while True:
        header("View Transactions")
        print(f"  {bold('Filter / sort options:')}\n")
        print(f"  1.  All transactions")
        print(f"  2.  Filter by type (income / expense)")
        print(f"  3.  Filter by category")
        print(f"  4.  Filter by date range")
        print(f"  5.  Search by keyword")
        print(f"  6.  Spending summary by category")
        print(f"  7.  Sort by column")
        print(f"  0.  Back")

        choice = input("\n  Choice: ").strip()

        if choice == "0":
            return

        elif choice == "1":
            _show_all()

        elif choice == "2":
            typ = pick_type()
            _show_filtered(where="type = ?", params=(typ,))

        elif choice == "3":
            print(f"\n  {bold('Choose category:')}")
            cat = pick_from_list(PRESET_CATEGORIES, "Category", allow_custom=True)
            _show_filtered(where="category = ?", params=(cat,))

        elif choice == "4":
            start = ask_date("Start date")
            end   = ask_date("End date")
            _show_filtered(where="date BETWEEN ? AND ?", params=(start, end))

        elif choice == "5":
            kw = input("  Keyword: ").strip()
            pattern = f"%{kw}%"
            _show_filtered(
                where="(description LIKE ? OR category LIKE ? OR notes LIKE ?)",
                params=(pattern, pattern, pattern),
            )

        elif choice == "6":
            _spending_summary()

        elif choice == "7":
            _sort_menu()

        else:
            print(red("  Invalid option."))


def _show_all(order="date DESC"):
    with get_connection() as conn:
        rows = conn.execute(f"SELECT * FROM transactions ORDER BY {order}").fetchall()
    print()
    print_transactions(rows)
    pause()


def _show_filtered(where: str, params: tuple, order="date DESC"):
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT * FROM transactions WHERE {where} ORDER BY {order}", params
        ).fetchall()
    print()
    print_transactions(rows)
    pause()


def _sort_menu():
    print(f"\n  {bold('Sort by column:')}")
    sortable = ["id", "date", "amount", "category", "type", "description"]
    for i, col in enumerate(sortable, 1):
        print(f"    {dim(str(i))}.  {col}")
    raw = input("\n  Column number: ").strip()
    try:
        col = sortable[int(raw) - 1]
    except (ValueError, IndexError):
        print(red("  Invalid column."))
        pause()
        return

    direction = input("  Order — [1] ASC  [2] DESC: ").strip()
    order = f"{col} {'ASC' if direction == '1' else 'DESC'}"
    _show_all(order=order)


def _spending_summary():
    header("Spending Summary")
    with get_connection() as conn:
        cats = conn.execute("""
            SELECT category,
                   SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) AS total_income,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_expense
            FROM transactions
            GROUP BY category
            ORDER BY total_expense DESC
        """).fetchall()

        totals = conn.execute("""
            SELECT SUM(CASE WHEN type='income'  THEN amount ELSE 0 END) AS total_income,
                   SUM(CASE WHEN type='expense' THEN amount ELSE 0 END) AS total_expense
            FROM transactions
        """).fetchone()

    if not cats:
        print(dim("  No data yet."))
        pause()
        return

    W = [22, 14, 14]
    print("  " + bold("CATEGORY".ljust(W[0])) + "  " +
          bold("INCOME".rjust(W[1])) + "  " + bold("EXPENSE".rjust(W[2])))
    separator(width=sum(W) + 6)

    for row in cats:
        income  = row["total_income"]  or 0
        expense = row["total_expense"] or 0
        print("  " +
              row["category"].ljust(W[0]) + "  " +
              green(f"${income:,.2f}".rjust(W[1])) + "  " +
              red(f"${expense:,.2f}".rjust(W[2])))

    separator(width=sum(W) + 6)
    ti = totals["total_income"]  or 0
    te = totals["total_expense"] or 0
    net = ti - te
    print("  " + bold("TOTAL".ljust(W[0])) + "  " +
          green(f"${ti:,.2f}".rjust(W[1])) + "  " +
          red(f"${te:,.2f}".rjust(W[2])))

    color = green if net >= 0 else red
    print(f"\n  {bold('Net balance:')}  {color(f'${net:,.2f}')}")
    print(f"  {'↑ Surplus' if net >= 0 else '↓ Deficit'}")
    pause()


def update_transaction():
    header("Update Transaction")

    raw_id = input("  Transaction ID to update: ").strip()
    try:
        txn_id = int(raw_id)
    except ValueError:
        print(red("  Invalid ID.")); pause(); return

    with get_connection() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()

    if not row:
        print(red(f"  No transaction found with ID {txn_id}.")); pause(); return

    print(f"\n  {bold('Current values')} — press Enter to keep unchanged.\n")

    def ask(prompt, current):
        raw = input(f"  {prompt} [{dim(str(current))}]: ").strip()
        return raw if raw else current

    description = ask("Description", row["description"])

    while True:
        raw = ask("Amount", row["amount"])
        try:
            amount = float(raw)
            if amount <= 0:
                print(red("  Must be > 0.")); continue
            break
        except ValueError:
            print(red("  Invalid number."))

    print(f"\n  {bold('Category')} (Enter to keep [{dim(row['category'])}]):")
    raw_cat = input("  Category (number or text, Enter to keep): ").strip()
    if raw_cat:
        try:
            idx = int(raw_cat) - 1
            category = PRESET_CATEGORIES[idx] if 0 <= idx < len(PRESET_CATEGORIES) else raw_cat
        except ValueError:
            category = raw_cat
    else:
        category = row["category"]

    print(f"\n  {bold('Type')} (Enter to keep [{dim(row['type'])}]):")
    raw_type = input("  Type [1=income / 2=expense, Enter to keep]: ").strip()
    if raw_type == "1":   typ = "income"
    elif raw_type == "2": typ = "expense"
    else:                 typ = row["type"]

    raw_date = input(f"  Date [{dim(row['date'])}] (YYYY-MM-DD, Enter to keep): ").strip()
    txn_date = parse_date(raw_date) if raw_date else row["date"]
    if not txn_date:
        print(yellow("  Invalid date, keeping original.")); txn_date = row["date"]

    raw_pm = input(f"  Payment method [{dim(str(row['payment_method']))}] (Enter to keep): ").strip()
    payment_method = raw_pm if raw_pm else row["payment_method"]

    raw_notes = input(f"  Notes [{dim(str(row['notes']))}] (Enter to keep): ").strip()
    notes = raw_notes if raw_notes else row["notes"]

    with get_connection() as conn:
        conn.execute("""
            UPDATE transactions
            SET description=?, amount=?, category=?, type=?, date=?,
                payment_method=?, notes=?
            WHERE id=?
        """, (description, amount, category, typ, txn_date, payment_method, notes, txn_id))

    print(green("\n  ✓  Transaction updated."))
    pause()


def delete_transaction():
    header("Delete Transaction")

    raw_id = input("  Transaction ID to delete: ").strip()
    try:
        txn_id = int(raw_id)
    except ValueError:
        print(red("  Invalid ID.")); pause(); return

    with get_connection() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (txn_id,)).fetchone()

    if not row:
        print(red(f"  No transaction found with ID {txn_id}.")); pause(); return

    print(f"\n  {bold('Transaction to delete:')}")
    print(f"  ID:          {row['id']}")
    print(f"  Description: {row['description']}")
    print(f"  Amount:      {fmt_amount(row['amount'], row['type'])}")
    print(f"  Date:        {row['date']}")
    print(f"  Type:        {fmt_type(row['type'])}")

    if confirm("Are you sure you want to permanently delete this transaction?"):
        with get_connection() as conn:
            conn.execute("DELETE FROM transactions WHERE id = ?", (txn_id,))
        print(green("\n  ✓  Transaction deleted."))
    else:
        print(dim("\n  Cancelled."))

    pause()


# ─── Main menu ────────────────────────────────────────────────────────────────

def main_menu():
    while True:
        clear()
        print()
        separator("═")
        print(bold(cyan("  💰  Personal Finance Tracker")))
        separator("═")
        print()
        print(f"  {green('1')}  Add transaction")
        print(f"  {cyan('2')}  View / filter / search transactions")
        print(f"  {yellow('3')}  Update transaction")
        print(f"  {red('4')}  Delete transaction")
        print()
        print(f"  {dim('0')}  {dim('Exit')}")
        separator()

        choice = input("\n  Choose an option: ").strip()

        if choice == "1":
            clear(); add_transaction()
        elif choice == "2":
            clear(); view_transactions()
        elif choice == "3":
            clear(); update_transaction()
        elif choice == "4":
            clear(); delete_transaction()
        elif choice == "0":
            print(green("\n  Goodbye! 👋\n"))
            sys.exit(0)
        else:
            print(red("  Invalid option, please try again."))
            pause()


# ─── Entry point ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    try:
        main_menu()
    except KeyboardInterrupt:
        print(green("\n\n  Goodbye! 👋\n"))
        sys.exit(0)
