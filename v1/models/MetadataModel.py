from marshmallow import Schema, fields
from marshmallow.validate import Equal
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

    def get_typeName(self):
        return self.typeName

    def get_value(self):
        return self.value

    def __repr__(self):
        return '{} ({}, {}): {}'.format(
            self.typeName,
            self.typeClass,
            "m" if self.multiple else 'nm',
            self.value)


class PrimitiveField(Field):
    def __init__(self, typeName, value=None):
        if value is None:
            value = ''
        super().__init__(typeName, value, False, 'primitive')

    def add_value(self, value):
        self.value = value


class CompoundField(Field):
    def __init__(self, typeName, value=None):
        if value is None:
            value = {}
        super().__init__(typeName, value, False, 'compound')

    def add_value(self, value, key):
        # print('add value {} with key {} to CF'.format(value, key))
        self.value[key] = value


class MultipleCompoundField(Field):
    def __init__(self, typeName, value=None):
        if value is None:
            value = []
        super().__init__(typeName, value, True, 'compound')

    def add_value(self, compound):
        if not isinstance(self.value, list):
            self.value = []
        if isinstance(compound, CompoundField):
            # print('add Value to MCF: ', compound.value)
            # hier eventuell noch Fehlerbehandlung hinzufügen
            self.value.append(compound.value)


class MultiplePrimitiveField(Field):
    def __init__(self, typeName, value=None):
        super().__init__(typeName, value, True, 'primitive')

    def add_value(self, value):
        if not isinstance(self.value, list):
            self.value = []
        self.value.append(value)
        
        
class MultipleVocabularyField(Field):
    def __init__(self, typeName, value=None):
        if value is None:
            value = []
        super().__init__(typeName, value, True, 'controlledVocabulary')

    def add_value(self, value):
        if not isinstance(self.value, list):
            self.value = []
            self.value.append(value)

    def __repr__(self):
        return "{}: {}".format(
            self.typeName,
            "[" + str([v for v in self.value]) + "]")
        
class VocabularyField(Field):
    def __init__(self, typeName, value=None):
        if value is None:
            value = ''
        super().__init__(typeName, value, False, 'controlledVocabulary')

    def add_value(self, value):
        self.value = value
        
    def __repr__(self):
        return "{}: {}".format(
            self.typeName,
            self.value)


class MetadataBlock():
    def __init__(self, id, name, fields=None):
        if fields is None:
            fields = []
        self.id = id
        self.displayName = name
        self.mFields = fields

    def add_field(self, field):
        self.mFields.append(field)

    def __repr__(self):
        return str(self.displayName) + " " + str(self.mFields)


class EditFormat():
    def __init__(self, fields=None):
        if fields is None:
            fields = []
        self.mFields = fields

    def add_field(self, field):
        self.mFields.append(field)

    def __repr__(self):
        r = ''
        for field in self.mFields:
            r += '{} ({}, {}): {}'.format(
                field.get_typeName(),
                field.get_typeClass(),
                'm' if field.get_multiple() else 'nm',
                field.get_value())
        return "fields = [{}]".format(r)


class CreateDataset():
    def __init__(self, datasetVersion):
        self.datasetVersion = datasetVersion


class Dataset():
    def __init__(self, blocks=None):
        if blocks is None:
            blocks = []
        self.metadataBlocks = blocks

    def add_block(self, block):
        if isinstance(block, MetadataBlock):
            self.metadataBlocks.append(block)

    def __repr__(self):
        return "blocks: " + str(self.metadataBlocks)


class PrimitiveFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(False))
    typeClass = fields.Str(validate=Equal('primitive'))
    value = fields.Str()


class MultiplePrimitiveFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(True))
    typeClass = fields.Str(validate=Equal('primitive'))
    value = fields.List(fields.Str())


class VocabularyFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(False))
    typeClass = fields.Str(validate=Equal('controlledVocabulary'))
    value = fields.Str()


class MultipleVocabularyFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(True))
    typeClass = fields.Str(validate=Equal('controlledVocabulary'))
    value = fields.List(fields.Str())


class SimpleFieldScheme(OneOfSchema):
    type_field_remove = True
    type_schemas = {
        'PrimitiveField': PrimitiveFieldScheme,
        'VocabularyField': VocabularyFieldScheme
    }


class EditSimpleFieldScheme(OneOfSchema):
    type_field_remove = True
    type_schemas = {
        'PrimitiveField': PrimitiveFieldScheme(only=["typeName", "value"]),
        'VocabularyField': VocabularyFieldScheme(only=["typeName", "value"])
    }    

    
class CompoundFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(False))
    typeClass = fields.Str(validate=Equal('compound'))
    value = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(SimpleFieldScheme))

class EditCompoundFieldScheme(CompoundFieldScheme):
    value = fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(EditSimpleFieldScheme)
    )


class MultipleCompoundFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Boolean(validate=Equal(True))
    typeClass = fields.Str(validate=Equal('compound'))
    value = fields.List(fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(SimpleFieldScheme)))


class EditMultipleCompoundFieldScheme(MultipleCompoundFieldScheme):
    value = fields.List(fields.Dict(
        keys=fields.Str(),
        values=fields.Nested(EditSimpleFieldScheme)
    ))


class FieldSchema(OneOfSchema):
    type_field_remove = True
    type_schemas = {
        'PrimitiveField': PrimitiveFieldScheme,
        'CompoundField': CompoundFieldScheme,
        'MultiplePrimitiveField': MultiplePrimitiveFieldScheme,
        'MultipleCompoundField': MultipleCompoundFieldScheme,
        'VocabularyField': VocabularyFieldScheme,
        'MultipleVocabularyField': MultipleVocabularyFieldScheme
    }


class EditFieldSchema(OneOfSchema):
    type_field_remove = True
    type_schemas = {
        'PrimitiveField': PrimitiveFieldScheme(
            only=["typeName", "value"]),
        'CompoundField': EditCompoundFieldScheme(
            only=["typeName", "value"]),
        'MultiplePrimitiveField': MultiplePrimitiveFieldScheme(
            only=["typeName", "value"]),
        'MultipleCompoundField': EditMultipleCompoundFieldScheme(
            only=["typeName", "value"]),
        'VocabularyField': VocabularyFieldScheme(
            only=["typeName", "value"]),
        'MultipleVocabularyField': MultipleVocabularyFieldScheme(
            only=["typeName", "value"])
    }


class EditScheme(Schema):
    mFields = fields.List(
        fields.Nested(
            EditFieldSchema()
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
