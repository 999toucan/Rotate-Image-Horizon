# Rotate Image Horizon

A common problem in photography is that without a tripod it is hard to get a perfectly flat horizon. This script rotates images so that the horizon of the image is parallel to the x-axis, this can simplify and streamline ph oto editing. The new horizon is found through hough lines.

## Simple Horizon

```python
line = image(r".\line.png") 
line.rotate_horizon(0, blur=False)
```
![1.1 Base image](images/line1.png?raw=true)

Put the image through Hough Line transformation and find the rotational angle of the best fitting line.

![1.2 Possible horizon found through hough line transformation](images/line1HoughLines.png?raw=true)
![1.3 After rotation](images/line1Rotated.png?raw=true)

## Example: With a Simple Line

A simple line.

In this example, a Gaussian blur is applied to smooth data. Otherwise due to the limited resolution the Hough Lines come out to be perfectly horizontal.

![2.1 Base image](images/line2.png?raw=true)
![2.2 Without gaussian](images/line2Flat.png?raw=true)

Put the image through Hough Line transformation and find the rotational angle of the best fitting line.

![2.3 New horizon](images/line2HoughLines.png?raw=true)
![2.2 Rotated image](images/line2Rotated.png?raw=true)

## One Point Perspective

```python
hall.rotate_horizon(1, blur=True, k=3, 
    threshold=100, minLineLength=100, minLineGap=5, tiltThreshold=(1.47, -1.47))
```

There are more parameters which can be adjusted for pictures with one point perspective. 

* **blur**: applies gaussian True/False 
* **k**: number of initial centers in k-means clustering
* **threshold**: parameter for [HoughLinesP](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga8618180a5948286384e3b7ca02f6feeb)
* **minLineLength**: parameter for [HoughLinesP](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga8618180a5948286384e3b7ca02f6feeb)
* **minLineGap**: parameter for [HoughLinesP](https://docs.opencv.org/3.4/dd/d1a/group__imgproc__feature.html#ga8618180a5948286384e3b7ca02f6feeb)
* **tiltThreshold**: tuple of radians, only lines with angle within the range (max,min) will be used (gets rid of vertical 90 degrees) 

Based on reference [[1]](https://iopscience.iop.org/article/10.1088/1742-6596/1748/3/032052/pdf)
[[2]](https://medium.com/@KuoyuanLi/detecting-the-vanishing-point-in-one-point-perspective-images-using-computer-vision-algorithms-c4352d4e6c3e) connecting like lines, clustering lines using k-means, and RANSAC sampling can better identify a vanishing point. We then use a Hough Line closest to the vanishing point to find the horizon. Selection can be improved with manual input: we can introduce more points to the set of points that are used to find the best fit line.

## Example: One Point Perspective

Example of script with image of hall way [[3]]( https://weloveeastvan.com/concrete-buildings/).

|![3.1 Base image](images/hall.png?raw=true)|
|3.1 Base image|

|![3.2 Hough lines and vanishing point](images/hallHoughLines.png?raw=true)|
|3.2 Diagram of calculated hough lines and vanishing point|

|![3.3 Pick new horizon with support points](images/hallHoughLinesCalibrate.png?raw=true)|
|3.3 Pick new horizon with support points|

|![3.2 After -0.0039 degree rotation](images/hallRotated.png?raw=true)|
|3.2 After -0.0039 degrees of rotation|



|![4.1 Base image](images/costco.jpg?raw=true)|
|4.1 Base image|

|![4.2 Hough lines and vanishing point](images/costcoHoughLines.png?raw=true)|
|4.2 Hough lines and vanishing point|

|![4.3 Pick new horizon with support points](images/costcoHoughLinesCalibrate.png?raw=true)|
|4.3 Pick new horizon with support points|

|![4.2 After rotation](images/costcoRotated.png?raw=true)|
|4.2 After rotation|

## References

[[1] Vanishing Point Detection based on Line Set Optimization](https://iopscience.iop.org/article/10.1088/1742-6596/1748/3/032052/pdf)

[[2] Detecting the vanishing point in one-point perspective images using Computer Vision algorithms](https://medium.com/@KuoyuanLi/detecting-the-vanishing-point-in-one-point-perspective-images-using-computer-vision-algorithms-c4352d4e6c3e)


[[3] Picture of concrete building]( https://weloveeastvan.com/concrete-buildings/)
