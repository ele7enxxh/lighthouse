from lighthouse.util import *

#------------------------------------------------------------------------------
# IDA Plugin Palette
#------------------------------------------------------------------------------

class LighthousePalette(object):
    """
    Color Palette for the Lighthouse plugin.

    TODO: external theme customization, controls
    """

    def __init__(self):
        """
        Initialize default palette colors for Lighthouse.
        """

        # the active theme name
        self._qt_theme  = "Light"
        self._ida_theme = "Light"

        # the list of available themes
        self._themes = \
        {
            "Dark":  0,
            "Light": 1,
        }

        #
        # Coverage Overview
        #

        self._coverage_bad  = [QtGui.QColor(221, 0, 0),    QtGui.QColor(207, 31, 0)]
        self._coverage_good = [QtGui.QColor(51, 153, 255), QtGui.QColor(75, 209, 42)]

        #
        # IDA Views / HexRays
        #

        self._ida_coverage = [0x990000, 0xC8E696] # NOTE: IDA uses BBGGRR

        #
        # Composing Shell
        #

        self._logic_token    = [0xF02070, 0xFF0000]
        self._comma_token    = [0x00FF00, 0x0000FF]
        self._paren_token    = [0x40FF40, 0x0000FF]
        self._coverage_token = [0x80F0FF, 0x000000]
        self._invalid_text   = [0x990000, 0xFF0000]

    #--------------------------------------------------------------------------
    # Theme Management
    #--------------------------------------------------------------------------

    @property
    def ida_theme(self):
        """
        Return the active IDA theme number.
        """
        return self._themes[self._ida_theme]

    @property
    def qt_theme(self):
        """
        Return the active Qt theme number.
        """
        return self._themes[self._qt_theme]

    def refresh_colors(self):
        """
        Dynamically compute palette color based on IDA theme.

        Depending on if IDA is using a dark or light theme, we *try*
        to select colors that will hopefully keep things most readable.
        """

        #
        # NOTE/TODO:
        #
        #   the dark table (Qt) theme is way better than the light theme
        #   right now, so we're just going to force that on for everyone
        #   for the time being.
        #

        self._qt_theme  = "Dark" # self._qt_theme_hint()
        self._ida_theme = self._ida_theme_hint()

    def _ida_theme_hint(self):
        """
        Binary hint of the IDA color theme.

        This routine returns a best effort hint as to what kind of theme is
        in use for the IDA Views (Disas, Hex, HexRays, etc).

        Returns 'Dark' or 'Light' indicating the user's theme
        """

        #
        # determine whether to use a 'dark' or 'light' paint based on the
        # background color of the user's disassembly view
        #

        bg_color = get_disas_bg_color()

        # return 'Dark' or 'Light'
        return test_color_brightness(bg_color)

    def _qt_theme_hint(self):
        """
        Binary hint of the Qt color theme.

        This routine returns a best effort hint as to what kind of theme the
        QtWdigets throughout IDA are using. This is to accomodate for users
        who may be using Zyantific's IDASkins plugins (or others) to further
        customize IDA's appearance.

        Returns 'Dark' or 'Light' indicating the user's theme
        """

        #
        # to determine what kind of Qt based theme IDA is using, we create a
        # test widget and check the colors put into the palette the widget
        # inherits from the application (eg, IDA).
        #

        test_widget = QtWidgets.QWidget()

        #
        # in order to 'realize' the palette used to render (draw) the widget,
        # it first must be made visible. since we don't want to be popping
        # random widgets infront of the user, so we set this attribute such
        # that we can silently bake the widget colors.
        #
        # NOTE/COMPAT: WA_DontShowOnScreen
        #
        #   https://www.riverbankcomputing.com/news/pyqt-56
        #
        #   lmao, don't ask me why they forgot about this attribute from 5.0 - 5.6
        #

        if using_pyqt5():
            test_widget.setAttribute(103) # taken from http://doc.qt.io/qt-5/qt.html
        else:
            test_widget.setAttribute(QtCore.Qt.WA_DontShowOnScreen)

        # render the (invisible) widget
        test_widget.show()

        # now we farm the background color from the qwidget
        bg_color = test_widget.palette().color(QtGui.QPalette.Window)

        # 'hide' & delete the widget
        test_widget.hide()
        test_widget.deleteLater()

        # return 'Dark' or 'Light'
        return test_color_brightness(bg_color)

    #--------------------------------------------------------------------------
    # Coverage Overview
    #--------------------------------------------------------------------------

    @property
    def coverage_bad(self):
        return self._coverage_bad[self.qt_theme]

    @property
    def coverage_good(self):
        return self._coverage_good[self.qt_theme]

    #--------------------------------------------------------------------------
    # IDA Views / HexRays
    #--------------------------------------------------------------------------

    @property
    def ida_coverage(self):
        return self._ida_coverage[self.ida_theme]

    #--------------------------------------------------------------------------
    # Composing Shell
    #--------------------------------------------------------------------------

    @property
    def logic_token(self):
        return self._logic_token[self.qt_theme]

    @property
    def comma_token(self):
        return self._comma_token[self.qt_theme]

    @property
    def paren_token(self):
        return self._paren_token[self.qt_theme]

    @property
    def coverage_token(self):
        return self._coverage_token[self.qt_theme]

    @property
    def invalid_text(self):
        return self._invalid_text[self.qt_theme]

    @property
    def TOKEN_COLORS(self):
        """
        Return the palette of token colors.
        """

        return \
        {

            # logic operators
            "OR":    self.logic_token,
            "XOR":   self.logic_token,
            "AND":   self.logic_token,
            "MINUS": self.logic_token,

            # misc
            "COMMA":   self.comma_token,
            "LPAREN":  self.paren_token,
            "RPAREN":  self.paren_token,
            #"WS":      self.whitepsace_token,
            #"UNKNOWN": self.unknown_token,

            # coverage
            "COVERAGE_TOKEN": self.coverage_token,
        }

#------------------------------------------------------------------------------
# Palette Util
#------------------------------------------------------------------------------

def test_color_brightness(color):
    """
    Test the brightness of a color.
    """
    if color.lightness() > 255.0/2:
        return "Light"
    else:
        return "Dark"

def compute_color_on_gradiant(percent, color1, color2):
    """
    Compute the color specified by a percent between two colors.

    TODO: This is silly, heavy, and can be refactored.
    """

    # dump the rgb values from QColor objects
    r1, g1, b1, _ = color1.getRgb()
    r2, g2, b2, _ = color2.getRgb()

    # compute the new color across the gradiant of color1 -> color 2
    r = r1 + percent * (r2 - r1)
    g = g1 + percent * (g2 - g1)
    b = b1 + percent * (b2 - b1)

    # return the new color
    return QtGui.QColor(r,g,b)
