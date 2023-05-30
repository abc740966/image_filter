# File: images.py
#
# Description: Read in a plain pgm format file and apply an image
# filter to it selected by the user. Write out the new image to a pgm
# file. The program assumes files are encoded with the plain pgm
# format per http://netpbm.sourceforge.net/doc/pgm.html.

def main():
    """Process one file based on user input.

    1. Get the name of the image file from the user.
    2. Read in the data from the file.
    3. Determine what filter to apply.
    4. Apply the filter.
    5. Write out the new file.
    We assume the user correctly enters the name of a file
    formatted in the plain pgm format"""
    infile_name = input('Enter file name: ')
    image_raster, max_value = read_pgm_file(infile_name)
    choice = get_filter_choice()
    if choice == 1:
        result = invert_colors(image_raster, max_value)
    else:
        choices = [mirror, blur, brighten]
        result = choices[choice - 2](image_raster)
    print_result(result)
    save_result(infile_name, max_value, result)


def get_filter_choice():
    """Ask user for which filet to apply to the current image."""
    print('OPTIONS FOR IMAGE FILTER TO APPLY:')
    print('1. Invert colors of image.')
    print('2. Get a mirror image.')
    print('3. Blur image.')
    print('4. Brighten image.')
    return int(input('Please enter your choice: '))


def read_pgm_file(infile_name):
    """Read in the file specified by the given file name.

    We assume infile_name refers to a file in the current working
    directory and that the file is in the plain pgm format.
    Return an image raster (list of lists) with the values from the
    file. Each row is a list in the returned value. Also return
    the max value as specified by the file."""
    with open(infile_name, 'r') as infile:
        magic_num = infile.readline().strip()
        if magic_num != 'P2':
            print('First line of file not magic num P2. '
                  'Instead it is:', magic_num, 'Logic errors may occur')
        second_line = infile.readline().strip()
        if second_line[0] == '#':
            print('in file contains comment:', second_line, '. Discarding.')
            second_line = infile.readline().strip()
        dimensions = second_line.split()
        max_val = int(infile.readline().strip())
        return read_raster(dimensions, infile), max_val


def read_raster(dimensions, infile):
    """Read in and return a list of lists for the values of the image.
    
    dimensions is a string with 2 ints, the height and width of the 
    image. infile is the inout file. We assume the file cursor is 
    positioned just before the first data value after the dimensions.
    Return the raster, a list of lists.
    """
    cols, rows = int(dimensions[0]), int(dimensions[1])
    result = [[0 for c in range(cols)] for r in range(rows)]
    row = 0
    current_data = infile.readline().strip().split()
    current_pos = 0
    while row < rows:
        col = 0
        while col < cols:
            if current_pos == len(current_data):
                # Used up the last line, need to read the next line.
                current_data = infile.readline().strip().split()
                current_pos = 0
            result[row][col] = int(current_data[current_pos])
            current_pos += 1
            col += 1
        row += 1
    return result


def print_result(raster):
    """Print the given raster to standard output."""
    for row in range(len(raster)):
        print('Row ', row, ": ", raster[row], sep='')


def get_dimensions(raster):
    return len(raster), len(raster[0])


def save_result(original_name, max_value, raster):
    """Save the raster to a plain pgm file.

    raster is a list of lists of ints representing a grayscale image
    in the plain pgm format. Write out the raster to a plain pgm file.
    Each row is placed on a single line.
    The file name is the original file name before the prefix
    with _alt and then .pgm.
    """
    name = original_name.split('.')[0]
    name += '_alt.pgm'
    with open(name, 'w') as outfile:
        outfile.write('P2\n')
        rows, cols = get_dimensions(raster)
        outfile.write(str(cols) + ' ' + str(rows) + '\n')
        outfile.write(str(max_value))
        outfile.write('\n')
        for row in raster:
            output_row = ''
            for value in row:
                output_row += str(value) + ' '
            output_row = output_row.strip() + '\n'
            outfile.write(output_row)


def invert_colors(raster, maxi):
    """Create and return an inverted version of the raster.

    raster is a rectangular list of lists of ints.
    All values are between 0 and max inclusive. [0, max]
    The returned value has each value altered to max - original_val.

    Simple example, given max is initially 31
     1  2  3  4  5
     6  7  8  9 10
    11 12 13 14 15
    16 17 18 19 20

    would return:
    30 29 28 27 26
    25 24 23 22 21
    20 19 18 17 16
    15 14 13 12 11
    """
    inverted_raster = []
    # Iterate through the list with nested loop to get original_val
    for i in range(len(raster)):
        inverted_raster_row = []
        for original_val in raster[i]:
            inverted_val = maxi - original_val
            inverted_raster_row.append(inverted_val)
        inverted_raster.append(inverted_raster_row)
    return inverted_raster


def mirror(raster):
    """Create a mirror image of the raster.

    Raster is a rectangular list of lists of ints representing an image.

    Simple example:
     1  2  3  4  5
     6  7  8  9 10
    11 12 13 14 15
    16 17 18 19 20

    would return:
     5  4  3  2  1
    10  9  8  7  6
    15 14 13 12 11
    20 19 18 17 16
    """
    mirror_raster = []
    for i in range(len(raster)):
        mirror_raster_row = raster[i]
        mirror_raster_row.reverse()
        mirror_raster.append(mirror_raster_row)
    return mirror_raster


def inbounds(r, c, raster):
    # Check if the row and column index is in range.
    return 0 <= r < len(raster) and 0 <= c < len(raster[r])


def get_blur_row(raster, row, col):
    """Determine the values in one row of the blur list"""
    # Determine whether the value is on the corner or the edge and
    # get the number of neighbors and total values
    num_neighbors = 0
    total_val = 0
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if inbounds(r, c, raster):
                num_neighbors += 1
                total_val += raster[r][c]
    return num_neighbors, total_val


def blur(raster):
    """Create a blurred version of the raster.

    Raster is a rectangular list of lists of ints representing an image.
    Each value in the returned result is the average of a cell and its
    8 neighboring cells. Corner cells only have 3 neighbors and edge
    cells not on the corner have 5 neighbors.
    """
    # Iterate through the list by row first
    blur_raster = []
    for r in range(0, len(raster)):
        blur_row = []
        for c in range(0, len(raster[r])):
            num_neighbors, total_val = get_blur_row(raster, r, c)
            average = total_val / num_neighbors
            blur_row.append(int(average))
        blur_raster.append(blur_row)
    return blur_raster


def get_brighten_row(raster, row, col):
    """Get the values surrounded a specific element and put them into a list
    for getting the maximum in the brighten function"""
    # Determine whether the value is on the corner or the edge
    brighten_row = []
    for r in range(row - 1, row + 2):
        for c in range(col - 1, col + 2):
            if inbounds(r, c, raster):
                brighten_row.append(raster[r][c])
    return brighten_row


def brighten(raster):
    """Create a brightened version of the raster.

    Raster is a rectangular list of lists of ints representing an image.
    Each value in the returned result is the maximum value of a cell
    and its 8 neighboring cells. Corner cells only have 3 neighbors
    and edge cells not on the corner have 5 neighbors.
    """
    brighten_raster = []
    for r in range(0, len(raster)):
        rows = []
        for c in range(0, len(raster[0])):
            brighten_row = get_brighten_row(raster, r, c)
            maxi = max(brighten_row)
            rows.append(maxi)
        brighten_raster.append(rows)
    return brighten_raster

main()

