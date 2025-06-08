import numpy as np
import plotly.graph_objects as go

# === Utility: Transformations ===
def apply_transform(points, translate=(0,0,0), rotate=(0,0,0), scale=(1,1,1)):
    """Apply scale → rotation (X, Y, Z) → translation to 3D points."""
    pts = points * np.array(scale)
    rx, ry, rz = rotate
    Rx = np.array([[1,0,0],
                   [0,np.cos(rx), -np.sin(rx)],
                   [0,np.sin(rx),  np.cos(rx)]])
    Ry = np.array([[ np.cos(ry),0,np.sin(ry)],
                   [0,1,0],
                   [-np.sin(ry),0,np.cos(ry)]])
    Rz = np.array([[np.cos(rz),-np.sin(rz),0],
                   [np.sin(rz), np.cos(rz),0],
                   [0,0,1]])
    pts = pts @ Rx.T @ Ry.T @ Rz.T
    return pts + np.array(translate)

# === Primitives: Basic 3D shapes ===
def create_cube(size):
    """Return vertices and faces for a cuboid (used for body and shelves)."""
    lx, ly, lz = size
    v = np.array([[0,0,0],[lx,0,0],[lx,ly,0],[0,ly,0],
                  [0,0,lz],[lx,0,lz],[lx,ly,lz],[0,ly,lz]])
    f = [[0,1,2],[0,2,3],[4,5,6],[4,6,7],
         [0,1,5],[0,5,4],[1,2,6],[1,6,5],
         [2,3,7],[2,7,6],[3,0,4],[3,4,7]]
    return v, f

def create_plane(size):
    """Return vertices and faces for a flat door plane."""
    lx, lz = size
    v = np.array([[0,0,0],[lx,0,0],[lx,0,lz],[0,0,lz]])
    f = [[0,1,2],[0,2,3]]
    return v, f

def create_cylinder(r=0.03, h=0.12, seg=18):
    """Return vertices and faces for cylindrical handle."""
    th = np.linspace(0, 2*np.pi, seg, endpoint=False)
    x, y = r*np.cos(th), r*np.sin(th)
    bot = np.stack([x, y, np.zeros_like(x)], 1)
    top = bot + np.array([0, 0, h])
    v = np.vstack([bot, top])
    f = []
    for i in range(seg):
        j = (i+1) % seg
        f.append([i, j, seg+j])
        f.append([i, seg+j, seg+i])
    return v, f

def create_cuboid(l, w, h):
    """Return vertices and faces for cuboid handle."""
    s = np.array([[-.5,-.5,-.5],[.5,-.5,-.5],[.5,.5,-.5],[-.5,.5,-.5],
                  [-.5,-.5,.5],[.5,-.5,.5],[.5,.5,.5],[-.5,.5,.5]])
    v = s * np.array([l, w, h])
    f = [[0,1,2],[0,2,3],[4,5,6],[4,6,7],
         [0,1,5],[0,5,4],[1,2,6],[1,6,5],
         [2,3,7],[2,7,6],[3,0,4],[3,4,7]]
    return v, f

# === Cabinet Parameters ===
lebar, dalam, tinggi = 1.0, 0.5, 2.0
tebal_rak, door_gap = 0.025, 0.02
door_angle = np.pi/3  # 60° open

traces = []

# === Cabinet Body ===
body_v, body_f = create_cube((lebar, dalam, tinggi))
traces.append(go.Mesh3d(x=body_v[:,0], y=body_v[:,1], z=body_v[:,2],
                        i=[f[0] for f in body_f], j=[f[1] for f in body_f], k=[f[2] for f in body_f],
                        color='saddlebrown', opacity=0.7, name='Body'))

# === Left Door (Open 60°) ===
door_v, door_f = create_plane((lebar/2 - door_gap, tinggi))
door_left = apply_transform(door_v,
                             rotate=(0,0,door_angle),
                             translate=(0, dalam+0.001, 0))  # hinge at x=0
traces.append(go.Mesh3d(x=door_left[:,0], y=door_left[:,1], z=door_left[:,2],
                        i=[f[0] for f in door_f], j=[f[1] for f in door_f], k=[f[2] for f in door_f],
                        color='peru', opacity=0.95, name='Pintu Kiri'))

# === Right Door (Closed) ===
door_right = door_v + np.array([lebar/2 + door_gap, dalam+0.001, 0])
traces.append(go.Mesh3d(x=door_right[:,0], y=door_right[:,1], z=door_right[:,2],
                        i=[f[0] for f in door_f], j=[f[1] for f in door_f], k=[f[2] for f in door_f],
                        color='peru', opacity=0.95, name='Pintu Kanan'))

# === Left Handle (Cuboid) ===
h_v, h_f = create_cuboid(0.04, 0.02, 0.04)
rel = np.array([(lebar/2 - door_gap) - 0.04, 0.02, tinggi / 2])
h_v = h_v + rel
h_v = apply_transform(h_v, rotate=(0, 0, door_angle))
h_v = h_v + np.array([0, dalam+0.001, 0])
traces.append(go.Mesh3d(x=h_v[:,0], y=h_v[:,1], z=h_v[:,2],
                        i=[f[0] for f in h_f], j=[f[1] for f in h_f], k=[f[2] for f in h_f],
                        color='gold', opacity=1.0, name='Handle Kiri'))

# === Right Handle (Cylinder) ===
cyl_v, cyl_f = create_cylinder()
cyl_v = apply_transform(cyl_v,
                        rotate=(np.pi/2, 0, 0),
                        translate=(0.75*lebar, dalam+0.03, tinggi/2))
traces.append(go.Mesh3d(x=cyl_v[:,0], y=cyl_v[:,1], z=cyl_v[:,2],
                        i=[f[0] for f in cyl_f], j=[f[1] for f in cyl_f], k=[f[2] for f in cyl_f],
                        color='gold', opacity=1.0, name='Handle Kanan'))

# === Shelves (4 Levels) ===
rak_p, rak_f = create_cube((lebar-0.04, dalam-0.04, tebal_rak))
for idx in range(4):
    zpos = tinggi * (idx + 1) / 5
    rv = rak_p + np.array([0.02, 0.02, zpos])
    traces.append(go.Mesh3d(x=rv[:,0], y=rv[:,1], z=rv[:,2],
                            i=[f[0] for f in rak_f], j=[f[1] for f in rak_f], k=[f[2] for f in rak_f],
                            color='sienna', opacity=1.0, name=f'Rak{idx+1}'))

# === Layout & Scene ===
fig = go.Figure(data=traces,
        layout=go.Layout(
            scene=dict(
                xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                aspectratio=dict(x=1, y=0.5, z=2),
                camera=dict(eye=dict(x=1.8, y=2, z=1.2))
            ),
            showlegend=False,
            margin=dict(l=0, r=0, t=0, b=0),
            title="Lemari 3D – Pintu Kiri Terbuka"
        ))

# === Export as JSON for embedding (e.g., in Pyodide) ===
fig_json = fig.to_json()
def get_plot_json():
    return fig_json
