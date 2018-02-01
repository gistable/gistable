# coding=UTF-8


# Python Goes To Church
# =====================

# What would Python be like if all we had was simple (single argument) lambda
# expressions?  We could write some helpful functions like these:

id = lambda a: a
const = lambda c: lambda a: c
flip = lambda f: lambda a: lambda b: f(b)(a)
compose = lambda f: lambda g: lambda a: f(g(a))
then = flip(compose)

# But what about data?  Do we really need Python's built-in data types or
# classes?  It turns out there are ways to encode all data types with only
# lambda expressions, which is what the rest of this code illustrates.  You
# can run this file to see that everything works:
#
#    $ python church.py

# Booleans
# --------

# Let's start with one of the simplest data types, booleans.  Rather than use
# Python's built-in `True` or `False` directly, here's alternate data
# constructors that use lambda expressions only:

true = lambda ifTrue: lambda ifFalse: ifTrue
false = lambda ifTrue: lambda ifFalse: ifFalse

# At first, you may not believe that these implementations are indeed valid
# booleans.  To support the claim, we'll also write some functions like `and`,
# `or`, and `not`, and show that they work as we'd expect.

# But first, here's some hint for how this encoding works.  It's like a
# "visitor pattern" from OO or languages with "pattern matching."  Each data
# type has a fixed number of data constructors.  In the case of a boolean,
# there's two possiblities, `true` and `false`.  Each implementation accepts as
# input a candidate transformation for each data constructor, selecting one of
# them.

# For booleans, our encoding resembles if-then-else conditional expressions.  A
# boolean can be treated as a predicate that accepts two arguments: a "then"
# block and an "else" block.

# When we make our encoding in this style, we can always make a "fold" function
# that has an interesting property.  When we pass our data constructors to it
# as arguments, we get an identity function like `id` above:
#
#     foldBool(true)(false) ≡ id

foldBool = lambda ifTrue: lambda ifFalse: lambda b: b(ifTrue)(ifFalse)

# Folds are a general enough function such that we can derive all other
# functions from it:

cond = lambda p: lambda ifTrue: lambda ifFalse: foldBool(ifTrue)(ifFalse)(p)
not_ = foldBool(false)(true)
or_ = lambda a: foldBool(true)(cond(a)(true)(false))
and_ = lambda a: foldBool(cond(a)(true)(false))(false)
eqBool = lambda a: foldBool(cond(a)(true)(false))(cond(a)(false)(true))

# Alternate Booleans
# ------------------

# You may notice that the following definitions are valid simplifications:

true = const
false = flip(const)
cond = id
not_ = flip

# For the sake of illustration, we'll stick to defining a fold function, and
# then deriving functions from that.  When we do this, we get the nice property
# that we can change our data constructors and fold, but leave all other
# functions the same.

# Testing
# -------

# Working with lambdas for both data and operations on data can get somewhat
# abstract.  To test that our functions actually do what we think they do, we
# need a few functions to help us tie our work back to our host language
# Python:

eqPy = lambda a: lambda b: true if a == b else false
showBool = foldBool("true")("false")
def test(bool):
    assert(cond(bool)(True)(False))
testEq = lambda eq: lambda a: lambda b: test(eq(a)(b))

# Now we can test our work:

testEq (eqBool) (foldBool(true)(false)(true)) (true)
testEq (eqBool) (foldBool(true)(false)(false)) (false)

testEq (eqBool) (not_(true)) (false)
testEq (eqBool) (not_(false)) (true)

testEq (eqBool) (or_(true)(true)) (true)
testEq (eqBool) (or_(true)(false)) (true)
testEq (eqBool) (or_(false)(true)) (true)
testEq (eqBool) (or_(false)(false)) (false)

testEq (eqBool) (and_(true)(true)) (true)
testEq (eqBool) (and_(true)(false)) (false)
testEq (eqBool) (and_(false)(true)) (false)
testEq (eqBool) (and_(false)(false)) (false)

# Pairs
# -----

# Now see if you can follow another data structure for a pair:

pair = lambda a: lambda b: lambda f: f(a)(b)

