"""Sweep the rotor 0..90 deg (clockwise) and check: no collision with housing/base outside the design
contacts; cam contacts the lever between 30 and 42 deg; stop lug hits the channel wall at 45 (and at 0)."""
import os, sys, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
import cadquery as cq
import params as P
from parts import socket as S

sf = S._parts_socket_frame()
housing, base, sw = sf['socket_housing'], sf['socket_base'], sf['switch_envelope']
rotor0 = sf['rotor']

def vol(w):
    try: return w.val().Volume()
    except Exception: return 0.0

def rotor_at(phi):
    return rotor0.rotate((0, 0, 0), (0, 0, 1), -phi)   # clockwise twist

print(f"magnet-to-sensor ({P.HALL_SENSOR}) ~{S.MAGNET_TO_SENSOR:.1f} mm; module depth {S.MODULE_DEPTH} mm below faceplate top")
ok = True
for phi in [0, 10, 20, 30, 35, 40, 42, 45, 46, 50, 60, 90]:
    r = rotor_at(phi)
    vh = vol(r.intersect(housing))
    vb = vol(r.intersect(base))
    vs = vol(r.intersect(sw))
    print(f"phi={phi:3d}  rotor^housing={vh:7.2f} mm3  rotor^base={vb:6.2f}  rotor^lever={vs:6.2f}")
    if phi <= 45 and vh > 0.5: ok = False
    if phi <= 45 and vb > 0.5: ok = False
# hard stop check: at 45.5 the lug must hit the channel wall
v455 = vol(rotor_at(45.8).intersect(housing)); v0 = vol(rotor_at(-0.8).intersect(housing))
print(f"stop check: at 45.8 deg overlap {v455:.2f} mm3 (must be > 0); at -0.8 deg overlap {v0:.2f} (must be > 0)")
ok = ok and v455 > 0 and v0 > 0
# lever contact
c30 = vol(rotor_at(29).intersect(sw)); c40 = vol(rotor_at(40).intersect(sw))
print(f"lever: contact at 29 deg {c30:.2f} (should be ~0), at 40 deg {c40:.2f} (must be > 0)")
ok = ok and c30 < 0.5 and c40 > 0
# A3144 post: a punch pushes the rotor toward the base plate; its skin must not reach the sensor post
if S.A3144:
    pushed = rotor_at(20).translate((0, 0, -(S.AXIAL_PLAY_DOWN - 0.05)))
    vp = vol(pushed.intersect(base))
    print(f"A3144 post: rotor pushed {S.AXIAL_PLAY_DOWN - 0.05:.2f} mm toward the base, overlap {vp:.2f} mm3 (must be ~0); "
          f"magnet to Hall element {S.MAGNET_TO_SENSOR:.1f} mm")
    ok = ok and vp < 0.5
print('SOCKET MECHANISM', 'OK' if ok else 'FAIL')
