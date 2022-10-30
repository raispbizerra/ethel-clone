class Patient:
    """
    This class represents a patient

    Attributes
    ----------
    cod : int
        Patient's code at the database
    name : str
        Patient's name
    sex : str
        Patient's sex
    birth : date
        Patient's birth
    height : float
        Patient's height
    weight : float
        Patient's weight
    imc : float
        Patient's imc
    """

    def __init__(
        self,
        cod=None,
        name=None,
        sex=None,
        birth=None,
        height=None,
        weight=None,
        imc=None,
    ):
        self._cod = cod
        self._name = name
        self._sex = sex
        self._birth = birth
        self._height = height
        self._weight = weight
        self._imc = imc

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
    def sex(self):
        return self._sex

    @sex.setter
    def sex(self, sex):
        self._sex = sex

    @property
    def birth(self):
        return self._birth

    @birth.setter
    def birth(self, birth):
        self._birth = birth

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, height):
        self._height = height

    @property
    def weight(self):
        return self._weight

    @weight.setter
    def weight(self, weight):
        self._weight = weight

    @property
    def imc(self):
        return self._imc

    @imc.setter
    def imc(self, imc):
        self._imc = imc
