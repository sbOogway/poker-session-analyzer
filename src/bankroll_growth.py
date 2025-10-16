import math

"""
https://en.wikipedia.org/wiki/Kelly_criterion

p -> probability of winning the hand
b -> pot_size / amount_to_call -> pot odds
a -> amount of wager lost -> we consider always all of it. in some cases can
     be split pot
f -> fraction of bankroll to bet
r -> growth rate of the bankroll
"""

def kelly(p, b):
  return p - (1-p) / b

def calc_growth_rate(f: float, a: float, b: float, p: float):
  """
  https://en.wikipedia.org/wiki/Kelly_criterion

  p -> probability of winning the hand

  b -> pot_size / amount_to_call -> pot odds

  a -> amount of wager lost -> we consider always all of it. in some cases can be split pot

  f -> fraction of bankroll to bet

  r -> growth rate of the bankroll
  """
  return ((1+f*b)**p) * ((1-f*a)**(1-p))

if __name__ == "__main__":

  from matplotlib import pyplot as plt # type: ignore

  plt.style.use('dark_background')

  x, y = [], []
  p = 0.84
  b = 160/120
  a = 1

  break_even_bet_size = 0
  break_even_index = 0
  for i in range(100):
    f = i/100
    x.append(f*100)
    r = calc_growth_rate(f, a, b, p)
    y.append(math.log(r)*100)
    try:
      tmp = 1/math.log(r)
      if tmp > break_even_bet_size:
        break_even_bet_size = tmp
        break_even_index = int(f*100)
    except ZeroDivisionError:
      pass

  print(f"optimal bet size\t-> {x[y.index(max(y))]}%")
  print(f"optimal growth rate\t-> {round(max(y), 2)}%")
  print(f"break even bet size\t-> {x[break_even_index]}%")



  plt.plot(x, y, color='purple')
  plt.grid(color='gray', linestyle='--', linewidth=0.5, alpha=0.7)
  plt.xlabel("fraction of the bankroll wagered")
  plt.ylabel("growth rate of the bankroll")
  plt.show()