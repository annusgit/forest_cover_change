

from __future__ import print_function
from __future__ import division
import os
import cv2
import gdal
import numpy as np
import scipy.misc
from PIL import Image
import matplotlib.pyplot as plt


def get_band_names(list_of_contents):
    """
        Will return a dictionary of names of bands
    :param list_of_contents:
    :return:
    """
    bands = {}
    for x in list_of_contents:
        if x.endswith('.tif'):
            if 'band4' in x:
                bands['red'] = x
            if 'band3' in x:
                bands['green'] = x
            if 'band2' in x:
                bands['blue'] = x
            if 'band5' in x:
                bands['near_ir'] = x
            if 'band7' in x:
                bands['sh_ir2'] = x
            if 'ndvi' in x:
                bands['ndvi'] = x
    return bands


def convert(arr):
    return np.asarray(255/4096*arr).astype(np.int16)


def get_data_from_single_folder(path):
    rgb_file = os.path.join(path, 'rgb.png')
    enh_veg_file = os.path.join(path, 'enh_veg.png')
    fal_col_file = os.path.join(path, 'fal_col.png')
    ndvi_file = os.path.join(path, 'ndvi.png')
    directory = os.listdir(path)
    bands = get_band_names(directory)

    band_images = {}
    for band in bands.keys():
        content = gdal.Open(os.path.join(path, bands[band]))
        band_data = content.GetRasterBand(1)
        arr = np.asarray(band_data.ReadAsArray())
        band_images[band] = arr
    pass

    # band_images['red'] = cv2.equalizeHist(band_images['red'])
    # band_images['green'] = cv2.equalizeHist(band_images['green'])
    # band_images['blue'] = cv2.equalizeHist(band_images['blue'])

    rgb = np.dstack((band_images['red'], band_images['green'], band_images['blue']))
    enhanced_veg = np.dstack((band_images['sh_ir2'], band_images['near_ir'], band_images['green']))
    false_color = np.dstack((band_images['near_ir'], band_images['red'], band_images['green']))
    rgb, enhanced_veg, false_color = map(convert, [rgb, enhanced_veg, false_color])
    scipy.misc.imsave(rgb_file, rgb)
    scipy.misc.imsave(enh_veg_file, enhanced_veg)
    scipy.misc.imsave(fal_col_file, false_color)

    # threshold the ndvi image for segmentation target
    thresh = 0.75
    ndvi_ = np.asarray(1/20000*(band_images['ndvi']+10000)).astype(np.float16)
    ndvi = np.zeros_like(ndvi_)
    ndvi[ndvi_>thresh] = 255
    scipy.misc.imsave(ndvi_file, ndvi)
    read_images = map(Image.open, [rgb_file, enh_veg_file, fal_col_file, ndvi_file])
    evaluate_threshold(read_images)


def evaluate_threshold(images):
    # rgb, false, enhanced, ndvi = images
    # w = 2; h = 2
    fig = plt.figure(figsize=(2, 2))
    columns = 2
    rows = 2
    for i in range(columns * rows):
        images[i] = np.asarray(images[i])
        fig.add_subplot(rows, columns, i+1)
        if images[i].ndim == 2:
            plt.gray()
        plt.axis('off')
        plt.imshow(images[i])
    # fig.set_size_inches(np.array(fig.get_size_inches()) * len(images))
    plt.show()
    pass


def main():
    path = '/home/annus/Desktop/forest_cover_change/region_3_data/malakand/data/' \
           'espa-annuszulfiqar@gmail.com-07012018-001522-723/untars/LC081510362013041401T1-SC20180701002950'
    get_data_from_single_folder(path=path)


if __name__ == '__main__':
    main()


