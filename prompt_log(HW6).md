# Prompt Log — Personal Finance Tracker
AI model used: Claude Sonnet (claude.ai)  


## Prompt 1
Prompt used:
"I want to create a SQLite database to track personal finances. Here are the columns I'm thinking of: id, description, amount, category, type (income or expense), date, payment_method, notes. Can you help me write a CREATE TABLE statement and suggest any constraints I should add?"


## Prompt 2
Prompt used:
"Show me how to set up a Python sqlite connection and create my transactions table using CREATE TABLE IF NOT EXISTS. I want it to create the database file automatically on first run."


## Prompt 3
Prompt used:
"Show me how to write a Python function that asks the user for description, amount, category, type, date, payment_method, and notes, then inserts a row into my transactions table using sqlite. Use parameterized queries with ? placeholders."


## Prompt 4
Prompt used:
"I want a view menu with these options: show all with running balance, filter by type, filter by category, filter by date range, keyword search across description/category/notes, a spending summary grouped by category, and sort by any column. Show me the SQL queries for each"


## Prompt 5
Prompt used:
"Write an update function that fetches the current row by ID, displays each field's current value in brackets, and lets the user press Enter to keep it unchanged or type a new value. Then run an UPDATE query with the final values."


## Prompt 6
Prompt used:
"Write a delete function that fetches the record by ID, displays it to the user, asks 'are you sure?' before running DELETE FROM transactions WHERE id = ?."


## Prmompt 7
Prompt used:
"Does my app correctly close the database connection? I'm using `with get_connection() as conn` but get_connection() just returns a connection object."


## Prompt 8
Prompt used:
"Does the program use `?` placeholders rather than f-strings or string concatenation when putting user input into SQL?"


## Prompt 9
Prompt used:
"Can you break down all the SQL in the app, explaining how each part works?"
