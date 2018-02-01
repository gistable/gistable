# -*- coding: utf-8 -*-
# 수치해석, 김상철 교수님
# 1. Incremental Search, Bisection, False Position,
#    Newton-Raphson, Secant Method 정리
# 20163179 홍승환

import numpy as np
import math
from scipy.optimize import fsolve

"""
    증분법을 계산하는 함수입니다.
    func : 대상 함수
    xmin, xmax : x의 최소, 최대값
    ns : 설정한 x 범위를 몇 개의 실제 값으로 쪼갤 것인지
"""
def incsearch(func, xmin, xmax, ns):
    # x 범위 설정
    x = np.linspace(xmin, xmax, ns)

    # 주어진 함수 실행 배열 세팅
    f = func(x)

    # 구간값의 갯수
    nb = 0

    # 구간값을 보관할 배열
    xb = []

    # 0부터 설정한 최고값까지 반복
    for k in np.arange(np.size(x) - 1):
        # 만약 f(x)랑 f(x+1)이 부호가 다르면 = 그래프가 x축을 뚫고 지나갔으면
        if np.sign(f[k]) != np.sign(f[k+1]):
            # 구간 하나 찾음!
            nb = nb + 1

            # 여기부터 여기까지임
            xb.append(x[k])
            xb.append(x[k + 1])

    # 구간 갯수(Number of Brackets), 구간 배열(Root Interval) 반환
    return nb, xb

"""
    이분법을 계산하는 함수입니다.
    func : 대상 함수
    xl : 계산할 x의 최저값 (lower guesses)
    xu : 계산할 x의 최고값 (upper guesses)
"""
def bisect(func, xl, xu):
    # 최대 반복 횟수, 기본 100으로 설정함
    maxit = 100

    # 예상된 오차의 범위, 기본 0.0001%로 설정
    es = 1.0e-4

    # f(최저값)과 x(최고값)을 곱함
    test = func(xl) * func(xu)

    """
        Bisection은, 계산할 x의 최저값과 최고값이 부호가 달라야 합니다.
        중간값 정의에 의해, 그 사이에 무조건적으로 근이 존재하기 때문입니다.
        그러나 f(최저값)과 f(최고값)을 곱한 값이 양수라면, 부호가 같다는 뜻이 됩니다.
        계산이 불가능하다는 뜻이므로, 함수를 종료합니다.
    """
    if test > 0:
        print("No sign change")
        return [], [], [], []
    
    # 반복 카운터
    iter = 0

    # 중심값 초기화
    xr = xl

    # 계산될 오차값 100%로 초기화
    ea = 100

    # 무한 반복
    while True:
        # 우선 현재 중심값을 xrold라는 변수에 저장해둠
        xrold = xr

        # 중심값을 현재의 최고, 최저값을 더한 후 2로 나눈 값(중앙값)으로 설정함
        xr = np.float((xl + xu) / 2)

        # 한 바퀴 더 돌았음
        iter = iter + 1

        # 중심값이 0이 아니라면
        if xr != 0:
            # 다음 식을 계산해서 오차값을 찾음
            # |{(현재 중심값) - (이전 중심값)} / (현재 중심값) | * 100
            ea = np.float(np.abs((np.float(xr) - np.float(xrold))/np.float(xr))*100)
        
        # f(최저값)과 x(최고값)을 곱함
        test = func(xl) * func(xr)

        # 만약 곱한 값이 양수라면
        if test > 0:
            # 최저값을 현재 중심값으로 설정함
            xl = xr
        # 아니고 만약 음수라면
        elif test < 0:
            # 최고값을 현재 중심값으로 설정함
            xu = xr
        # 만약 양수도, 음수도 아닌 0이라면
        else:
            # 오차 없음, 정확히 찾음
            ea = 0
        
        # 만약 (1) 계산된 오차값이 허용된 오차값보다 작다면 = 대강 이쯤되면 답이다 싶으면
        # 또는
        # 만약 (2) 설정한 최대 반복값보다 더 많이 돌았으면
        if np.int(ea < es) | np.int(iter >= maxit):
            # 계산 그만, 반복 종료
            break
    
    # 구한 중심값을 근으로 침
    root = xr

    # f(x)에 구한 근 넣어서 계산
    fx = func(xr)

    # 근, f(근) 값, 계산된 오차값, 반복값
    return root, fx, ea, iter

