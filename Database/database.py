import sqlite3, json, time, random, math, os
import matplotlib
matplotlib.use("Agg")  # Use non-GUI backend for headless servers
import matplotlib.pyplot as plt
from datetime import datetime


def generate_shaky_data(num_samples, freq=5.0, amplitude=3.0, noise_std=0.5):
    """Generate fake accelerometer + temperature data simulating hand shakiness."""
    data = []
    start_time_ms = time.time_ns() // 1_000_000  # current time in ms
    sample_period_ms = 20  # 50Hz -> 20ms spacing

    for i in range(num_samples):
        t = i / 50.0
        phase = 2 * math.pi * freq * t

        x = amplitude * math.sin(phase) + random.gauss(0, noise_std)
        y = amplitude * math.sin(phase + math.pi / 2) + random.gauss(0, noise_std)
        z = amplitude * math.sin(phase + math.pi / 4) + random.gauss(0, noise_std)
        temp = 37.0 + random.uniform(-0.5, 0.5)

        entry = {
            "timestamp_ms": start_time_ms + i * sample_period_ms,
            "xaxis": round(x, 3),
            "yaxis": round(y, 3),
            "zaxis": round(z, 3),
            "temperature": round(temp, 2),
        }
        data.append(json.dumps(entry))
    return data


def insert_json_entry(conn, json_string, table_name="readings_raw"):
    """Insert one JSON entry into SQLite."""
    try:
        item = json.loads(json_string)
        ts = int(item["timestamp_ms"])
        x = float(item["xaxis"])
        y = float(item["yaxis"])
        z = float(item["zaxis"])
        tC = float(item["temperature"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return False

    cur = conn.cursor()
    cur.execute(
        f"""INSERT OR IGNORE INTO {table_name}
            (timestamp_ms, xaxis, yaxis, zaxis, temperature)
            VALUES (?, ?, ?, ?, ?)""",
        (ts, x, y, z, tC)
    )
    conn.commit()
    return cur.rowcount > 0


def fetch_motion_series(conn, table_name, limit=None):
    """Fetch motion data for plotting."""
    sql = f"""
        SELECT timestamp_ms, xaxis, yaxis, zaxis
        FROM {table_name}
        ORDER BY timestamp_ms ASC
    """
    if limit:
        sql += f" LIMIT {int(limit)}"

    rows = conn.execute(sql).fetchall()
    if not rows:
        return {"timestamp_ms": [], "t_s": [], "x": [], "y": [], "z": [], "mag": []}

    ts = [int(r[0]) for r in rows]
    x = [float(r[1]) for r in rows]
    y = [float(r[2]) for r in rows]
    z = [float(r[3]) for r in rows]

    t0 = ts[0]
    t_s = [(t - t0) / 1000.0 for t in ts]
    mag = [(xi**2 + yi**2 + zi**2) ** 0.5 for xi, yi, zi in zip(x, y, z)]
    return {"timestamp_ms": ts, "t_s": t_s, "x": x, "y": y, "z": z, "mag": mag}


def plot_motion_from_db(conn, table_name, limit=1000):
    """Plot and save motion data."""
    series = fetch_motion_series(conn, table_name, limit)
    t = series["t_s"]
    x, y, z, mag = series["x"], series["y"], series["z"], series["mag"]

    plt.figure(figsize=(8, 5))
    plt.plot(t, x, label="X-axis", color="r")
    plt.plot(t, y, label="Y-axis", color="g")
    plt.plot(t, z, label="Z-axis", color="b")
    plt.plot(t, mag, label="|a|", color="k", linestyle="--")
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration")
    plt.title("Motion Data from Database")
    plt.legend()
    plt.tight_layout()
    plt.savefig("motion_plot.png")
    print("Saved motion plot to motion_plot.png")


# ------------------- MAIN -------------------

if __name__ == "__main__":
    start_demo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[DEMO] Starting database demo at {start_demo}\n")

    conn = sqlite3.connect("steadyHand.db")
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS readings_raw")
    cur.execute("""
    CREATE TABLE readings_raw (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp_ms INTEGER,
        xaxis REAL,
        yaxis REAL,
        zaxis REAL,
        temperature REAL
    )
    """)
    conn.commit()

    num_samples = 5000
    print(f"[DEMO] Generating {num_samples:,} fake readings...")
    data_entries = generate_shaky_data(num_samples)

    # --- Measure insertion performance ---
    print("[DEMO] Inserting data...")
    t_start = time.time()
    for entry in data_entries:
        insert_json_entry(conn, entry, table_name="readings_raw")
    t_end = time.time()

    elapsed = t_end - t_start
    rate = num_samples / elapsed
    print(f"[RESULT] Inserted {num_samples:,} rows in {elapsed:.2f} seconds ({rate:,.0f} rows/sec)")

    # --- Count total rows and DB size ---
    cur.execute("SELECT COUNT(*) FROM readings_raw;")
    total_rows = cur.fetchone()[0]
    db_size_mb = os.path.getsize("steadyHand.db") / (1024 * 1024)
    print(f"[RESULT] Database now holds {total_rows:,} rows, size = {db_size_mb:.2f} MB")

    # --- Estimate 1-week data capacity ---
    week_rows = 50 * 60 * 60 * 3 * 7  #  samples/week @50Hz
    scale_factor = week_rows / total_rows
    est_size_gb = (db_size_mb * scale_factor) / 1024
    est_time_sec = scale_factor * elapsed
    est_time_hr = est_time_sec / 3600

    print(f"\n[ESTIMATE] 1 week of 50Hz data = {week_rows:,} rows")
    print(f"[ESTIMATE] Estimated DB size: {est_size_gb:.2f} GB")
    # print(f"[ESTIMATE] Estimated insert time (same rate): {est_time_hr:.2f} hours\n")

    # --- Show sample rows ---
    print("[DEMO] Sample data (first 5 rows):")
    cur.execute("SELECT * FROM readings_raw LIMIT 5;")
    for row in cur.fetchall():
        print(row)
    print()

    # --- Plot motion data ---
    plot_motion_from_db(conn, table_name="readings_raw", limit=1000)

    conn.close()
    print("[DEMO] Completed successfully.\n")
