import json
import numpy as np

iter = 0

# last testing phase on 2500 iteration
while iter < 2500:
    iter += 250
    print(f"############### Iteration - {iter} ###############")

    # put path to file here
    with open(f'scores/scores_{iter}.json') as f:
        data = json.load(f)

    data_list = []

    for key in data:
        for i in range(data[key]):
            data_list.append(int(key))

    print(f"Max score: {np.amax(data_list)}")
    print(f"Avg score: {np.mean(data_list)}")
    print(f"Variance: {np.var(data_list)}")
    print("\n\n")
