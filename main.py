#!/usr/bin/env python3

#import the necessary packages
from skimage.measure import compare_ssim as ssim
import numpy as np
import cv2
import os
import glob
import threading

import argparse

parser = argparse.ArgumentParser(description = 'Delete duplicate photos from a folder')
parser.add_argument('-p', type=str, help='Path of the directory containing the photos to be checked', dest='directory')
parser.add_argument("-s", help="Minumum similar ratio, between 0.0 and 1.0", type=float, dest='threshold', default=0.90)
parser.add_argument("-m", help="Maximum size ratio between two files (smaller means fast process)", type=float, dest='multiplicator', default=1.2)
parser.add_argument("-n", help="Number of threads", type=int, dest='n_threads', default=16)
args = parser.parse_args()

directory_path = args.directory
threshold = args.threshold
multiplicator = args.multiplicator
n_threads = args.n_threads

if directory_path is None:
    print("You must specify the path of the images!")
    exit(1)

directory_path = directory_path if directory_path.endswith('/') else directory_path + '/'

def compare_images(imageA, imageB): #compute the structural similarity
    s = ssim(imageA, imageB)
    return s


image_formats = ['*.jpg', '*.tiff', '*.png', '*.jpeg', '*.JPG', '*.TIFF', '*.PNG', '*.JPEG']

file_names = []
for x in image_formats:
    file_names += glob.glob(directory_path + x)
file_names = list(set(file_names))


file_sizes = [os.path.getsize(path) for path in file_names]
file_sizes, file_names = (list(t) for t in zip( * sorted(zip(file_sizes, file_names))))
number_of_files = len(file_names)
to_be_deleted = [False] * number_of_files

assert(len(file_names) == len(file_sizes))

print("Number of files to check: %d\n" % number_of_files)

cache = dict()

def load_image(index):
    if index in cache:
        return cache[index]
    else:
        img = cv2.imread(file_names[index], cv2.IMREAD_GRAYSCALE)
        cache[index] = img
        return img


def check_images(image1,j):

    image2 = load_image(j)

    if image1.shape != image2.shape:
        image2 = cv2.resize(image2, (image1.shape[1], image1.shape[0]), interpolation=cv2.INTER_CUBIC)

    if compare_images(image1, image2) > threshold:
        #duplicate found!
        to_be_deleted[j] = True
        cache.pop(j)



for i in range(len(file_names)):
    if to_be_deleted[i]:
        continue

    image1 = load_image(i)

    j = i + 1

    while (j < number_of_files) and (file_sizes[j] < multiplicator * file_sizes[i]):

        threads = []
        while (j < number_of_files) and (file_sizes[j] < multiplicator * file_sizes[i]) and (len(threads) <= n_threads):
            if to_be_deleted[j]:
                j += 1
                continue

            t = threading.Thread(target=check_images, args=(image1,j))
            threads.append(t)
            t.start()
            j += 1

        for t in threads:
            t.join()

    cache.pop(i)

    print("\rAdvancement: {:5.2f}%".format((i + 1.0)*100 / number_of_files), end = "")

print("\nFound %d duplicates, now removing them" % sum([1 if x else 0 for x in to_be_deleted]) )
#removing files
for i in range(number_of_files):
    if to_be_deleted[i]:
        os.remove(file_names[i])

print('\n')
