import numpy as np
import math


def find_intersection_slopepoint(psline1,psline2):
    # return point in cartesian coordinate
    slope1, zero1 = psline1
    slope2, zero2 = psline2
    
    np.seterr(divide='ignore', invalid='ignore')
    if slope1 == slope2 and zero1 != zero2:
        return False
    if 1/(slope1 - slope2) == 0: 
        return False
    else:
        x = (zero2 - zero1)/(slope1 - slope2)
        y = slope1*x + zero1
        return (x,y)
        
# Function 2: Find the distance from a point to a line
def find_dist_to_line(line, point):
    # line: y = mx + b
    # point: in cartesian coordinates
    x1, y1 = point
    slope2, zero2 = line
    # print("point is " + str(point))
    # print("slope equals " + str(slope2))
    if slope2 != 0:
        zero1 = y1 + (1/slope2)*x1
        # sign should be negative or smth
        slope1 = -1/slope2
        if find_intersection_slopepoint((slope2, zero2), (slope1, zero1)) != False:
            x2, y2 = find_intersection_slopepoint((slope2, zero2), (slope1, zero1))
            dist = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
            return dist
        else:
            return 0
    else: 
        return math.sqrt((zero2 - y1)**2)

def RANSAC(lines,ransac_iterations,ransac_threshold,ransac_ratio):
    """Implementation is based on code from Computer Vision material, owned by the University of Melbourne
    Use RANSAC to identify the vanishing points for a given image
    Args: lines: The lines for the image
    ransac_iterations,ransac_threshold,ransac_ratio: RANSAC hyperparameters
    Return: vanishing_point: Estimated vanishing point for the image
    """
    # lines is array
    inlier_count_ratio = 0
    vanishing_point = (0,0)
    # perform RANSAC iterations for each set of lines
    for iteration in range(ransac_iterations):
        # randomly sample 2 lines
        n = 2
        index = np.random.choice(lines.shape[0], 2)
        line1 = lines[index[0]]
        line2 = lines[index[1]]
        intersection_point = find_intersection_slopepoint(line1,line2)
        if intersection_point is not False:
            # count the number of inliers num
            inlier_count = 0
            # inliers are lines whose distance to the point is less than ransac_threshold
            for line in lines:
                # find the distance from the line to the point
                # zero if point ison the line
                dist = find_dist_to_line(line, intersection_point)
                # check whether it's an inlier or not
                if dist < ransac_threshold:
                    inlier_count += 1

            # If the value of inlier_count is higher than previously saved value, save it, and save the current point
            if inlier_count / float(len(lines)) > inlier_count_ratio:
                inlier_count_ratio = inlier_count / float(len(lines))
                vanishing_point = intersection_point

            # We are done in case we have enough inliers
            if inlier_count > len(lines)*ransac_ratio:
                break
    return vanishing_point