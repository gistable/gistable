#!/usr/bin/env python
# Look! It's Statementless Python
# Copyright Peter Corbett 2005
# NO WARRANTY: If you use this for anything important, you're mad!
# Credits to: Ian Jackson for having the idea, Ken Slonneger for 
# "Syntax and Semantics of Programming Languages" (large parts this program
# were hand-translated from one of the examples), and fanf, with whom I
# cannot hope to compete.
# Unlike most Python programs, whitespace matters little here. It could
# be a one-liner if you had a monitor long enough.
#
# Note: originally found at http://www.pick.ucam.org/~ptc24/yvfc.html
(globals().__setitem__("sg", globals().__setitem__),
 sg("glet", lambda **kw: globals().update(kw)),
 glet(yimport = lambda x: sg(x, __import__(x))),
 yimport("sys"),
 yimport("re"),
 glet(yprint = lambda x: sys.stdout.write(str(x)),
     yclass = lambda name, sclass=(), **attribs:
      sg(name, type(name, sclass, attribs))),
 yclass("YObject", (), clet = lambda self, **kw: self.__dict__.update(kw)),
 yclass("Cons", (YObject, ),
        __init__ = lambda self, car, cdr: self.clet(car=car, cdr=cdr),
        tolist   = lambda self:
        (self.cdr.__class__ != Cons and [self.car, self.cdr] or
         [self.car] + self.cdr.tolist()),
        setcar   = lambda self, x: self.clet(car=x),
        setcdr   = lambda self, x: self.clet(cdr=x),
        __repr__ = lambda self: (
        (self.cdr is None and ("%s" % repr_yobj(self.car)))
        or ((self.cdr.__class__) != Cons and
            ("(%s . %s)" % (repr_yobj(self.car), repr_yobj(self.cdr))))
        or (lambda l: (l[-1] is None and
                       ("(" + " ".join([repr_yobj(i) for i in l[:-1]]) + ")")
        or ("(" + " ".join([repr_yobj(i) for i in l[:-1]]) + " . %s)" %
            repr_yobj(l[-1]))))(self.tolist())),
        __eq__   = lambda self, other:
        ((other.__class__ != Cons and [False]) or
         [(self.car == other.car) and (self.cdr == other.cdr)])[0]),
 glet(repr_yobj = lambda yobj: (yobj is None and "()" or
                               yobj is True and "#t" or
                               yobj is False and "#f" or
                               "%s" % yobj),
      print_yobj = lambda yobj: yprint(repr_yobj(yobj)),
      println_yobj = lambda yobj: yprint(repr_yobj(yobj) + "\n"),
     str_conv = lambda a:
      (re.match("-?[0-9]+(\\.[0-9]+)$", a) and [float(a)] or
       re.match("-?[0-9]+$", a) and [int(a)] or
       a == "True" and [True] or a == "#t" and [True] or
       a == "False" and [False] or a == "#f" and [False] or [a])[0],
     digest_e = lambda e: e.replace("(", " ( ").replace(")", " ) ").split(),
     parse_e  = lambda e:
      (lambda stack: [i == "(" and [stack.append([])] or
                      i == ")" and [stack[-2].append(stack.pop())] or
                      stack[-1].append(str_conv(i)) for i in digest_e(e)]
                        and stack[0])([[]]),
     consify  = lambda l:
      ((l == [] and [None]) or
       (type(l) == type([]) and [Cons(consify(l[0]), consify(l[1:]))]) or
       [l])[0],
     is_atom  = lambda a: not a.__class__ == Cons,
     micro_repl = lambda env:
      (lambda s: (s == "quit" and [yprint("Bye!\n")]) or
       (is_atom(s) and (println_yobj(micro_eval(s, env)), micro_repl(env)) or
        (s.car == "define" and
         [micro_repl(update_env(env, s.cdr.car.car,
           consify(["lambda", s.cdr.car.cdr, s.cdr.cdr.car])))]) or
        ([println_yobj(micro_eval(s, env))] and micro_repl(env))))
        (consify(parse_e(raw_input(">> "))[0])),
     micro_exec_sl = lambda env, sl:
      sl and (lambda s: (s == "quit" and [yprint("Bye!\n")]) or
              (is_atom(s) and (micro_eval(s, env), micro_exec_sl(env, sl))) or
              (s.car == "define" and [micro_exec_sl(update_env(env,
                s.cdr.car.car, consify(["lambda",
                                     s.cdr.car.cdr, s.cdr.cdr.car])), sl)]) or
              (s.car == "read-eval-print-loop" and [micro_repl(env)]) or
              ([micro_eval(s, env)] and micro_exec_sl(env,sl)))
      (consify(sl.pop(0))),
     update_env = lambda env, ide, binding:
      Cons(consify([ide, binding]), env),
     apply_env  = lambda env, ide:
      ((env.car.car == ide and [env.car.cdr.car]) or
       [apply_env(env.cdr, ide)])[0],
     micro_eval = lambda s, env:
      (is_atom(s) and
       (s is None and [None] or
        s is True and [True] or s is False and [False] or
        (type(s) == type(1) or type(s) == type(1.2)) and [s] or
        [apply_env(env, s)] ) or
       s.car == "quote" and [s.cdr.car] or
       s.car == "lambda" and [s] or
       s.car == "display" and [(lambda ev: [print_yobj(ev)] and ev)
                               (micro_eval(s.cdr.car, env))] or
       s.car == "newline" and [[yprint("\n")] and None] or
       s.car == "cond" and [micro_evalcond(s.cdr, env)] or
       s.car == "let" and [micro_eval_slist(s.cdr.cdr,
                            micro_let_bind(s.cdr.car, env))] or
       s.car == "begin" and [micro_eval_slist(s.cdr, env)] or
       [micro_apply(s.car, micro_eval_args(s.cdr, env), env)])[0],
     micro_eval_args = lambda scdr, env:
      (not scdr and [None] or
       [(lambda oc: [micro_eval_args_core(scdr, oc, env)] and oc)
        (Cons(None, None))])[0],
     micro_eval_args_core = lambda s, ocp, env:
      ([ocp.setcar(micro_eval(s.car, env))] and
       (s.cdr and [ocp.setcdr(Cons(None, None))] and
        micro_eval_args_core(s.cdr, ocp.cdr, env))),
     micro_evalcond = lambda clauses, env:
      (not clauses and [False] or
       micro_eval(clauses.car.car, env) and
       [micro_eval(clauses.car.cdr.car, env)] or
       [micro_evalcond(clauses.cdr, env)])[0],
     micro_eval_slist = lambda exprlist, env:
      (exprlist.cdr is None and [micro_eval(exprlist.car, env)] or
       [micro_eval(exprlist.car, env)] and
       [micro_eval_slist(exprlist.cdr, env)])[0],
     micro_let_bind = lambda pairlist, env:
      (pairlist is None and [env] or
       [Cons(consify([pairlist.car.car,
                      micro_eval(pairlist.car.cdr.car, env)]),
             micro_let_bind(pairlist.cdr, env))])[0],
     micro_apply = lambda fn, args, env:
      (is_atom(fn) and 
       (fn == "car" and [args.car.car] or
        fn == "cdr" and [args.car.cdr] or
        fn == "cons" and [Cons(args.car, args.cdr.car)] or
        fn == "atom?" and [is_atom(args.car)] or
        fn == "null?" and [args.car is None] or
        fn == "equal?" and [args.car == args.cdr.car] or 
        fn == "+" and [args.car + args.cdr.car] or
        fn == "-" and [args.car - args.cdr.car] or
        fn == "*" and [args.car * args.cdr.car] or
        fn == "/" and [args.car / args.cdr.car] or
        [micro_apply(micro_eval(fn, env), args, env)]) or
       [micro_eval(fn.cdr.cdr.car, micro_bind(fn.cdr.car, args, env))])[0],
     micro_bind = lambda key_list, value_list, env:
      ((key_list is None or value_list is None) and [env] or
       [Cons(consify([key_list.car, value_list.car]),
             micro_bind(key_list.cdr, value_list.cdr, env))])[0]),
 glet(slist = parse_e(len(sys.argv) > 1 and
                      (open(sys.argv[1]).read()+"\n") or """
(define (factorial n) (cond ((equal? n 0) 1) (#t (* n (factorial (- n 1))))))
(define (fibonacci n) 
  (cond ((equal? n 0) 1)
  ((equal? n 1) 1)
  (#t (+ (fibonacci (- n 1)) (fibonacci (- n 2))))))
(define (cadr s) (car (cdr s)))
(define (srf-inner n)
  (cond ((equal? n 0) (quote (1 0)))
  (#t (let ((p (srf-inner (- n 1))))
       (cons (+ (car p) (cadr p)) (cons (car p) ()))))))
(define (single-recursive-fibonacci n) (car (srf-inner n)))
(define (display-with-newline d) (begin (display d) (newline) d))
(display-with-newline (factorial 6))
(display-with-newline (fibonacci 6))
(display-with-newline (single-recursive-fibonacci 6))
(read-eval-print-loop)
 """)),
 micro_exec_sl(None, slist)
)
