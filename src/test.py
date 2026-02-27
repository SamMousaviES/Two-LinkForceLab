import numpy as np
import matplotlib.pyplot as plt
Mc = 1 #kg
Mb = 2 #kg

L1 = 1 #m
L2 = 0.5 #m

w1 = 10.0 #rad/s
w2 = -20.0 #rad/s


N = 721 #number of points (every 0.5 degrees)

theta_deg = np.linspace(0, 360, N) #degrees
theta = theta_deg * 3.1415 / 180 #radians

# position of the center of mass of the body
xB = L1 * np.sin(theta) #m
yB = L1 * np.cos(theta) #m

# velocity of the center of mass of the body
vb_x = -L1 * w1 * np.sin(theta) #m/s
vb_y = -L1 * w1 * np.cos(theta) #m/s

# acceleration of the center of mass of the body
a_b_x = -L1 * w1**2 * np.sin(theta) #m/s^2
a_b_y = -L1 * w1**2 * np.cos(theta) #m/s^2

# unit vector function for the direction
def e(alpha):
    return np.sin(alpha), np.cos(alpha)

# force on the body due to its acceleration
F_B_x = Mb * a_b_x # force on body in x direction
F_B_y = Mb * a_b_y # force on body in y direction

F_AB = F_B_x * e_ABx + F_B_y * e_ABy # force on body A due to body B

plt.figure(figsize=(10, 6))
plt.plot(theta_deg, F_AB)
plt.title("Force on Body A due to Body B")
plt.xlabel("AB rotation angle (degrees)")
plt.ylabel("axial force in AB (N) (positive is tension and negative is compression)")
plt.grid(True)

print("Maximum tension in AB: {:.2f} N".format(np.max(F_AB)))
print("Maximum compression in AB: {:.2f} N".format(np.min(F_AB)))

plt.show()