# In this case, we only have one data constructor for the pair, but unlike
# booleans, the data constructor requires two arguments to build the pair (`a`
# and `b` above).  We have one remaining input `f`, which is because we have
# just one data constructor for a pair.  We use the parameter to transform the
# arguments passed to the pair constructor.

# With this encoding, we can now write a fold function that when passed our one
# data constructor becomes an identity function:
#
#     foldPair(pair) ≡ id

foldPair = lambda f: lambda p: p(f)

# And as before, we can use this fold function to derive other useful functions
# for pairs.

first = foldPair(const)
second = foldPair(flip(const))
mapFirst = lambda f: foldPair(lambda a: pair(f(a)))
mapSecond = lambda f: foldPair(lambda a: lambda b: pair(a)(f(b)))
eqPair = \
  lambda eqA: lambda eqB: lambda p1: \
    foldPair \
      (lambda a2: lambda b2: \
        foldPair(lambda a1: lambda b1: and_(eqA(a1)(a2))(eqB(b1)(b2)))(p1))
eqPairPy = eqPair(eqPy)(eqPy)
showPair = \
  lambda showA: lambda showB: \
    foldPair(lambda a: lambda b: "(" + showA(a) + ", " + showB(b) + ")")
showPairPy = showPair(str)(str)

# Here's some tests for our pair functions:

aPair = pair(1)(2)
times10 = lambda a: a * 10

testEq (eqPairPy) (foldPair(pair)(aPair)) (aPair)
testEq (eqPy) (first(aPair)) (1)
testEq (eqPy) (second(aPair)) (2)
testEq (eqPairPy) (mapFirst(times10)(aPair)) (pair(10)(2))
testEq (eqPairPy) (mapSecond(times10)(aPair)) (pair(1)(20))

# Options
# -------

# Let's try another one.  This one is called an "option" type (it's also called
# "maybe" in some languages).  The option is a lot like a singleton list.  It's
# either "none" (empty) or it has a "some" value.

# We're mostly applying the same techniques as we did for booleans and pairs
# above.  Here's the two data constructors:

none = lambda ifNone: lambda ifSome: ifNone
some = lambda a: lambda ifNone: lambda ifSome: ifSome(a)

# Here's a fold satisfying our property:
#
#     foldOpt(none)(some) ≡ id

foldOpt = lambda ifNone: lambda ifSome: lambda opt: opt(ifNone)(ifSome)

# Here's some useful functions for options:

orElse = lambda a: foldOpt(a)(id)
mapOpt = lambda f: foldOpt(none)(lambda a: some(f(a)))
bindOpt = lambda f: foldOpt(none)(f)
joinOpt = bindOpt(id)
eqOpt = \
  lambda eqA: lambda optA1: \
    foldOpt \
      (foldOpt(true)(const(false))(optA1)) \
      (lambda a2: foldOpt(false)(eqA(a2))(optA1))
eqOptPy = eqOpt(eqPy)
showOpt = lambda showA: foldOpt("none")(lambda a: "some(" + showA(a) + ")")
showOptPy = showOpt(str)

# And here's some tests:

testEq (eqPy) (orElse(2)(some(1))) (1)
testEq (eqPy) (orElse(2)(none)) (2)
testEq (eqOptPy) (mapOpt(times10)(some(1))) (some(10))
testEq (eqOptPy) (joinOpt(some(some(1)))) (some(1))
testEq (eqOptPy) (joinOpt(some(none))) (none)

# Lists
# -----

# Finally, let's build a singly linked list.  Unlike a the data types we've
# encoded thus far, lists are a recursive type.  This is because one of the
# data constructors for list, cons, contains another list (the tail).  The
# encoding for our constructors require a twist:

nil = lambda ifNil: lambda ifCons: ifNil
cons = \
  lambda head: lambda tail: lambda ifNil: lambda ifCons: \
    ifCons(head)(tail(ifNil)(ifCons))

# We have two data constructors, so both take two transformation functions, one
# for the nil case and the other for the cons case.  `nil` is encoded as we've
# done before.  For `cons` rather than just return `ifCons(head)(tail)`, we
# also pass `ifNil` and `ifCons` to the tail because it's also a list.

# We can then make a fold with our familiar property:
#
#     foldList(nil)(cons) ≡ id

