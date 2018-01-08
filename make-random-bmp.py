from PIL import Image
import requests

class QuotaNotPositiveException(Exception):
    """
    Raised when random.org quota isn't positive.
    """
    pass

def is_quota_positive():
    """
    Checks whether this machine's random.org quota is positive.
    """
    response_text = requests.request(
        'GET', 'https://www.random.org/quota/', params={'format': 'plain'}
    ).text
    return (int(response_text) > 0)

def get_randomness(num, bits):
    """
    Returns num random numbers, all of length bits (i.e. uniformly drawn
    from the range [0, 2^bits-1)).
    NOTE: num should not exceed 1E4.
    """
    if not is_quota_positive():
        raise QuotaNotPositiveException()
    params = {
        'num': num,
        'min': 0,
        'max': (1<<bits) - 1,
        'col': 1,
        'base': 10,
        'format': 'plain',
        'rnd': 'new',
        'user-agent': 'bmhuang@mit.edu',
    }
    response_text = requests.request(
        'GET', 'https://www.random.org/integers/', params=params
    ).text
    # parse response text.  :num is to remove the final '' in the array
    # returned by .split
    stringified_ints = response_text.split('\n')[:num]
    return [int(stringified_int) for stringified_int in stringified_ints]

def gen_random_matrix(rows, cols, bits):
    """
    Generates a random rows by cols matrix, each entry of which is a
    random integer of length bits.
    rows * cols should not exceed 1e4.
    """
    random_numbers = get_randomness(rows*cols, bits)
    matrix = []
    for i in xrange(rows):
        matrix.append(random_numbers[i*cols : (i+1)*cols])
    return matrix

RGB_LENGTH = 8
def rgb_from_encoding(encoding):
    """
    Converts a 24-bit input into (R,G,B), where each component is 8 bits.
    The first 8 bits become R, the next 8 bits become G, and the last 8
    bits become B.
    This util method allows us to query random.org for 24-bit ints which
    we process into (R,G,B), instead of three times as many 8-bit ints.
    """
    rgb_filter = (1 << RGB_LENGTH) - 1
    R = encoding >> 2*RGB_LENGTH
    G = (encoding >> RGB_LENGTH) & rgb_filter
    B = encoding & rgb_filter
    return (R,G,B)

def gen_image(rgb_encodings):
    """
    Generates an image from a 2-D array of 24-bit ints representing RGB
    encodings.  Each row of the matrix should map to a row of the image.
    """
    height = len(rgb_encodings)
    width = len(rgb_encodings[0])
    img = Image.new( 'RGB', (width, height), "black")
    pixels = img.load()

    for i in xrange(width):
        for j in xrange(height):
            pixels[i,j] = rgb_from_encoding(rgb_encodings[j][i])
    return img

IMG_DIMENSION = 128
def gen_random_image():
    """
    Generates a width by height bitmap image, each entry of which is a
    random RGB.
    """
    try:
        # 128*128 exceeds 1e4, so we generate the rgb-encoding matrix for
        # this image in two halves.  Note that 64*128 = 8192 < 1e4.
        top_half_rgb_encodings = gen_random_matrix(
            IMG_DIMENSION/2, IMG_DIMENSION, 3*RGB_LENGTH
        )
        bottom_half_rgb_encodings = gen_random_matrix(
            IMG_DIMENSION/2, IMG_DIMENSION, 3*RGB_LENGTH
        )
        rgb_encodings = top_half_rgb_encodings + bottom_half_rgb_encodings
        return gen_image(rgb_encodings)
    except QuotaNotPositiveException:
        print ("Ran out of random.org quota.")
        return gen_image([[]])

img = gen_random_image()
img.show()
img.save('output/random.bmp')
