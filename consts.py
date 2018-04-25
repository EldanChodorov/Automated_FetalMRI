'''
Constants used by the FetalSegBrainTool project.
'''

# paint tool
USE_PAINTBRUSH = 1
OUTER_SQUARE = 2
INNER_SQUARE = 3
USE_ERASER = 4

BRUSH_WIDTH_SMALL = 4
BRUSH_WIDTH_MEDIUM = 6
BRUSH_WIDTH_LARGE = 9

# alpha channel to show paint as transparent
ALPHA_TRANSPARENT = 20
ALPHA_NON_TRANSPARENT = 255

PAINT_COLOR = (255, 36, 36)

MIN_ZOOM = 0
INITIAL_ZOOM = 1

NO_SEG_RUNNING = -1

# representation of scans' status in workspace table
SEGMENTED = 'Segmented'
QUEUED = 'In Queue...'
PROCESSING = 'Processing...'
