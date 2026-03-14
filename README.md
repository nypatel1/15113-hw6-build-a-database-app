# Personal Finance Tracker
The app is a command-line interface for tracking personal income and expenses, with Python and SQLite. I chose this because it seemed like an interesting and usable application of data since managing money is something everyone does daily, and having a local, private tracker with no accounts or subscriptions is useful.

---

## Database Schema

Table:
| Column | Type | Constraints | Description |
| `id` | INTEGER | Unique row identifier |
| `description` | TEXT | NOT NULL | Short label for the transaction |
| `amount` | FLOAT | NOT NULL | Positive dollar amount |
| `category` | TEXT | NOT NULL | Food & Dining, Salary, Rent, etc. |
| `type` | TEXT | NOT NULL | Classification |
| `date` | TEXT | NOT NULL | Stored as YYYY-MM-DD |
| `payment_method` | TEXT | optional | e.g. Cash, Credit Card |
| `notes` | TEXT | optional | Free-form notes |

---

## How to Run

Need Python's standard library, Python 3.8 or newer
python3 finance_tracker.py

The app will create `finance.db` in the same directory on first launch.

---
CRUD Operations
### Create — Add a transaction
Select "1" from the main menu. The app walks you through each field:
- Description (free text)
- Amount (must be > 0)
- Category (choose from 15 presets or type a custom one)
- Type (income or expense)
- Date (defaults to today, accepts YYYY-MM-DD)
- Payment method (optional, choose from list)
- Notes (optional, free text)

### Read — View / filter / search transactions
Select "2" from the main menu. A sub-menu has seven modes:
- All transactions, Shows every row with a running balance
- Filter by type, Shows only income or only expenses
- Filter by category, Shows rows matching a chosen category
- Filter by date range, Shows rows between a start and end date
- Search by keyword, Matches keyword against description, category, and notes
- Spending summary, Groups totals by category; shows net balance
- Sort by column, Sorts by any column, ascending or descending

### Update — Edit an existing transaction
Select "3" from the main menu. Enter the transaction ID (visible in the View screen). The app shows the current value for each field in brackets, user presses Enter to keep it, or type a new value. Only the fields you change are updated.

### Delete — Remove a transaction
Select "4" from the main menu. Enter the transaction ID. The app displays the full record and asks for confirmation (`y/n`) before permanently deleting it.
