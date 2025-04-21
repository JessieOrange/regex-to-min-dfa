from collections import defaultdict, deque
def regex_to_rpn(regex):
    precedence = {'*': 3, '.': 2, '|': 1}
    output, stack = [], []

    def add_concat(regex):
        res = ''
        for i in range(len(regex) - 1):
            res += regex[i]
            if regex[i] not in '(|' and regex[i + 1] not in '|)*':
                res += '.'
        res += regex[-1]
        return res

    regex = regex.replace('ε', '#')  # 用 # 表示 epsilon
    regex = add_concat(regex)

    for c in regex:
        if c == '(':
            stack.append(c)
        elif c == ')':
            while stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()
        elif c in precedence:
            while stack and stack[-1] in precedence and precedence[stack[-1]] >= precedence[c]:
                output.append(stack.pop())
            stack.append(c)
        else:
            output.append(c)

    while stack:
        output.append(stack.pop())
    return output


# ---------------- NFA ----------------
class State:
    def __init__(self, id):
        self.id = id
        self.edges = defaultdict(list)  # char -> list of States
        self.epsilon = []  # list of States


class NFA:
    def __init__(self, start, accept):
        self.start = start
        self.accept = accept
        self.states = set()
        self.char_set = set()


def rpn_to_nfa(rpn):
    state_counter = [0]  # 用 list 包装以在嵌套函数中更新

    def new_state():
        state_counter[0] += 1
        return State(f"S{state_counter[0]}")

    stack = []

    for t in rpn:
        if t not in {'*', '.', '|'}:
            s = new_state()
            a = new_state()
            if t == '#':
                s.epsilon.append(a)
            else:
                s.edges[t].append(a)
            nfa = NFA(s, a)
            nfa.states.update({s, a})
            if t != '#':
                nfa.char_set.add(t)
            stack.append(nfa)

        elif t == '.':
            n2 = stack.pop()
            n1 = stack.pop()
            n1.accept.epsilon.append(n2.start)
            nfa = NFA(n1.start, n2.accept)
            nfa.states = n1.states.union(n2.states)
            nfa.char_set = n1.char_set.union(n2.char_set)
            stack.append(nfa)

        elif t == '|':
            n2 = stack.pop()
            n1 = stack.pop()
            s = new_state()
            a = new_state()
            s.epsilon += [n1.start, n2.start]
            n1.accept.epsilon.append(a)
            n2.accept.epsilon.append(a)
            nfa = NFA(s, a)
            nfa.states = n1.states.union(n2.states).union({s, a})
            nfa.char_set = n1.char_set.union(n2.char_set)
            stack.append(nfa)

        elif t == '*':
            n = stack.pop()
            s = new_state()
            a = new_state()
            s.epsilon += [n.start, a]
            n.accept.epsilon += [n.start, a]
            nfa = NFA(s, a)
            nfa.states = n.states.union({s, a})
            nfa.char_set = n.char_set
            stack.append(nfa)

    final_nfa = stack.pop()
    return final_nfa
  # ---------------- DFA ----------------
def epsilon_closure(states):
    stack = list(states)
    closure = set(states)
    while stack:
        state = stack.pop()
        for t in state.epsilon:
            if t not in closure:
                closure.add(t)
                stack.append(t)
    return closure


def move(states, symbol):
    return {t for s in states for t in s.edges.get(symbol, [])}


def nfa_to_dfa(nfa):
    symbols = nfa.char_set

    dfa = {}
    start_closure = frozenset(epsilon_closure({nfa.start}))
    finals = set()
    unmarked = deque([start_closure])
    dfa[start_closure] = {}

    if nfa.accept in start_closure:
        finals.add(start_closure)

    while unmarked:
        current = unmarked.popleft()
        for sym in symbols:
            moved = move(current, sym)
            if not moved:
                continue
            closure = frozenset(epsilon_closure(moved))
            if closure not in dfa:
                dfa[closure] = {}
                unmarked.append(closure)
                if nfa.accept in closure:
                    finals.add(closure)
            dfa[current][sym] = closure

    return dfa, start_closure, finals, symbols
  # ---------------- DFA 最小化 ----------------
def minimize_dfa(dfa, start, finals, symbols):
    # 初始划分为接受状态和非接受状态
    P = []
    finals_group = set()
    non_finals_group = set()

    for state in dfa:
        if state in finals:
            finals_group.add(state)
        else:
            non_finals_group.add(state)
    if finals_group:
        P.append(finals_group)
    if non_finals_group:
        P.append(non_finals_group)

    W = P.copy()

    while W:
        A = W.pop()
        for c in symbols:
            X = {s for s in dfa if c in dfa[s] and dfa[s][c] in A}
            new_P = []
            for Y in P:
                i = X & Y
                d = Y - X
                if i and d:
                    new_P.append(i)
                    new_P.append(d)
                    if Y in W:
                        W.remove(Y)
                        W.append(i)
                        W.append(d)
                    else:
                        W.append(i if len(i) <= len(d) else d)
                else:
                    new_P.append(Y)
            P = new_P

    # 重新编号最小DFA状态，从0开始
    group_map = {}
    for idx, group in enumerate(P):
        for state in group:
            group_map[state] = idx

    min_dfa = {i: {} for i in range(len(P))}
    for state in dfa:
        for sym, tgt in dfa[state].items():
            min_dfa[group_map[state]][sym] = group_map[tgt]

    min_start = group_map[start]
    min_finals = {group_map[s] for s in finals}

    return min_dfa, min_start, min_finals
  # ---------------- 字符串匹配 ----------------
def match_string_with_min_dfa(dfa, start, finals, input_str):
    state = start
    for c in input_str:
        if c not in dfa[state]:
            return False
        state = dfa[state][c]
    return state in finals
