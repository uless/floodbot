# test_multiturn_all_groups.py
#import streamlit as st
from utils.chatbot import (
    get_response_control,
    get_response_high_proc_low_dist,
    get_response_low_proc_high_dist,
    get_response_high_proc_high_dist
)

# 创建一个简单的假的 session_state，用于替代 Streamlit 内置的会话状态
class FakeSessionState(dict):
    pass

fake_session_state = FakeSessionState()
st.session_state = fake_session_state

def test_multiturn(group_name, response_func, inputs):
    print("==== Experiment group：", group_name, "====")
    # 重置会话状态中的 question_round，确保每个测试组从第一轮开始
    st.session_state["question_round"] = 1
    for i, user_input in enumerate(inputs, start=1):
        response = response_func(user_input)
        print(f"Round {i} ")
        print("User said：", user_input)
        print("Model said：", response)
        print("Current question_round：", st.session_state.get("question_round"))
        print("-" * 20)

def main():
    # 定义每轮对话的输入，可以根据实际情况调整
    test_inputs = [
        "12345",         # 第一轮，假设输入一个邮编
        "I need urgent food.",   # 第二轮，提出请求
        "I need some money for my pet.",  # 第三轮，继续对话
        "I want to ensure my safety when evacuate."            # 第四轮，对话结束
    ]
    
    # 分别测试四个不同的模型组
    test_multiturn("Control", get_response_control, test_inputs)
    test_multiturn("High Procedural + Low Distributive", get_response_high_proc_low_dist, test_inputs)
    test_multiturn("Low Procedural + High Distributive", get_response_low_proc_high_dist, test_inputs)
    test_multiturn("High Procedural + High Distributive", get_response_high_proc_high_dist, test_inputs)

if __name__ == '__main__':
    main()
