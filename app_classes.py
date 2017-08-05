from PyQt4.QtCore import *
from PyQt4.QtGui import *
from tools import logger
import config
from db_operations import open_sales, get_categories, get_subcategories, get_users
import sip

"""
Here we define the class structures that will allow us to operate the POS.
"""

# this class represents the main window of the POS that will be initially called
class PosWindow(QMainWindow):
    def __init__(self, db_session):
        super(PosWindow, self).__init__()

        # set the title
        self.setWindowTitle('Developing Foundation POS')

        # the db session
        self.db_session = db_session()

        # set the main widget
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.base_layout = QGridLayout(self.main_widget)

        # set the minimum size
        self.setMinimumSize(QSize(800, 600))

        # list of objects that appear in the UI
        self.product_box = None
        self.cat_box = None
        self.subcat_box = None
        self.scan_box = None
        self.utilities_box = None
        self.utilities_content = None
        self.sale_scroll = None
        self.price_box = None
        self.quantity_box = None
        self.overlay = None

        # actually set up the UI
        self.setup_ui()

        # private variables
        self._sales_session = None
        self._current_category = None
        self._sales_open = False
        self._running_total = 0.0
        self._users = []

    # setup the UI elements
    def setup_ui(self):
        # set the product box up
        self.product_box = QGroupBox()
        product_box_layout = QGridLayout(self.product_box)

        # category box which will hold the categories
        self.cat_box = QGroupBox()
        self.cat_box.setMaximumWidth(200)

        # add to the various layouts
        cat_layout = QVBoxLayout(self.cat_box)
        product_box_layout.addWidget(self.cat_box, 0, 0)
        self.base_layout.addWidget(self.product_box, 0, 0)

        # add this so it doesn't sit up the top
        cat_layout.addStretch()
        cat_layout.addWidget(QPushButton('Deals'))

        # The subcategory box
        self.subcat_box = QGroupBox()
        subcat_layout = QGridLayout(self.subcat_box)

        # add to the product box layout
        product_box_layout.addWidget(self.subcat_box, 0, 1)

        # add the scan box and holder
        scan_group_box = QGroupBox()
        scan_layout = QHBoxLayout(scan_group_box)
        self.base_layout.addWidget(scan_group_box, 1, 0)
        self.scan_box = QLineEdit()
        self.scan_box.setPlaceholderText('scan here')
        scan_layout.addStretch()
        scan_layout.addWidget(QLabel('Sale Scan:'))
        scan_layout.addWidget(self.scan_box)

        # TODO - Put sales button in proper place
        self.sales_button = QPushButton('Open Sales')
        self.sales_button.clicked.connect(self.set_sales)
        scan_layout.addWidget(self.sales_button)

        # add the utilities box for search and menu etc
        self.utilities_box = QGroupBox()
        utilities_layout = QGridLayout(self.utilities_box)
        utilities_menu = QGroupBox()
        utilities_menu.setMaximumWidth(200)
        utilities_menu_layout = QVBoxLayout(utilities_menu)
        utilities_layout.addWidget(utilities_menu, 0, 0)

        # load the utilities controls
        utilities_buttons = ['Search', 'Books', 'Notifications', 'Messages']
        for b in utilities_buttons:
            utilities_menu_layout.addWidget(QPushButton(b))

        self.base_layout.addWidget(self.utilities_box, 2, 0)

        # the utilities content area
        self.utilities_content = QGroupBox()
        utilities_content_layout = QGridLayout(self.utilities_content)
        utilities_layout.addWidget(self.utilities_content, 0, 1)

        # add the status bar to the application window
        self.setStatusBar(QStatusBar())

        # add the sales group
        sales_box = QGroupBox()
        sales_box_layout = QVBoxLayout(sales_box)
        self.base_layout.addWidget(sales_box, 0, 1, 3, 1)
        sales_box.setMinimumWidth(400)
        sales_box.setMaximumWidth(400)

        # sale scroll for holding current sale items
        self.sale_scroll = QScrollArea()
        scroll_layout = QVBoxLayout(self.sale_scroll)
        self.sale_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.sale_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        sales_box_layout.addWidget(self.sale_scroll)
        scroll_layout.addWidget(SaleButton('Test Sale (C1,SC1,Q1,$1.00)'))

        # price group box
        price_box = QGroupBox()
        price_box_layout = QGridLayout(price_box)
        sales_box_layout.addWidget(price_box)

        # actual controls for changing the values
        self.price_box = QLineEdit()
        self.price_box.setPlaceholderText('price')
        self.quantity_box = QLineEdit()
        self.quantity_box.setPlaceholderText('quantity')

        # add them to the layout
        price_box_layout.addWidget(self.price_box, 0, 0)
        price_box_layout.addWidget(self.quantity_box, 1, 0)
        price_box_layout.addWidget(QPushButton('Apply'), 2, 0)

        # the overlay for logging in and stuff
        self.overlay_widget = QGroupBox()
        overlay_layout = QGridLayout(self.overlay_widget)
        self.overlay_widget.setStyleSheet('QGroupBox{background-color: rgba(0,0,0,40%)}')
        login_form = LoginForm(self.db_session)
        overlay_layout.addWidget(login_form)
        self.base_layout.addWidget(self.overlay_widget, 0, 0, 3, 3)

        QObject.connect(login_form, SIGNAL('user_validated'), self.strip_overlay)
        # ---------------------------------------------------------------------------
        # ---------------------------------------------------------------------------
        # get the style sheet and apply it
        try:
            style = ''
            style_file = open('./style.css')
            for line in style_file:
                style += line
            self.setStyleSheet(style)
        except IOError as e:
            logger('Could not apply styles: %s' % str(e.args))

    def strip_overlay(self, username):
        # only log if not cancelling
        if username != '<cancel>':
            logger('Validated user %s' % username)

        # remove the layout
        self.base_layout.removeWidget(self.overlay_widget)
        sip.delete(self.overlay_widget)

    # call the open and close sales operations
    def set_sales(self):
        if self._sales_open:
            # TODO - add some post calculations
            # close the sales
            self.sales_button.setText('Open Sales')
            self._sales_open = False

            # clear all the controls
            self.clear_product_controls(True)

            logger('Sales closed. Running total: %s' % str(self._running_total))
        else:
            # get the sales session
            self._sales_session = open_sales(self.db_session)

            # set the sales to open
            self.sales_button.setText('Close Sales')
            self. _sales_open = True

            # load the categories and subcategories
            self.load_categories()
            self.load_subcategories()

            # log the opening
            logger('Sales opened.')

    def load_categories(self):
        # populate the category box
        cats = get_categories(self.db_session)
        # sort them according to their relative position
        cats = sorted(cats, key=lambda cat: cat.relative_position)

        # counter for relative position
        position_counter = 0
        for c in cats:
            self.cat_box.layout().insertWidget(position_counter, QPushButton(c.name.capitalize()))
            position_counter += 1

    def load_subcategories(self):
        # populate the product box
        subcat_query = get_subcategories(self.db_session)
        for sc in subcat_query:
            self.subcat_box.layout().addWidget(QPushButton(sc.name.capitalize() + ', ' + str(sc.category_id)))

    def clear_product_controls(self, categories=False):
        if categories:
            # get the list of items and delete from the bottom up
            cat_control_range = range(0, self.cat_box.layout().count())
            cat_control_range.reverse()

            # loop and delete
            for i in cat_control_range:
                control = self.cat_box.layout().itemAt(i)

                # if it is not a deal button or the spacer
                if type(control.widget()) is QPushButton:
                    if control.widget().text() != 'Deals':

                        # take and delete later (safe)
                        self.cat_box.layout().takeAt(i)
                        control.widget().deleteLater()

        # for all items in the subcat box try removing them
        while self.subcat_box.layout().itemAt(0):
            # take the item and delete later (safe)
            item = self.subcat_box.layout().takeAt(0)
            item.widget().deleteLater()


