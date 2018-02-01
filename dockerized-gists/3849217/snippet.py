# -*- coding: utf-8 -*-
'''
Created on 2012-10-07

@author: Sergey <me@seriyps.ru>

Альтернативный вариант решения из статьи http://habrahabr.ru/post/153595/
на базе модификации AST

@asynchronous
@gen.engine
@shortgen
def get():
    result << my_task(args, *kwargs)

преобразуется в

@asynchronous
@gen.engine
def get():
    result = yield gen.Task(my_task, args, *kwargs)
'''
import ast
import marshal
import py_compile
import time
import os.path


class RewriteGenTask(ast.NodeTransformer):

    def __init__(self, *args, **kwargs):
        self.on_decorator = []
        self.on_assign = []
        super(RewriteGenTask, self).__init__(*args, **kwargs)

    def shortgen_deco_pos(self, decorator_list):
        # проверяет, что в списке декораторов имеется декоратор с именем
        # shortgen и возвращает его позицию.
        for pos, deco in enumerate(decorator_list):
            # Name(id='shortgen', ctx=Load())
            if isinstance(deco, ast.Name) and deco.id == 'shortgen':
                return pos
        return -1

    def visit_FunctionDef(self, node):
        """
        Проверяет, что функция обернута в декоратор shortgen.
        Если обернута, удаляем декоратор и трансформируем содержимое.
        FunctionDef(
            name='get_short',
            args=arguments(...),
            body=[...],
            decorator_list=[
                Attribute(value=Name(id='web', ...), attr='asynchronous', ...),
                Attribute(value=Name(id='gen', ...), attr='engine', ...),
                Name(id='shortgen', ctx=Load())])
        """
        deco_pos = self.shortgen_deco_pos(node.decorator_list)
        if deco_pos >= 0:
            # если функция обернута в shortgen декоратор, удаляем его,
            # делаем пометку в стеке и запускаем Visitor по содержимому
            # функции
            self.on_decorator.append(True)
            node.decorator_list.pop(deco_pos)
            self.generic_visit(node)  # трансформируем содержимое функции
            self.on_decorator.pop()
        return node

    def visit_Expr(self, expr):
        """
        == Основная трансформация ==
        Трансформируем
          result2 << func(arg, k=v, *args, **kwargs)
        в
          result2 = gen.Task(func, arg, k=v, *args, **kwargs)

        Пример AST представления "stmt << func(...)" (исходные данные):
        Expr(value=BinOp(left=Name(id='result', ctx=Load()),
              op=LShift(),
              right=Call(
                  func=Name(id='fetch', ctx=Load()),
                  args=[Num(n=1)],
                  keywords=[keyword(arg='k', value=Num(n=2))],
                  starargs=Tuple(elts=[Num(n=3)], ctx=Load()),
                  kwargs=Dict(keys=[Str(s='k2')], values=[Num(n=4)])))))
        ---- vvvvvvvvvvv ----
        Пример AST представления "stmt = yield func(...)" (результат):
        Assign(targets=[Name(id='result', ctx=Store())],
               value=Yield(value=Call(
                   func=Attribute(value=Name(id='gen', ctx=Load()),
                                  attr='Task', ctx=Load()),
                   args=[Name(id='fetch', ctx=Load()), Num(n=1)],
                   keywords=[keyword(arg='k', value=Num(n=2))],
                   starargs=Tuple(elts=[Num(n=3)], ctx=Load()),
                   kwargs=Dict(keys=[Str(s='k2')], values=[Num(n=4)]))))
        """
        node = expr.value       # BinOp
        if not (self.on_decorator
                and isinstance(expr.value, ast.BinOp)
                and isinstance(node.op, ast.LShift)):
            # если функция не обернута в декоратор (on_decorator пуст), ничего
            # не меняем
            return expr
        # если функция, содержащая LShift, обернута в декоратор,
        # то заменяем на вызов gen.Task()

        # для начала конвертируем изменение на месте (stmt <<) на
        # присваивание (stmt =). Для этого заменяем ctx=Load на
        # ctx=Store (см self.visit_Load())
        self.on_assign.append(True)
        assign_target = self.visit(node.left)
        self.on_assign.pop()
        # генерируем присваивание ... = ...
        (new_node, ) = ast.Assign(
            targets = [assign_target],
            value = ast.Yield(
                value=self.construct_gen_task_call(node.right))),
        # копируем номер линии оригинальной конструкции
        new_node = ast.fix_missing_locations(ast.copy_location(new_node, expr))
        return new_node

    def construct_gen_task_call(self, func_call):
        """
        Конвертируем вызов функции в вызов gen.Task с именем функции первым
        параметром
          func(arg, k=v, *args, **kwargs)
        в
          gen.Task(func, arg, k=v, *args, **kwargs)
        Пример AST представления "func(...)":
        Call(
            func=Name(id='fetch', ctx=Load()),
            args=[Num(n=1)],
            keywords=[keyword(arg='k', value=Num(n=2))],
            starargs=Tuple(elts=[Num(n=3)], ctx=Load()),
            kwargs=Dict(keys=[Str(s='k2')], values=[Num(n=4)])))
        ---- vvvvvvvvv ----
        Пример AST представления "gen.Task(func, ...)":
        Call(
            func=Attribute(value=Name(id='gen', ctx=Load()),
                           attr='Task', ctx=Load()),
            args=[Name(id='fetch', ctx=Load()), Num(n=1)],
            keywords=[keyword(arg='k', value=Num(n=2))],
            starargs=Tuple(elts=[Num(n=3)], ctx=Load()),
            kwargs=Dict(keys=[Str(s='k2')], values=[Num(n=4)]))
        """
        # Генерируем gen.Task
        gen_task = ast.Attribute(
                value=ast.Name(id='gen', ctx=ast.Load()),
                attr='Task', ctx=ast.Load())
        # Генерируем вызов gen.Task(func, ...)
        call = ast.Call(
            func=gen_task,
            # имя оригинальной ф-ции 1-м аргументом:
            args=[func_call.func] + func_call.args,
            keywords=func_call.keywords,
            starargs=func_call.starargs,
            kwargs=func_call.kwargs)
        return self.visit(call)

    def visit_Load(self, node):
        # Заменяем Load() на Store()
        if self.on_assign:
            return ast.copy_location(ast.Store(), node)
        return node


def shortgen(f):
    raise RuntimeError("ERROR! file must be compiled with yield_ast!")


def compile_file(filepath):
    path, filename = os.path.split(filepath)
    with open(filepath) as src:
        orig_ast = ast.parse(src.read())
    new_ast = RewriteGenTask().visit(orig_ast)
    code = compile(new_ast, filename, 'exec')

    pyc_filename = os.path.splitext(filename)[0] + '.pyc'
    pyc_filepath = os.path.join(path, pyc_filename)

    with open(pyc_filepath, 'wb') as fc:
        fc.write(py_compile.MAGIC)
        py_compile.wr_long(fc, long(time.time()))
        marshal.dump(code, fc)
        fc.flush()

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 2:
        print "Usage: %s file_to_compile1.py [file2.py] ..." % sys.argv[0]
    for filename in sys.argv[1:]:
        compile_file(filename)
