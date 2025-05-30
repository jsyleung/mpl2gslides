from .auth import get_slides_service
from .slides_api import get_presentation, add_blank_slide
from .drawing import plot_to_api_requests

__all__ = [
    "get_slides_service",
    "get_presentation",
    "add_blank_slide",
    "plot_to_api_requests"
]