"""
    가위치법을 계산하는 함수입니다.
    func : 대상 함수
    xl : 계산할 x의 최저값 (lower guesses)
    xu : 계산할 x의 최고값 (upper guesses)
"""
def false_position(func, xl, xu):
    # 최고 반복 한계값, 에러 최댓값 설정
    maxit = 100
    es = 1.0e-4

    # f(최저값)과 x(최고값)을 곱함
    test = func(xl) * func(xu)

    """
        False Position은 Bisection과 마찬가지로 구간을 기반으로 판단하는 알고리즘입니다.
        그러므로 역시 중간값 정리를 적용하여, 양쪽 끝값의 부호가 달라야 계산이 가능합니다.
        그렇지 않다면, 계산을 하지 않고 함수를 종료합니다.
    """
    if test > 0:
        print("No sign change")
        return [], [], [], []
    
    # 반복 카운터 초기화
    iter = 0

    # 중간값 초기화
    xr = xl

    # 오차 초기화
    ea = 100

    # 무한 반복
    while True:
        # 이전 중간값 저장
        xrold = xr

        # False Position 알고리즘 : 삼각형의 닮은꼴 기반 계산법 (PPT 참조)
        xr = np.float(xu - func(xu) * (xl - xu) / (func(xl) - func(xu)))

        # 반복 카운터 1 증가
        iter = iter + 1

        # 중간값이 0이 아니면
        if xr != 0:
            # 다음 식을 계산해서 오차값을 찾음
            # |{(현재 중심값) - (이전 중심값)} / (현재 중심값) | * 100
            ea = np.float(np.abs((np.float(xr) - np.float(xrold))/np.float(xr)) * 100)
        
        # f(최저값)과 x(최고값)을 곱함
        test = func(xl) * func(xr)

        # 만약 곱한 값이 양수라면
        if test > 0:
            # 최저값을 현재 중심값으로 설정함
            xl = xr
        # 아니고 만약 음수라면
        elif test < 0:
            # 최고값을 현재 중심값으로 설정함
            xu = xr
        # 만약 양수도, 음수도 아닌 0이라면
        else:
            # 오차 없음, 정확히 찾음
            ea = 0
        
        # 만약 (1) 계산된 오차값이 허용된 오차값보다 작다면 = 대강 이쯤되면 답이다 싶으면
        # 또는
        # 만약 (2) 설정한 최대 반복값보다 더 많이 돌았으면
        if np.int(ea < es) | np.int(iter >= maxit):
            # 계산 그만, 반복 종료
            break

    # 찾은 중심값을 근으로 함
    root = xr

    # f(근) 계산
    fx = func(xr)

    # 근, f(근), 오차, 반복 횟수 반환
    return root, fx, ea, iter

"""
    Newton-Raphson을 계산하는 함수입니다.
    func : 대상 함수
    dfunc : 대상 함수의 미분 함수
    xr : 시작값
"""
def newtraph(func, dfunc, xr):
    # 최대 반복 횟수, 오차 최댓값, 반복 카운터 초기화
    maxit = 50
    es = 1.0e-4
    iter = 0
    
    # 무한 반복
    while True:
        # 현재 값 보관
        xrold = xr

        # Newton-Raphson Algorithm 계산
        xr = np.float(xr - func(xr) / dfunc(xr))
        # 반복 카운터 1 증가
        iter = iter + 1

        # xr이 0이 아닐 경우
        if xr != 0:
            # 다음 식을 계산해서 오차값을 찾음
            # |{(현재 중심값) - (이전 중심값)} / (현재 중심값) | * 100
            ea = np.float(np.abs((np.float(xr) - np.float(xrold))/np.float(xr)) * 100)

        # 만약 (1) 계산된 오차값이 허용된 오차값보다 작다면 = 대강 이쯤되면 답이다 싶으면
        # 또는
        # 만약 (2) 설정한 최대 반복값보다 더 많이 돌았으면
        if np.int(ea < es) | np.int(iter >= maxit):
            break
    
    # 구해진 xr을 근으로 함
    root = xr
    # 근, 오차값, 반복 횟수 반환
    return root, ea, iter

