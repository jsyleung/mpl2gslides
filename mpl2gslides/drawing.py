import matplotlib.colors as mcolors
import uuid
from .utils import data_to_slide_coords

def create_line_request(x1, y1, x2, y2, color_rgba, object_id, slide_id, unit="PT"):
    dx = x2 - x1
    dy = y2 - y1
    red, green, blue = color_rgba[:3]

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
                                "red": red,
                                "green": green,
                                "blue": blue
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

def group_segments(segment_ids, line_index, session_id=None):
    if session_id is None:
        session_id = uuid.uuid4().hex[:6]
    group_id = f"group_{line_index}_{session_id}"

    request = [{
        "groupObjects": {
            "childrenObjectIds": segment_ids,
            "groupObjectId": group_id
        }
    }]
    return request

def plot_to_api_requests(ax, slide_id, session_id=None):
    if session_id is None:
        session_id = uuid.uuid4().hex[:6]
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
        requests.append(group_segments(line_ids, "grid", session_id))

    # Plot lines
    for i, line in enumerate(ax.get_lines()):
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
        requests.append(group_segments(segment_ids, i, session_id))

    return requests
