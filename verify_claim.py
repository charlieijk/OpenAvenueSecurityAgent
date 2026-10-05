"""Independent local check of parameter binding; no Gemini request or attack."""

import sqlite3


def main():
    with sqlite3.connect(":memory:") as connection:
        connection.execute("CREATE TABLE users (id INTEGER, username TEXT)")
        connection.executemany(
            "INSERT INTO users VALUES (?, ?)", [(1, "Alice"), (2, "O'Reilly")]
        )
        row = connection.execute(
            "SELECT id, username FROM users WHERE username = ?", ("O'Reilly",)
        ).fetchone()
        assert row == (2, "O'Reilly")
        assert connection.execute("SELECT count(*) FROM users").fetchone()[0] == 2
        print("PASS: a quoted name is treated as a bound value; both rows remain intact.")
        print("This checks the specific binding behavior, not the security of an entire app.")
        print("Reference: https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders")


if __name__ == "__main__":
    main()