"""
    Secant Method(할선법)를 계산하는 함수입니다.
    func : 대상 함수
    x0, x1 : 시작값, 끝값
"""
def secant_method(func, x0, x1):
    # 최대 반복 횟수, 최대 오차, 반복 카운터 초기화
    maxit = 100
    es = 1.0e-4
    iter = 0
    
    # 무한 반복
    while True:
        # Secant Method
        xr = np.float(x1 - (func(x1) * (x1 - x0) * 1.0) / (func(x1) - func(x0)))
        # 반복 카운터 초기화
        iter = iter + 1

        # xr이 0이 아닐 경우
        if xr != 0:
            # 다음 식을 계산해서 오차값을 찾음
            # |{(현재 구한 값) - (바로 전에 구한 값)} / (현재 구한 값) | * 100
            ea = np.float(np.abs((np.float(xr) - np.float(x1))/np.float(xr)) * 100)

        # 만약 (1) 계산된 오차값이 허용된 오차값보다 작다면 = 대강 이쯤되면 답이다 싶으면
        # 또는
        # 만약 (2) 설정한 최대 반복값보다 더 많이 돌았으면
        if np.int(ea < es) | np.int(iter >= maxit):
            break
        
        # 값을 하나씩 뒤로 옮김
        x0 = x1
        x1 = xr
    
    # 구해진 xr을 근으로 함
    root = xr
    # 근, 오차값, 반복 횟수를 반환
    return root, ea, iter

# 실제적 계산값
print("[!] 0. Real Root\n")

fm = lambda m: np.sqrt(9.81 * m / 0.25) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - 36
m = fsolve(fm, 1)

print("[+] Real Root:", m)
print()

# 증분법
print("[!] 1. Incremental Search\n")
g = 9.81; m = 68.1; cd = 0.25; v = 36; t = 4

fp = lambda mp: np.sqrt(g * np.asarray(mp) / cd) * np.tanh(np.sqrt(g * cd / np.asarray(mp)) * t) - v
nb, xb = incsearch(fp, 1, 200, 50)

# 구간의 갯수
print("[+] Number of Brackets =", nb)

# 구간들
print("[+] Root Interval =", xb)
print()

# 이분법
print("[!] 2. Bisection\n")
fm = lambda m: np.sqrt(9.81 * m / 0.25) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - 36
root, fx, ea, iter = bisect(fm, 40, 200)

# 근
print("[+] root:", root)

# f(근)
print("[+] f(root):", fx, "(Must Be Zero)")

# 계산된 오차
print("[+] Estimated Error:", ea, "(Must Be Zero Error)")

# 근을 찾기 위해 반복한 계산 횟수
print("[+] Iterated Number to Find Root: ", iter)
print()

# 가위치법
print("[!] 3. False Position\n")
fm = lambda m: np.sqrt(9.81 * m / 0.25) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - 36
root, fx, ea, iter = false_position(fm, 40, 200)

# 근
print("[+] root:", root, "(False Position)")

# f(근)
print("[+] f(root):", fx, "(Must Be Zero, False Position)")

# 계산된 오차
print("[+] Estimated Error:", ea, "(Must Be Zero Error, False Position)")

# 근을 찾기 위해 반복한 계산 횟수
print("[+] Iterated Number to Find Root: ", iter, "(False Position)")
print()

# Newton-Raphson
print("[!] 4. Newton-Raphson\n")

# 대상 함수
y = lambda m: np.sqrt(9.81 * m / 0.25) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - 36

