from ai.agent_manager import RuntimeAgentManager

def run_debug_prompt_loop():
    agent_manager = RuntimeAgentManager()

    while True:
        try:
            user_input = input("user> ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            response = agent_manager.invoke_main_with_text("TEMP_USERNAME", user_input)
            print(f"AI> {response}")

            for t in agent_manager.tracer.get_history():
                print(t.model_dump_json())

        except Exception as ex:
            print(f"error: {ex}")
            break

def main():
    run_debug_prompt_loop()

if __name__ == "__main__":
    main()