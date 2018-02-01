#Decorador de Função
def coroutine(func):
  def start(*args,**kwargs):
    cr = func(*args,**kwargs)
    next(cr)
    return cr
  return start

# Source
def source_fizzbuzz(fim, target):
  i = 1;
  while i <= fim:
    target.send(i)
    i += 1
  target.close()

#Filter
@coroutine
def filter_fizzbuzz(target):
  while True:
    i = (yield)
    if i % 15 == 0: target.send("FizzBuzz")
    elif i % 3 == 0: target.send("Fizz")
    elif i % 5 == 0: target.send("Buzz")
    else: target.send(i)
    i += 1

#Sync
@coroutine
def printer():
  while True:
    linha = (yield)
    print(linha)

if __name__ == "__main__":
  source_fizzbuzz(20, filter_fizzbuzz(printer()))