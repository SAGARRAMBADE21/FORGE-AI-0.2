"""Tests for parser utilities."""
import pytest
from pathlib import Path
from frontend_scanner.parsers.framework_detector import FrameworkDetector
from frontend_scanner.parsers.route_extractor import RouteExtractor
from frontend_scanner.parsers.js_parser import JSParser


def test_js_parser_functions():
    """Test JavaScript function extraction."""
    code = """
    function myFunction() {
        return 'test';
    }
    
    const arrowFunc = () => {
        return 'arrow';
    };
    """
    
    functions = JSParser.extract_functions(code)
    assert len(functions) >= 1


def test_js_parser_classes():
    """Test JavaScript class extraction."""
    code = """
    class MyClass extends BaseClass {
        constructor() {
            super();
        }
    }
    """
    
    classes = JSParser.extract_classes(code)
    assert len(classes) == 1
    assert classes[0]["name"] == "MyClass"


def test_framework_detector(tmp_path):
    """Test framework detection."""
    # Create mock package.json
    package_json = tmp_path / "package.json"
    package_json.write_text('{"dependencies": {"react": "^18.0.0"}}')
    
    framework = FrameworkDetector.detect(tmp_path)
    assert framework == "react"


def test_route_extractor_react_router():
    """Test React Router extraction."""
    sample_code = """
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<About />} />
        <Route path="/users/:id" element={<User />} />
      </Routes>
    </BrowserRouter>
    """
    
    routes = RouteExtractor.extract_react_router_routes(sample_code)
    
    assert "/" in routes
    assert "/about" in routes
    assert "/users/:id" in routes
