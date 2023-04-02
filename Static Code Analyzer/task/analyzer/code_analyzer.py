from collections import defaultdict
import re
import argparse
import os
import ast


errors = defaultdict(lambda: defaultdict(list))
err_S001 = "S001 Too long"
err_S002 = "S002 Indentation is not a multiple of four"
err_S003 = "S003 Unnecessary semicolon"
err_S004 = "S004 At least two spaces required before inline comments"
err_S005 = "S005 TODO found"
err_S006 = "S006 More than two blank lines used before this line"
err_S007 = "S007 Too many spaces after 'class'"
# err_S008 = ""
# err_S009 = ""
err_S010 = "S010 Argument name should be written in snake_case"
err_S011 = "S011 Variable should be written in snake_case"
err_S012 = "S012 The default argument value is mutable"

parser = argparse.ArgumentParser()
parser.add_argument('path', help='input the file path')
args = parser.parse_args()


def len_check(path, index, line):
    if len(line) > 79:
        process_dict(path, index, err_S001)


def indentation_check(path, index, line):
    if line.strip():
        if (len(line) - len(line.lstrip())) % 4 != 0:
            process_dict(path, index, err_S002)


def semicolon_check(path, index, line):
    if not re.search(r'#', line) and line.rstrip().endswith(';'):
        process_dict(path, index, err_S003)
    elif re.search(r"#", line):
        substring = line.split("#")[0].rstrip()
        if substring.endswith(';'):
            process_dict(path, index, err_S003)


def comments_spaces_check(path, index, line):
    if re.search(r"#", line) and not line.startswith('#'):
        substring = line.split("#")[0]
        if not substring.endswith("  "):
            process_dict(path, index, err_S004)


def todo_check(path, index, line):
    if re.search('#', line):
        substring = line.split("#")[1]
        if re.search('todo', substring, re.I):
            process_dict(path, index, err_S005)


def blank_line_check(path, index, line, blank_lines):
    if not line.strip():
        blank_lines += 1
    elif line.strip():
        if blank_lines > 2:
            process_dict(path, index, err_S006)
        blank_lines = 0
    return blank_lines


def cl_f_spaces_check(path, index, line):
    if re.search(r'(class|def)\s\s', line):
        errors[path][index + 1].append(err_S007)


def class_camelcase_check(path, index, line):
    if re.search(r'class\s+', line) and not re.search(r'class\s+[A-Z][a-z]+', line) or re.search(r'class\s+[A-Za-z]+_', line):
        class_name = re.sub(':', '', line.split(' ')[1].strip())
        err_S008 = f"""S008 Class name '{class_name}' should use CamelCase"""
        errors[path][index + 1].append(err_S008)


def def_snake_case_check(path, index, line):
    if re.search(r'def\s+', line) and re.search(r'def\s+\w*[A-Z]+\w*[A-Z]*', line) and not re.search(r'def\s+[a-z]+_[a-z]+', line):
        def_name = line.split(' ')[1].strip()
        err_S009 = f"S009 Function name '{def_name}' should use snake_case"
        errors[path][index + 1].append(err_S009)


def def_args_check(file, path):
    for node in ast.walk(file):
        if isinstance(node, ast.FunctionDef):
            args = [arg.arg for arg in node.args.args]
            defaults = node.args.defaults
            for default in defaults:
                if default is not None:
                    if isinstance(default, (ast.List, ast.Dict, ast.Set)):
                        process_dict(path, (node.lineno - 1), err_S012)
            for arg in args:
                if not re.match(r'_*[a-z]*_?[a-z]*_*', arg) or re.search(r'[A-Z]', arg):
                    process_dict(path, (node.lineno - 1), err_S010)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
            if not re.match(r'[a-z]*_?[a-z]*', node.id) or re.search(r'[A-Z]+', node.id):
                process_dict(path, (node.lineno - 1), err_S011)



def process_dict(path, index, err):
    errors[path][index + 1].append(err)


def process_file(path):
    with open(path, 'r') as file:
        blank_lines = 0
        for index, line in enumerate(file):
            len_check(path, index, line)
            indentation_check(path, index, line)
            semicolon_check(path, index, line)
            comments_spaces_check(path, index, line)
            todo_check(path, index, line)
            cl_f_spaces_check(path, index, line)
            class_camelcase_check(path, index, line)
            def_snake_case_check(path, index, line)
            blank_lines = blank_line_check(path, index, line, blank_lines)
    module = ast.parse(open(path).read())
    def_args_check(module, path)


def get_paths():
    if args.path.endswith('.py'):
        process_file(args.path)
    else:
        directory = "../task/test/this_stage"
        path = os.path.abspath(directory)
        paths = os.listdir(path)
        paths.sort()
        for link in paths:
            full_path = os.path.join(path, link)
            if full_path.endswith('py') and re.match(r'test_\d.py', link):
                process_file(full_path)


def print_info():
    for path, values in errors.items():
        for line, error in values.items():
            for index in range(len(error)):
                print(f'{path}: Line {line}: {error[index]}')


get_paths()
print_info()
