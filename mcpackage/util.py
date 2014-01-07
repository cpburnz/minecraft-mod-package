# coding: utf-8
"""
This module contains utility functions.
"""
from __future__ import unicode_literals

import errno
import functools
import itertools
import io
import os
import os.path
import shutil
import textwrap

import yaml
import yaml.scanner

def get_line(file, line): # pylint: disable=W0622
	"""
	Gets the specified line from the file.

	*file* is either the ``file`` to read, or the path (``str``) of the
	file to read.

	*line* (``int``) is the line offset to get.

	Returns the line (``str``).
	"""
	if callable(getattr(file, 'read', None)):
		fh = file
		close = False
	else:
		fh = open(file, 'rb')
		close = True
	try:
		text = next(itertools.islice(fh, line, None))
	finally:
		if close:
			fh.close()
	return text

def get_nested_value(data, keys):
	"""
	Gets the nested value.

	*data* (``dict``) is the data structure.

	*keys* (``Sequence``) contains each key (``str``) in *data* to
	traverse.

	Returns the nested value (``object``).
	"""
	return functools.reduce(dict.get, keys, data)

def load_config(file): # pylint: disable=W0622
	"""
	Loads the configuration.

	*file* is either the ``file`` to read, or hte path (``str``) of the
	file to read.

	Returns the configuration (``dict``).
	"""
	if callable(getattr(file, 'read', None)):
		fh = file
		close = False
	else:
		fh = io.open(file, mode='r', encoding='UTF-8')
		close = True
	try:
		config = yaml.safe_load(fh)
	except yaml.scanner.ScannerError as e:
		context = (e.context or '').lower()
		problem = (e.problem or '').lower()
		if context == 'while scanning for the next token' and problem == 'found character {!r} that cannot start any token'.format('\t'):
			# Give a friendly message if a tab is mistakenly used for
			# indentation.
			fh.seek(0, os.SEEK_SET)
			mark = e.problem_mark
			e.note = "\n{info}\n\n{source}\n{here}\n{hint}".format(
				info=textwrap.fill(textwrap.dedent("""
					Found TAB character being used for indentation in {name!r}
					on line {line}, column {column}:
				""".format(
					name=mark.name,
					line=mark.line + 1,
					column=mark.column + 1,
				))).strip(),
				source=get_line(fh, mark.line).rstrip(),
				here=' ' * mark.column + '^',
				hint=textwrap.fill(textwrap.dedent("""
					Use spaces for indentation instead.
				""")).strip()
			)
		raise
	finally:
		if close:
			fh.close()
	return config

def merge_config(base, update):
	"""
	Merges two configurations recursively.

	*base* (``dict``) is the base config to update.

	*update* (``dict``) is the config to merge into *base*.

	Returns the merged configuration (``dict``).
	"""
	merge = base.copy()
	for key, update_value in update.items():
		if key in base:
			if update_value is not None:
				base_value = base[key]
				if isinstance(base_value, dict):
					merge[key] = merge_config(base_value, update_value)
				else:
					merge[key] = update_value
		else:
			merge[key] = update_value
	return merge

def set_nested_value(data, keys, value):
	"""
	Sets the nested value.

	*data* (``dict``) is the data structure.

	*keys* (``Sequence``) contains each key (``str``) in *data* to
	traverse.

	*value* (``object``) is the value to set.
	"""
	sub = functools.reduce(dict.get, keys[:-1], data)
	sub[keys[-1]] = value

def short_path(path, root):
	"""
	Returns the relative path from the specified root, but including the
	tail of the root.

	*path* (``str``) is the path to determine the relative path to.

	*root* (``str``) is the root path.

	Returns the short path (``str``)
	"""
	return os.path.join(os.path.basename(root), os.path.relpath(path, root))

