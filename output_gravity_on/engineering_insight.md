# Engineering Insight

- Highest tensile load: `G4__M5` with `F = 335.463 N` at `AB angle = 189.0 deg` | Gravity: `ON (9.810 m/s^2)`
- Highest compressive load: `G5__M1` with `F = -41.175 N` at `AB angle = 52.0 deg` | Gravity: `ON (9.810 m/s^2)`
- Gravity setting for this scenario set: `ON (9.810 m/s^2)`
- Primary load driver in this scenario set: `omega_ab`

## Quick Explanation
- Positive axial force means link `AB` is in tension (pulled).
- Negative axial force means link `AB` is in compression (pushed).
- Gravity is applied globally for this scenario set and is reported explicitly as `ON` or `OFF`.
- In this scenario set, `omega_ab` has the strongest linear trend with extreme load magnitude.

## Correlation Snapshot
- `length_ab`: correlation = +0.303
- `length_bc`: correlation = +0.107
- `mass_b`: correlation = +0.366
- `mass_c`: correlation = +0.128
- `gravity_m_s2`: correlation = +0.000
- `omega_ab`: correlation = +0.871
- `omega_bc_clockwise`: correlation = +0.486