# Form we use form logging in a user
class LoginForm(QGroupBox):
    def __init__(self, db_session, allow_cancel=False):
        super(LoginForm, self).__init__()

        # set up the login interface
        self.main_layout = QGridLayout(self)

        self.username_box = QComboBox()
        self.password_box = QLineEdit()
        self.password_box.setPlaceholderText('password')
        self.password_box.setEchoMode(QLineEdit.Password)
        self.submit_button = QPushButton('Submit')
        self.submit_button.clicked.connect(self.validate)

        self.setFixedSize(QSize(300,300))

        self.main_layout.addWidget(self.username_box, 0, 0)
        self.main_layout.addWidget(self.password_box, 1, 0)
        self.main_layout.addWidget(self.submit_button, 2, 0)

        # determine whether they should be allowed to cancel or not
        if allow_cancel:
            self.cancel_button = QPushButton('Cancel')
            self.cancel_button.clicked.connect(self.cancel)
            self.main_layout.addWidget(self.cancel_button, 3, 0)

        # get the users and add them to the box
        users = get_users(db_session)
        self.username_box.addItems([u.username for u in users])
        self.setStyleSheet('background-color: black')

    # validate a user
    # todo - actually validate
    def validate(self):
        logger('Validating user %s' % self.username_box.currentText())
        self.emit(SIGNAL('user_validated'), self.username_box.currentText())

    # cancel the login form
    def cancel(self):
        self.emit(SIGNAL('user_validated'), '<cancel>')


class SaleButton(QPushButton):
    def __init__(self, text=''):
        super(SaleButton, self).__init__(text)

    def paintEvent(self, QPaintEvent):
        # call the standard paint event
        QPushButton.paintEvent(self, QPaintEvent)

        # define the pen and set the width
        pen = QPen(Qt.black, Qt.SolidLine)
        pen.setWidth(5)

        # set the painter object
        painter = QPainter()
        painter.begin(self)
        painter.setPen(pen)

        # get the height so we know where to put the lines
        h = self.height()

        # draw a line in the relevant spots
        painter.drawLine(10, 0, 10, h)


