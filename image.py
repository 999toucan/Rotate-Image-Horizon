import numpy as np
import cv2 as cv
import os 
import math
import helper
import sample


class image(object):
    def __init__(self, src):
        self.img_src = cv.imread(src)
        self.img_transform = self.img_src.copy()
        self.rotation_angle = 0
        self.vanishing_point = (-1, -1)
        self.hough_lines = np.asarray([False])
        self.mouse_coordinate = []
        # Check if image is loaded fine
        if self.img_src is None:
            raise ValueError
        

    def extract_coordinate(self, event, x, y, flag, param):
        if event == cv.EVENT_LBUTTONDOWN:
            # append point
            self.mouse_coordinate.append((x, y))
            cv.circle(self.img_transform, (int(x),int(y)), radius=10, color=(0, 0, 255), thickness=-1)
            cv.imshow('image',self.img_transform)
        if event == cv.EVENT_RBUTTONDOWN:
            # reset
            self.mouse_coordinate = []
            self.img_transform = self.img_src.copy()
            self.draw_hough_lines()
            self.draw_vanishing_point()
            cv.imshow('image',self.img_transform)

    def draw_vanishing_point(self):
        x, y = self.vanishing_point
        cols, rows, channel = self.img_src.shape
        if x < rows and y < cols and x > 0 and y >0:
            cv.circle(self.img_transform, (int(x),int(y)), radius=10, color=(0, 0, 255), thickness=-1)
    
    def draw_hough_lines(self):
        lines = self.hough_lines
        if lines.all() != False:
            cols, rows, channel = self.img_src.shape
            for slope, zero in lines:
                y2  = slope * rows + zero
                cv.line(self.img_transform,(0,int(-zero)),(rows,int(-y2)),(0,255,0),2)

    def get_transform_image(self):
        return self.img_transform
    
    def reset_image(self):
        self.img_transform = self.img_src.copy()

    def get_theta(self):
        return self.rotation_angle 

    def save_transformation(self, directory, filename):

        os.chdir(directory)         
        cv.imwrite(filename, self.img_transform) 
        
        print('Successfully saved') 

    # rotate the image based on hough line closest to caluclated vanishing point
    def rotate_horizon(self, vanishing_point, blur=True, k=3, threshold=50, minLineLength=5, maxLineGap=5, 
                    tiltThreshold = (1.48353, -1.48353)):
        # for flat images vanishing_point = 0
        # for images with one vanishing point, vanishing_point = 1
        # for images with two vanishing points, vanishing_point = 2

        img = cv.cvtColor(self.img_src, cv.COLOR_BGR2GRAY)
        cols, rows = img.shape
        theta = 0

        # filter img with canny filter /and gaussian
        if blur:
            edges = cv.GaussianBlur(cv.Canny(img,50,200,apertureSize = 3), (3,3), 0)
        else:
            edges = cv.Canny(img,50,200,apertureSize = 3)


        if vanishing_point == 0:
            lines = cv.HoughLinesP(edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
            lines_list = []
            max_length = 0
            longest_line = []

            for points in lines:
                x1,y1,x2,y2=points[0]
                lines_list.append([(x1,y1),(x2,y2)])
                # find longest line
                length = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
                if length > max_length:
                    max_length = length
                    longest_line = [(x1,y1),(x2,y2)]
            # record
            self.hough_lines = np.asarray([(helper.get_slope(longest_line), helper.get_zero(longest_line))])
            # self.draw_hough_lines()
            # self.save_transformation(r"C:\Users\gkw82\Downloads", r"line2HoughLines.png")

            # rotate image
            theta = helper.get_angle(longest_line)
            rotated_matrix = cv.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),-(theta*180/np.pi),1)
            self.img_transform = cv.warpAffine( src=self.img_src, M=rotated_matrix, dsize=(rows, cols)) 
            cv.imshow('image',self.img_transform)
            cv.waitKey(0) 

        if vanishing_point == 1:
            rerun = True
            while rerun:
                lines = cv.HoughLinesP(edges, 1, np.pi/180, threshold, minLineLength, maxLineGap)
                lines_list = [] 
                diag = np.sqrt(cols**2 + rows**2)
                cv.imshow('image',self.img_src)
                cv.waitKey(0) 

                # filter out lines that are too vertical 
                for points in lines:
                    x1,y1,x2,y2=points[0]
                    angle = helper.get_angle([(x1,y1),(x2,y2)])
                    if angle > -1.48353 and angle < 1.48353:
                        lines_list.append([(x1,y1),(x2,y2)])

                # use k-means to catergorize lines
                k_means = helper.k_means(k, lines_list)
                cluster = k_means[0]
                centers = k_means[1]

                # filter hough lines 
                filtered = []
                for i in range(0, len(centers)): 
                    group= np.asarray([x for (x,y) in zip(lines_list, cluster) if y == centers[i]])
                    filtered = filtered + helper.merge_lines(group, maxSlopeDiff=0.15, maxZeroDiff=30)

                filtered = np.asarray(filtered)
                filtered = filtered[filtered[:, 0] < tiltThreshold[0], :]            
                filtered = filtered[filtered[:, 0] > tiltThreshold[1], :]            
                self.hough_lines = filtered

                # find vanishing point
                vanishing_point = sample.RANSAC(filtered, math.comb(len(filtered), 2), diag/100, 0.8)
                x, y = vanishing_point
                y = -1 * y
                self.vanishing_point = (x, y)

                # draw onto self.img_transform
                self.draw_hough_lines()
                self.draw_vanishing_point()
                
                # manual input supporting points 
                print("The vanishing point is approximate " + str(self.vanishing_point))
                print("Left click to add more weighted points ...")
                cv.namedWindow('image')
                cv.imshow('image',self.img_transform)
                wait = True
                while wait:
                    cv.setMouseCallback('image', self.extract_coordinate) 
                    if cv.waitKey(0):
                        wait = False

                # find best matching line to horizon
                min_dist = math.sqrt(cols**2 + rows**2)
                min_line_index = -1 
                if self.hough_lines.all() != False:
                    for i in range(0, self.hough_lines.shape[0]):
                        line = self.hough_lines[i, :]
                        dist = 0
                        points = self.mouse_coordinate + [(self.vanishing_point[0], self.vanishing_point[1])]
                        for j in range(0, len(points)):
                            x, y = points[j]
                            dist += sample.find_dist_to_line(line, (x, -y))
                        if dist < min_dist:
                            min_dist = dist
                            min_line_index = i
                
                best_line = self.hough_lines[min_line_index, :]
                slope, zero = best_line
                y2 = slope * rows + zero
                cv.line(self.img_transform,(0,int(-zero)),(rows,int(-y2)),(0,0,255),2)
                cv.imshow('image',self.img_transform)
                cv.waitKey(0)

                theta = helper.get_angle([(0,int(-zero)),(rows,int(-y2))])
                rotated_matrix = cv.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),-(theta*180/np.pi),1)
                self.img_transform = cv.warpAffine( src=self.img_src, M=rotated_matrix, dsize=(rows, cols)) 
                print("Theta is " +  str(theta) + " press 'Esc' to reevaluate and press any to continue")
                print('\n')
                cv.imshow('image',self.img_transform)
                # any keystroke to continue
                key = cv.waitKey(0)
                if (key == 27):
                    self.reset_image()
                    rerun = True
                else:
                    rerun = False

                    
        print('record')
        # record rotation angle
        self.rotation_angle = -(theta*180/np.pi)
        # rotate image
        self.reset_image()
        rotated_matrix = cv.getRotationMatrix2D(((cols-1)/2.0,(rows-1)/2.0),self.rotation_angle,1)
        self.img_transform = cv.warpAffine( src=self.img_src, M=rotated_matrix, dsize=(rows, cols)) 
 



#line = image(r"C:\Users\gkw82\Downloads\line.png") 
#line.rotate_horizon(0)
#line.save_transformation(r"C:\Users\gkw82\Downloads", r"lineRotated.png")
#line2 = image(r"C:\Users\gkw82\Downloads\line2.png")
#line2.rotate_horizon(0)
#line2.save_transformation(r"C:\Users\gkw82\Downloads", r"lineRotated2.png")
#hall = image(r"C:\Users\gkw82\Downloads\hall2.png")
#hall.rotate_horizon(1, k=3, threshold=100, minLineLength=100, tiltThreshold=(1.3, -1.47))
#hall.save_transformation(r"C:\Users\gkw82\Downloads", r"hallRotated.png")
#costco = image(r"C:\Users\gkw82\Downloads\costco.jpg")
#costco.rotate_horizon(1, k=5, threshold=400, minLineLength=300, tiltThreshold=(1.47, -0.785))
#costco.save_transformation(r"C:\Users\gkw82\Downloads", r"costcoRotated.png")
