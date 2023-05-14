# pip install python-opencv

import imageio.v3 as iio
import numpy as np
import cv2

import random

noise_level = 1
num_randomized_points = 40


# Add some random noise if you want to make each picture bit-unique
def noisify(im):
    w, h, d = im.shape
    for i in range(num_randomized_points):
        x = random.randint(1, w-2)
        y = random.randint(1, h-2)
        for id in range(d):
            if im[x][y][id] > 127:
                im[x][y][id] -= noise_level
            else:
                im[x][y][id] += noise_level


def pad_to_ratio(w, h, ratio):
    if w * ratio[1] > ratio[0] * h:
        # lacks some height!
        return 0, (ratio[1] * w / ratio[0] - h) / 2.0
    else:
        # Lacks some width!
        return (ratio[0] * h / ratio[1] - w) / 2.0, 0


#
# viewport: TopLeft, TopRight, BottomRight, BottomLeft points of the
# destination transformed rectangle
# Each of these points can be outside of the dst_template - this will only
# affect how matrix transformation is calculated / performed
#
def perspective_transform(src, dst_template, viewport, viewport_aspect):
    src_width = src.shape[1]
    src_height = src.shape[0]

    w_pad, h_pad = pad_to_ratio(src_width, src_height, viewport_aspect)

    src_tri = np.array(
        [
            [-w_pad, -h_pad],
            [src_width - 1 + w_pad, -h_pad],
            [src_width - 1 + w_pad, src_height - 1 + h_pad],
            [-w_pad, src_height - 1 + h_pad]
        ]
    )

    dst_tri = np.array(viewport)

    warp_mat = cv2.getPerspectiveTransform(src_tri.astype(np.float32), dst_tri.astype(np.float32))

    dst = dst_template.copy()

    return cv2.warpPerspective(src, warp_mat, (dst.shape[1], dst.shape[0]), dst=dst, borderValue=(255, 255, 255))


#
# viewport: TopLeft, TopRight, BottomRight points
#
def affine_transform(src, dst_template, viewport, viewport_aspect):
    src_width = src.shape[1]
    src_height = src.shape[0]

    w_pad, h_pad = pad_to_ratio(src_width, src_height, viewport_aspect)

    src_tri = np.array(
        [
            [-w_pad, -h_pad],
            [src_width - 1 + w_pad, -h_pad],
            [src_width - 1 + w_pad, src_height - 1 + h_pad]
        ]
    )

    dst_tri = np.array(viewport)

    warp_mat = cv2.getAffineTransform(src_tri.astype(np.float32), dst_tri.astype(np.float32))

    dst = dst_template.copy()

    return cv2.warpAffine(src, warp_mat, (dst.shape[1], dst.shape[0]), dst=dst, borderValue=(255, 255, 255))


def apply_green_mask(template, img):
    # Discard alpha channel if necessary
    if img.shape[2] == 4:
        img = img.copy()[:, :, :3]

    if template.shape[2] == 4:
        template = template.copy()[:, :, :3]

    # This will do per-channel array to array comparison
    mask = template == np.array([0, 255, 0])

    # AND components to find exact matches (it is green if all components match green color components)
    is_green_mask = mask[:,:,0] & mask[:,:,1] & mask[:,:,2]

    mask[:,:,0] = is_green_mask
    mask[:,:,1] = is_green_mask
    mask[:,:,2] = is_green_mask

    # Apply the mask finally
    img = np.where(mask, img, template)

    return img


def cottonify(src, template, viewport, viewport_aspect, noise=False):
    img = perspective_transform(src, template, viewport, viewport_aspect)
    img = apply_green_mask(template, img)
    if noise:
        noisify(img)
    return img


def main():
    template_viewport = [[0, 0], [710-1, 0], [710-1, 475-1], [0, 475-1]]
    template_aspect = (710, 475)  # aspect ratio of the view port in the template image

    src = iio.imread(r'test\test.jpg').copy()
    template = iio.imread(r'c_templates\7.png').copy()

    img = cottonify(src, template, template_viewport, template_aspect, noise=True)
    iio.imwrite(r'test\out.png', img)


if __name__ == "__main__":
    main()