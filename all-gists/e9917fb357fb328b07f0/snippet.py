def circle(people, i=0):
  killer = people[i % len(people)]
  i = (i + 1) % len(people)
  killed = people.pop(i)
  return circle(people, i) if len(people) > 1 else people.pop()

print circle(range(1, 101))