# 미분 함수
"""
    미분 함수에서, 원래대로라면 sech(Hyperbolic Secant)의 제곱이 필요합니다.
    하지만 Numpy + Scipy 조합에서는 이 함수가 존재하지 않습니다.
    그래서 sech = 1 / cosh에서 착안하여 {1 / np.cosh(...)}의 제곱으로 계산하여야 합니다.
"""
dy = lambda m: (1 / 2) * np.sqrt(9.81 / (m * 0.25)) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - \
               (9.81 * 4 / (2 * m)) * (1 / np.cosh(np.sqrt(9.81 * 0.25 / m) * 4)) ** 2

# 시작값이 140일 때
root, ea, iter = newtraph(y, dy, 140)
print("[=] On xr = 140\n")

print("[+] Root:", root)
print("[+] Estimated Error:", ea, "(Must Be Zero Error)")
print("[+] Iterated Number to Find Root: ", iter)
print()

# 시작값이 200일 때
root, ea, iter = newtraph(y, dy, 200)
print("[=] On xr = 200\n")

print("[+] root:", root)
print("[+] Estimated Error:", ea, "(Must Be Zero Error)")
print("[+] Iterated Number to Find Root: ", iter)
print()

# 시작값이 40일 때
root, ea, iter = newtraph(y, dy, 40)
print("[=] On xr = 40\n")

print("[+] root:", root)
print("[+] Estimated Error:", ea, "(Must Be Zero Error)")
print("[+] Iterated Number to Find Root: ", iter)
print()
    
# Secant Method (할선법)
print("[!] 5. Secant Method\n")
y = lambda m: np.sqrt(9.81 * m / 0.25) * np.tanh(np.sqrt(9.81 * 0.25 / m) * 4) - 36

# 40에서 200을 범위로 잡았을 때
root, ea, iter = secant_method(y, 40, 200)
print("[=] On 40 to 200:\n")

print("[+] Root:", root)
print("[+] Estimated Error:", ea, "(Must Be Zero Error)")
print("[+] Iterated Number to Find Root: ", iter)
print()


# 기대 출력 결과
"""
[!] 0. Real Root

[+] Real Root: [ 142.73763311]

[!] 1. Incremental Search

[+] Number of Brackets = 1
[+] Root Interval = [139.08163265306123, 143.14285714285717]

[!] 2. Bisection

[+] root: 142.73765563964844
[+] f(root): 4.60891335763e-07 (Must Be Zero)
[+] Estimated Error: 5.3450468252827136e-05 (Must Be Zero Error)
[+] Iterated Number to Find Root:  21

[!] 3. False Position

[+] root: 142.73783844758196 (False Position)
[+] f(root): 4.20034974269e-06 (Must Be Zero, False Position)
[+] Estimated Error: 7.781013805708828e-05 (Must Be Zero Error, False Position)
[+] Iterated Number to Find Root:  29 (False Position)

[!] 4. Newton-Raphson

[=] On xr = 140

[+] Root: 142.73763310844788
[+] Estimated Error: 9.907775669827273e-06 (Must Be Zero Error)
[+] Iterated Number to Find Root:  3

[=] On xr = 200

[+] root: 142.73763310844814
[+] Estimated Error: 9.466905354044462e-06 (Must Be Zero Error)
[+] Iterated Number to Find Root:  5

[=] On xr = 40

[+] root: 142.73763310844924
[+] Estimated Error: 1.0756383652963496e-10 (Must Be Zero Error)
[+] Iterated Number to Find Root:  7

[!] 5. Secant Method

[=] On 40 to 200:

[+] Root: 142.73763310875134
[+] Estimated Error: 6.298919092046472e-06 (Must Be Zero Error)
[+] Iterated Number to Find Root:  7
"""

