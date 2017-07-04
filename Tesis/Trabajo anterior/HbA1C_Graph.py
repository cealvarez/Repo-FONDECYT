__author__ = 'Tania'

import matplotlib.pyplot as plt
import DMCompensation as dm
import Reader as rd


def graph_points(points_lists, cluster_name):
    for points in points_lists:
        print(points_lists[points][1])
        plt.plot(points_lists[points][0], points_lists[points][1], '-o', linewidth=2)

    # Create a list of values in the best fit line
    x = [i for i in range(21)]
    y = [7 for i in range(21)]
    plt.plot(x, y, '-.', linewidth=3)
    plt.title('cluster: ' + cluster_name)
    plt.show()

clusters = 'Log/FinalTables/quad_int_new.csv'
dm_file = 'Log/FinalTables/dm_compensation_T90.csv'
cluster_list = ["1", "2", "3", "4", "5", "6"]
dm.set_only_dm_data(clusters, cluster_list, dm_file, 'X', 0, 600, [1, 2014], [5, 2016], 2)
#rd.read_clusters(clusters, ["1", "2", "3", "4"])
#rd.read_dm_compensation_t90(dm_file, 'X', 0, 600, [1, 2014], [5, 2016], 2)
points = dm.mark_periods()
for cluster in cluster_list:
    graph_points(points[cluster], cluster)
