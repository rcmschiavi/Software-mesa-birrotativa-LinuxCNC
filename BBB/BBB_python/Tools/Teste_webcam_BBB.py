# coding: utf-8
'''

Código que realiza a cpatura de um único frame pela BBB

Foi criado para corrigir e testar bugs de transmissão de dados

Códigos de referência - Comentários do código foram copiados das referências:
    - https://github.com/gebart/python-v4l2capture/blob/master/capture_video.py
    - https://gist.github.com/royshil/0f674c96281b686a9a62


'''

import Image
import select
import v4l2capture
import time
import cv2
import numpy as np


# Open the video device.
video = v4l2capture.Video_device("/dev/video8")

# Suggest an image size to the device. The device may choose and
# return another size if it doesn't support the suggested one.
size_x, size_y = video.set_format(640, 480, fourcc='MJPG')

# Create a buffer to store image data in. This must be done before
# calling 'start' if v4l2capture is compiled with libv4l2. Otherwise
# raises IOError.
video.create_buffers(1)

# Send the buffer to the device. Some devices require this to be done
# before calling 'start'.
video.queue_all_buffers()

# Start the device. This lights the LED if it's a camera that has one.
video.start()

stop_time = time.time() + 10
frame = None

while frame==None:
    # Wait for the device to fill the buffer.
    select.select((video,), (), ())

    image_data = video.read_and_queue()
    frame = cv2.imdecode(np.frombuffer(image_data, dtype=np.uint8), cv2.cv.CV_LOAD_IMAGE_COLOR)
    rows, cols = frame.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 90, 1)
    frame = cv2.warpAffine(frame, M, (cols, rows))

cv2.imwrite('foto_final9_rotanionada.jpg', frame)

video.close()
print "Saved video.mjpg (Size: " + str(size_x) + " x " + str(size_y) + ")"






