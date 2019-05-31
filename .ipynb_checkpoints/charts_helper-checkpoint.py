def get_approaches_results(datasets, column_mean, column_std, group_by_th = False, items_num = 1000):
    mean = []
    std = []
    #initial
    if group_by_th == True:
        ths = datasets[0]["threshold"]
        for th in ths:
            for data in datasets:
                data = data[data["threshold"]==th]
                if(column_mean == 'cost'):
                    vals = data[column_mean]/data['cost_ratio'][0]/items_num
                    for v in vals:
                        mean.append(v)
                    vals_std = data[column_std]/data['cost_ratio'][0]/items_num
                    for s in vals_std:
                        std.append(s)
                else:
                    vals = data[column_mean]
                    for v in vals:
                        mean.append(v)
                    vals_std = data[column_std]
                    for s in vals_std:
                        std.append(s)
    else:
        for data in datasets:
            if(column_mean == 'cost'):
                vals = data[column_mean]/data['cost_ratio']/items_num
                for v in vals:
                    mean.append(v)
                vals_std = data[column_std]/data['cost_ratio']/items_num
                for s in vals_std:
                    std.append(s)
            else:
                vals = data[column_mean]
                for v in vals:
                    mean.append(v)
                vals_std = data[column_std]
                for s in vals_std:
                    std.append(s)
        
    return mean, std

def get_group_colors(groups, subgroups):
    #colors = ['blue', 'green', 'red', 'cyan', 'magenta', 'yellow', 'black', 'white']
    return np.concatenate([[np.concatenate(np.random.rand(3,1))] * subgroups for x in range(groups)])

def concatenate(list1, list2):
    result = []
    for elem1 in list1:
        result.append(elem1)
        
    for elem2 in list2:
        result.append(elem2)
        
    return result

def get_total_results(list1, list2, column, mv_num=None, cost_ratio=None, decision_fn=None, threshold=None, class_fn=None, c=None, e=None):
    if mv_num != None:
        return concatenate(list1[list1['votes']==mv_num][column].values, 
                           list2[list2['votes']==mv_num][column].values)
    elif c != None:
        return concatenate(list1[list1['c']==c][list1['e']==e][column].values, 
                           list2[list2['c']==c][list2['e']==e][column].values)
    elif class_fn != None:
        return concatenate(list1[list1['class_fn']==class_fn][list1['decision_fn']==decision_fn][list1['cost_ratio']==cost_ratio][list1['threshold']==threshold][column].values, 
                           list2[list2['class_fn']==class_fn][list2['decision_fn']==decision_fn][list2['cost_ratio']==cost_ratio][list2['threshold']==threshold][column].values)
    elif decision_fn != None:
        return concatenate(list1[list1['decision_fn']==decision_fn][list1['cost_ratio']==cost_ratio][list1['threshold']==threshold][column].values, 
                           list2[list2['decision_fn']==decision_fn][list2['cost_ratio']==cost_ratio][list2['threshold']==threshold][column].values)
    else:
        return concatenate(list1[column].values, 
                           list2[column].values)
    
from itertools import cycle

def plot_elems_lines(elems, x_values, columns, ylabel, legends, url_to_save_fig, titles, legend_loc = 'best'):
    lines = ["-", "--", "-.", ":"]
    xticks_ind = np.arange(len(x_values))
    plt.figure()
    #plt.grid(zorder=0)

    for key, column in enumerate(columns):
        linecycler = cycle(lines)
        #plt.subplot(3, 2, key + 1)
        column_std = f'{column}_std'

        for elem in elems:
            plt.errorbar(xticks_ind, column, column_std, data=elem, linestyle=next(linecycler), marker='o',
                         markersize=5)
        # end for

        plt.xticks(xticks_ind, x_values, fontsize=10)
        plt.yticks(fontsize=10)
        plt.xlabel(ylabel, fontsize=12)
        plt.ylabel(column.capitalize(), fontsize=12)
       
        plt.title(titles[key], fontweight="bold", fontsize=15)
        plt.legend(legends, loc=legend_loc)

    #plt.tight_layout()
    plt.grid()
    plt.savefig(url_to_save_fig, bbox_inches = 'tight', pad_inches = 0)
    plt.show()