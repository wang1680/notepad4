#!/usr/bin/env python3
import sys
import os.path
import re
import shutil
import uuid
import subprocess

app = os.path.basename(__file__)
localeDir = os.getcwd()
notepad4_src = os.path.abspath('../src/Notepad4.rc')
matepath_src = os.path.abspath('../matepath/src/matepath.rc')

def get_available_locales():
	result = []
	with os.scandir(localeDir) as it:
		for entry in it:
			if entry.is_dir() and entry.name[:2].islower():
				result.append(entry.name)

	result.sort()
	return result

def get_project_guid():
	return '{' + str(uuid.uuid4()).upper() + '}'

def patch_vc_project_file(path, src_lang, language):
	with open(path, encoding='utf-8', newline='\n') as fd:
		doc = fd.read()
	# change output folder
	doc = doc.replace(f'\\{src_lang}\\', f'\\{language}\\')

	# change project GUID
	guid = get_project_guid()
	doc = re.sub(r'(<ProjectGuid>)(.+)(</ProjectGuid>)', r'\1' + guid + r'\3', doc)

	with open(path, 'w', encoding='utf-8', newline='\n') as fd:
		fd.write(doc)

def update_resource_include_path(path, matepath):
	with open(path, encoding='utf-8', newline='\n') as fd:
		doc = fd.read()
	if matepath:
		# resource path
		doc = doc.replace(r'..\\res', r'..\\..\\matepath\\res')
		# include path
		doc = re.sub(r'^(#include\s+")(.+)(")', r'\1../../matepath/src/\2\3', doc, flags=re.MULTILINE)
	else:
		# resource path
		doc = doc.replace(r'..\\res', r'..\\..\\res')
		# include path
		doc = re.sub(r'^(#include\s+")(.+)(")', r'\1../../src/\2\3', doc, flags=re.MULTILINE)
		# string table for lexers and styles
		doc = re.sub(r'^//(#include\s+")(.+)(")', r'\1../../src/\2\3', doc, flags=re.MULTILINE)
		doc = re.sub(r'^#if\s+0\s*//\s*(NP2_ENABLE_LOCALIZE\w+)', r'#if \1', doc, flags=re.MULTILINE)

	doc = re.sub(r'^//(#if\s+!NP2_ENABLE_APP_LOCALIZATION_DLL)', r'\1', doc, flags=re.MULTILINE)
	doc = re.sub(r'^//(#endif\s*//\s*NP2_ENABLE_APP_LOCALIZATION_DLL)', r'\1', doc, flags=re.MULTILINE)
	with open(path, 'w', encoding='utf-8', newline='\n') as fd:
		fd.write(doc)

def make_new_localization(language):
	print(f'{app}: make new localization for {language}.')
	target = os.path.join(localeDir, language)
	if not os.path.exists(target):
		os.makedirs(target)

	matepath_dest = os.path.join(target, 'matepath.rc')
	notepad4_dest = os.path.join(target, 'Notepad4.rc')
	shutil.copyfile(matepath_src, matepath_dest)
	shutil.copyfile(notepad4_src, notepad4_dest)

	update_resource_include_path(matepath_dest, True)
	update_resource_include_path(notepad4_dest, False)

	src_lang = 'zh-Hans'
	src_folder = os.path.join(localeDir, src_lang)
	matepath_vcxproj_src = os.path.join(src_folder, f'matepath({src_lang}).vcxproj')
	notepad4_vcxproj_src = os.path.join(src_folder, f'Notepad4({src_lang}).vcxproj')
	matepath_vcxproj = os.path.join(target, f'matepath({language}).vcxproj')
	notepad4_vcxproj = os.path.join(target, f'Notepad4({language}).vcxproj')

	shutil.copyfile(matepath_vcxproj_src, matepath_vcxproj)
	shutil.copyfile(matepath_vcxproj_src + '.filters', matepath_vcxproj + '.filters')
	shutil.copyfile(notepad4_vcxproj_src, notepad4_vcxproj)
	shutil.copyfile(notepad4_vcxproj_src + '.filters', notepad4_vcxproj + '.filters')

	patch_vc_project_file(matepath_vcxproj, src_lang, language)
	patch_vc_project_file(notepad4_vcxproj, src_lang, language)

	matepath_dest = os.path.basename(matepath_dest)
	notepad4_dest = os.path.basename(notepad4_dest)
	matepath_vcxproj = os.path.basename(matepath_vcxproj)
	notepad4_vcxproj = os.path.basename(notepad4_vcxproj)
	print(f"""{app}: resources and projects added for {language}.
    Please manually update language tags in {matepath_dest} and {notepad4_dest},
    and open Locale.sln with Visual Studio to add project {matepath_vcxproj} and {notepad4_vcxproj}.""")


