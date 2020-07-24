from marshmallow import Schema, fields
from marshmallow.validate import OneOf, Equal
from marshmallow_oneofschema import OneOfSchema


class Field():
    def __init__(self, typeName, value, multiple=False, typeClass='primitive'):
        self.typeName = typeName
        self.value = value
        self.multiple = multiple
        self.typeClass = typeClass

    def get_typeClass(self):
        return self.typeClass

    def get_multiple(self):
        return self.multiple


class PrimitiveField(Field):
    def __init__(self, typeName, value=''):
        super().__init__(typeName, value, False, 'primitive')

    def add_value(self, value):
        self.value = value


class CompoundField(Field):
    def __init__(self, typeName, value={}):
        super().__init__(typeName, value, False, 'compound')

    def add_value(self, value, key):
        self.value[key] = value


class MultipleCompoundField(Field):
    def __init__(self, typeName, value=[]):
        super().__init__(typeName, value, True, 'compound')

    def add_value(self, value):
        if not isinstance(self.value, list):
            self.value = []
        self.value.append(value)

    def add_value_to_element(self, value, key, index=None):
        if not isinstance(self.value, list):
            self.value = []
        if index is None:
            index = len(self.value)
        self.value[index][key] = value


class MultiplePrimitiveField(Field):
    def __init__(self, typeName, value=[]):
        super().__init__(typeName, value, True, 'primitive')

    def add_value(self, value):
        if not isinstance(self.value, list):
            self.value = []
        self.value.append(value)


class VocabularyField(Field):
    def __init__(self, typeName, value=[], vocab=[]):
        self.vocab = vocab
        super().__init__(typeName, value, False, 'compound')

    def add_value(self, value):
        if value in self.vocab:
            self.value.append(value)
        #else:
            # exception mit warning werfen


class MetadataBlock():
    def __init__(self, id, name, fields=[]):
        self.id = id
        self.name = name
        self.fields = fields

    def add_field(self, field):
        self.fields.append(field)


class PrimitiveFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(False))
    typeClass = fields.Str(validate=Equal('primitive'))
    value = fields.Str()


class CompoundFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(False))
    typeClass = fields.Str(validate=Equal('compound'))
    value = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(PrimitiveFieldScheme))


class MultipleCompoundFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(True))
    typeClass = fields.Str(validate=Equal('compound'))
    value = fields.List(fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(PrimitiveFieldScheme)))


class MultiplePrimitiveFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(True))
    typeClass = fields.Str(validate=Equal('primitive'))
    value = fields.List(fields.Str())


class FieldSchema(OneOfSchema):
    type_schemas = {
        'PrimitiveField': PrimitiveFieldScheme,
        'CompoundField': CompoundFieldScheme,
        'MultiplePrimitiveField': MultiplePrimitiveFieldScheme,
        'MultipleCompoundField': MultipleCompoundFieldScheme
    }


class EditScheme(Schema):
    mFields = fields.List(
        fields.Nested(
            #FieldSchema(only=['typeName', 'value'])
            FieldSchema()
            ),
        data_key='fields')


class MetadataBlockSchema(Schema):
    id = fields.Str()
    displayName = fields.Str()
    mFields = fields.List(fields.Nested(FieldSchema), data_key='fields')


class DatasetSchema(Schema):
    metadataBlocks = fields.List(fields.Nested(MetadataBlockSchema))


class CreateDatasetSchema(Schema):
    datasetVersion = fields.Nested(DatasetSchema)
