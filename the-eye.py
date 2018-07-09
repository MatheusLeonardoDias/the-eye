#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
from imutils.video import VideoStream
import cv2
import argparse
import imutils
import time
import numpy as np
import PIL.Image
import PIL.ImageTk

frame_samples = 20
limiar = 20
limiar_pixel_pessoa = 7000
limiar_pixel_animal = 5000

point_list = []
ap = argparse.ArgumentParser()
ap.add_argument("-v", "--video", help="Caminho do arquivo de video.")
ap.add_argument("-L", "--limiarp", help="Limiar para identificacao de pessoas.")
ap.add_argument("-l", "--limiara", help="Limiar para identificacao de animais.")
ap.add_argument("-g", "--limiargeral", help="Limiar para calculo de diferença de pixels.")
args = vars(ap.parse_args())

if not args.get("limiarp", None) is None:
	limiar_pixel_pessoa = int(args.get("limiarp", None))

if not args.get("limiara", None) is None:
	limiar_pixel_animal = int( args.get("limiara", None))

if not args.get("limiargeral", None) is None:
	limiar = int( args.get("limiargeral", None))

root = Tk()

def image_capture():
    global vs
    global canvas
    global photo

    if not args.get("video", None) is None:
    	vs = cv2.VideoCapture(args["video"])

    baseFrame = None

    while True:
        if baseFrame == None:
            baseFrame = vs.read()
            baseFrame = baseFrame if args.get("video", None) is None else baseFrame[1]
            baseFrame = imutils.resize(baseFrame, width=500, height=400)
            baseFrame = cv2.cvtColor(baseFrame, cv2.COLOR_BGR2GRAY)
            continue

        frame_mean, gray_frame, diff_frame, actual_frame, pixel_diff = read_from_camera(baseFrame)

        if frame_mean is None:
			break

        print pixel_diff
        if pixel_diff > limiar_pixel_pessoa:
			cv2.putText(frame_mean, "Pessoa Detectada!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
			cv2.putText(diff_frame, "Pessoa Detectada!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255), 1)
			cv2.putText(actual_frame, "Pessoa Detectada!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255), 1)				
        elif pixel_diff > limiar_pixel_animal:
			cv2.putText(frame_mean, "Animal Detectado!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
			cv2.putText(diff_frame, "Animal Detectado!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255), 1)
			cv2.putText(actual_frame, "Animal Detectado!", (10, 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255), 1)		
        else:
			baseFrame = gray_frame

        cv2.imshow("Limiarização", actual_frame)
        cv2.imshow("Diferença", diff_frame)
        cv2.imshow("Média de N imagens", frame_mean)

        if (cv2.waitKey(25) & 0xFF == ord('q')):
            break

    cv2.destroyAllWindows()
    for count in range(0, 8):
        cv2.waitKey(1)

def read_from_camera(base_frame):
    frame_acc = np.zeros((len(base_frame), len(base_frame[0]), 3), int)
    for i in range(0, frame_samples):
        frame = vs.read()
        frame = frame if args.get("video", None) is None else frame[1]
        if frame is None:
			return frame, frame, frame, frame, frame
        frame = imutils.resize(frame, width=500, height=400)
        frame_acc += frame

    frame_mean = frame_acc / frame_samples
    frame_mean = frame_mean.astype(np.uint8)

    # Mascara
    if len(point_list) > 0:
        mask = np.zeros(frame_mean.shape, dtype=np.uint8)
        roi_corners = np.array([point_list], dtype=np.int32)
        channel_count = frame_mean.shape[2]
        ignore_mask_color = (255,)*channel_count
        cv2.fillPoly(mask, roi_corners, ignore_mask_color)
        frame_mean = cv2.bitwise_and(frame_mean, mask)
		# Fundo também deve ser aplicado a mascara
        mask = np.zeros(base_frame.shape, dtype=np.uint8)
        roi_corners = np.array([point_list], dtype=np.int32)
        ignore_mask_color = (255,)*1
        cv2.fillPoly(mask, roi_corners, ignore_mask_color)
        base_frame = cv2.bitwise_and(base_frame, mask)

    # gray = cv2.cvtColor(frame_mean, cv2.COLOR_BGR2GRAY)
    gray = np.dot(frame_mean[...,:3], [0.299, 0.587, 0.114]).astype(np.uint8)

    # frameDelta = cv2.absdiff(base_frame, gray)
    frameDelta = np.clip(np.subtract(base_frame.astype(int), gray), 0, 255 ).astype(np.uint8)

    thresh = cv2.threshold(frameDelta, limiar, 255, cv2.THRESH_BINARY)[1]

    pixel_diff = sum( sum(i > limiar for i in frameDelta) )

    return frame_mean, gray, frameDelta, thresh, pixel_diff

def key(event):
    print "pressed", repr(event.char)

id_poly = None
def callback(event):
    global point_list
    global id_poly
    point_list.append((event.x, event.y))
    if id_poly != None:
        canvas.delete(id_poly)
    id_poly = canvas.create_polygon(
        point_list, outline='gray', fill='green', width=1)

# create a button, then when pressed, will trigger a file chooser
# dialog and allow the user to select an input image; then add the
# button the GUI


def buttonaction_iniciar():
    image_capture()


def buttonaction_area():
    canvas.bind("<Key>", key)
    canvas.bind("<Button-1>", callback)

def buttonaction_clear():
    global point_list
    point_list = []
    canvas.delete(id_poly)


grid = Frame(root)
grid.pack(fill=X, side=BOTTOM, padx="10", pady="10")

grid.columnconfigure(0, weight=1)
grid.columnconfigure(1, weight=1)
grid.columnconfigure(2, weight=1)
grid.columnconfigure(3, weight=1)

btn_iniciar = Button(grid, text="Iniciar Captura",
                     command=buttonaction_iniciar)
btn_iniciar.grid(row=0, column=0, sticky=W+E)
btn_selecionar = Button(grid, text="Selecionar Área",
                        command=buttonaction_area)
btn_selecionar.grid(row=0, column=2, sticky=W+E)
btn_limpar = Button(grid, text="Limpar Seleção", command=buttonaction_clear)
btn_limpar.grid(row=0, column=3, sticky=W+E)

# Inicia Canvas
canvas = Canvas(root, width=500, height=400)
canvas.pack()
if args.get("video", None) is None:
    vs = VideoStream(src=0).start()
    time.sleep(2.0)
else:
    vs = cv2.VideoCapture(args["video"])

canvas_frame = vs.read()
canvas_frame = canvas_frame if args.get("video", None) is None else canvas_frame[1]
canvas_frame = imutils.resize(canvas_frame, width=500, height=400)
canvas_frame = cv2.cvtColor(canvas_frame, cv2.COLOR_BGR2RGB)
photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(canvas_frame))

canvas.create_image(0, 0, image=photo, anchor=NW)

# kick off the GUI
root.mainloop()

'''
assalto_noite = 5000 3000
casa = 6000 3000
'''
