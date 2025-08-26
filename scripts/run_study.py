import os, sys, csv
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from main import solve_tournament
from utils.io import save_result_json

def main():
    ns = [6,8,10,12,14]
    outDir = "res/study"
    os.makedirs(outDir, exist_ok=True)

    rows = [("n",
             "time_highs", "optimal_highs", "obj_highs",
             "time_cbc",   "optimal_cbc",   "obj_cbc")]

    highsTimes = []
    cbcTimes = []

    for n in ns:
        print(f"running n={n} using highs methods")
        resH, statusH = solve_tournament(n=n, time_limit=300, verbose=False, solver_name="highs")
        save_result_json(resH, n, approach_name="highs_dev", base_dir="res/MIP", compact=True)

        print(f"runnning n={n} using cbc")
        resC, statusC = solve_tournament(n=n, time_limit=300, verbose=False, solver_name="cbc")
        save_result_json(resC, n, approach_name="cbc_dev", base_dir="res/MIP", compact=True)

        rows.append((n,
                     resH["time"], int(resH["optimal"]), resH["obj"],
                     resC["time"], int(resC["optimal"]), resC["obj"]))

        highsTimes.append(resH["time"])
        cbcTimes.append(resC["time"])

        print(f"highs time is{resH['time']}s, cbc time is {resC['time']}s")

    csvPath = os.path.join(outDir, "study_lvn.csv")
    with open(csvPath, "w", newline="") as f:
        w = csv.writer(f)
        w.writerows(rows)
    print(f"wrote csv: {csvPath}")

    plt.figure()
    plt.plot(ns, highsTimes, marker="o", label="HiGHS (dev)")
    plt.plot(ns, cbcTimes,   marker="o", label="CBC (dev)")
    plt.xlabel("number of teams")
    plt.ylabel("time (s)")
    plt.title("STS runtime vs teams num")
    plt.legend()
    pngPath = os.path.join(outDir, "study_lvn.png")
    plt.savefig(pngPath, bbox_inches="tight")
    print(f"wrote plot: {pngPath}")

if __name__ == "__main__":
    main()
