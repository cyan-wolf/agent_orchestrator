from server.agents import AgentManager

def run_debug_prompt_loop():
    agent_manager = AgentManager()

    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            response = agent_manager.invoke_main_with_text(user_input)
            print(f"AI> {response}")

            for t in agent_manager.tracer.get_history():
                print(t)

        except Exception as ex:
            print(f"error: {ex}")
            break
