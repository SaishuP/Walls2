#new commit test
#second test commit
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
time.sleep(3)

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
screenshot = pyautogui.screenshot()
screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
imgBall = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
imgBall = imgBall[425:, 1225:]
imgBall = imgBall[:-350, :-1225]

ball = np.where((imgBall == 233) | (imgBall == 255))
radius = (max(ball[1]) - min(ball[1]))/2

print("radius: " + str(radius))

meanY = (np.mean(ball[0])/2) + 425/2
meanX = (np.mean(ball[1])/2) + 1225/2

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
minYblockade = min(blockadeY)/2 + 175
maxYblockade = max(blockadeY)/2 + 175


#Initialize top_bottom_wall 
#Top_bottom_wall -> true -> the blockade is on the top or bottom wall
#Top_bottom_wall -> true -> the blockade is on the left or right wall
top_bottom_wall = False

#X values will be far apart on the red blocakde if they are on the top or bottom wall
#Checks for top/bottom wall or left/right wall
if maxXblockade - minXblockade > 100:
    #the border is on the horizontal axis TOP OR BOTTOM
    #(0,100) (200,100) The Y coordinates would remain the same on the x axis

    """
    If the blockade is on the roof the ROOF BLOCKADE  will always be LESS then Y VALUE of the ball
    If the blockade is on the bottom the BOTTOM BLOCKADE will always be GREATER than the Y VALUE of the ball
    """
    #Determines top or bottom wall
    if maxYblockade < meanY:
        #topWall
        blockade1 = (minXblockade, maxYblockade)
        blockade2 = (maxXblockade, maxYblockade)
    else:
        #bottomWall
        blockade1 = (minXblockade, minYblockade)
        blockade2 = (maxXblockade, minYblockade)

    top_bottom_wall = True
else:
    #the border is on the vertical axis LEFT OR RIGHT
    #(0,100) (0,300) The X coordinates would remain the same on the Y axis

    """
    If the blockade is on the left the LEFT BLOCKADE  will always be LESS then X VALUE of the ball
    If the blockade is on the RIGHT the RIGHT BLOCKADE will always be GREATER than the X VALUE of the ball
    """
    #Determines left or right wall
    if maxXblockade < meanX:
        #Left wall I think
        blockade1 = (maxXblockade, minYblockade)
        blockade2 = (maxXblockade, maxYblockade)
    else:
        #Right wall I think
        blockade1 = (minXblockade, minYblockade)
        blockade2 = (minXblockade, maxYblockade)

#blockade 1 and blockade 2 are the red border

#Converts from degrees to randians
def to_radians(angle):
    return angle * (math.pi / 180)

#Gives coordinates for launch angle (unit circle conversion)
def launch_angle(angle):
    return ((math.cos(to_radians(angle))),(math.sin(to_radians(angle))))

#Adjusts to the system. Enter value based on your desire
def launch_flip_angle(angle):
    if (angle <= 180):
        flip_angle = 180 - angle
        return launch_angle(flip_angle)
    else:
        flip_angle = 540 - angle
        return launch_angle(flip_angle)

#Splits a list of numbers into sublists based on consecutive sequences.
def split_consecutive(lst):
    result = []
    sub_list = [lst[0]]

    for i in range(1, len(lst)):
        if lst[i] == lst[i-1] + 1:
            sub_list.append(lst[i])
        else:
            result.append(sub_list)
            sub_list = [lst[i]]

    result.append(sub_list)
    return result

#Finds longest subarray
def longest_subarray(arrays):
    longest = []
    for array in arrays:
        if len(array) > len(longest):
            longest = array
    return longest

leftWallX = topLeftCorner[0]
rightWallX = bottomRightCorner[0]
topWallY = topLeftCorner[1]
bottomWallY = bottomRightCorner[1]

