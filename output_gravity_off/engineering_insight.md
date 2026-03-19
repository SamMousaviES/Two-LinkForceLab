# Engineering Insight

- Highest tensile load: `G4__M5` with `F = 287.500 N` at `AB angle = 0.0 deg` | Gravity: `OFF`
- Highest compressive load: `G5__M1` with `F = -11.000 N` at `AB angle = 180.0 deg` | Gravity: `OFF`
- Gravity setting for this scenario set: `OFF`
- Primary load driver in this scenario set: `omega_ab`

## Quick Explanation
- Positive axial force means link `AB` is in tension (pulled).
- Negative axial force means link `AB` is in compression (pushed).
- Gravity is applied globally for this scenario set and is reported explicitly as `ON` or `OFF`.
- In this scenario set, `omega_ab` has the strongest linear trend with extreme load magnitude.

## Correlation Snapshot
- `length_ab`: correlation = +0.282
- `length_bc`: correlation = +0.094
- `mass_b`: correlation = +0.330
- `mass_c`: correlation = +0.109
- `gravity_m_s2`: correlation = +0.000
- `omega_ab`: correlation = +0.875
- `omega_bc_clockwise`: correlation = +0.529