def restore_resource_include_path(path, matepath):
	with open(path, encoding='utf-8', newline='\n') as fd:
		doc = fd.read()
	if matepath:
		# include path
		doc = doc.replace('../../matepath/src/', '')
		# resource path
		doc = doc.replace(r'..\\matepath\\', '')
	else:
		# include path
		doc = doc.replace('../../src/', '')
		# resource path
		doc = doc.replace(r'..\\..\\res', r'..\\res')

	with open(path, 'w', encoding='utf-8', newline='\n') as fd:
		fd.write(doc)

def copy_back_localized_resources(language):
	print(f'{app}: copy back localized resources for {language}.')
	backupDir = os.path.join(localeDir, 'en')
	if os.path.exists(backupDir):
		if language != 'en':
			print(f"""{app}: please delete the backup folder {backupDir}
    on first run to ensure proper backup for English resources.""")
	else:
		os.makedirs(backupDir)
		shutil.copyfile(matepath_src, os.path.join(backupDir, 'matepath.rc'))
		shutil.copyfile(notepad4_src, os.path.join(backupDir, 'Notepad4.rc'))

	folder = os.path.join(localeDir, language)
	shutil.copyfile(os.path.join(folder, 'matepath.rc'), matepath_src)
	shutil.copyfile(os.path.join(folder, 'Notepad4.rc'), notepad4_src)

	restore_resource_include_path(matepath_src, True)
	restore_resource_include_path(notepad4_src, False)

	print(f"""{app}: resources for building standalone localized program for {language} are ready.
    you can copy English resources back by run: {app} back en""")