# 설명
"""
    먼저 실제 근값(0번)을 보면 142.73763311을 볼 수 있습니다. 
    이것이 실제 근이고, 이 값과 1, 2에서 구한 값을 비교합니다.

    1의 Root Interval을 보면, 139.08... 부터 143.14... 사이에 
    근이 있다는 것을 알 수 있습니다.
    증분법의 특성상 저 사이 쯤에 근이 있을 것이라는 추정 정도가 가능합니다.
    만약 linspace의 ns 값을 늘려서 대입값을 더 촘촘하게 한다면 
    더욱 정확한 구간 값을 도출할 수 있을 것입니다.

    2의 root를 보면, 142.73765563... 이 나옵니다. 실제 근과 소숫점 뒤
    4자리까지 일치하는 거의 정확한 값입니다.
    근을 x라고 할 때, 근이 맞다면 f(x)는 0이 되어야 합니다. 
    넣어보니 4.6089...e-07, 즉 0.000000460... 의 경미한 오차를 보입니다.
    또, 계산된 오차값을 보면, 위에서 기초적으로 설정한 0.0001%보다 작은 오차로
    21번만에 계산이 종료된 것을 알 수 있습니다.

    3의 root를 보면, 142.73783844... 이 나옵니다. 실제 근과 소숫점 뒤
    3자리까지 일치하는 것을 볼 수 있습니다.
    그러다 보니 f(근)과 계산된 오차 또한 실제값과 거리가 조금 더 있습니다.
    반복도 조금 더 한 것 같습니다.
    즉, 여기서는 이분법이 가위치법보다 더 정확한 값이 나왔다는 뜻이 됩니다.

    이건 원인이 있습니다.
    가위치법은, 근과 그래프의 설정된 양 끝값을 기준으로 삼각형 2개를 그린 후
    그 두 삼각형이 닮은꼴인가를 tan 함수와 비슷하게 판정하게 됩니다.
    그래서, 가위치법은 "원래 함수가 어떻게 생겼느냐"에 따라서 계산 횟수가 바뀌게 됩니다.
    하지만, 이분법은 삼각형과 상관이 없는 계산 방식을 가집니다.
    따라서 우리가 사용한 번지 점프 공식은 가위치법보다는 이분법이 더 적합한
    함수 모양이었다는 결론을 낼 수 있습니다.

    [의견 반영: 박은환 (@dainelpark)]
        또한, 함수의 모양을 보면 이분법과 가위치법의 소스가 매우 비슷합니다.
        이 두 알고리즘은 구간을 판정할 때 f(왼쪽 끝값)과 f(오른쪽 끝값)의
        곱이 음수일 때, 즉 부호가 다를 때를 기준으로 판정한다는 공통점이 있습니다.
        구간을 얻었을 때, xr(중간값)을 구하는 방법이 각각 다르고, 이 차이가
        이분법과 가위치법을 구분합니다.

    Newton-Raphson(4번)의 경우, 미분계수를 구하는 방식을 매우 철저하게
    구현한 알고리즘으로, 우리가 알고 있는 미분의 과정을 그대로 흉내냅니다.
    시작값이 어디이냐에 따라서 결과가 달라지는데, 반복의 횟수가 3~7회인 것으로 보입니다.
    같은 식을 이분법으로 계산해보면, 24번의 반복 횟수가 나옵니다.
    이분법과 비교했을 때 매우 효율적인 계산 방법이라고 할 수 있습니다.

    그러나 Newton-Raphson법에는 문제가 있는데, 미분 함수를 따로
    구해서 넣어주고 그것을 지속적으로 계산해야 한다는 점입니다.
    그래서 나온 방법이 Secant Method(할선법, 5번)입니다.
    할선법은 도함수를 이용하는 대신 2개의 함숫값을 통해서 지속적으로
    선을 그어가며 새로운 끝점을 찾아서 근에 접근하는 방식입니다.
    이 방식을 이용하면 Newton-Raphson법과 비슷하게 계산하되
    연산력을 낭비하지 않고, 도함수 없이도 계산할 수 있다는
    장점이 있습니다.

    실제 할선법의 계산 결과를 보면, 40에서 200의 구간을 주었습니다.
    위의 이분법과 같은 구간을 주었는데 7번의 반복만에 계산이 끝났습니다.
    Newton-Raphson법의 장점을 취하면서, 동시에 단점을 보완한 방법이라고 할 수 있습니다.
"""