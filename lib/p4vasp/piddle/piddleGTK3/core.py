"""GTK3 drawing surfaces and events for p4vasp graphs.

Replaces the GdkPixmap/GdkGC backend with Cairo image surfaces. Drawing does
not require a realized window; GTK's draw signal paints the buffered surface.
"""
import math
import cairo
import gi

gi.require_foreign('cairo')
gi.require_version('Gtk', '3.0')
gi.require_version('Gdk', '3.0')
gi.require_version('Pango', '1.0')
gi.require_version('PangoCairo', '1.0')
from gi.repository import Gtk, Gdk, Pango, PangoCairo
from p4vasp.piddle import piddle


class BasicCanvas(piddle.Canvas):
    def __init__(self, area=None):
        piddle.Canvas.__init__(self)
        self.area = area if area is not None else Gtk.DrawingArea()
        self.backgroundColor = piddle.white
        self.background_buffer = None
        self.drawable = cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1)
        self._allocation = None
        self._handlers = [self.area.connect('draw', self._draw),
                          self.area.connect('size-allocate', self._resize)]
        self.clear()

    def close(self):
        for handler in self._handlers:
            if self.area.handler_is_connected(handler):
                self.area.disconnect(handler)
        self._handlers = []

    def isInteractive(self):
        return False

    def canUpdate(self):
        return True

    def get_drawing_area(self):
        return self.area

    def area_drawable(self):
        return self.area.get_window()

    def _draw(self, area, context):
        context.set_source_surface(self.drawable, 0, 0)
        context.paint()
        return False

    def _resize(self, area, allocation):
        size = (allocation.width, allocation.height)
        if size == self._allocation:
            return
        self._allocation = size
        self.ensure_size(*size)
        if hasattr(self, 'resizeCallback'):
            self.resizeCallback(*size)

    def ensure_size(self, width, height):
        width = max(1, int(math.ceil(width)), self.drawable.get_width())
        height = max(1, int(math.ceil(height)), self.drawable.get_height())
        if (width, height) != (self.drawable.get_width(), self.drawable.get_height()):
            old = self.drawable
            self.drawable = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
            self.clear()
            context = cairo.Context(self.drawable)
            context.set_source_surface(old, 0, 0)
            context.paint()
        return self.drawable

    @staticmethod
    def _color(context, color):
        context.set_source_rgb(color.red, color.green, color.blue)

    def clear(self, background=None):
        if background is not None:
            self.backgroundColor = background
        context = cairo.Context(self.drawable)
        context.set_operator(cairo.OPERATOR_SOURCE)
        if self.backgroundColor == piddle.transparent:
            context.set_source_rgba(0, 0, 0, 0)
        else:
            self._color(context, self.backgroundColor)
        context.paint()

    def flush(self):
        self.drawable.flush()
        self.area.queue_draw()

    def to_background_buffer(self):
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, self.drawable.get_width(), self.drawable.get_height())
        context = cairo.Context(surface)
        context.set_source_surface(self.drawable, 0, 0)
        context.paint()
        self.background_buffer = surface
        return surface

    def from_background_buffer(self):
        if self.background_buffer is not None:
            context = cairo.Context(self.drawable)
            context.set_operator(cairo.OPERATOR_SOURCE)
            context.set_source_surface(self.background_buffer, 0, 0)
            context.paint()
            self.flush()

    def drawLine(self, x1, y1, x2, y2, color=None, width=None):
        self.drawLines([(x1, y1, x2, y2)], color, width)

    def drawLines(self, lineList, color=None, width=None):
        color = self.defaultLineColor if color is None else color
        if color == piddle.transparent:
            return
        context = cairo.Context(self.drawable)
        self._color(context, color)
        context.set_line_width(self.defaultLineWidth if width is None else width)
        for x1, y1, x2, y2 in lineList:
            context.move_to(x1, y1)
            context.line_to(x2, y2)
        context.stroke()

    def drawPolygon(self, pointlist, edgeColor=None, edgeWidth=None, fillColor=None, closed=0):
        if not pointlist:
            return
        edgeColor = self.defaultLineColor if edgeColor is None else edgeColor
        fillColor = self.defaultFillColor if fillColor is None else fillColor
        context = cairo.Context(self.drawable)
        context.move_to(*pointlist[0])
        for point in pointlist[1:]:
            context.line_to(*point)
        if closed:
            context.close_path()
        if fillColor != piddle.transparent:
            self._color(context, fillColor)
            context.fill_preserve()
        if edgeColor != piddle.transparent:
            self._color(context, edgeColor)
            context.set_line_width(self.defaultLineWidth if edgeWidth is None else edgeWidth)
            context.stroke()

    def drawRect(self, x1, y1, x2, y2, edgeColor=None, edgeWidth=None, fillColor=None):
        self.drawPolygon([(x1, y1), (x2, y1), (x2, y2), (x1, y2)],
                         edgeColor, edgeWidth, fillColor, closed=1)

    def getFontDescription(self, font):
        description = Pango.FontDescription()
        face = font.face or 'sans'
        if isinstance(face, (list, tuple)):
            face = face[0] if face else 'sans'
        description.set_family({'sansserif': 'sans', 'serif': 'serif', 'monospaced': 'monospace'}.get(face, face))
        description.set_size(int(font.size * Pango.SCALE))
        description.set_weight(Pango.Weight.BOLD if font.bold else Pango.Weight.NORMAL)
        description.set_style(Pango.Style.ITALIC if font.italic else Pango.Style.NORMAL)
        return description

    def _layout(self, text, font=None, context=None):
        font = self.defaultFont if font is None else font
        context = context if context is not None else cairo.Context(self.drawable)
        layout = PangoCairo.create_layout(context)
        layout.set_font_description(self.getFontDescription(font))
        layout.set_text(str(text), -1)
        if font.underline:
            attributes = Pango.AttrList()
            attributes.insert(Pango.attr_underline_new(Pango.Underline.SINGLE))
            layout.set_attributes(attributes)
        return layout

    def drawString(self, s, x, y, font=None, color=None, angle=0.0):
        color = self.defaultLineColor if color is None else color
        if color == piddle.transparent:
            return
        context = cairo.Context(self.drawable)
        self._color(context, color)
        context.translate(x, y)
        context.rotate(-math.radians(angle))
        layout = self._layout(s, font, context)
        context.move_to(0, -layout.get_baseline() / Pango.SCALE)
        PangoCairo.show_layout(context, layout)

    def stringSize(self, s, font=None):
        return self._layout(s, font).get_pixel_size()

    def stringWidth(self, s, font=None):
        return self.stringSize(s, font)[0]

    def stringHeight(self, s, font=None):
        return self.stringSize(s, font)[1]

    def fontAscent(self, font=None):
        return self._layout('Mg', font).get_baseline() / Pango.SCALE

    def fontDescent(self, font=None):
        return self.stringHeight('Mg', font) - self.fontAscent(font)

    def fontHeight(self, font=None):
        return self.stringHeight('Mg', font)

    def drawImage(self, image, x1, y1, x2=None, y2=None):
        import io
        stream = io.BytesIO()
        image.save(stream, format='PNG')
        stream.seek(0)
        surface = cairo.ImageSurface.create_from_png(stream)
        width, height = surface.get_width(), surface.get_height()
        context = cairo.Context(self.drawable)
        context.translate(x1, y1)
        context.scale((x2-x1)/width if x2 is not None else 1,
                      (y2-y1)/height if y2 is not None else 1)
        context.set_source_surface(surface, 0, 0)
        context.paint()


