import json
from dataclasses import dataclass
from enum import auto, IntEnum
from typing import List, Dict, Any, Optional

type_map: Dict[str, Any] = {
	str.__name__: str,
	int.__name__: int,
	float.__name__: float
}


class Dimension(IntEnum):
	ANY = auto()  # can use any dimension
	SPECIFIC = auto()  # can only use specific dimensions
	INCREASE = auto()  # increases the dimension
	DECREASE = auto()  # decreases the dimension


@dataclass
class Function:
	name: str
	code: int
	param_count: int
	dimension_type: Dimension = None
	# only used is dimension_type == SPECIFIC
	input_dimensions: Optional[List[int]] = None
	# only used is dimension_type == SPECIFIC
	output_dimensions: Optional[List[int]] = None
	input_types: Optional[List[Any]] = None
	output_types: Optional[List[Any]] = None

	@property
	def input_type_names(self) -> Optional[List[Any]]:
		if self.input_types is not None:
			return [e.__name__ for e in self.input_types]
		return None

	@property
	def output_type_names(self) -> Optional[List[Any]]:
		if self.output_types is not None:
			return [e.__name__ for e in self.output_types]
		return None

	def to_JSON(self):
		class_dict: Dict[str, Any] = {}

		class_dict["name"] = self.name
		class_dict["code"] = self.code
		class_dict["param_count"] = self.param_count
		class_dict["dimension_type"] = self.dimension_type
		class_dict["input_dimensions"] = self.input_dimensions
		class_dict["output_dimensions"] = self.output_dimensions
		class_dict["input_types"] = self.input_type_names
		class_dict["output_types"] = self.output_type_names

		return json.dumps(class_dict)

	@classmethod
	def from_JSON(cls, data):
		class_dict = json.loads(data)

		function = cls(name=class_dict["name"],
		               code=class_dict["code"],
		               param_count=class_dict["param_count"],
		               dimension_type=Dimension(class_dict["dimension_type"]))

		function.input_dimensions = class_dict["input_dimensions"]
		function.output_dimensions = class_dict["output_dimensions"]

		if class_dict["input_types"] is not None:
			function.input_types = []
			for t in class_dict["input_types"]:
				if t in type_map:
					function.input_types.append(type_map[t])
				else:
					print("cannot get object from str")

		if class_dict["output_types"] is not None:
			function.output_types = []
			for t in class_dict["output_types"]:
				if t in type_map:
					function.output_types.append(type_map[t])
				else:
					print("cannot get object from str")

		return function


# list of supported functions
supported_functions: Dict[int, Function] = {}

# functions for test purposes only
supported_functions[0x50] = Function(
	"pass",
	0x50,
	0,
	Dimension.ANY
)

supported_functions[0x51] = Function(
	"params",
	0x51,
	1,
	Dimension.ANY
)

supported_functions[0x52] = Function(
	"dims",
	0x52,
	0,
	Dimension.SPECIFIC,
	input_dimensions=[0]
)

supported_functions[0x53] = Function(
	"types",
	0x53,
	0,
	Dimension.ANY,
	input_types=[str]
)
