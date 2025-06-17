from agents import AgentManager, get_latest_agent_msg

def run_debug_prompt_loop():
    agent_manager = AgentManager()

    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            resp = agent_manager.invoke_with_text(user_input)
            message = get_latest_agent_msg(resp)

            for m in resp["messages"]:
                # print(type(m))
                # print(m.content)
                m.pretty_print()

            # print(f"AI> {message}")

        except Exception as ex:
            print(f"error: {ex}")
            break


if __name__ == "__main__":
    run_debug_prompt_loop()
