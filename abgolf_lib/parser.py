import json
from enum import Enum, auto
from typing import Tuple, List, Optional, Any, Dict

from .functions import Function, supported_functions, Dimension
from .utils import cp437_to_unicode


class Parsed:
	def __init__(self, program_bytes: List[int]):
		self.bytes: List[int] = program_bytes

		self.program: List[Optional[Function]] = [None]
		self.params: List[List[int]] = [[0]]
		self.dimensions: List[int] = [0]
		self.types: List[Any] = [str]

	@property
	def to_type_names(self):
		if self.types is not None:
			new_types: List[Optional[str]] = []
			for e in self.types:
				if e is not None:
					new_types.append(e.__name__)
				else:
					new_types.append(e)
		else:
			return self.types

	def to_JSON(self):
		class_dict: Dict[str, Any] = {}

		class_dict["bytes"] = self.bytes
		class_dict["program"] = []
		for f in self.program:
			if isinstance(f, Function):
				class_dict["program"].append(f.to_JSON())
			else:
				class_dict["program"].append(f)
		class_dict["params"] = self.params
		class_dict["dimensions"] = self.dimensions
		class_dict["types"] = self.to_type_names

		return json.dumps(class_dict)

	@classmethod
	def from_JSON(cls, data: str):
		class_dict = json.loads(data)

		parsed = cls(class_dict["bytes"])

		parsed.program = []
		for f in class_dict["program"]:
			if f is not None:
				parsed.program.append(Function.from_JSON(f))
			else:
				parsed.program.append(f)

		parsed.params = class_dict["params"]
		parsed.dimensions = class_dict["dimensions"]
		parsed.types = class_dict["types"]

		return parsed


class Parse_Result_Type(Enum):
	PARSING = auto()
	SUCCESS = auto()
	INVALID_FUNCTION = auto()
	OUT_OF_BYTES = auto()
	INVALID_DIMENSION = auto()
	INVALID_TYPE = auto()


class Parse_Result:
	def __init__(self, result_type: Parse_Result_Type) -> None:
		self.result_type: Parse_Result_Type = result_type
		self.byte_number: Optional[int] = None
		self.current_function: Optional[Function] = None
		self.data: List[int] = []
		self.info: Dict[str, Any] = {}

	def __str__(self):
		output: str = ""
		if self.result_type == Parse_Result_Type.PARSING:
			output += "The Program is still being Parsed"
		elif self.result_type == Parse_Result_Type.SUCCESS:
			output += "The Program was Parsed Successfully."
		elif self.result_type == Parse_Result_Type.INVALID_FUNCTION:
			output += "The Function %s (%s) is Invalid at byte %i." % (
				hex(self.data[self.byte_number]),
				cp437_to_unicode(self.data[self.byte_number]),
				self.byte_number)
		elif self.result_type == Parse_Result_Type.OUT_OF_BYTES:
			output += "Function %s (%s) requires %i bytes, but %i were given." % (
				hex(self.current_function.code),
				cp437_to_unicode(self.current_function.code),
				self.current_function.param_count,
				self.info["given"])
		elif self.result_type == Parse_Result_Type.INVALID_DIMENSION:
			output += "Invalid Dimension %s" % (self.info["input"] or "Any")
			output += "\nFor Function %s (%s) at byte %i" % (
				hex(self.current_function.code),
				cp437_to_unicode(self.current_function.code),
				self.byte_number)
			output += "\nWhich can only take Dimensions: %s" % (self.current_function.input_dimensions or "Any")
		elif self.result_type == Parse_Result_Type.INVALID_TYPE:
			output += "Invalid Type %s" % (self.info["input"].__name__ or "Any")
			output += "\nFor Function %s (%s) at byte %i" % (
				hex(self.current_function.code),
				cp437_to_unicode(self.current_function.code),
				self.byte_number)
			output += "\nWhich can only take Types: %s" % (self.current_function.input_type_names or "Any")

		return output


def parse(source_path: str) -> Tuple[Parsed, Parse_Result]:
	# read the bytes from the source file
	program_bytes: List[int] = []
	with open(source_path, "rb") as file:
		byte = file.read(1)
		while byte:
			program_bytes.append(int(byte.hex(), 16))
			byte = file.read(1)

	parsed = Parsed(program_bytes)
	parsed_result = Parse_Result(Parse_Result_Type.PARSING)
	parsed_result.data = program_bytes

	# parse the bytes
	pc = 0
	while pc < len(program_bytes):
		if program_bytes[pc] in supported_functions:  # function is supported
			# add the function to the program
			parsed.program.append(supported_functions[program_bytes[pc]])

			pc += 1  # increment pc by 1

			# get the amount of params
			param_count = parsed.program[-1].param_count

			# check there is enough bytes left for params
			if pc + param_count <= len(program_bytes):
				# add the params
				parsed.params.append(program_bytes[pc:pc + param_count])

				pc += param_count  # increment pc to next function
			else:  # out of bytes
				pc -= 1  # revert pc to point to current function
				parsed_result.result_type = Parse_Result_Type.OUT_OF_BYTES
				parsed_result.byte_number = pc
				parsed_result.current_function = supported_functions[program_bytes[pc]]
				parsed_result.info["given"] = len(program_bytes) - pc - 1
				return parsed, parsed_result

		else:  # function is not supported
			parsed_result.result_type = Parse_Result_Type.INVALID_FUNCTION
			parsed_result.byte_number = pc
			return parsed, parsed_result

	# parse the functions, checking dimensions and types
	if len(parsed.program) > 1:
		for i, f in enumerate(parsed.program):
			if i == 0:  # ignore first program (it it the input)
				continue

			# check dimension
			if f.dimension_type == Dimension.SPECIFIC and parsed.dimensions[
				i - 1] not in f.input_dimensions:  # invalid dimension
				parsed_result.result_type = Parse_Result_Type.INVALID_DIMENSION
				parsed_result.byte_number = i + 1
				parsed_result.current_function = f
				parsed_result.info["input"] = parsed.dimensions[i - 1]
				return parsed, parsed_result

			else:  # valid dimension
				if f.dimension_type == Dimension.ANY:  # any dimension
					parsed.dimensions.append(parsed.dimensions[i - 1])

				elif f.dimension_type == Dimension.SPECIFIC:  # one of X dimensions
					parsed.dimensions.append(parsed.dimensions[i - 1])

				elif f.dimension_type == Dimension.INCREASE:  # increase the dimension
					parsed.dimensions.append(parsed.dimensions[i - 1] + 1)

				elif f.dimension_type == Dimension.DECREASE:  # decrease the dimension
					parsed.dimensions.append(parsed.dimensions[i - 1] - 1)

			# check types
			if f.input_types is None or parsed.types[i - 1] in f.input_types:  # valid type
				if f.output_types is None:  # output any type
					# copy the previous type
					parsed.types.append(parsed.types[i - 1])

				elif isinstance(f.output_types, list):  # one of X types
					parsed.types.append(parsed.types[i - 1])

				else:  # one type
					parsed.types.append(f.input_types)

			else:  # invalid types
				parsed_result.result_type = Parse_Result_Type.INVALID_TYPE
				parsed_result.byte_number = i + 1
				parsed_result.current_function = f
				parsed_result.info["input"] = parsed.types[i - 1]
				return parsed, parsed_result

	parsed_result.result_type = Parse_Result_Type.SUCCESS

	return parsed, parsed_result
