import scriptcontext
import time
import System
import Rhino

rc, view = Rhino.Input.RhinoGet.GetView("select view")

print "position mouse where you want"
for i in [5,4,3,2,1]:
    time.sleep(0.5)
    print i

screen_point = System.Windows.Forms.Cursor.Position
print "screen_point =", screen_point

# convert screen coordinates to the client coordinates of
# the active view
view = scriptcontext.doc.Views.ActiveView
view_screen_rect = view.ScreenRectangle
x, y = screen_point.X - view_screen_rect.Left, screen_point.Y - view_screen_rect.Top
view_client_point = System.Drawing.Point(x, y)
print "view_client_point =", view_client_point

# convert the client coordinates of the view to the client
# coordinates of the active viewport (there are only multiple
# active viewports when working in layouts)
viewport = view.ActiveViewport
rc, viewport_point = viewport.ClientToScreenPort(view_client_point)
print "viewport_point =", viewport_point
rc, line = viewport.GetFrustumLine(viewport_point.X, viewport_point.Y)

if rc:
    scriptcontext.doc.Objects.AddPoint(line.From)
    scriptcontext.doc.Objects.AddPoint(line.To)
    scriptcontext.doc.Views.Redraw();