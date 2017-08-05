from PyQt4.QtGui import QApplication
from db_structures import *
from tools import load_settings, debug_operations, logger
import config
from app_classes import PosWindow

if __name__ == '__main__':
    #!! run this before doing anything else !!
    load_settings()
    # ---------------------------------------------------
    # ---------------------------------------------------

    logger('POS initialising...')

    # run any debug operations if we want to
    if config.settings.get('debug', False):
        debug_operations()

    # initialise the database
    db_session = init_database()

    # define the application
    app = QApplication([])

    # define the main window and pass the database session
    main_window = PosWindow(db_session)
    main_window.show()

    # execute the qt application
    app.exec_()

    logger('POS closing down...')
    logger('-'*100)
