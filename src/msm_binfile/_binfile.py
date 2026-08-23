from os import PathLike, path
from struct import pack, unpack
from typing import TYPE_CHECKING, Any, IO, Self, TypeVar
import os

if TYPE_CHECKING:
	from ._binserialisable import BinSerializable

__all__: list[str] = ['BinFile']


T = TypeVar('T', bound=BinSerializable)
class BinFile:
	__CHUNK_SIZE: int = 4

	def __init__(self, filename: PathLike[str], mode: str = 'rb') -> None:
		if 'b' not in mode:
			mode += 'b'

		filename = os.fspath(filename)
		self.__fp: IO[bytes] = open(filename, mode)
		self.__filename: str = path.basename(filename)

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
		return unpack('<B', self.read(1, align))[0]

	def read_uint16(self, align: bool = True) -> int:
		return unpack('<H', self.read(2, align))[0]

	def read_uint32(self, align: bool = True) -> int:
		return unpack('<I', self.read(4, align))[0]

	def read_uint64(self, align: bool = True) -> int:
		return unpack('<Q', self.read(8, align))[0]

	def read_int8(self, align: bool = True) -> int:
		return unpack('<b', self.read(1, align))[0]

	def read_int16(self, align: bool = True) -> int:
		return unpack('<h', self.read(2, align))[0]

	def read_int32(self, align: bool = True) -> int:
		return unpack('<i', self.read(4, align))[0]

	def read_int64(self, align: bool = True) -> int:
		return unpack('<q', self.read(8, align))[0]

	def read_float(self, align: bool = True) -> float:
		return unpack('<f', self.read(4, align))[0]

	def read_double(self, align: bool = True) -> float:
		return unpack('<d', self.read(8, align))[0]

	def read_string(self) -> str:
		string_len: int = self.read_uint32() - 1

		if string_len < 0:
			raise ValueError(f'{self.__filename} has an invalid string length at 0x{self.tell()-4:x}')

		string: str = self.read(string_len, False).decode('ascii')
		self.__string_align(string)
		return string

	def read_serializable(self, cls: type[T]) -> T:
		return cls.read(self)

	def write_uint8(self, val: int, align: bool = True) -> int:
		return self.write(pack('<B', val), align)

	def write_uint16(self, val: int, align: bool = True) -> int:
		return self.write(pack('<H', val), align)

	def write_uint32(self, val: int, align: bool = True) -> int:
		return self.write(pack('<I', val), align)

	def write_uint64(self, val: int, align: bool = True) -> int:
		return self.write(pack('<Q', val), align)

	def write_int8(self, val: int, align: bool = True) -> int:
		return self.write(pack('<b', val), align)

	def write_int16(self, val: int, align: bool = True) -> int:
		return self.write(pack('<h', val), align)

	def write_int32(self, val: int, align: bool = True) -> int:
		return self.write(pack('<i', val), align)

	def write_int64(self, val: int, align: bool = True) -> int:
		return self.write(pack('<q', val), align)

	def write_float(self, val: float, align: bool = True) -> int:
		return self.write(pack('<f', val), align)

	def write_double(self, val: float, align: bool = True) -> int:
		return self.write(pack('<d', val), align)

	def write_string(self, val: str) -> int:
		self.write_uint32(len(val) + 1)
		written: int = self.write(val.encode('ascii'), False)
		self.__string_align(val)
		return written

	def write_serializable(self, serializable: T) -> None:
		serializable.write(self)