DrawingAreaCanvas = BasicCanvas


class InteractiveCanvas(BasicCanvas):
    def __init__(self, area, window=None):
        super().__init__(area)
        self.window = window
        self._button = 0
        self._events_initialized = False
        self.initEvents()

    def isInteractive(self):
        return True

    def initEvents(self):
        if self._events_initialized:
            return
        self._events_initialized = True
        self.area.set_can_focus(True)
        self.area.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.BUTTON_RELEASE_MASK |
                             Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.SCROLL_MASK)
        self._handlers.append(self.area.connect('event', self._event))

    def _event(self, widget, event):
        if event.type == Gdk.EventType.BUTTON_PRESS:
            self._button = event.button
            widget.grab_focus()
        elif event.type == Gdk.EventType.BUTTON_RELEASE:
            self._button = 0
            self.onClick(self, event.x, event.y, event.button)
        elif event.type == Gdk.EventType.MOTION_NOTIFY:
            self.onOver(self, event.x, event.y, self._button)
        elif event.type == Gdk.EventType.SCROLL:
            if event.direction in (Gdk.ScrollDirection.UP, Gdk.ScrollDirection.DOWN):
                self.onClick(self, event.x, event.y, 4 if event.direction == Gdk.ScrollDirection.UP else 5)
        elif event.type == Gdk.EventType.KEY_PRESS:
            keys = {'Left': piddle.keyLeft, 'Right': piddle.keyRight, 'Up': piddle.keyUp,
                    'Down': piddle.keyDown, 'Prior': piddle.keyPgUp, 'Next': piddle.keyPgDn,
                    'Home': piddle.keyHome, 'End': piddle.keyEnd}
            key = keys.get(Gdk.keyval_name(event.keyval), event.string)
            modifiers = (piddle.modShift if event.state & Gdk.ModifierType.SHIFT_MASK else 0)
            modifiers |= (piddle.modControl if event.state & Gdk.ModifierType.CONTROL_MASK else 0)
            self.onKey(self, key, modifiers)
        return False


class InteractiveBoxCanvas(InteractiveCanvas):
    def __init__(self, box):
        self.box = box
        area = Gtk.DrawingArea()
        box.pack_start(area, True, True, 0)
        super().__init__(area, box.get_toplevel())
        area.show()


class GTKCanvas(InteractiveCanvas):
    def __init__(self, size=(300, 300), name='Piddle-GTK3', infoline=1):
        self.top = Gtk.Window(title=name)
        self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.top.add(self.vbox)
        area = Gtk.DrawingArea()
        area.set_size_request(*map(int, size))
        self.vbox.pack_start(area, True, True, 0)
        self.sbar = Gtk.Statusbar() if infoline else None
        if self.sbar is not None:
            self.vbox.pack_end(self.sbar, False, False, 0)
        super().__init__(area, self.top)
        self.ensure_size(*size)
        self.top.show_all()

    def setInfoLine(self, text):
        if self.sbar is not None:
            self.sbar.pop(1)
            if text:
                self.sbar.push(1, str(text))

    def get_toplevel(self):
        return self.top

    def get_vbox(self):
        return self.vbox

    def get_statusbar(self):
        return self.sbar


class DialogCanvas(GTKCanvas):
    def __init__(self, size=(300, 300), name='Piddle-GTK3'):
        super().__init__(size, name, infoline=0)
        button = Gtk.Button(label='Dismiss')
        button.connect('clicked', lambda button: self.top.destroy())
        self.vbox.pack_end(button, False, False, 0)
        button.show()
