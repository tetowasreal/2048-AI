import random
import os
import time
import json

SIZE = 4
LOG_FILE = "log.json"
BEST_FILE = "best.json"


# =========================
# BOARD UTIL
# =========================

def empty_board():
    return [[0]*SIZE for _ in range(SIZE)]


def copy(b):
    return [row[:] for row in b]


def equal(a, b):
    return all(a[y][x] == b[y][x] for y in range(SIZE) for x in range(SIZE))


# =========================
# DISPLAY
# =========================

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def show(b):
    for row in b:
        print(" ".join(f"{x:4}" if x else "   ." for x in row))
    print("-" * 20)


# =========================
# MOVE SYSTEM (PURE)
# =========================

def merge(row):
    row = [x for x in row if x != 0]
    out = []
    i = 0

    while i < len(row):
        if i + 1 < len(row) and row[i] == row[i+1]:
            out.append(row[i] * 2)
            i += 2
        else:
            out.append(row[i])
            i += 1

    return out + [0] * (SIZE - len(out))


def left(b):
    return [merge(r) for r in b]


def right(b):
    return [merge(r[::-1])[::-1] for r in b]


def rotate_cw(b):
    return [[b[SIZE-1-x][y] for x in range(SIZE)] for y in range(SIZE)]


def rotate_ccw(b):
    return [[b[x][SIZE-1-y] for x in range(SIZE)] for y in range(SIZE)]


def up(b):
    return rotate_cw(left(rotate_ccw(b)))


def down(b):
    return rotate_ccw(left(rotate_cw(b)))


MOVES = [left, right, up, down]


# =========================
# GAME RULES
# =========================

def spawn(b):
    empty = [(y, x) for y in range(SIZE) for x in range(SIZE) if b[y][x] == 0]
    if not empty:
        return b

    y, x = random.choice(empty)
    b[y][x] = 4 if random.random() < 0.1 else 2
    return b


def can_move(b):
    for m in MOVES:
        if not equal(b, m(b)):
            return True
    return False


def max_tile(b):
    return max(max(row) for row in b)


# =========================
# AI (단순 heuristic)
# =========================

def score(b):
    empty = sum(x == 0 for r in b for x in r)
    return empty + max_tile(b) * 0.01


def ai(b):
    best = None
    best_score = -1

    for m in MOVES:
        nb = m(b)

        if equal(nb, b):
            continue

        s = score(nb)

        if s > best_score:
            best_score = s
            best = nb

    return spawn(best) if best else None


# =========================
# SAVE / LOAD
# =========================

def save_best(data):
    with open(BEST_FILE, "w") as f:
        json.dump(data, f)


def load_best():
    try:
        with open(BEST_FILE, "r") as f:
            return json.load(f)
    except:
        return {"best": 0}


def save_log(log):
    with open(LOG_FILE, "w") as f:
        json.dump(log, f)


# =========================
# PLAY MODE
# =========================

def play():

    b = spawn(spawn(empty_board()))

    while True:

        clear()
        show(b)

        if not can_move(b):
            print("Game Over")
            print("Max:", max_tile(b))
            break

        b = ai(b)
        time.sleep(0.1)


# =========================
# TRAIN MODE
# =========================

def train():

    log = []
    best_data = load_best()
    best_score = best_data["best"]

    game = 0

    while True:

        b = spawn(spawn(empty_board()))
        game += 1

        while can_move(b):

            b = ai(b)

        m = max_tile(b)

        best_score = max(best_score, m)

        print(f"Game {game} | Max {m} | Best {best_score}")

        log.append({
            "game": game,
            "max": m,
            "best": best_score
        })

        # 저장 (안 날아가게)
        if game % 10 == 0:
            save_log(log)
            save_best({"best": best_score})


# =========================
# MAIN
# =========================

if __name__ == "__main__":

    mode = input("train or play? ")

    if mode == "play":
        play()
    else:
        train()