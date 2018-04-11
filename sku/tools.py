# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import random
import urllib

from django.conf import settings


def download_photo(img_url, filename):
    try:
        image_on_web = urllib.urlopen(img_url)
        print image_on_web.headers.maintype
        if image_on_web.headers.maintype == 'image':
            buf = image_on_web.read()
            file_path = os.path.join(settings.MEDIA_ROOT + "lpic/", filename)

            print "filepath : %s" % file_path
            downloaded_image = file(file_path, "wb")
            downloaded_image.write(buf)
            downloaded_image.close()
            image_on_web.close()
        else:
            return False
    except:
        return False
    return True


def countIndexNumer(idx):
    #y = 1 * np.exp(-1  * idx)
    idx = idx + 1
    y = 100 / idx 
    return y

def create_discount(minNum, maxNum):
    amount = []
    idx = 0
    maxNum = maxNum + 1
    for i in range(1,maxNum):
        j = i 
        num = int(countIndexNumer(j))
        for j in range(num):
            amount.append(i)

    idx = random.randint(0, len(amount) - 1)
    ret =  amount[idx]
    return float(ret)/10