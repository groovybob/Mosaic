import os, os.path
import numpy as np
import math
from PIL import Image, ImageStat
import glob
import cv2

dir = "C:/Users/User/GITHUB/Mars Curiosity Image Gallery _ NASA"
pics = [] #list of image file names
brights = [] #average brighnesses of pics
tilebrights = [] # average brightnesses of each tile
mosaicblocks = [] # a list of tiles in order to make new image
picks_small = []

# clear out smalls folder ready for new run
folder_path = dir+'/smalls'
for file_object in os.listdir(folder_path):
    file_object_path = os.path.join(folder_path, file_object)
    if os.path.isfile(file_object_path):
        os.unlink(file_object_path)
    else:
        shutil.rmtree(file_object_path)



def brightness( im_file ):
    im = Image.open(im_file)
    stat = ImageStat.Stat(im)
    bright = stat.rms[0]
    return bright

#make a list of image names
for file in os.listdir(dir):  # open each file and find average brightness
    filename = os.fsdecode(file)
    if filename.endswith(".jpg"):
        name = dir+'/'+file
        pics = np.append(pics,name)

#find the average brightness of each image
for file in os.listdir(dir):  # open each file and find average brightness
    filename = os.fsdecode(file)
    if filename.endswith(".jpg"):
        name = dir+'/'+file
        bright = brightness(name)
        brights = np.append(brights,bright)


img = cv2.imread(dir+'/'+'master.jpg')
img_shape = img.shape
# divide each side into X
X = 100
tile_size = (int(img_shape[1]/X), int(img_shape[0]/X))
offset = (int(img_shape[1]/X), int(img_shape[0]/X))

#split the main image up onto tiles and work out their brightness.

for i in range(int(img.shape[1]/tile_size[0])):
    for j in range(int(img.shape[1]/tile_size[0])):
        cropped_img = img[offset[1]*i:min(offset[1]*i+tile_size[1], img_shape[0]), offset[0]*j:min(offset[0]*j+tile_size[0], img_shape[1])]
        # Debugging the tiles
        cropped_img = cv2.imwrite("debug_" + str(i) + "_" + str(j) + ".jpg", cropped_img)
        tilebright = brightness("debug_" + str(i) + "_" + str(j) + ".jpg")
        tilebrights = np.append(tilebrights,tilebright)
        os.remove("debug_" + str(i) + "_" + str(j) + ".jpg")

# begin building mosaic
total = int((img.shape[1]/tile_size[0])**2)
brightness_factor = np.average(tilebrights)/np.average(brights)
tilebrights = tilebrights/brightness_factor

def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return pics[idx]

# select mosaic images based om brightness.
for k in range(total):
    selected_im = find_nearest(brights,tilebrights[k])
    mosaicblocks = np.append(mosaicblocks,selected_im)

print(len(mosaicblocks))
print(total)


# resize origional images and save in new dir to be used for build
for k in range(len(mosaicblocks)):
    foo = Image.open(mosaicblocks[k])
    foo = foo.resize(tile_size,Image.ANTIALIAS)
    foo.save(dir+"/smalls/smalls"+str(k)+".jpg",quality=95)


#begin building the new mosaic image
new_im = Image.new('RGB', (1600,900))
os.chdir(dir+"/smalls")
images = glob.glob("*.jpg")
j = 0
for l in range(X):
    i = 0

    #print(l)
    for im in range(X):
        num = int((l*X)+im)
        img = Image.open(dir+'/smalls/smalls' + str(num) + '.jpg')
        y_cord = j
        new_im.paste(img, (i,y_cord))
        i=(i+tile_size[0])
    j += tile_size[1]



#new_im.show()
new_im.save(dir+"/out.jpg", "JPEG", quality=80, optimize=True, progressive=True)

