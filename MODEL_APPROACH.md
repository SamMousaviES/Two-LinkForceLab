# Modeling Approach

## 1) Kinematics convention
- 2D Cartesian frame, origin at point `A`.
- Zero angle is vertical upward.
- `AB` angle $\theta$ is positive counterclockwise.
- `BC` angle $\psi$ is positive counterclockwise, but assignment says `BC` rotates clockwise, so:

$$
\dot{\psi} = -\omega_{BC,\mathrm{cw}}
$$

Unit vector from vertical-up angle:

$$
\mathbf{u}(\alpha) =
\begin{bmatrix}
-\sin(\alpha) \\
\cos(\alpha)
\end{bmatrix}
$$

## 2) Position, velocity, acceleration
For each time sample over one full `AB` turn:

$$
\mathbf{r}_B = L_{AB}\,\mathbf{u}(\theta)
$$

$$
\mathbf{r}_C = \mathbf{r}_B + L_{BC}\,\mathbf{u}(\psi)
$$

With constant angular speeds:

$$
\mathbf{v}_B = L_{AB}\,\frac{d\mathbf{u}(\theta)}{dt}, \qquad
\mathbf{a}_B = L_{AB}\,\frac{d^2\mathbf{u}(\theta)}{dt^2}
$$

$$
\mathbf{v}_C = \mathbf{v}_B + L_{BC}\,\frac{d\mathbf{u}(\psi)}{dt}, \qquad
\mathbf{a}_C = \mathbf{a}_B + L_{BC}\,\frac{d^2\mathbf{u}(\psi)}{dt^2}
$$

## 3) Axial force in AB
Dynamic force from point masses:

$$
\mathbf{F}_{\mathrm{dyn}} = M_b\,\mathbf{a}_B + M_c\,\mathbf{a}_C
$$

Project onto `AB` direction:

$$
F_{\mathrm{proj}} = \mathbf{F}_{\mathrm{dyn}} \cdot \mathbf{u}_{AB}
$$

Sign convention in assignment:
- Positive means tension
- Negative means compression

For this sign convention:

$$
F_{AB,\mathrm{axial}} = -F_{\mathrm{proj}}
$$

The minus sign makes inward centripetal pull correspond to positive tension.

## 4) Batch combinations
- Read up to 5 geometry sets and up to 5 motion sets.
- Simulate all Cartesian combinations.
- Produce one force-angle line plot per combination.

## 5) Insight extraction
- Highest tensile case: maximum of $F_{AB,\mathrm{axial}}$.
- Highest compressive case: minimum of $F_{AB,\mathrm{axial}}$.
- Primary driver: strongest absolute correlation with max absolute force across combinations.