class StringExtractor:
	def reset(self, path, reversion):
		self.path = path
		self.reversion = reversion
		self.changed_lines = set()
		if reversion:
			self.find_changed_lines(reversion)
			if not self.changed_lines:
				return False

		with open(path, encoding='utf-8', newline='\n') as fd:
			doc = fd.read()
		self.lines = doc.splitlines()
		return len(self.lines)

	def find_changed_lines(self, reversion):
		cmd = ['git', 'diff', '--no-color', '--unified=0', '--text', reversion, self.path]
		result = subprocess.run(cmd, capture_output=True, check=True, encoding='utf-8')
		if result.stderr:
			print(result.stderr, file=sys.stderr)

		items = re.findall(r'^@@\s+\-\d+(,\d+)?\s+\+(\d+)(,\d+)?\s+@@', result.stdout, re.MULTILINE)
		if not items:
			return

		for item in items:
			_, line, count = item
			line = int(line)
			count = int(count[1:]) if count else 0
			if count:
				self.changed_lines.update(range(line, line + count))
			else:
				self.changed_lines.add(line)

		# reversion time
		cmd =['git', 'show', '--no-patch', '--no-notes', "--pretty='%ci'", reversion]
		result = subprocess.run(cmd, capture_output=True, check=True, encoding='utf-8')
		if result.stderr:
			print(result.stderr, file=sys.stderr)
		items = result.stdout.replace("'", '').split()[:2]
		self.reversion = f"{reversion} {' '.join(items)}".strip()

	def is_line_changed(self, start, end):
		if not self.changed_lines:
			return True

		while start <= end:
			if start in self.changed_lines:
				return True
			start += 1
		return False

	def match_line(self, line, word):
		if line.startswith(word):
			ch = ' ' if len(line) == len(word) else line[len(word)]
			return ch.isspace() or ch == '/'
		return False

	def scan_string(self, line, escape_sequence, format_specifier, access_key, start):
		index = 0
		if start:
			# identifier "string"
			index = line.find('"')
			if index <= 0:
				return '', 0, 0, False

		length = len(line)
		begin = index
		if start:
			index += 1
		stop = False

		while index < length:
			ch = line[index]
			index += 1
			if ch == '\\':
				ch = line[index] if index < length else ''
				end = index + 1
				if ch and ch in 'abfnrtvxu':
					if ch == 'x':
						end += 2
					elif ch == 'u':
						end += 4
					sequence = line[index - 1:end]
					escape_sequence.add(sequence)
				index = end
			elif ch == '&':
				ch = line[index]
				if ch == '&':
					index += 1
				elif not ch.isspace():
					access_key.append(ch.upper())
			elif ch == '%':
				ch = line[index]
				# we only use '%s' in resource files
				if ch == 's':
					format_specifier.add('%' + ch)
			elif ch == '"':
				if index < length and line[index] == ch:
					index += 1
				else:
					stop = True
					break

		value = line[begin:index]
		return value, begin, index, stop

	def build_hint(self, escape_sequence, format_specifier, access_key):
		hint = ''
		if access_key:
			hint += ', access key: ' + ', '.join(access_key)
		if escape_sequence:
			hint += ', escape sequence: ' + ', '.join(sorted(escape_sequence))
		if format_specifier:
			hint += ', format specifier: ' + ', '.join(sorted(format_specifier))
		return hint

	def parse_resource_item(self, lineno, line, block_items):
		if not self.is_line_changed(lineno, lineno):
			return None

		escape_sequence = set()
		format_specifier = set()
		access_key = []
		value, begin, index, _ = self.scan_string(line, escape_sequence, format_specifier, access_key, True)
		if not any(ch.isalpha() for ch in value):
			return None

		# type "string", id
		word = line[:begin].strip()
		if not word.isidentifier():
			return None

		rcid = ''
		begin = line.find(',', index)
		if begin > 0:
			index = line.find(',', begin + 1)
			if index > 0:
				rcid = line[begin + 1:index].strip()
			else:
				rcid = line[begin + 1:].strip()
			assert rcid.isidentifier()

		if word == 'CAPTION':
			return f'{word} {value}'
		if len(access_key) > 1:
			print(f'multiple access keys {lineno} {word} {rcid}', access_key)

		comment = f'// {lineno} {word} {rcid}'.strip()
		comment += self.build_hint(escape_sequence, format_specifier, access_key)
		block_items.append({
			'value': value,
			'comment': comment
		})
		return None

	def parse_string_table_item(self, lineno, line, block_items):
		# id "multiline string"
		escape_sequence = set()
		format_specifier = set()
		access_key = []
		value, begin, index, stop = self.scan_string(line, escape_sequence, format_specifier, access_key, True)

		rcid = line[:begin].strip()
		assert rcid.isidentifier()

		result = [value]
		start = lineno
		while not stop:
			line = self.lines[lineno]
			lineno += 1
			value, begin, index, stop = self.scan_string(line, escape_sequence, format_specifier, access_key, False)
			result.append(value)

		if not self.is_line_changed(start, lineno):
			return lineno

		value = '\n'.join(result)
		if not any(ch.isalpha() for ch in value):
			return lineno
		if len(access_key) > 1:
			print(f'multiple access keys {start} {rcid}', access_key)

		comment = f'// {start} {rcid}'
		comment += self.build_hint(escape_sequence, format_specifier, access_key)
		block_items.append({
			'value': value,
			'comment': comment
		})
		return lineno

	def extract(self, path, reversion, out_path=None):
		if not self.reset(path, reversion):
			return

		Block_None = 0
		Block_Menu = 1
		Block_DialogEx = 2
		Block_StringTable = 3
		Block_Ignore = 4

		block_type = Block_None
		block_name = ''
		block_caption = ''
		begin = 0
		block_begin = 0
		block_items = []

		lineno = 0
		line_count = len(self.lines)
		string_list = []

		while lineno < line_count:
			line = self.lines[lineno]
			line = line.strip()
			lineno += 1
			if not line or line.startswith('//') or line.startswith('#'):
				continue

			if block_type == Block_None:
				begin = 0
				if self.match_line(line, 'STRINGTABLE'):
					block_type = Block_StringTable
					block_name = 'STRINGTABLE'
				else:
					items = line.split()
					if len(items) >= 2:
						word = items[1]
						if word == 'MENU':
							block_type = Block_Menu
							block_name = ' '.join(items[:2])
						elif word == 'DIALOGEX':
							block_type = Block_DialogEx
							block_name = ' '.join(items[:2])
						elif word in ('ACCELERATORS', 'DESIGNINFO', 'TEXTINCLUDE'):
							block_type = Block_Ignore
				if block_type != Block_None:
					block_begin = lineno
					block_items = []
					block_caption = ''
			elif self.match_line(line, 'BEGIN'):
				begin += 1
			elif self.match_line(line, 'END'):
				begin -= 1
				if begin <= 0:
					block_type = Block_None
					if block_items:
						string_list.append({
							'name': block_name,
							'comment': f'// line {block_begin} - {lineno}',
							'caption': block_caption,
							'items': block_items
						})
						block_items = []
			elif block_type != Block_Ignore:
				try:
					if block_type in (Block_Menu, Block_DialogEx):
						caption = self.parse_resource_item(lineno, line, block_items)
						if caption:
							block_caption = caption
					elif block_type == Block_StringTable:
						lineno = self.parse_string_table_item(lineno, line, block_items)
				except Exception:
					print(f'parse {block_type} {block_name} fail at {lineno} for {self.path}')
					raise

		if string_list:
			self.save(string_list, out_path)

	def save(self, string_list, out_path=None):
		if not out_path:
			path, ext = os.path.splitext(self.path)
			out_path = path + '-string' + ext

		print('save:', out_path)
		with open(out_path, 'w', encoding='utf-8') as fd:
			fd.write("//! Ignore line starts with //, it's a comment line.\n")
			fd.write("//! Please don't translate escape sequence or format specifiers.\n")
			if self.reversion:
				fd.write("//! Updated strings since: " + self.reversion + '\n')
			fd.write('\n')

			for block in string_list:
				fd.write(block['comment'] + '\n')
				fd.write(block['name'] + '\n')
				caption = block['caption']
				if caption:
					fd.write(caption + '\n')

				fd.write('BEGIN' + '\n')
				for item in block['items']:
					fd.write('\t' + item['comment'] + '\n')
					fd.write('\t' + item['value'] + '\n')
				fd.write('END' + '\n\n')

