# Warmup-1
def sleep_in(weekday, vacation):
  if weekday and not vacation:
    return False
  return True

def monkey_trouble(a_smile, b_smile):
  if a_smile and not b_smile or not a_smile and b_smile:
    return False
  return True  

def sum_double(a, b):
  if a == b:
    return 2 * (a+b)
  return a+b

def diff21(n):
  delta = 21 - n
  if delta < 0:
    return 2 * -delta
  return delta

def parrot_trouble(talking, hour):
  if talking and (hour < 7 or hour > 20):
    return True
  return False

def makes10(a, b):
  if a == 10 or b == 10 or a+b == 10:
    return True
  return False
  
def near_hundred(n):
  if abs(100-n) <= 10 or abs(200-n) <= 10:
    return True
  return False

def pos_neg(a, b, negative):
  if negative:
    if a < 0 and b < 0:
      return True
    return False
  else:
    if a < 0 and b > 0 or a > 0 and b < 0:
      return True
  return False

def not_string(str):
  if len(str) > 3 and str[0:3] == "not" or str == "not":
    return str
  return "not " + str

def missing_char(str, n):
  return str[0:n] + str[n+1:]

def front_back(str):
  if len(str) >= 3:
    return str[-1] + str[1:-1] + str[0]
  elif len(str) == 2:
    return str[1] + str[0]
  return str

def front3(str):
  if len(str) < 3:
    return 3*str
  return 3*str[0:3]

# Warmup-2
def string_times(str, n):
  return str*n

def front_times(str, n):
  if len(str) < 3:
    return str*n
  return str[0:3]*n

def string_bits(str):
  s = ""
  for x in xrange(0, len(str), 2):
    s += str[x]
  return s

def string_splosion(str):
  s = ""
  limit = len(str)
  n = 1
  while n <= limit:
    s += str[0:n]
    n = n + 1
  return s
  
def last2(str):
  if len(str) < 2:
    return 0
  f=str[-2:]
  c=0
  for p in xrange(len(str)-2):
    if str[p:p+2] == f:
      c += 1
  return c

def array_count9(nums):
  c = 0
  for n in nums:
    if n == 9:
      c += 1
  return c

def array_front9(nums):
  limit = 4
  if len(nums) < 4:
    limit = len(nums)
  for p in xrange(limit):
    if nums[p] == 9:
      return True
  return False   

def array123(nums):
  if len(nums) == 3 and nums == [1,2,3]:
    return True
  for p in xrange(len(nums)-2):
    if nums[p:p+3] == [1,2,3]:
      return True
  return False

def string_match(a, b):
  c = 0
  limit = len(a)
  if len(b) < limit:
    limit = len(b)
  for p in xrange(limit-1):
    if a[p:p+2] == b[p:p+2]:
      c += 1
  return c
  
# String-1
def hello_name(name):
  return "Hello " + name + "!"

def make_abba(a, b):
  return a + b*2 + a

def make_tags(tag, word):
  return ("<%s>%s</%s>"%(tag,word,tag))

def make_out_word(out, word):
  return ("%s%s%s"%(out[0:2],word,out[2:]))

def extra_end(str):
  return str[-2:]*3

def first_two(str):
  if str == "":
    return str
  if len(str) < 2:
    return str
  return str[0:2]

def first_half(str):
  return str[0:len(str)/2]

def without_end(str):
  return str[1:-1]

def combo_string(a, b):
  if len(a) < len(b):
    return a+b+a
  return b+a+b

def non_start(a, b):
  return a[1:]+b[1:]

def left2(str):
  if len(str) > 2:
    return str[2:]+str[0:2]
  return str

# List-1
def first_last6(nums):
  if nums[0] == 6 or nums[-1] == 6:
    return True
  return False

def same_first_last(nums):
  return len(nums) >= 1 and nums[0] == nums[-1]

def make_pi():
  return [3,1,4]

def common_end(a, b):
  return a[0] == b[0] or a[-1] == b[-1]

def sum3(nums):
  return nums[0]+nums[1]+nums[2]

def rotate_left3(nums):
  return [nums[1],nums[2],nums[0]]

def reverse3(nums):
  return [nums[2], nums[1], nums[0]]

def max_end3(nums):
  return [max(nums[0],nums[-1])]*len(nums)

def sum2(nums):
  return sum(nums[0:2])

def middle_way(a, b):
  return [a[1],b[1]]

def make_ends(nums):
  return [nums[0], nums[-1]]

def has23(nums):
  return 2 in nums or 3 in nums

