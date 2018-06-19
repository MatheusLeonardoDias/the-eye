import time

import cv2
import numpy as np


coeficiente_r = 0.3
coeficiente_g = 0.59
coeficiente_b = 0.11
qtd_amostras = 6

# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")
 
# Read until video is completed
frame_number = 1
# average_frame = []
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()

  # Muda para escala cinza
  # grayscale_frame = np.zeros( shape=(len(frame), len(frame[0])), dtype=np.uint8 )  
  # for line in range(0, len(frame)):
  #   for col in range( 0, len(frame[line])):
  #     grayscale_frame[line][col] = np.uint8(coeficiente_r*frame[line][col][0] + coeficiente_g* frame[line][col][1]+coeficiente_b*frame[line][col][2])
  # Solucao eficientemente temporaria  
  grayscale_frame = cv2.cvtColor( frame, cv2.COLOR_BGR2GRAY )
  
  if frame_number == 1:
    average_frame = grayscale_frame.astype(int)
  else:
    average_frame = np.add( average_frame, grayscale_frame )
  
  if ret == True:

    # Display the resulting frame
    frame_number += 1
    if frame_number == qtd_amostras:
      average_frame = average_frame / qtd_amostras
      cv2.imshow('Frame', average_frame.astype(np.uint8) )
      frame_number = 1

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
 
  # Break the loop
  else: 
    break
 
# When everything done, release the video capture object
cap.release()
 
# Closes all the frames
cv2.destroyAllWindows()