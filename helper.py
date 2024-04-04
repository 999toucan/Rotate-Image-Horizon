import numpy as np

def get_angle(line):
    # return [-pi/2, pi/2]
    if line[1][0] - line[0][0] == 0:
        return np.pi/2
    else:
        angle = np.arctan(-(line[1][1] - line[0][1]) / (line[1][0] - line[0][0]))
        return angle     

def get_slope(line):
    return -(line[1][1] - line[0][1]) / (line[1][0] - line[0][0])

def get_zero(line):
    # line = [(x1,y1), (x2,y2)]
    # return: zero, such that line intersects the (0, -zero) coordinate
    m = get_slope(line)
    zero = - line[0][1] - m*line[0][0]
    return zero
   
def avg(arr):
    if len(arr) != 0:
        return np.sum(arr)/len(arr)
    else:
        return np.nan

def find_distance(centers, th):
    # centers is array of elements from [-pi/2, pi/2]
    # th from [-pi/2, pi/2]
    # returns absval of magnitude
    norm = centers + np.pi/2
    th += np.pi/2
    return np.absolute(norm - th)

def k_means(k, lines_list):
    if lines_list == []:
        print('err:empty list for k-means')
        return (0,0)
    length = len(lines_list)
    centers = np.random.random(k)*np.pi-np.pi/2
    angles = np.zeros(length)
    assigned = np.zeros(length)
    for i in range(0, length):
        theta = get_angle(lines_list[i])
        angles[i] = theta
        dist = find_distance(centers, angles[i])
        assigned[i] = centers[np.argmin(dist, axis = 0)]
    next_centers = np.zeros(k)
    n = 10
    while (n):
    # calculate new centers
        for i in range(0, len(centers)):
            next_centers[i] = avg(angles[np.where(assigned == centers[i])])
        next_centers = next_centers[next_centers == next_centers]
        # new assignment
        for j in range(0, length):
            dist = find_distance(next_centers, angles[j])
            assigned[j] = next_centers[np.argmin(dist)]
        if np.array_equal(centers, next_centers):
            break
        else:
            centers = next_centers
            n -= 1
    return [assigned,centers]

def filter(lines_list):
    return 0

def merge_lines(list_lines, maxSlopeDiff=0.5, maxZeroDiff=5):
    # list_lines is np array
    # combine lines with similar 

    param = np.zeros((2, list_lines.shape[0]))

    # get point slope form
    for i in range(0, list_lines.shape[0]):
        line = list_lines[i]
        param[0,i] = get_slope(line)
        param[1,i] = get_zero(line)

    # sort
    arg = np.argsort(param[0,:])
    param[:,:] = param[:, arg]
    lines = []
    pointer = 0

    # merge lines that have close intercepts and slopes
    while (pointer < param.shape[1] - 1):
        slope = param[0, pointer]
        zero = param[1, pointer]
        
        # find lines that meet threshold 
        index_slope = np.nonzero(param[0,:] < slope + maxSlopeDiff)
        index_zero = np.nonzero(param[1,:] < zero + maxZeroDiff)
        index = np.intersect1d(index_slope, index_zero)

        # merge line and append as 'point-slope form'
        merged = param[:, index]
        avg_slope = np.sum(merged[0,:])/index.size
        avg_zero = np.sum(merged[1,:])/index.size
        lines.append((avg_slope, avg_zero))
        # change pointer
        pointer = np.max(index) + 1
    return lines