# Logic-1
def cigar_party(cigars, is_weekend):
  return cigars >= 40 and cigars <= 60 and not is_weekend or is_weekend and cigars >= 40

def date_fashion(you, date):
  if you <= 2 or date <= 2:
    return 0
  if you >= 8 or date >= 8:
    return 2
  return 1

def squirrel_play(temp, is_summer):
  return temp >= 60 and temp <= 90 and not is_summer or is_summer and temp >= 60 and temp <= 100

def caught_speeding(speed, is_birthday):
  if speed <= 60 and not is_birthday or speed <= 65 and is_birthday:
    return 0
  if speed >= 61 and speed <= 80 and not is_birthday or is_birthday and speed >= 66 and speed <= 85:
    return 1
  return 2

def sorta_sum(a, b):
  c = a+b
  if c >= 10 and c <= 19:
    return 20
  return c

def alarm_clock(day, vacation):
  if not vacation:
    if day == 6 or day == 0:
      return "10:00"
    return "7:00"
  else:
    if day == 6 or day == 0:
      return "off"
    return "10:00"

def love6(a, b):
  return a==6 or b==6 or a+b==6 or abs(a-b)==6

def in1to10(n, outside_mode):
  return ((n >= 1 and n <= 10) and not outside_mode) or ((n <= 1 or n >= 10) and outside_mode)

def near_ten(num):
  return 0==((num-2)%10) or 0==((num-1)%10) or 0==(num%10) or 0==((num+1)%10) or 0==((num+2)%10)

# Logic-2
def make_bricks(small, big, goal):
  if goal > small + big * 5: 
    return False
  return goal % 5 <= small

def lone_sum(a, b, c):
  if a==b and b==c: return 0
  if a==b: return c
  if b==c: return a
  if a==c: return b
  return a+b+c

def lucky_sum(a, b, c):
  if a==13: return 0
  if b==13: return a
  if c==13: return a+b
  return a+b+c

def no_teen_sum(a, b, c):
  fa=fix_teen(a)
  fb=fix_teen(b)
  fc=fix_teen(c)
  return fa+fb+fc
  
def fix_teen(n):
  if n == 15 or n == 16 or n > 19 or n < 13: return n
  return 0

def round_sum(a, b, c):
  return round10(a)+round10(b)+round10(c)

def round10(num):
  return 10 * ((num+num%10)/10)

def close_far(a, b, c):
  dab = abs(a-b)
  dac = abs(a-c)
  dbc = abs(b-c)
  if dab <= 1 and dac >= 2 and dbc >= 2: return True
  if dac <= 1 and dab >= 2 and dbc >= 2: return True
  return False

def make_chocolate(small, big, goal):
  smalls = goal - min(big, goal / 5) * 5
  if smalls <= small:
    return smalls
  return -1

# String-2
def double_char(str):
  s = ""
  for c in str:
    s += c*2
  return s

def count_hi(str):
  return str.count('hi')

def cat_dog(str):
  return str.count('cat') == str.count('dog')

def count_code(str):
  l = len(str)
  c = 0;
  co = "co"
  e = "e"
  if l < 4: return 0
  for i in xrange(l-3):
    if co==str[i:i+2] and e==str[i+3:i+4]:
      c += 1
  return c

def end_other(a, b):
  alow = a.lower()
  blow = b.lower()
  return alow.endswith(blow) or blow.endswith(alow)

def xyz_there(str):
  if len(str) < 3: return False
  if str == ".xyz": return False
  if str == "xyz": return True
  for i in xrange(len(str)-2):
    if str[i:i+3]=="xyz" and str[i-1]!=".":
      return True 
  return False

# List-2
def count_evens(nums):
  c = 0
  for n in nums:
    if n % 2 == 0:
      c += 1
  return c

def big_diff(nums):
  return abs(min(nums) - max(nums))

def centered_average(nums):
  c=0
  for n in nums:
    c += n
  lo=min(nums)
  hi=max(nums)
  return (c - lo - hi) / (len(nums)-2) 

def sum13(nums):
  if len(nums)==0: return 0
  for i in xrange(len(nums)):
    if nums[i]==13:
      nums[i]=0
      if i+1<len(nums):
        nums[i+1]=0
  return sum(nums)

def sum67(nums):
  for i in range(0, len(nums)):
    if nums[i] == 6:
      nums[i] = 0
      for j in range(i+1, len(nums)):
        temp = nums[j]
        nums[j] = 0
        if temp == 7:
          i = j + 1
          break
  return sum(nums)

def has22(nums):
  for i in range(0, len(nums)-1):
    if nums[i:i+2] == [2,2]:
      return True    
  return False

