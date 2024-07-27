import sys

import astropy.cosmology
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

box_size = int(sys.argv[1])
n_part = int(sys.argv[2])
run = sys.argv[3]
n_frame = int(sys.argv[4])

sim_name = f'L{box_size:04d}N{n_part:04d}/{run}/'
# TODO: Set dir
output_dir = f'/snap8/scratch/dp004/dc-mcgi1/movies/flamingo/stars_sw/{sim_name}/'

# TODO: Make sure this matches with generated frames
zmin = 0
zmax = 15
a_range = np.linspace(1.0 / (1 + zmax), 1.0, n_frame)
z_range = 1.0 / a_range - 1.0

for i_frame in range(n_frame):
    print(f'Plotting frame: {i_frame}')
    z = z_range[i_frame]

    fig, ax = plt.subplots(figsize=(16, 9))

    try:
        # Load mapdata, cut to create 16:9 video
        mapdata = np.load(f'{output_dir}/stars_{i_frame:04d}.npz')['surfdens']
        i_cut = mapdata.shape[0] * 7 // 32
        mapdata = mapdata[:, i_cut:-i_cut]

        dmax = mapdata.max()
        dmin = 1.0e-9 * dmax
        mapdata[mapdata < dmin] = dmin
        mapdata[mapdata > dmin] = dmax
        mapdata = matplotlib.colors.LogNorm(vmin=dmin, vmax=dmax)(mapdata)

        star_map = plt.get_cmap('gist_gray')
        mapdata = star_map(mapdata.T)

        ax.imshow(mapdata, origin="lower")
    except FileNotFoundError:
        black = black_image = np.zeros((9, 16, 3), dtype=np.uint8)
        ax.imshow(black, origin="lower")

    cosmo = astropy.cosmology.FlatLambdaCDM(H0=68.1, Om0=0.306)
    age = cosmo.age(z).value
    time_label = f'Universe Age: {age:.2f} Gyr'
    ax.text(0.02, 0.05, time_label, color="w", transform = ax.transAxes, fontsize='x-large')
    ax.text(0.85, 0.08, "FLAMINGO", color="w", transform = ax.transAxes, fontsize='large')
    ax.text(0.85, 0.04, "Virgo Consortium", color="w", transform = ax.transAxes, fontsize='large')
    ax.axis("off")

    plt.tight_layout(pad=0)

    logo = plt.imread("flamingo_logo.png")
    ax1 = fig.add_axes([0.92,0.02,0.08,0.1])
    ax1.imshow(logo)
    ax1.axis('off')

    plt.savefig(f'{output_dir}/frame_{i_frame:04d}.png', dpi=240)
    fig.clear()
    plt.close(fig)

