def auc(num_positives, num_negatives, predicted):
    l_sorted = sorted(range(len(predicted)),key=lambda i: predicted[i],
                      reverse=True)
    fp_cur = 0.0
    tp_cur = 0.0
    fp_prev = 0.0
    tp_prev = 0.0
    fp_sum = 0.0
    auc_tmp = 0.0
    last_score = float("nan")

    for i in range(len(predicted)): # for each pos of pCTR
        if last_score != predicted[l_sorted[i]]:
            auc_tmp += trapezoid_area(fp_cur,fp_prev,tp_cur,tp_prev)
            last_score = predicted[l_sorted[i]]            
            fp_prev = fp_cur
            tp_prev = tp_cur
        tp_cur += num_positives[l_sorted[i]]
        fp = num_negatives[l_sorted[i]]
        if(fp < 0):
            raise Exception("Line: " + str(i))
        fp_cur += fp
        fp_sum += fp
    auc_tmp += trapezoid_area(fp_cur,fp_prev,tp_cur,tp_prev)
    auc = auc_tmp / (tp_cur * fp_sum)
    return auc

def trapezoid_area(x1, x2, y1, y2):
    if(x1 == x2):
        return 0.0
    base = abs(x1 - x2)
    height_avg = (y1 + y2) / 2
    return base * height_avg
