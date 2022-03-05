from PIL import Image
from PIL.ExifTags import TAGS
import piexif
# https://piexif.readthedocs.io/en/latest/sample.html


image_name = 'jujutsu.jpeg'

image = Image.open(image_name)
print(image.size)

exif_dict = piexif.load(image_name)
print(exif_dict)
# new_exif = adjust_exif(exif_dict)
# exif_bytes = piexif.dump(new_exif)
# piexif.insert(exif_bytes, path)

# should probably set these
# ImageWidth
# ImageHeight
# PixelXDimension
# PixelYDimension

# Could use these?
# ImageNumber (use directly for ordering)
# following 2 should be within a few seconds of eachother, Create Date should be later
# DateTimeOriginal
# DateTimeDigitized (CreateDate)
# ModifiyDate
# ImageUniqueID
# ImageID?
# CopyRight