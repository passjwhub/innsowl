# -*- coding:utf-8 -*-
import re
import os
import sys
sys.path.append('.')


service_ip = "192.168.31.121"
user_email = "test_analysis.txt@foxmail.com"
print(service_ip, user_email)


class Builder:
    # 每次缩进的空格数
    INDENT_STEP = 4

    def __init__(self, indent=0):
        # 当前缩进
        self.indent = indent
        # 保存一行一行生成的代码
        self.lines = []

    def forward(self):
        """ahead one step"""
        self.indent += self.INDENT_STEP

    def backward(self):
        """back one step"""
        self.indent -= self.INDENT_STEP

    def add(self, code):
        self.lines.append(code)

    def add_line(self, code):
        self.lines.append(' ' * self.indent + code)

    def __str__(self):
        """addition source code at code lines 拼接所有代码行后的源码"""
        return '\n'.join(map(str, self.lines))

    def __repr__(self):
        """for test"""
        return str(self)


class Generater:
    def __init__(self, raw_text, indent=0, default_context=None,
                 func_name='__func_name', result_var='__result',
                 template_dir='', encoding='UTF-8'):
        self.raw_text = raw_text
        self.default_context = default_context or {}
        self.func_name = func_name
        self.result_var = result_var
        self.template_dir = template_dir
        self.encoding = encoding
        self.code_builder = code_builder = Builder(indent=indent)
        self.buffered = []
        # 变量
        self.re_variable = re.compile(r'\{\{ .*? \}\}')
        # 注释
        self.re_comment = re.compile(r'\{# .*? #\}')
        # 标签
        self.re_tag = re.compile(r'\{% .*? %\}')
        # 用于按变量，注释，标签分割模版字符串
        self.re_tokens = re.compile(r'''((?:\{\{ .*? \}\})|(?:\{\# .*? \#\})|(?:\{% .*? %\}))''', re.X)

        # 生成 def __func_name():
        code_builder.add_line('def {}():'.format(self.func_name))
        code_builder.forward()
        # 生成 __result = []
        code_builder.add_line('{} = []'.format(self.result_var))
        # 解析模板
        self._parse_text()

        self.flush_buffer()
        # 生成 return "".join(__result)
        code_builder.add_line('return "".join({})'.format(self.result_var))
        code_builder.backward()

    def _parse_text(self):
        """analysis  module template"""
        tokens = self.re_tokens.split(self.raw_text)
        handlers = (
            # {{ variable }}
            (self.re_variable.match, self._handle_variable),
            # {% tag %}
            (self.re_tag.match, self._handle_tag),
            # {# comment #}
            (self.re_comment.match, self._handle_comment),
        )
        # 普通字符串
        default_handler = self._handle_string

        for token in tokens:
            for match, handler in handlers:
                if match(token):
                    handler(token)
                    break
            else:
                default_handler(token)

    def _handle_variable(self, token):
        """处理变量"""
        variable = token.strip('{} ')
        self.buffered.append('str({})'.format(variable))

    def _handle_comment(self, token):
        """处理注释"""
        pass

    def _handle_string(self, token):
        """处理字符串"""
        self.buffered.append('{}'.format(repr(token)))

    def _handle_tag(self, token):
        """处理标签"""
        # 将前面解析的字符串，变量写入到 code_builder 中
        # 因为标签生成的代码需要新起一行
        self.flush_buffer()
        tag = token.strip('{%} ')
        tag_name = tag.split()[0]
        if tag_name == 'include':
            self._handle_include(tag)
        else:
            self._handle_statement(tag)

    def _handle_statement(self, tag):
        """处理 if/for"""
        tag_name = tag.split()[0]
        if tag_name in ('if', 'elif', 'else', 'for'):
            # elif 和 else 之前需要向后缩进一步
            if tag_name in ('elif', 'else'):
                self.code_builder.backward()
            # if True:, elif True:, else:, for xx in yy:
            self.code_builder.add_line('{}:'.format(tag))
            # if/for 表达式部分结束，向前缩进一步，为下一行做准备
            self.code_builder.forward()
        elif tag_name in ('break',):
            self.code_builder.add_line(tag)
        elif tag_name in ('endif', 'endfor'):
            # if/for 结束，向后缩进一步
            self.code_builder.backward()

    def _handle_include(self, tag):
        filename = tag.split()[1].strip('"\'')
        included_template = self._parse_another_template_file(filename)
        '''
        # 把解析 include 模版后得到的代码加入当前代码中
        # def __func_name():
        #    __result = []
        #    ...
        #    def __func_name_hash():
        #        __result_hash = []
        #        return ''.join(__result_hash)
        '''
        self.code_builder.add(included_template.code_builder)
        # 把上面生成的代码中函数的执行结果添加到原有的结果中
        # __result.append(__func_name_hash())
        self.code_builder.add_line(
            '{0}.append({1}())'.format(
                self.result_var, included_template.func_name
            )
        )

    def _parse_another_template_file(self, filename):
        template_path = os.path.realpath(
            os.path.join(self.template_dir, filename)
        )
        name_suffix = str(hash(template_path)).replace('-', '_')
        func_name = '{}_{}'.format(self.func_name, name_suffix)
        result_var = '{}_{}'.format(self.result_var, name_suffix)
        with open(template_path, encoding=self.encoding) as fp:
            template = self.__class__(
                fp.read(), indent=self.code_builder.indent,
                default_context=self.default_context,
                func_name=func_name, result_var=result_var,
                template_dir=self.template_dir
            )
        return template

    def flush_buffer(self):
        # 生成类似代码: __result.extend(['<h1>', name, '</h1>'])
        line = '{0}.extend([{1}])'.format(
            self.result_var, ','.join(self.buffered)
        )
        self.code_builder.add_line(line)
        self.buffered = []

    def render(self, context=None):
        """渲染模板"""
        namespace = {}
        namespace.update(self.default_context)
        if context:
            namespace.update(context)
        exec (str(self.code_builder), namespace)
        # print namespace
        print(namespace[self.func_name])
        # print namespace[self.func_name]()
        result = namespace[self.func_name]()
        return result


