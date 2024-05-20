#before converting to do while
import cv2
import numpy as np
import time
import pyautogui
import matplotlib.pyplot as plt
import sys
import math

np.set_printoptions(threshold=sys.maxsize)

#1512  x 982 Estimated
#3024 × 1964 Actual

#borders are rgba(255,255,255,255)
#ball is rgba(233,233,233,255)
time.sleep(2)

#Take Screenshot and convert to grayscale_image np array
screenshot = pyautogui.screenshot()
screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
img = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)

#Ignore last few rows (avoid pickingup misinformation because of ad)
#img = img[:1750] 
img = img[350:-200]

#img = img[75:]
#plt.imshow(img, cmap='gray')
#plt.axis('off')
#plt.show()

pixels = np.where((img == 255)) #find white pixels

#find corner of the boundaries
topLeftCorner = (pixels[1][0]/2, (pixels[0][0] + 350)/2)  # Adjust y-coordinate for cropping
topRightCorner = (pixels[1][-1]/2, (pixels[0][0] + 350)/2)  # Adjust y-coordinate for cropping
bottomRightCorner = (pixels[1][-1]/2, (pixels[0][-1] + 350)/2 )  # Adjust y-coordinate for cropping
bottomLeftCorner = (pixels[1][0]/2, (pixels[0][-1] + 350)/2 )  # Adjust y-coordinate for cropping

#find ball
ball = np.where((img == 233))
radius = (max(ball[1]) - min(ball[1]))/2
meanY = (np.mean(ball[0])/2) + 175
meanX = np.mean(ball[1])/2
centerBall = (meanX,meanY)

#Find red blockade
blockadeCoords = np.where(img == 120)

blockadeX = blockadeCoords[1]
blockadeX = blockadeX[50:]
blockadeX = blockadeX[:-50]

blockadeY = blockadeCoords[0]
blockadeY = blockadeY[50:]
blockadeY = blockadeY[:-50]

minXblockade = min(blockadeX)/2
maxXblockade = max(blockadeX)/2
minYblockade = min(blockadeY)/2
maxYblockade = max(blockadeY)/2

#if np.std(blockadeCoords[1]) > 100:
if maxXblockade - minXblockade > 100:
    #the border is on the horizontal axis
    #(0,100) (200,100) The Y coordinates would remain the same on the x axis
    blockade1 = (minXblockade, maxYblockade)
    blockade2 = (maxXblockade, maxYblockade)
else:
    #the border is on the vertical axis
    blockade1 = (minXblockade, minYblockade)
    blockade2 = (minXblockade, maxYblockade)

#blockade 1 and blockade 2 are the red border

#converts from degrees to randians
def to_radians(angle):
    return angle * (math.pi / 180)

#gives coordinates for launch angle
def launch_angle(angle):
    return ((math.cos(to_radians(angle))),(math.sin(to_radians(angle))))

def launch_flip_angle(angle):
    if (angle <= 180):
        flip_angle = 180 - angle
        return launch_angle(flip_angle)
    else:
        flip_angle = 540 - angle
        return launch_angle(flip_angle)



#pyautogui.drag(50, 50, 0.5, button='left')

leftWallX = topLeftCorner[0]
rightWallX = bottomRightCorner[0]
topWallY = topLeftCorner[1]
bottomWallY = bottomRightCorner[1]


#returns coordinates of where the ball is and which direction it will be going upon contact with wall
def calculate_ball_collision(launch_coords, xPos, yPos):
    while ((xPos > (leftWallX + radius/2) and xPos < (rightWallX - radius/2) and (yPos > (topWallY + radius/2) and yPos < (bottomWallY - radius/2)))):
        xPos += launch_coords[0] 
        yPos -= launch_coords[1]
    
    #if bounces off the right wall what is the new launch_coords (launch angle is given through launch coords)
    if not ((xPos > (leftWallX + radius/2) and xPos < (rightWallX - radius/2))):
        launch_coords = (-launch_coords[0], launch_coords[1])
    elif not ((yPos > (topWallY + radius/2) and yPos < (bottomWallY - radius/2))): #if bouncing off top or bottom law
        launch_coords = (launch_coords[0], -launch_coords[1])

    #returns contact with wall position and direction
    return [launch_coords, xPos, yPos]

def calculate_ball_position_after_bounces(number_of_bounces, angle, xPos, yPos):
    launch_coords = launch_angle(angle)
    finalXPos = xPos
    finalYPos = yPos
    for i in range(number_of_bounces + 1):
        collision_details = calculate_ball_collision(launch_coords, finalXPos, finalYPos)
        launch_coords = collision_details[0]
        finalXPos = collision_details[1]
        finalYPos = collision_details[2]
        print("Launch Coords: " + str(collision_details[0]))
        print("XPos: " + str(collision_details[1]))
        print("YPos: " + str(collision_details[2]))
    return(finalXPos, finalYPos)


xPos = centerBall[0]
yPos = centerBall[1]
finalCoords = calculate_ball_position_after_bounces(1, 270, xPos, yPos)
print("Final Coords: " + str(finalCoords))
pyautogui.moveTo(finalCoords)


#pyautogui.drag(launch_coords[0]*75, launch_coords[1]*75, 0.5, button='left')

"""
for angle in range(360):
    launch_flip_angle(angle)
"""
#print(f"this is the sd of the x coords: {np.std(blockadeCoords[1])}")
#print(f"this is the sd of the y coords: {np.std(blockadeCoords[0])}")

#for horizontal border, the x standard deviation > 100 and y standard deviation < 10
#for veritcal border, the y stanndard deviation > 100 and x sd < 25