class MapElement(object):

    def __init__(self, key, value):
        self._key = key
        self._value = value

    @property
    def key(self):
        return self._key

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        self._value = new_value

class Map(object):

    def __init__(self):
        self._data = []

    def __getitem__(self, key):
        for item in self._data:
            if item.key == key:
                return item.value
        raise KeyError('Desired key does not exist')

    def __setitem__(self, key, value):
        for item in self._data:
            if item.key == key:
                item.value = value
                return
        self._data.append(MapElement(key, value))

    def __delitem__(self, key):
        length = len(self._data)
        for i in range (length):
            if self._data[i].key == key:
                self._data.pop(i)
                return
        raise KeyError('Desired key does not exist')

    def __len__(self):
        return len(self._data)

    def __contains__(self, key):
        for item in self._data:
            if item.key == key:
                return True
        return False

    def __iter__(self):
        for item in self._data:
            yield item.key # yield je kao return ali vraca trenutnu vrednost i ne prekida skroz

    def items(self):
        for item in self._data:
            yield item.key, item.value

    def keys(self):
        keys = []
        for item in self._data:
            keys.append(item.key)
        return keys

    def values(self):
        values = []
        for item in self._data:
            values.append(item.value)
        return values

    def clear(self):
        self._data = []