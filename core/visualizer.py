import graphviz
def visualize_nfa(nfa):
    dot = graphviz.Digraph()
    visited = set()

    def dfs(state):
        if state in visited:
            return
        visited.add(state)
        shape = 'doublecircle' if state == nfa.accept else 'circle'
        dot.node(state.id, shape=shape)

        for symbol, targets in state.edges.items():
            for t in targets:
                dot.edge(state.id, t.id, label=symbol)
                dfs(t)

        for t in state.epsilon:
            dot.edge(state.id, t.id, label='ε')
            dfs(t)

    dfs(nfa.start)
    dot.node("start", shape="plaintext")
    dot.edge("start", nfa.start.id, label="start")
    return dot
def visualize_dfa(dfa, start, finals):
    dot = graphviz.Digraph()
    state_names = {s: f"S{i}" for i, s in enumerate(dfa)}

    for s in dfa:
        shape = 'doublecircle' if s in finals else 'circle'
        label = ','.join(str(state.id) for state in s)
        dot.node(state_names[s], label=label, shape=shape)
        for sym, tgt in dfa[s].items():
            dot.edge(state_names[s], state_names[tgt], label=sym)

    dot.node("start", shape="plaintext")
    dot.edge("start", state_names[start], label="start")
    return dot
def visualize_min_dfa(dfa, start, finals):
    dot = graphviz.Digraph()
    for s in dfa:
        shape = 'doublecircle' if s in finals else 'circle'
        dot.node(f"S{s}", shape=shape)
        for sym, tgt in dfa[s].items():
            dot.edge(f"S{s}", f"S{tgt}", label=sym)
    dot.node("start", shape="plaintext")
    dot.edge("start", f"S{start}", label="start")
    return dot
