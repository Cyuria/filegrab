import requests
import pygame
import threading
import os
from git import Repo

X = 640
Y = 480

pygame.init()
screen = pygame.display.set_mode((X, Y), flags = pygame.NOFRAME)
font = pygame.font.Font('./Assets/ComicMono.ttf', 32)

url = ''
giturl = ''

colour = (15, 15, 50)
colourstate = list(colour)
runEventLoop = True

fileslst = []
progress = 0
progressBar = 0.0

PATHFILES = './filetest/'

def stop():
    runEventLoop = False
    for t in threading.enumerate():
        if t != threading.main_thread() and t != threading.current_thread():
            t.join(timeout = 0.1)
            if t.is_alive():
                try:
                    t._stop()
                except AssertionError as e:
                    pass
    pygame.quit()
    quit()

def getProgress():
    global progress, fileslst
    if len(fileslst):
        return ((progress) * 100) // len(fileslst)
    else:
        return 0

def updateScreen():
    global colour, X, Y, screen, progressBar

    step = 1

    for i in range(3):
        tmp = int((colour[i] - colourstate[i]) / abs(colour[i] - colourstate[i]) if colour[i] != colourstate[i] else 0)
        tmp = step * tmp if abs(colour[i] - colourstate[i]) >= step else tmp
        colourstate[i] += tmp
    
    screen.fill(colourstate)
    text = font.render('Progress: ' + str(getProgress()) + '%', True, (200, 200, 200))
    textRect = text.get_rect()
    textRect.center = (X // 2, Y // 2)
    screen.blit(text, textRect)

    if progressBar * 100 < getProgress():
        progressBar += 1 / (0.8 * X)
    barRect = (int(0.1 * X), int(0.8 * Y), int(progressBar * 0.8 * X), Y // 50)
    pygame.draw.rect(screen, (20, 255, 20), barRect)

    pygame.display.flip()

def handleEvents():
    global colour
    event = pygame.event.poll()
    while not event.type == pygame.NOEVENT:
        if event.type == pygame.QUIT:
            stop()
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_ESCAPE:
                stop()
            else:
                colour = (15, 15, 50)
        elif event.type == pygame.MOUSEBUTTONUP:
            colour = (15, 15, 50)
        elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
            colour = (50, 50, 75)
        
        event = pygame.event.poll()

def displayloop():
    global runEventLoop
    while runEventLoop:
        updateScreen()
    print('displayloopdone')

DT = threading.Thread(target = displayloop)
DT.start()
def getFiles():
    global fileslst, progress
    fileslst = requests.get('https://'+url+'index').text.split('\n')

    print(fileslst)
    for filename in fileslst:
        os.makedirs(os.path.dirname(PATHFILES + filename), exist_ok=True)
        r = requests.get('https://' + url + filename, stream = True)
        with open(PATHFILES + filename, 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)
        progress += 1
        print(filename)
    pygame.time.Clock().tick(0.5)
    
WT = threading.Thread(target = getFiles)
WT.start()
while WT.is_alive():
    handleEvents()
    
runEventLoop = False

DT.join()

pygame.quit()