def extract_resource_string(language, reversion):
	print(f'{app}: extract updated string for {language} since {reversion}.')

	extractor = StringExtractor()
	if language == 'en':
		extractor.extract(matepath_src, reversion)
		extractor.extract(notepad4_src, reversion)
	else:
		folder = os.path.join(localeDir, language)
		path = os.path.join(folder, 'matepath.rc')
		extractor.extract(path, reversion)
		path = os.path.join(folder, 'Notepad4.rc')
		extractor.extract(path, reversion)


def show_help():
	print(f"""Usage: {app} action language [reversion]
action:
    new     create a new localization for specific language.

    back    prepare building standalone localized program for specific language,
            copy back localized resources to overwrite English resources.
            English resources are copied into en folder when the folder does not exist.

    string  extract all resource string or updated strings since specific reversion.
""")

def main(argv):
	if len(argv) < 3:
		show_help()
		return

	action = argv[1]
	language = argv[2]
	availableLocales = get_available_locales()
	if action == 'new':
		if language in availableLocales:
			print(f'{app}: language {language} already localized.')
			return
		make_new_localization(language)
	elif action == 'back':
		if language not in availableLocales:
			print(f'{app}: language {language} not localized [{", ".join(availableLocales)}].')
			return
		copy_back_localized_resources(language)
	elif action == 'string':
		if language != 'en' and language not in availableLocales:
			print(f'{app}: language {language} not localized [{", ".join(availableLocales)}].')
			return
		reversion = argv[3] if len(argv) > 3 else ''
		extract_resource_string(language, reversion)
	else:
		show_help()

if __name__ == '__main__':
	main(sys.argv)
