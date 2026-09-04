import sqlite3

def check():
    c = sqlite3.connect('nova.db')
    try:
        res = c.execute("SELECT sql FROM sqlite_master WHERE type='table'").fetchall()
        for r in res:
            print(r[0])
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    check()
