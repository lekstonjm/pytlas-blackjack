class Card:
    def __init__(self, color, figure, value):
        self.color = color
        self.figure = figure
        self.value = value
        self.is_ace = False
        if self.figure == 'ace':
            self.is_ace = True

    def __str__(self):
        return '{0} of {1}'.format(self.figure, self.color)

    def i18n(self, req):
        return req._(self)