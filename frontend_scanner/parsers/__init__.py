"""Parser utilities."""
from frontend_scanner.parsers.js_parser import JSParser
from frontend_scanner.parsers.framework_detector import FrameworkDetector
from frontend_scanner.parsers.route_extractor import RouteExtractor

__all__ = [
    "JSParser",
    "FrameworkDetector",
    "RouteExtractor"
]
