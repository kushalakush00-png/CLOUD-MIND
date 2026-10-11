
import numpy as np
import pandas as pd


def generate_telemetry(servers=12, periods=120, seed=42):
    rng = np.random.default_rng(seed)

    timestamps = pd.date_range(
        end=pd.Timestamp.now().floor("min"),
        periods=periods,
        freq="min",
    )

    rows = []

    for i in range(1, servers + 1):
        phase = rng.uniform(0, 2 * np.pi)
        baseline = rng.uniform(25, 55)

        cpu = (
            baseline
            + 12 * np.sin(
                np.linspace(0, 5 * np.pi, periods) + phase
            )
            + rng.normal(0, 5, periods)
        )

        ram = (
            rng.uniform(35, 60)
            + np.linspace(0, rng.uniform(0, 12), periods)
            + rng.normal(0, 3, periods)
        )

        network = (
            rng.uniform(80, 300)
            + 60 * np.sin(
                np.linspace(0, 4 * np.pi, periods) + phase
            )
            + rng.normal(0, 20, periods)
        )

        if i % 4 == 0:
            cpu[-8:] += np.linspace(10, 38, 8)

        cpu = np.clip(cpu, 2, 100)
        ram = np.clip(ram, 5, 100)
        network = np.clip(network, 1, None)

        for j, timestamp in enumerate(timestamps):
            rows.append({
                "timestamp": timestamp,
                "server_id": f"VM-{i:02d}",
                "cpu_percent": round(float(cpu[j]), 2),
                "ram_percent": round(float(ram[j]), 2),
                "network_mbps": round(float(network[j]), 2),
            })

    df = pd.DataFrame(rows)

    df["status"] = np.select(
        [
            (df["cpu_percent"] >= 90)
            | (df["ram_percent"] >= 92),
            (df["cpu_percent"] >= 75)
            | (df["ram_percent"] >= 80),
        ],
        ["Critical", "Warning"],
        default="Normal",
    )

    return df