#Takes in launch coords (direction of ball's movement (0.5,0.5)), current xPos, current yPos
#Returns launch coords (direction of ball after bounce), new Xpos, new Ypos upon contact with wall
def calculate_ball_collision(launch_coords, xPos, yPos):
    #While X coords and Y coords of ball are within boundaries of the walls keep adjusting the coords until it hits a wall
    while ((xPos > (leftWallX + radius/2) and xPos < (rightWallX - radius/2) and (yPos > (topWallY + radius/2) and yPos < (bottomWallY - radius/2)))):
        xPos += launch_coords[0] 
        yPos -= launch_coords[1]
    
    #Figures out if bounces of top/bottom wall or right/left wall and adjust the launch_coords
    #Also subtract one movement so the ball is not IN the wall
    if not ((xPos > (leftWallX + radius/2) and xPos < (rightWallX - radius/2))):
        xPos -= launch_coords[0] 
        yPos += launch_coords[1]
        launch_coords = (-launch_coords[0], launch_coords[1])
    elif not ((yPos > (topWallY + radius/2) and yPos < (bottomWallY - radius/2))): #if bouncing off top or bottom law
        xPos -= launch_coords[0] 
        yPos += launch_coords[1]
        launch_coords = (launch_coords[0], -launch_coords[1])

    return [launch_coords, xPos, yPos]

#Calculates ball position after x amount of bounces, for ONE angle
def calculate_ball_position_after_bounces(number_of_bounces, angle, xPos, yPos):
    launch_coords = launch_angle(angle)
    finalXPos = xPos
    finalYPos = yPos

    for i in range(number_of_bounces + 1):
        collision_details = calculate_ball_collision(launch_coords, finalXPos, finalYPos)
        launch_coords = collision_details[0]
        finalXPos = collision_details[1]
        finalYPos = collision_details[2]
        #print("Launch Coords: " + str(collision_details[0]))
        #print("XPos: " + str(collision_details[1]))
        #print("YPos: " + str(collision_details[2]))
        
        #While ball is still bouncing, when i == numberOfBounces the ball is suppoused to go through the blockade
        #Meant to check that other bouncehs are avoidiing the blockade
        if not (i == number_of_bounces):
            if top_bottom_wall:
                #If top/bottom wall and xPos is within range of blockade return 0,0 which wont pass the test later for 'working coords'
                if (blockade1[0] - 10) < finalXPos < (blockade1[0] + 10):
                    return 0,0
            else:
                 #If top/bottom wall and yPos is within range of blockade return 0,0 which wont pass the test later for 'working coords'
                if (blockade1[1] - 10) < finalXPos < (blockade1[1] + 10):
                    return 0,0
        
    return(finalXPos, finalYPos)


xPos = centerBall[0]
yPos = centerBall[1]
final_coords_list = []

#Calculates which angles work for ALL 360 angles
for bounce_angle in range(360):
    #Customize number of bounces
    number_of_bounces = 4
    #Gets all final coordinate for certain angle
    final_coords = calculate_ball_position_after_bounces(number_of_bounces, bounce_angle, xPos, yPos)
    

    if top_bottom_wall:
        #check if y is within 10 pixels and x is within 10 pixels on either side
        if ( ((blockade1[0] + radius) < final_coords[0] < (blockade2[0] - radius)) and (((blockade1[1] - 10) < final_coords[1] < (blockade1[1] + 10))) ):
            final_coords_list.append(bounce_angle)
    else:
        #check if x is within 10 pixels and y is within 10 pixels on either side
        if ( ((blockade1[1] + radius) < final_coords[1] < (blockade2[1] - radius)) and (((blockade1[0] - 10) < final_coords[0] < (blockade1[0] + 10))) ):
            final_coords_list.append(bounce_angle)
    


print("This is the list of final coords: " + str(final_coords_list))
split_final_coords_list = split_consecutive(final_coords_list)
longest_subarr = longest_subarray(split_final_coords_list)

final_angle = longest_subarr[int((len(split_final_coords_list[0]) - 1) / 2)]
print(final_angle)
launch_coords = launch_flip_angle(final_angle)

pyautogui.click(button='left')
pyautogui.moveTo(centerBall)
#pyautogui.drag(launch_coords[0]*60, launch_coords[1]*60, 0.5, button='left')
