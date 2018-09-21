from pyqiwi import Wallet
import cfg


w = Wallet(token=cfg.QIWI_TOKEN, number=cfg.QIWI_NUMBER)
