"""Independent local check of parameter binding; no Gemini request or attack."""

import sqlite3


def verify_parameter_binding():
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
        return {
            "status": "passed",
            "claim": "SQLite binds the quoted username as a value.",
            "queried_username": "O'Reilly",
            "returned_row": list(row),
            "remaining_rows": 2,
            "scope": "This checks the specific binding behavior, not the security of an entire app.",
            "reference": "https://docs.python.org/3/library/sqlite3.html#sqlite3-placeholders",
        }


def main():
    result = verify_parameter_binding()
    print("PASS: a quoted name is treated as a bound value; both rows remain intact.")
    print(result["scope"])
    print(f"Reference: {result['reference']}")


if __name__ == "__main__":
    main()
