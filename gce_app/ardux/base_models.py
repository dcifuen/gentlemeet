import inspect
import logging
import googledatastore as datastore

class BaseProperty(object):
    _datastore_property = None #implement on subclases
    @property
    def name(self):
        return self.__name__

    @property
    def value(self):
        if hasattr(self, "_value"):
            return self._value
        else:
            return None

    @value.setter
    def value(self, value):
        self._value = value

class StringProperty(BaseProperty):
    _datastore_property = "string_value"

class BaseDataStoreModel(object):
    def put(self, id=None):
        try:

            obj = datastore.Entity()
            path_element = obj.key.path_element.add()
            path_element.kind = self.__class__.__name__
            if id:
                path_element.name = id

            properties = inspect.getmembers(self, lambda a:isinstance(a, BaseProperty))
            for name, property in properties:
                if property.value:
                    property_obj = obj.property.add()
                    property_obj.name = name
                    if property._datastore_property:
                        setattr(property_obj.value, property._datastore_property, property.value)
                    else:
                        raise Exception("Property needs _datastore_property implemented")
                    logging.info("%s = %s", name, property.value)

            resp = datastore.commit(obj)
        except:
            logging.exception("Error")

    def __setattr__(self, key, value):
        attr = getattr(self.__class__, key)
        if isinstance(attr, BaseProperty):
            attr.value = value
        else:
            setattr(self, key, value)

    def __getattr__(self, item):
        if isinstance(item, BaseProperty):
            return item.value
        else:
            return item

    def delete(self):
        pass

    def get_by_id(self):
        pass
