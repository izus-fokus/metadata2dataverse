from datetime import date
from marshmallow import Schema, fields, pprint
from marshmallow_oneofschema import OneOfSchema

class DatasetSchema(Schema):
    metadataBlocks = fields.List(fields.Nested(MetadataBlockSchema))

class MetadataBlockSchema(Schema):
    id = fields.Str()
    displayName = fields.Str()
    mFields = fields.List(fields.Nested(FieldsScheme))

class FieldsScheme(OneOfSchema):
    type_schemas('primitiveField': primitiveFieldScheme,
                 'compoundField': compoundFieldScheme,
                 'multipleField': multipleFieldScheme)

class SimpleFieldSchema(OneOfSchema):
    type_schemas('primitiveField': primitiveFieldScheme,
                 'compoundField': compoundFieldScheme)

class primitiveFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = False
    typeClass = 'primitive'
    value = fields.Str()

class multipleFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = True
    typeClass = fields.Str(default='primitive', validate=OneOf(['primitive', 'compound']))
    value = fields.List(fields.Nested(SimpleFieldSchema))


class compoundFieldScheme(Schema):
    typeName = fields.Str(required=True)
    multiple = fields.Bool()
    typeClass = fields.Str(default='primitive', validate=OneOf(['primitive', 'compound']))
    value = fields.Nested(field.List(primitiveFieldScheme))