def sync_files(src, dest, files=None, keep=None):
	"""
	Synchronizes the files from the source directory to the destination
	directory.

	*src* (``str``) is the path to the source directory.

	*dest* (``str``) is the path to the destination directory.

	*files* (``Iterable`` of ``str``) optionally contains the relative
	paths to the files to sync. Default is ``None`` for all files under
	*src*.

	*keep* (``Iterable`` of ``str``) optionally contains the relative
	paths to files to keep (or ignore) in the destination directory.
	Default is ``None`` to keep no destination files.
	"""
	src_dir = os.path.abspath(src)
	dest_dir = os.path.abspath(dest)

	keep_dirs = set() # Relative directory paths to keep.
	keep_files = set()
	if keep is not None:
		for file_path in keep:
			# Record parent directories.
			dir_path = os.path.dirname(file_path)
			while dir_path:
				keep_dirs.add(dir_path)
				dir_path = os.path.dirname(dir_path)

			# Record keep file.
			keep_files.add(file_path)

	src_dirs = set() # Relative directory paths to sync.
	src_files = {} # Maps each relative file path to source modified time.
	if files is not None:
		# Get file modified times.
		file_path = None
		for file_path in files:
			# Record parent directories.
			dir_path = os.path.dirname(file_path)
			while dir_path:
				src_dirs.add(dir_path)
				dir_path = os.path.dirname(dir_path)

			# Record source file with modified time.
			src_files[file_path] = os.path.getmtime(os.path.join(src_dir, file_path))

	else:
		# Traverse source directory, find files, and record modified times.
		encountered = {} # Map real path to relative path to detect recursion.
		for parent, dirs, files in os.walk(src_dir, followlinks=True):
			# Make parent path relative to source directory.
			parent = os.path.relpath(parent, src_dir)

			# Check for recursion.
			real = os.path.realpath(parent)
			if real in encountered:
				raise Exception("Real path {real!r} was encountered at {first!r} and then {second!r}.".format(
					real=real,
					first=os.path.join(src_dir, encountered[real]),
					second=os.path.join(src_dir, parent),
				))
			encountered[real] = parent

			# Record source directories.
			if parent != '.':
				src_dirs.update(os.path.join(parent, dir_name) for dir_name in dirs)
			else:
				src_dirs.update(dirs)

			# Record source files with modified times.
			if parent != '.':
				src_files.update((
					os.path.join(parent, file_name),
					os.path.getmtime(os.path.join(src_dir, parent, file_name)),
				) for file_name in files)
			else:
				src_files.update((
					file_name,
					os.path.getmtime(os.path.join(src_dir, file_name))
				) for file_name in files)

	# Traverse destination directory, update modified files, and delete
	# unneeded files.
	for parent, dirs, files in os.walk(dest_dir):
		# Make parent path relative to destination directory.
		parent = os.path.relpath(parent, dest_dir)

		# Check for unneeded directories.
		for i, dir_name in reversed(list(enumerate(dirs))):
			dir_path = os.path.join(parent, dir_name) if parent != '.' else dir_name
			if dir_path not in src_dirs and dir_path not in keep_dirs:
				# Delete unneeded directory.
				dir_full = os.path.join(dest_dir, dir_path)
				shutil.rmtree(dir_full)
				del dirs[i]

		# Check if files are needed and modified times.
		for file_name in files:
			file_path = os.path.join(parent, file_name) if parent != '.' else file_name
			dest_full = os.path.join(dest_dir, file_path)
			if file_path in src_files:
				if os.path.getmtime(dest_full) < src_files[file_path]:
					# Source file has been modified, copy it.
					src_full = os.path.join(src_dir, file_path)
					shutil.copy2(src_full, dest_full)
				# Record that this file was handled.
				del src_files[file_path]
			elif file_path not in keep_files:
				# Delete unneeded file.
				os.remove(dest_full)

	# Copy remaining files which were not handled.
	for file_path in src_files:
		dest_full = os.path.join(dest_dir, file_path)
		src_full = os.path.join(src_dir, file_path)

		# Make sure destination directory exists.
		try:
			os.makedirs(os.path.dirname(dest_full))
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise

		# Copy source file to destination.
		shutil.copy2(src_full, dest_full)
