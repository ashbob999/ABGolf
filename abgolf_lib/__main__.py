import argparse
import sys
from os.path import isfile
from timeit import default_timer

from .compiler import compile_program, run
from .parser import parse, Parse_Result_Type
from .utils import to_unicode_str

if __name__ == "__main__":
	arg_handler = argparse.ArgumentParser(description="Run ABGolf")

	arg_handler.add_argument("-p", "--print", action="store_true",
	                         help="Prints the source code, using unicode characters.")

	arg_handler.add_argument("-c", "--check", action="store_true",
	                         help="Checks whether the source code is valid.")

	arg_handler.add_argument("--save", action="store", type=str,
	                         help="The path of the file to save the parsed program to.\n Will Overwrite any existing file")

	arg_handler.add_argument("--load", action="store", type=str,
	                         help="The path of the file to load the parsed program.")

	arg_handler.add_argument("-s", "--source", action="store", type=str, required=True,
	                         help="The path of the source file.")

	arg_handler.add_argument("-o", "--output", action="store", default=None, type=str,
	                         help="The path of the output file.")

	arg_handler.add_argument("-i", "--input", action="store", type=str,
	                         help="The path of the input file.")

	arg_handler.add_argument("-m", "--measured", action="store_true",
	                         help="Should execution time be measured.")

	args = arg_handler.parse_args()

	if not isfile(args.source):
		pass  # source file does not exist
		sys.exit(1)

	if args.print:
		print("Program as unicode characters:")
		text = to_unicode_str(args.source)
		if text:  # is text not null
			print(text)
	else:

		# set the name of the default output file to the same name as the source file
		if args.output is None:
			index = args.source.rfind(".")
			if index >= 0:
				args.output = args.source[:index]
			else:
				args.output = args.source

			# add a .py file extension to the output file path
			args.output += ".py"

		# start measuring the parse time
		parse_start_time = default_timer()

		# parse the program
		if args.load:  # load the parsed program from file
			if isfile(args.load):
				parsed, result = None, None
			# TODO: Load parsed program from json
			else:  # load file does not exist
				pass
				sys.exit(1)
		else:
			# parse the program from source
			parsed, result = parse(source_path=args.source)

		# stop measuring the parse time
		parse_end_time = default_timer()

		# did parsing fail
		if result.result_type != Parse_Result_Type.SUCCESS:  # the program failed to parse
			print(result)
			sys.exit(1)
		else:
			# are we just checking if the program will parse
			if args.check:
				print(result)  # the program was parsed successfully
				sys.exit(0)

			# save the parsed program to a file
			if args.save:
				# convert the parsed program to json
				# save the json to a file
				# TODO: Save parsed program to json.
				pass

			if not isfile(args.input):
				pass  # the input file does not exist
				sys.exit(1)

			# start measuring compile time
			compile_start_time = default_timer()

			# compile to program
			compile_program(parsed_program=parsed, output_path=args.output)

			# stop measuring compile time
			compile_end_time = default_timer()

			# output file should always exist?
			# if not isfile(args.output):
			# 	pass  # the output file does not exist
			# 	sys.exit(1)

			# start measuring run time
			run_start_time = default_timer()

			# run the program
			run(output=args.output)

			# stop measuring run time
			run_end_time = default_timer()

			# TODO: Check measure flag, and output run times.
			pass  # because formatter puts above line on previous indent
