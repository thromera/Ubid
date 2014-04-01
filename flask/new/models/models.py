from flask import abort, make_response

import modelmanager
import json
import copy
import glob

class Models(object):
	def __init__(self, json=None):
		self.__set_fields__(json)

	def new(self, attributes = None):
		# Attributes var is type of dict.
		if attributes is not None :
			for key in attributes:
				if self.verify_errors(key, attributes[key]) >= 0:
					setattr(self, key, attributes[key])

		setattr(self, "id", modelmanager.model_size(self.__class__.__name__))
		return self

	def save(self):
		modelmanager.save(self)

	def __set_fields__(self, json=None):
		if json is not None:
			for j in json:
				setattr(self, j, json[j])
		else:
			for field in self.fields:
				setattr(self, field, '') # Set the  fields to default value
			if hasattr(self, 'unique'):
				for uniq in self.unique: # Set the Unique field to default value
					setattr(self, uniq, '')
			if hasattr(self, 'mandatory'):
				for mandatory in self.mandatory: # Set the Unique field to default value
					if mandatory != 'password':
						setattr(self, mandatory, '')
			if hasattr(self, 'intern_fields'):
				for intern_field in self.intern_fields: # Set the Unique field to default value
					setattr(self, intern_field, '')
		return self

	def verify_errors(self, key, value):
		status = self._attribute_exist_(key)
		if status == 1: #Normal field
			return 0
		elif status == 2: # Unique (Is also mandatory)
			if value is '' or value is None or len(value) == 0:
				abort(make_response('Mandatory field : ' + key, 400))
			if  glob.Models().getBy(self.__class__.__name__, key, value) is not None:
				abort(make_response(key + ' Already taken.', 400))
		elif status == 3 : # Mandatory field
			if value is '' or value is None or len(value) == 0:
				abort(make_response('Mandatory field : ' + key, 400))
		return 0

	def _attribute_exist_(self, attribute):
		if hasattr(self, 'fields') and attribute in self.fields:
			return 1
		elif hasattr(self, 'unique') and attribute in self.unique:
			return 2
		elif hasattr(self, 'mandatory') and attribute in self.mandatory:
			return 3
		else:
			abort(make_response('Forbiden field : ' + attribute, 400))

	def _verify_mandatory_fields(self):
		if hasattr(self, 'mandatory'):
			for mandatory in self.mandatory:
				value = eval('self.' + mandatory)
				if  value is  None or value is '' or len(value) is 0:
					abort(make_response('Mandatory field : ' + mandatory, 400))
		return 0

	def _to_json(self):
		to_remove = ['fields', 'unique', 'mandatory', 'intern_fields']
		obj_copy = copy.deepcopy(self) #We dont want to work directly on the object, but rather on a copy of it
		for remove in to_remove:
			if hasattr(obj_copy, remove):
				delattr(obj_copy, remove)

		js = json.loads(json.dumps(obj_copy.__dict__))
		return js