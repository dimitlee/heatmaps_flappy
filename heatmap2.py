import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import json
import os


def annotate_heatmap(im, data=None, valfmt="{x:.2f}",
                     textcolors=["black", "white"],
                     threshold=None, **textkw):
    """
    A function to annotate a heatmap.

    Parameters
    ----------
    im
        The AxesImage to be labeled.
    data
        Data used to annotate.  If None, the image's data is used.  Optional.
    valfmt
        The format of the annotations inside the heatmap.  This should either
        use the string format method, e.g. "$ {x:.2f}", or be a
        `matplotlib.ticker.Formatter`.  Optional.
    textcolors
        A list or array of two color specifications.  The first is used for
        values below a threshold, the second for those above.  Optional.
    threshold
        Value in data units according to which the colors from textcolors are
        applied.  If None (the default) uses the middle of the colormap as
        separation.  Optional.
    **kwargs
        All other arguments are forwarded to each call to `text` used to create
        the text labels.
    """

    if not isinstance(data, (list, np.ndarray)):
        data = im.get_array()

    # Normalize the threshold to the images color range.
    if threshold is not None:
        threshold = im.norm(threshold)
    else:
        threshold = im.norm(data.max())/2.

    # Set default alignment to center, but allow it to be
    # overwritten by textkw.
    kw = dict(horizontalalignment="center",
              verticalalignment="center")
    kw.update(textkw)

    # Get the formatter in case a string is supplied
    if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

    # Loop over the data and create a `Text` for each "pixel".
    # Change the text's color depending on the data.
    texts = []
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            kw.update(color=textcolors[int(im.norm(data[i, j]) < threshold)])
            text = im.axes.text(j, i, valfmt(data[i, j], None), **kw)
            texts.append(text)

    return texts

iteration = 250
while iteration <= 2500:
    # Open json file with qvalues
    rounding = 50
    dir_name = f"Qiter_{iteration}"
    if not os.path.exists(dir_name):
        os.mkdir(dir_name)
    qvals_json = dict()
    with open(f"Qvalues/qValues_{iteration}.json") as f:
        qvals_json = json.load(f)

    # vertical distance (y-axis) and velocity (x-axis), heatmap for horizontal distance of 0


    # key example: "player_vel -7.0 hor_dist_to_next_pipe 50 ver_dist_to_next_pipe 100 action 1"
    # Find maximum and minimum values of states
    max_ver_dist = -np.inf
    min_ver_dist = np.inf
    max_hor_dist = -np.inf
    min_hor_dist = np.inf
    max_vel = -np.inf
    min_vel = np.inf
    for key in qvals_json:
        key_parsed = key.split(" ")
        if max_ver_dist < int(key_parsed[5]):
            max_ver_dist = int(key_parsed[5])
        if min_ver_dist > int(key_parsed[5]):
            min_ver_dist = int(key_parsed[5])
        if max_hor_dist < int(key_parsed[3]):
            max_hor_dist = int(key_parsed[3])
        if min_hor_dist > int(key_parsed[3]):
            min_hor_dist = int(key_parsed[3])
        if max_vel < float(key_parsed[1]):
            max_vel = float(key_parsed[1])
        if min_vel > float(key_parsed[1]):
            min_vel = float(key_parsed[1])

    # Create two-dimensional array of Q-Values, calculate length of label arrays
    ver_dist_len = ((max_ver_dist - min_ver_dist)//rounding) + 1
    vel_len = int(max_vel - min_vel) + 1
    hor_dist_len = ((max_hor_dist - min_hor_dist)//rounding) + 1
    qvals = np.zeros((ver_dist_len, vel_len))

    # Fill arrays of labels
    ver_dist = []
    vel = []
    hor_dist = []
    action = [0, 1]

    for i in range(ver_dist_len):
        ver_dist.append(f"vert {min_ver_dist + (i*rounding)}")

    for i in range(hor_dist_len):
        hor_dist.append(min_hor_dist + (i*rounding))

    for i in range(vel_len):
        vel.append(f"vel {min_vel + i}")

    # Iterate through hor_dist and action values to plot heatmaps for each hor_dist and action combination
    for hor in hor_dist:
        for a in action:
            # Fill Q-Values array with values from json dictionary
            for i in range(ver_dist_len):
                for j in range(vel_len):
                    key = f"player_vel {min_vel + j} hor_dist_to_next_pipe {hor} ver_dist_to_next_pipe {min_ver_dist + (i*rounding)} action {a}"
                    if key in qvals_json:
                        qvals[i][j] = qvals_json[key]
                    else:
                        qvals[i][j] = 0.0

            fig, ax = plt.subplots()
            im = ax.imshow(qvals)

            # We want to show all ticks...
            ax.set_xticks(np.arange(len(vel)))
            ax.set_yticks(np.arange(len(ver_dist)))
            # ... and label them with the respective list entries
            ax.set_xticklabels(vel)
            ax.set_yticklabels(ver_dist)

            # Rotate the tick labels and set their alignment.
            plt.setp(ax.get_xticklabels(), rotation=45, ha="right",
                    rotation_mode="anchor")

            texts = annotate_heatmap(im, valfmt="{x:1.1e}", fontsize="5")

            ax.set_title(f"Hor_dist: {hor}, action: {a}")
            fig.tight_layout()
            fig.set_size_inches(10.0, 5)
            plt.savefig(f"Qiter_{iteration}/Qvals_hor{hor}_a{a}.png", dpi=300)
            plt.close()

    # Go to next iteration of the loop
    iteration += 250
