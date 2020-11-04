import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import json

def heatmap(data, row_labels, col_labels, ax=None,
            cbar_kw={}, cbarlabel="", **kwargs):
    """
    Create a heatmap from a numpy array and two lists of labels.

    Parameters
    ----------
    data
        A 2D numpy array of shape (N, M).
    row_labels
        A list or array of length N with the labels for the rows.
    col_labels
        A list or array of length M with the labels for the columns.
    ax
        A `matplotlib.axes.Axes` instance to which the heatmap is plotted.  If
        not provided, use current axes or create a new one.  Optional.
    cbar_kw
        A dictionary with arguments to `matplotlib.Figure.colorbar`.  Optional.
    cbarlabel
        The label for the colorbar.  Optional.
    **kwargs
        All other arguments are forwarded to `imshow`.
    """

    if not ax:
        ax = plt.gca()

    # Plot the heatmap
    im = ax.imshow(data, **kwargs)

    # Create colorbar
    cbar = ax.figure.colorbar(im, ax=ax, **cbar_kw)
    cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

    # We want to show all ticks...
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_yticks(np.arange(data.shape[0]))
    # ... and label them with the respective list entries.
    ax.set_xticklabels(col_labels)
    ax.set_yticklabels(row_labels)

    # Let the horizontal axes labeling appear on top.
    ax.tick_params(top=True, bottom=False,
                   labeltop=True, labelbottom=False)

    # Rotate the tick labels and set their alignment.
    plt.setp(ax.get_xticklabels(), rotation=-30, ha="right",
             rotation_mode="anchor")

    # Turn spines off and create white grid.
    for edge, spine in ax.spines.items():
        spine.set_visible(False)

    ax.set_xticks(np.arange(data.shape[1]+1)-.5, minor=True)
    ax.set_yticks(np.arange(data.shape[0]+1)-.5, minor=True)
    ax.grid(which="minor", color="w", linestyle='-', linewidth=3)
    ax.tick_params(which="minor", bottom=False, left=False)

    return im, cbar


# Open json file with qvalues
qvals_json = dict()
with open("Qvalues/qValues_2500.json") as f:
    qvals_json = json.load(f)

# vertical distance (y-axis) and velocity (x-axis), heatmap for horizontal distance of 0
ver_dist = []
vel = []
hor_dist = 50
action = 0
rounding = 50

# key example: "player_vel -7.0 hor_dist_to_next_pipe 50 ver_dist_to_next_pipe 100 action 1"
# Find maximum and minimum values of states
max_ver_dist = -np.inf
min_ver_dist = np.inf
max_vel = -np.inf
min_vel = np.inf
for key in qvals_json:
    key_parsed = key.split(" ")
    if max_ver_dist < int(key_parsed[5]):
        max_ver_dist = int(key_parsed[5])
    if min_ver_dist > int(key_parsed[5]):
        min_ver_dist = int(key_parsed[5])
    if max_vel < float(key_parsed[1]):
        max_vel = float(key_parsed[1])
    if min_vel > float(key_parsed[1]):
        min_vel = float(key_parsed[1])

# Create two-dimensional array of Q-Values
ver_dist_len = ((max_ver_dist - min_ver_dist)//rounding) + 1
vel_len = int(max_vel - min_vel) + 1
qvals = np.zeros((ver_dist_len, vel_len))


# Fill Q-Values array with values from json dictionary
for i in range(ver_dist_len):
    for j in range(vel_len):
        key = f"player_vel {min_vel + j} hor_dist_to_next_pipe {hor_dist} ver_dist_to_next_pipe {min_ver_dist + (i*rounding)} action {action}"
        if key in qvals_json:
            qvals[i][j] = qvals_json[key]

print(np.amin(qvals))
        
# Fill arrays of labels
for i in range(ver_dist_len):
    ver_dist.append(f"vert {min_ver_dist + (i*rounding)}")

for i in range(vel_len):
    vel.append(f"vel {min_vel + i}")

fig, ax = plt.subplots()

im, cbar = heatmap(qvals, ver_dist, vel, ax=ax,
                   cmap="YlGn", cbarlabel="Qvalues")


fig.tight_layout()
fig.set_size_inches(18.5, 10.5)
plt.savefig("Qvals.svg", dpi=600, bbox_inches="tight")
