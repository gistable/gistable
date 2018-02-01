from AppKit import NSPoint
from mojo.events import MeasurementTool

measurement = MeasurementTool.measurementClass()
measurement.startPoint = NSPoint(100, 100)
measurement.endPoint = NSPoint(200, 200)

g = CurrentGlyph()
g.naked().measurements.append(measurement)
g.update()