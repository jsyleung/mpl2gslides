import numpy as np

def data_to_slide_coords(ax, x, y, slide_width_pt=720, slide_height_pt=405):
    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Keep data within axis limits
    x = np.clip(np.atleast_1d(x), xlim[0], xlim[1])
    y = np.clip(np.atleast_1d(y), ylim[0], ylim[1])

    # Data → display (pixel coords)
    xy_pixels = ax.transData.transform(np.column_stack([x, y]))

    # Display → normalized figure coordinates (0 to 1)
    xy_fig = ax.figure.transFigure.inverted().transform(xy_pixels)

    # Normalized → slide coordinates (flip Y axis for Slides)
    x_slide = xy_fig[:, 0] * slide_width_pt
    y_slide = (1 - xy_fig[:, 1]) * slide_height_pt  # Flip Y

    return x_slide, y_slide
