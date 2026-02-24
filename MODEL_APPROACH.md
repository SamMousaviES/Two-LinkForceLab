# Modeling Approach

## 1) Kinematics convention
- 2D Cartesian frame, origin at point `A`.
- Zero angle is vertical upward.
- `AB` angle `theta` is positive counterclockwise.
- `BC` angle `psi` is positive counterclockwise, but assignment says `BC` rotates clockwise, so `psi_dot = -omega_bc_clockwise`.

Unit vector from vertical-up angle:
`u(angle) = [-sin(angle), cos(angle)]`

## 2) Position, velocity, acceleration
For each time sample over one full `AB` turn:
- `r_B = L_AB * u(theta)`
- `r_C = r_B + L_BC * u(psi)`

With constant angular speeds:
- `v_B = L_AB * d(u(theta))/dt`
- `a_B = L_AB * d2(u(theta))/dt2`
- `v_C = v_B + L_BC * d(u(psi))/dt`
- `a_C = a_B + L_BC * d2(u(psi))/dt2`

## 3) Axial force in AB
Dynamic force from point masses:
`F_dyn = M_b * a_B + M_c * a_C`

Project onto `AB` direction:
`F_proj = dot(F_dyn, u_AB)`

Sign convention in assignment:
- Positive means tension
- Negative means compression

For this sign convention:
`F_axial_AB = -F_proj`

The minus sign makes inward centripetal pull correspond to positive tension.

## 4) Batch combinations
- Read up to 5 geometry sets and up to 5 motion sets.
- Simulate all Cartesian combinations.
- Produce one force-angle line plot per combination.

## 5) Insight extraction
- Highest tensile case: maximum of `F_axial_AB`.
- Highest compressive case: minimum of `F_axial_AB`.
- Primary driver: strongest absolute correlation with max absolute force across combinations.

