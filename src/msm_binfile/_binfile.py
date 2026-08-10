from os import PathLike, path
from struct import pack, unpack
from typing import Any, IO, Self
import os

__all__: list[str] = ['BinFile']


class BinFile:
	__CHUNK_SIZE: int = 4

	def __init__(self, filename: PathLike | str, mode: str = 'rb') -> None:
		if 'b' not in mode:
			mode += 'b'

		self.__fp: IO = open(filename, mode)
		self.__filename: PathLike | str = path.split(filename)[1]

	def __enter__(self) -> Self:
		return self

	def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
		self.close()

	def __string_align(self, string: str) -> int:
		return self.seek(self.__CHUNK_SIZE - (len(string) % self.__CHUNK_SIZE), os.SEEK_CUR)

	def __align(self, size: int) -> int:
		offset: int = self.tell() % size

		return self.__fp.seek(size - offset if offset != 0 else 0, os.SEEK_CUR)

	def close(self) -> None:
		self.__fp.close()

	def tell(self) -> int:
		return self.__fp.tell()

	def seek(self, offset: int, whence: int = 0) -> int:
		return self.__fp.seek(offset, whence)

	def read(self, size: int, align: bool) -> bytes:
		if align:
			self.__align(size)

		return self.__fp.read(size)

	def write(self, data: bytes, align: bool) -> int:
		if not self.__fp.writable():
			raise IOError(f'{self.__filename} is not writable')

		if align:
			self.__align(len(data))

		return self.__fp.write(data)

	def read_uint8(self, align: bool = True) -> int:
		return unpack('B', self.read(1, align))[0]

	def read_uint16(self, align: bool = True) -> int:
		return unpack('H', self.read(2, align))[0]

	def read_uint32(self, align: bool = True) -> int:
		return unpack('I', self.read(4, align))[0]

	def read_int8(self, align: bool = True) -> int:
		return unpack('b', self.read(1, align))[0]

	def read_int16(self, align: bool = True) -> int:
		return unpack('h', self.read(2, align))[0]

	def read_int32(self, align: bool = True) -> int:
		return unpack('i', self.read(4, align))[0]

	def read_float(self, align: bool = True) -> float:
		return unpack('f', self.read(4, align))[0]

	def read_string(self) -> str:
		string_len: int = self.read_uint32() - 1
		string: str = self.read(string_len, False).decode('ascii')
		self.__string_align(string)
		return string

	def write_uint8(self, val: int, align: bool = True) -> int:
		return self.write(pack('B', val), align)

	def write_uint16(self, val: int, align: bool = True) -> int:
		return self.write(pack('H', val), align)

	def write_uint32(self, val: int, align: bool = True) -> int:
		return self.write(pack('I', val), align)

	def write_int8(self, val: int, align: bool = True) -> int:
		return self.write(pack('b', val), align)

	def write_int16(self, val: int, align: bool = True) -> int:
		return self.write(pack('h', val), align)

	def write_int32(self, val: int, align: bool = True) -> int:
		return self.write(pack('i', val), align)

	def write_float(self, val: float, align: bool = True) -> int:
		return self.write(pack('f', val), align)

	def write_string(self, val: str) -> int:
		self.write_uint32(len(val) + 1)
		written: int = self.write(val.encode('ascii'), False)
		self.__string_align(val)
		return written
