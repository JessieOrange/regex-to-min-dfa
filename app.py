import streamlit as st
from core.regex_engine import (
    regex_to_rpn, rpn_to_nfa, nfa_to_dfa,
    minimize_dfa, match_string_with_min_dfa
)
from core.visualizer import visualize_nfa, visualize_dfa, visualize_min_dfa

st.title("正则表达式 → 最小DFA 可视化工具")

regex = st.text_input("输入正则表达式：", "(a|b)*abb")

if regex:
    st.subheader("1️⃣ 逆波兰表达式")
    rpn = regex_to_rpn(regex)
    st.code(' '.join(rpn))

    st.subheader("2️⃣ NFA 可视化")
    nfa = rpn_to_nfa(rpn)
    st.graphviz_chart(visualize_nfa(nfa))

    st.subheader("3️⃣ DFA 可视化")
    dfa, start_dfa, finals_dfa, symbols = nfa_to_dfa(nfa)
    st.graphviz_chart(visualize_dfa(dfa, start_dfa, finals_dfa))

    st.subheader("4️⃣ 最小DFA 可视化")
    min_dfa, min_start, min_finals = minimize_dfa(dfa, start_dfa, finals_dfa, symbols)
    st.graphviz_chart(visualize_min_dfa(min_dfa, min_start, min_finals))

    st.subheader("5️⃣ 字符串匹配")
    input_str = st.text_input("请输入要匹配的字符串：", "abb")
    if input_str:
        matched = match_string_with_min_dfa(min_dfa, min_start, min_finals, input_str)
        st.success("✅ 匹配成功！" if matched else "❌ 不匹配。")