def page_index(data):
    html = list(sys.path)[0] + os.sep + 'template/items.html'
    index_txt = open(html, 'r', encoding="utf-8").read()
    temp = Generater(index_txt)
    print("temp.code_builder:", temp.code_builder)
    if not isinstance(data, dict):
        raise BaseException(data)
    index_with_service = temp.render(data)
    with open('index.html', 'w') as idx:
        if isinstance(index_with_service, str):
            index_with_service.encode('utf-8')
        print("temp.index_with_service:", index_with_service)
        idx.write(index_with_service)


def generate_execute(data):
    html = list(sys.path)[0] + os.sep + 'template/execute.html'
    index_txt = open(html).read()
    temp = Generater(index_txt)
    print(temp.code_builder)
    if not isinstance(data, dict):
        raise BaseException(data)
    execute_with_service = temp.render(data)
    print('execute_with_service', execute_with_service)
    return execute_with_service


def generate_complete(data):
    html = list(sys.path)[0] + os.sep + 'template/complete.html'
    index_txt = open(html).read()
    temp = Generater(index_txt)
    print(temp.code_builder)
    if not isinstance(data, dict):
        raise BaseException(data)
    complete_with_execute = temp.render(data)
    print('complete_with_execute', complete_with_execute)
    return complete_with_execute

if __name__ == '__main__':
    complete_page = generate_complete({'resp': 'resp', 'pids': 'pids', 'reportDiv': 'reportDiv', 'picDiv': 'picDiv',
                                       'time_now':'time_now', 'tmpLog': 'tmpLog', 'run_host': 'run_host',
                                        'path': 'path', 'service_ip': 'service_ip'})
    generate_execute({'run_host': '127.0.0.1', 'case_name': 'runtest', 'user_email': 'test_analysis.txt@foxmai.com'})
