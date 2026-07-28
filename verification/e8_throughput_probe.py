"""E8 throughput probe - measure on the AUTHOR'S machine, not the container.
E7 proved the container is the wrong yardstick: it projected 8.5h, the real run took 11.6h."""
import sys, time
sys.path.insert(0, "analysis/vendor")
from phase2_7_validation_runner import (
    get_validation_environments, make_pricing_scenarios, run_pricing_trial,
)

envs = get_validation_environments()
scen = make_pricing_scenarios()
SCEN = ["no_pricing", "naive_reactive", "phi_gated_symmetric", "phi_gated_asymmetric"]
ENVS = ["level_shift_up_persistent", "low_phi_shift_up",
        "level_shift_down_persistent", "low_phi_shift_down", "mid_phi_shift_down"]

print("timing the vendored engine: 2 seeds x 4 scenarios on level_shift_up_persistent")
t0 = time.time(); n = 0
for s in (9000, 9001):
    for sc in SCEN:
        r = run_pricing_trial(envs["level_shift_up_persistent"], "all_sr", sc, scen[sc], s)
        n += 1
        if not r.get("success"):
            print("  TRIAL FAILED:", r.get("error")); sys.exit(1)
dt = (time.time() - t0) / n
print("  per trial: %.2f s   (one seed x 4 scenarios: %.1f s)" % (dt, dt * 4))
print()
print("projected full run: 5 environments x 4 scenarios")
print("  %6s %8s %12s %10s" % ("seeds", "trials", "minutes", "hours"))
for N in (50, 115, 195, 250, 525, 1000):
    tot = dt * 4 * len(ENVS) * N
    print("  %6d %8d %12.1f %10.2f" % (N, 4 * len(ENVS) * N, tot / 60, tot / 3600))
print()
print("seeds needed to RESOLVE claim A (formula vs naive) per env, from the")
print("source's own 50-seed SEs:  level_shift_down ~115 | mid_phi_shift_down ~195")
print("                           level_shift_up_persistent ~525 (effect is only +13.01)")
