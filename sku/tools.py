# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
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