foldList = lambda z: lambda f: lambda l: l(z)(f)

# Using this fold we can derive some useful functions for lists:

foldListLeft = \
  lambda z: lambda f: lambda l: \
    (foldList(id)(lambda a: then(flip(f)(a)))(l))(z)
isEmpty = foldList(true)(const(const(false)))
append = lambda la: lambda lb: foldList(lb)(cons)(la)
reverse = foldListLeft(nil)(flip(cons))
head = foldList(none)(lambda a: const(some(a)))
last = foldListLeft(none)(const(some))
tail = \
  lambda l: \
    mapOpt \
      (second) \
      (foldList \
        (none) \
        (lambda a: lambda acc: \
          some \
            (pair \
              (a) \
              (foldOpt(nil)(lambda p: cons(first(p))(second(p)))(acc)))) \
        (l))
mapList = lambda f: foldList(nil)(lambda a: cons(f(a)))
bindList = lambda f: foldList(nil)(lambda a: append(f(a)))
joinList = bindList(id)
eqList = \
  lambda eqA: lambda l1: lambda l2: \
    foldOpt \
      (isEmpty(l2)) \
      (lambda a1: \
        and_ \
          (eqOpt(eqA)(some(a1))(head(l2))) \
          (eqOpt(eqList(eqA))(tail(l1))(tail(l2)))) \
      (head(l1))
eqListPy = eqList(eqPy)
showList = \
  lambda showA: lambda l: \
    "[" + foldList("nil")(lambda a: lambda acc: showA(a) + ", " + acc)(l) + "]"
showListPy = showList(str)

# And here's some tests for our list:

aList = cons(1)(cons(2)(nil))
bList = cons(3)(cons(4)(nil))

testEq (eqBool) (isEmpty(nil)) (true)
testEq (eqBool) (isEmpty(aList)) (false)

testEq (eqListPy) (reverse(aList)) (cons(2)(cons(1)(nil)))

testEq (eqListPy) (append(aList)(nil)) (aList)
testEq (eqListPy) (append(nil)(aList)) (aList)
testEq (eqListPy) (append(aList)(bList)) \
    (cons(1)(cons(2)(cons(3)(cons(4)(nil)))))

testEq (eqOptPy) (head(nil)) (none)
testEq (eqOptPy) (head(aList)) (some(1))

testEq (eqOptPy) (last(nil)) (none)
testEq (eqOptPy) (last(aList)) (some(2))

testEq (eqOpt(eqListPy)) (tail(nil)) (none)
testEq (eqOpt(eqListPy)) (tail(aList)) (some(cons(2)(nil)))

testEq (eqListPy) (mapList(times10)(aList)) (cons(10)(cons(20)(nil)))

testEq (eqListPy) (joinList(cons(cons(1)(nil))(cons(cons(2)(nil))(nil)))) \
    (cons(1)(cons(2)(nil)))

# Summary
# -------

# For some people, it's eye-opening that so much can be done with just lambda
# expressions.  Furthermore, although very little Python code is currently
# written this way, the code has an elegance, despite some of Python's
# syntactic awkwardness.

# Most languages with lambda expressions do offer data types as well.  You may
# wonder if anyone actually codes with lambda expressions anyway.  They do,
# often for a performance benefit due to less object creation and garbage
# collection.  However, in some contexts, normal data types are actually
# faster.

# Unfortunately, because Python doesn't have a good type checker, we can't
# easily discriminate one lambda expression from another.  Everything looks
# like one type (a lambda).  This can lead to defects and difficulty
# debugging.  Lambda expressions give us the added flexibility of currying,
# partial application, and higher order functions.  But without a type
# checker, we seem penalized for taking too much advantage of these
# facilities.

# If you take away anything, notice how almost mechanically we can port data
# types from "OO" languages to something extremely function-based.  There's
# more to say about encapsulation and interfaces, but it's well understood
# that the difference between "OO" and "FP" isn't that complex once you know
# how to translate between the two.  As William Cook puts it,
#
#     I believe that Church's untyped lambda-calculus was the first
#     object-oriented language.

# ----

print("SUCCESS: all tests pass")
