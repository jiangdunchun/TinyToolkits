import numpy as np

def ColorDistance(img1, img2):
    img1 = img1.astype(float)
    img2 = img2.astype(float)

    delta = img1 - img2
    delta_2 = delta * delta

    distance = np.sqrt(delta_2[:,:,0] + delta_2[:,:,1] + delta_2[:,:,2])
    return distance

def LABColorDistance(img1, img2):
    img1 = img1.astype(float)
    img2 = img2.astype(float)

    r_mean = (img1[:,:,0] + img2[:,:,0]) / 2

    delta = img1 - img2
    delta_2 = delta * delta

    distance = np.sqrt((2 + r_mean / 256) * delta_2[:,:,0] + 4 * delta_2[:,:,1] + (2 + (255 - r_mean) / 256) * delta_2[:,:,2])
    return distance


DiffFunctions = {
    'ColorDistance':ColorDistance,
    'LABColorDistance':LABColorDistance,
}