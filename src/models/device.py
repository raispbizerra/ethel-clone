class Device:
    """
    This class represents a device

    Attributes
    ----------
    cod : int
        Device's code at the database
    name : str
        Device's name
    mac : str
        Device's MAC address
    is_default : bool
        Flag that identifies which one is the default device
    calibrations : dict
        Device's calibrations
    calibration_date : datetime.date
        Device's calibrations date
    """

    def __init__(
        self,
        cod=None,
        name=None,
        mac=None,
        is_default=None,
        calibrations=None,
        calibration_date=None,
    ):
        self._cod = cod
        self._name = name
        self._mac = mac
        self._is_default = is_default
        self._calibrations = calibrations
        self._calibration_date = calibration_date

    @property
    def cod(self):
        return self._cod

    @cod.setter
    def cod(self, cod):
        self._cod = cod

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def mac(self):
        return self._mac

    @mac.setter
    def mac(self, mac):
        self._mac = mac

    @property
    def is_default(self):
        return self._is_default

    @is_default.setter
    def is_default(self, is_default):
        self._is_default = is_default

    @property
    def calibrations(self):
        return self._calibrations

    @calibrations.setter
    def calibrations(self, calibrations):
        self._calibrations = calibrations

    @property
    def calibration_date(self):
        return self._calibration_date

    @calibration_date.setter
    def calibration_date(self, calibration_date):
        self._calibration_date = calibration_date
