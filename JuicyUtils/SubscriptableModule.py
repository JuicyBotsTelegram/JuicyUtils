class MakeSubscriptableModule(object):
    # MSubModule = MakeSubscriptableModule(__import__('Module_name').__dict__)
    # MSubModule = MakeSubscriptableModule(SomeObject.__dict__)
    # MultiLang = {'EN': MakeSubscriptableModule(__import__('JuicyEN').__dict__),
    #              'RU': MakeSubscriptableModule(__import__('JuicyRU').__dict__)}
    def __init__(self, namespace: dict):
        self.__dict__ = namespace

    def __getitem__(self, name):
        return self.__dict__[name]