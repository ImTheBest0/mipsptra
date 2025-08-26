import argparse, time, math
import pulp
from utils.symmetry import round_robin_weeks
from utils.io import save_result_json
from pulp import PulpSolverError

def get_solver(solver_name: str, time_limit: int, msg: bool):
    solver_name = solver_name.lower()
    if solver_name == "highs":
        return pulp.HiGHS_CMD(timeLimit=time_limit, msg=msg, threads=1)
    elif solver_name == "cbc":
        return pulp.PULP_CBC_CMD(timeLimit=time_limit, msg=msg)
    else:
        raise ValueError("solver must be 'highs' or 'cbc'")

def solve_tournament(n: int, time_limit: int = 300, verbose: bool = False, solver_name: str = "highs"):
    assert n % 2 == 0 and n >= 4
    teams   = list(range(1, n+1))
    weeks   = list(range(1, n))
    periods = list(range(1, n//2 + 1))
    week_pairs = round_robin_weeks(n)
    prob = pulp.LpProblem("STS", pulp.LpMinimize)

    week_of, matches = {}, []
    for w_idx, pairs in enumerate(week_pairs, start=1):
        for (i, j) in pairs:
            week_of[(i, j)] = w_idx
            matches.append((i, j))

    y = pulp.LpVariable.dicts("y", [(i, j, p) for (i, j) in matches for p in periods], 0, 1, cat="Binary")
    h = pulp.LpVariable.dicts("h", matches, 0, 1, cat="Binary")
    home_count = pulp.LpVariable.dicts("home_count", teams, lowBound=0, upBound=len(weeks), cat="Continuous")
    z_min = pulp.LpVariable("z_min", lowBound=0, cat="Continuous")
    z_max = pulp.LpVariable("z_max", lowBound=0, upBound=len(weeks), cat="Continuous")

    for (i, j) in matches:
        prob += pulp.lpSum(y[(i, j, p)] for p in periods) == 1
    for w in weeks:
        for p in periods:
            prob += pulp.lpSum(y[(i, j, p)] for (i, j) in week_pairs[w-1]) == 1
    for t in teams:
        for p in periods:
            prob += pulp.lpSum(y[(i, j, p)] for (i, j) in matches if i == t or j == t) <= 2
    for i in teams:
        left  = pulp.lpSum(h[(i, j)] for (a, j) in matches if a == i)
        right = pulp.lpSum(1 - h[(k, i)] for (k, b) in matches if b == i)
        prob += home_count[i] == left + right
        prob += z_max >= home_count[i]
        prob += z_min <= home_count[i]
    for (i, j) in week_pairs[0]:
        if 1 in (i, j):
            a, b = (i, j) if i < j else (j, i)
            prob += y[(a, b, 1)] == 1
            break

    target = (n - 1) / 2.0
    d_plus  = pulp.LpVariable.dicts("d_plus", teams, lowBound=0, cat="Continuous")
    d_minus = pulp.LpVariable.dicts("d_minus", teams, lowBound=0, cat="Continuous")
    for i in teams:
        prob += home_count[i] - target == d_plus[i] - d_minus[i]
    prob += pulp.lpSum(d_plus[i] + d_minus[i] for i in teams)

    start = time.time()
    try:
        solver = get_solver(solver_name, time_limit, verbose)
        prob.solve(solver)
    except PulpSolverError:
      
        solver = get_solver("cbc", time_limit, verbose)
        prob.solve(solver)
        solver_name = "cbc"
    wall = int(math.floor(time.time() - start))

    status = pulp.LpStatus[prob.status]
    optimal = (prob.status == pulp.LpStatusOptimal)
    if not optimal:
        wall = 300

    feasible = any((pulp.value(y[(i, j, p)]) or 0) > 0.5 for (i, j) in matches for p in periods)
    obj_val = int(round(pulp.value(prob.objective))) if pulp.value(prob.objective) is not None else None

    solution = []
    if feasible:
        solution = [[None for i in weeks] for i in periods]
        for (i, j) in matches:
            w = week_of[(i, j)]
            pp = next(p for p in periods if (pulp.value(y[(i, j, p)]) or 0) > 0.5)
            hij = int(round(pulp.value(h[(i, j)]) or 0))
            home, away = (i, j) if hij == 1 else (j, i)
            solution[pp - 1][w - 1] = [home, away]

    return {"time": wall, "optimal": optimal, "obj": obj_val, "sol": solution, "solver": solver_name}, status

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, required=True)
    ap.add_argument("--solver", choices=["highs", "cbc"], default="highs") 
    ap.add_argument("--time-limit", type=int, default=300)
    ap.add_argument("--msg", action="store_true")
    args = ap.parse_args()

    result, status = solve_tournament(args.n, args.time_limit, verbose=args.msg, solver_name=args.solver)
    print(f"Solver={result['solver']} | Status={status} | Optimal={result['optimal']} | Obj={result['obj']} | Time={result['time']}s")

    if result["sol"]:
        key = f"{result['solver']}_dev"
        out_path = save_result_json(result, args.n, key, compact=True)
        print(f"Saved: {out_path}")

if __name__ == "__main__":
    main()
