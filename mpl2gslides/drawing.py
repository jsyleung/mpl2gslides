import matplotlib.colors as mcolors
import matplotlib.container as mcont
import uuid
from .utils import points_to_pixels, data_to_slide_coords

def create_line_request(x1, y1, x2, y2, color_rgba, object_id, slide_id, unit="PT"):
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        raise ValueError("Start and end points are the same.")

    # Slides API accepts only non-zero width and height, but small values
    #   are rendered as zero, so we set a minimum size
    min_size = 0.001
    width = max(abs(dx), min_size)
    height = max(abs(dy), min_size)

    request = []
    request.append({
        "createLine": {
            "objectId": object_id,
            "lineCategory": "STRAIGHT",
            "elementProperties": {
                "pageObjectId": slide_id,
                "size": {
                    "width": {"magnitude": width, "unit": unit},
                    "height": {"magnitude": height, "unit": unit}
                },
                "transform": {
                    "scaleX": 1 if dx >= 0 else -1,
                    "scaleY": 1 if dy >= 0 else -1,
                    "shearX": 0,
                    "shearY": 0,
                    "translateX": x1,
                    "translateY": y1,
                    "unit": unit
                }
            }
        }
    })

    request.append({
        "updateLineProperties": {
            "objectId": object_id,
            "lineProperties": {
                "lineFill": {
                    "solidFill": {
                        "color": {
                            "rgbColor": {
                                "red": color_rgba[0],
                                "green": color_rgba[1],
                                "blue": color_rgba[2]
                            }
                        }
                    }
                },
                "weight": {"magnitude": 1, "unit": unit}
            },
            "fields": "lineFill,weight"
        }
    })

    return request

def create_group_request(children_ids, group_id):
    request = [{
        "groupObjects": {
            "childrenObjectIds": children_ids,
            "groupObjectId": group_id
        }
    }]
    return request

def plot_to_api_requests(ax, slide_id, session_id=None):
    if session_id is None:
        session_id = uuid.uuid4().hex[:6]
    group_ids = {}
    requests = []

    xlim = ax.get_xlim()
    ylim = ax.get_ylim()

    # Grid Lines
    if True: # include_grid:
        color = mcolors.to_rgba(ax.get_xgridlines()[0].get_color())
        line_ids = []

        # Vertical
        for i, x in enumerate(ax.get_xticks()):
            # Skip ticks outside the xlim
            if x < xlim[0] or x > xlim[1]:
                continue
            x_data = [x, x]
            y_data = list(ylim)

            x_pts, y_pts = data_to_slide_coords(ax, x_data, y_data)

            object_id = f"grid_x_{i}_{session_id}"
            line_ids.append(object_id)
            requests.append(create_line_request(x_pts[0], y_pts[0], x_pts[1], y_pts[1], color, object_id, slide_id))

        # Horizontal
        for i, y in enumerate(ax.get_yticks()):
            # Skip ticks outside the ylim
            if y < ylim[0] or y > ylim[1]:
                continue
            x_data = list(xlim)
            y_data = [y, y]

            x_pts, y_pts = data_to_slide_coords(ax, x_data, y_data)

            object_id = f"grid_y_{i}_{session_id}"
            line_ids.append(object_id)
            requests.append(create_line_request(x_pts[0], y_pts[0], x_pts[1], y_pts[1], color, object_id, slide_id))

        # Group all grid lines together
        requests.append(create_group_request(line_ids, f"grid_{session_id}"))

    # Plot lines
    for i, line in enumerate(ax.get_lines()):
        if line.get_linestyle() == 'None':
            continue

        x_data = line.get_xdata()
        y_data = line.get_ydata()
        color = mcolors.to_rgba(line.get_color())

        x_pts, y_pts = data_to_slide_coords(ax, x_data, y_data)

        # Each segment of the line must be added separately
        segment_ids = []
        for k in range(len(x_data) - 1):
            object_id = f"line_{i}_{k}_{session_id}"
            segment_ids.append(object_id)
            requests.append(create_line_request(x_pts[k], y_pts[k], x_pts[k + 1], y_pts[k + 1], color, object_id, slide_id))
        group_ids[line] = f"line_{i}_{session_id}"
        requests.append(create_group_request(segment_ids, group_ids[line]))

    # Error bars and caps
    errs = [c for c in ax.containers if isinstance(c, mcont.ErrorbarContainer)]
    for i, cont in enumerate(errs):
        line, caps, bars = cont
        segment_ids = []

        # Retrieve main line's ID for grouping
        if line.get_linestyle() != 'None':
            segment_ids.append(group_ids[line])

        # Draw barlines
        ybars = bars[0].get_segments()
        color = mcolors.to_rgba(bars[0].get_edgecolor())
        for k, seg in enumerate(ybars):
            x, y1 = seg[0]  # bottom
            _, y2 = seg[1]  # top

            sx, sy1 = data_to_slide_coords(ax, x, y1)
            _ , sy2 = data_to_slide_coords(ax, x, y2)

            object_id = f"bar_{i}_{k}_{session_id}"
            segment_ids.append(object_id)
            requests.append(create_line_request(sx[0], sy1[0], sx[0], sy2[0], color, object_id, slide_id))

        # Draw caps
        if len(caps) == 0:
            continue
        caps_bottom, caps_top = caps
        # mpl may draw caps as markers '_'
        if caps_bottom.get_marker() is not None:
            x, y = caps_bottom.get_data()
            sx, sy = data_to_slide_coords(ax, x, y)
            color = mcolors.to_rgba(caps_bottom.get_color())
            markersize = points_to_pixels(caps_bottom.get_markersize(), ax.figure.dpi)
            segments = [(_x - markersize , _x + markersize) for _x in sx]
            for k, s in enumerate(segments):
                if y[k] >= ylim[0]:
                    object_id_bottom = f"error_cap_bottom_{i}_{k}_{session_id}"
                    segment_ids.append(object_id_bottom)
                    requests.append(create_line_request(s[0], sy[k], s[1], sy[k], color, object_id_bottom, slide_id))
        if caps_top.get_marker() is not None:
            x, y = caps_top.get_data()
            sx, sy = data_to_slide_coords(ax, x, y)
            color = mcolors.to_rgba(caps_top.get_color())
            markersize = points_to_pixels(caps_top.get_markersize(), ax.figure.dpi)
            segments = [(_x - markersize , _x + markersize) for _x in sx]
            for k, s in enumerate(segments):
                if y[k] <= ylim[1]:
                    object_id_top = f"error_cap_top_{i}_{k}_{session_id}"
                    segment_ids.append(object_id_top)
                    requests.append(create_line_request(s[0], sy[k], s[1], sy[k], color, object_id_top, slide_id))

        requests.append(create_group_request(segment_ids, f"errorbar_{i}_{session_id}"))

    return requests
