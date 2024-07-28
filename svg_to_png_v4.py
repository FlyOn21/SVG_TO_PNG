import base64
import json
import io
import timeit
import cairo
from typing import Optional
import cProfile
import multiprocessing

import gi
gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg, GdkPixbuf, GLib


def is_valid_svg(svg_data: str) -> bool:
    """
    Validate the SVG data for common issues that might cause convert to fail.
    :param svg_data: SVG data as a string
    :return: True if valid, False otherwise
    """
    # Basic check for SVG header
    if not svg_data.strip().startswith("<svg"):
        return False

    # Check for common issues in the SVG data
    required_attributes = ["xmlns", "width", "height"]
    for attr in required_attributes:
        if attr not in svg_data:
            return False

    return True


def svg_to_png(svg_base64: str, name: str, result_collector: dict) -> Optional[str]:
    """
    Convert a base64-encoded SVG to a base64-encoded PNG.
    :param svg_base64: base64-encoded SVG
    :param name: Name for saving the files
    :param result_collector: Dictionary to store the results
    :return: base64-encoded PNG
    """
    try:
        svg_data = base64.b64decode(svg_base64).decode('utf-8')

        if not is_valid_svg(svg_data):
            raise ValueError("Invalid SVG data")

        with open(f"results/{name}.svg", "w") as f:
            f.write(svg_data)

        handle = Rsvg.Handle.new_from_data(svg_data.encode('utf-8'))
        width = handle.get_property("width")
        height = handle.get_property("height")
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, int(width), int(height))
        context = cairo.Context(surface)
        # Define the viewport
        viewport = Rsvg.Rectangle()
        viewport.x = 0
        viewport.y = 0
        viewport.width = width
        viewport.height = height

        handle.render_document(context, viewport)

        png_io = io.BytesIO()
        surface.write_to_png(png_io)
        png_io.seek(0)

        with open(f"results/{name}.png", "wb") as f:
            f.write(png_io.read())

        png_io.seek(0)  # Reset the buffer to the beginning
        png_base64 = base64.b64encode(png_io.read()).decode('utf-8')
        result_collector[name] = png_base64
        return
    except Exception as e:
        print(f"Error converting SVG to PNG: {e}")
        return


def worker(item, result_collector):
    key, svg_base64 = item
    svg_to_png(svg_base64, key, result_collector)

def process_json_file(input_file: str, output_file: str):
    """
    Process the input JSON file, convert the SVG to PNG, and save to output JSON file.
    :param input_file: Path to the input JSON file
    :param output_file: Path to the output JSON file
    """
    with open(input_file, 'r') as f:
        data = json.load(f)

    with multiprocessing.Manager() as manager:
        result_collector = manager.dict()
        items = list(data.items())
        cpu_count = 2

        with multiprocessing.Pool(cpu_count) as pool:
            pool.starmap(worker, [(item, result_collector) for item in items])

        data.update(result_collector)

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=4)


if __name__ == '__main__':
    input_json_path = 'Json.txt'
    output_json_path = 'Result.json'
    time = timeit.timeit(lambda: process_json_file(input_json_path, output_json_path), number=1)
    cProfile.run('process_json_file(input_json_path, output_json_path)')
    print(f"Processing time: {time}")
