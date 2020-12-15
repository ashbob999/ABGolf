import codecs


def get_time_diff(start, end) -> str:
	diff = end - start

	# convert s to ns
	diff *= 1e9

	print(str(diff))
	# seconds
	if diff > 1e9:
		return str(round(diff / 1e9, 2)) + "s"
	elif diff > 1e6:
		return str(int(round(diff / 1e6, 0))) + "ms"
	elif diff > 1e3:
		return str(int(round(diff / 1e3, 0))) + "us"
	else:
		return str(int(round(diff, 0))) + "ns"


def test():
	import timeit

	s = timeit.default_timer()

	a = 0
	for i in range(int(1e6)):
		a += i

	e = timeit.default_timer()

	print(get_time_diff(s, e))


def to_unicode_str(source_path: str) -> str:
	with codecs.open(source_path, "rb", "cp437") as file:
		return file.read()


def cp437_to_unicode(value) -> str:
	if isinstance(value, list):
		return codecs.decode(bytes(value), "cp437")
	elif isinstance(value, int):
		return codecs.decode(bytes([value]), "cp437")
	else:
		return ""
