import sqlite3, json, time, random, math
import matplotlib.pyplot as plt

def generate_shaky_data(num_samples, freq=5.0, amplitude=3.0, noise_std=0.5):
    """
    Generate fake accelerometer + temperature data simulating hand shakiness.

    Args:
        num_samples (int): number of data points to generate
        freq (float): base tremor frequency in Hz (default 5Hz)
        amplitude (float): amplitude of tremor in 'g-like' units (default 3)
        noise_std (float): std dev of added random jitter noise (default 0.5)

    Returns:
        list of JSON strings, each representing one data entry
    """

    data = []
    start_time_ms = time.time_ns() // 1_000_000  # current time in ms
    sample_period_ms = 20  # 50Hz -> 20ms spacing

    for i in range(num_samples):
        t = i / 50.0  # time in seconds relative to start
        phase = 2 * math.pi * freq * t

        # Tremor-like sinusoidal shaking + noise
        x = amplitude * math.sin(phase) + random.gauss(0, noise_std)
        y = amplitude * math.sin(phase + math.pi / 2) + random.gauss(0, noise_std)  # phase-shifted
        z = amplitude * math.sin(phase + math.pi / 4) + random.gauss(0, noise_std)  # another shift

        # Temperature: 37 ± 0.5 C
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
    """
    Insert a single JSON string into SQLite.

    - Uses existing connection `conn`.
    - Inserts into table_name (default: readings_raw).
    - Ignores duplicate timestamp_ms entries (INSERT OR IGNORE).
    - Returns True if inserted, False if skipped (duplicate or malformed).
    """
    try:
        item = json.loads(json_string)
        ts  = int(item["timestamp_ms"])
        x   = float(item["xaxis"])
        y   = float(item["yaxis"])
        z   = float(item["zaxis"])
        tC  = float(item["temperature"])
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        return False  # bad record

    cur = conn.cursor()
    cur.execute(
        f"""INSERT OR IGNORE INTO {table_name}
            (timestamp_ms, xaxis, yaxis, zaxis, temperature)
            VALUES (?, ?, ?, ?, ?)""",
        (ts, x, y, z, tC)
    )
    conn.commit()
    return cur.rowcount > 0

def fetch_motion_series(conn, table_name, start_ms=None, end_ms=None, limit=None):
    """
    Pull x, y, z motion vs time from SQLite.

    Args:
        conn       : sqlite3.Connection
        table_name : table to read from 
        start_ms   : inclusive lower bound on timestamp_ms (int, optional)
        end_ms     : inclusive upper bound on timestamp_ms (int, optional)
        limit      : max rows to return (int, optional). If set, returns the most recent `limit` rows.

    Returns:
        dict with lists: {
            "timestamp_ms": [...],
            "t_s": [...],   # seconds relative to first returned sample
            "x": [...],
            "y": [...],
            "z": [...],
            "mag": [...],   # sqrt(x^2 + y^2 + z^2)
        }
    """
    where = []
    params = []
    if start_ms is not None:
        where.append("timestamp_ms >= ?")
        params.append(int(start_ms))
    if end_ms is not None:
        where.append("timestamp_ms <= ?")
        params.append(int(end_ms))

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    # If a limit is provided without a window, grab the most recent rows then re-sort ascending.
    if limit is not None and not where:
        sql_latest = f"""
            SELECT timestamp_ms, xaxis, yaxis, zaxis
            FROM {table_name}
            ORDER BY timestamp_ms DESC
            LIMIT ?
        """
        rows = conn.execute(sql_latest, (int(limit),)).fetchall()
        rows.reverse()  # ascending time
    else:
        sql = f"""
            SELECT timestamp_ms, xaxis, yaxis, zaxis
            FROM {table_name}
            {where_sql}
            ORDER BY timestamp_ms ASC
        """
        if limit is not None:
            sql += f" LIMIT {int(limit)}"
        rows = conn.execute(sql, params).fetchall()

    if not rows:
        return {"timestamp_ms": [], "t_s": [], "x": [], "y": [], "z": [], "mag": []}

    ts = [int(r[0]) for r in rows]
    x  = [float(r[1]) for r in rows]
    y  = [float(r[2]) for r in rows]
    z  = [float(r[3]) for r in rows]

    t0 = ts[0]
    t_s = [(t - t0) / 1000.0 for t in ts]
    mag = [(xi*xi + yi*yi + zi*zi) ** 0.5 for xi, yi, zi in zip(x, y, z)]

    return {
        "timestamp_ms": ts,
        "t_s": t_s,
        "x": x,
        "y": y,
        "z": z,
        "mag": mag,
    }


def plot_motion_from_db(conn, table_name, start_ms=None, end_ms=None, limit=None):
    """
    Connect to SQLite DB, fetch entries, and plot X, Y, Z, and |a| vs time in separate graphs.

    Args:
        db_path   : path to SQLite file
        table_name: table containing data (default 'readings')
        start_ms  : lower bound timestamp (optional)
        end_ms    : upper bound timestamp (optional)
        limit     : maximum number of samples (optional)
    """
    series = fetch_motion_series(conn, table_name, start_ms, end_ms, limit)
    conn.close()

    t = series["t_s"]  # seconds relative to first sample
    x, y, z, mag = series["x"], series["y"], series["z"], series["mag"]

    # X vs time
    plt.figure()
    plt.plot(t, x, label="x", color="r")
    plt.xlabel("Time (s)")
    plt.ylabel("X-axis")
    plt.title("X Motion vs Time")
    plt.tight_layout()

    # Y vs time
    plt.figure()
    plt.plot(t, y, label="y", color="g")
    plt.xlabel("Time (s)")
    plt.ylabel("Y-axis")
    plt.title("Y Motion vs Time")
    plt.tight_layout()

    # Z vs time
    plt.figure()
    plt.plot(t, z, label="z", color="b")
    plt.xlabel("Time (s)")
    plt.ylabel("Z-axis")
    plt.title("Z Motion vs Time")
    plt.tight_layout()

    # Magnitude vs time
    plt.figure()
    plt.plot(t, mag, label="|a|", color="k")
    plt.xlabel("Time (s)")
    plt.ylabel("Magnitude")
    plt.title("Acceleration Magnitude vs Time")
    plt.tight_layout()

    plt.show()
    
# ------------------- MAIN -------------------

if __name__ == "__main__":
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

    # generate 5000 fake entries
    list_of_json_entries = generate_shaky_data(num_samples=5000)
    
    # insert each entry one at a time into database (maybe could do batches idk)
    for json_entry in list_of_json_entries:
        insert_json_entry(conn=conn, json_string=json_entry, table_name="readings_raw")
    
    # generate x, y, z, and magnitude vs time plots
    plot_motion_from_db(conn=conn, table_name="readings_raw")

    conn.close()