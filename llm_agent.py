from groq import Groq
from dotenv import load_dotenv
import json
import os

from action_executor import ActionExecutor


class ConversationAgent:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.model_name = "openai/gpt-oss-120b"        
        self.action_executor_object = ActionExecutor()
        self.conversation_history = [
            {
                "role": "system",
                "content": self.read_file(file_path="./context.txt"),
            }
        ]

    @staticmethod
    def read_file(file_path):
        with open(file_path, "r") as file:
            return file.read()

    def update_conversation_history(self, role, text_interaction):
        self.conversation_history.append(
            {
                "role": role,
                "content": text_interaction,
            }
        )

    def get_conversation_history(self):
        visible_messages = []
        for message in self.conversation_history:
            if message["role"] in ("user", "assistant") and "tool_calls" not in message:
                visible_messages.append(message)
        return visible_messages

    def transcribe(self, audio_interaction):
        transcription = self.groq_client.audio.transcriptions.create(
            file=("audio.wav", audio_interaction),
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            timestamp_granularities=["word", "segment"],
            temperature=0.0,
        )
        return transcription.text

    def call_groq(self):
        # Un seul endroit qui parle à Groq : plus simple à relire et à corriger
        return self.groq_client.chat.completions.create(
            model=self.model_name,
            messages=self.conversation_history,
            tools=ActionExecutor.get_tools_description(),
        ).choices[0].message

    @staticmethod
    def build_tool_calls_message(response_message):
        # Transforme la réponse de Groq en dictionnaire, pour rester cohérent avec le reste de l'historique
        tool_calls = []
        for tool_call in response_message.tool_calls:
            tool_calls.append(
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments,
                    },
                }
            )
        return {
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": tool_calls,
        }

    def run_tool_call(self, tool_call):
        tool_name = tool_call.function.name
        tool_arguments = json.loads(tool_call.function.arguments)
        return self.action_executor_object.execute_action(tool_name, tool_arguments)

    def ask_llm(self, text_interaction):
        history_length_before = len(self.conversation_history)
        try:
            return self.run_conversation_turn(text_interaction)
        except Exception as error:
            print("[erreur]", error)
            # On efface les messages ajoutés par le tour qui a échoué
            del self.conversation_history[history_length_before:]
            return "Désolé, je n'ai pas réussi à traiter ta demande."

    def run_conversation_turn(self, text_interaction):
        self.update_conversation_history(role="user", text_interaction=text_interaction)
        response_message = self.call_groq()

        if not response_message.tool_calls:
            self.update_conversation_history(role="assistant", text_interaction=response_message.content)
            return response_message.content

        self.conversation_history.append(self.build_tool_calls_message(response_message))

        for tool_call in response_message.tool_calls:
            action_result = self.run_tool_call(tool_call)
            self.conversation_history.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": action_result,
                }
            )

        final_message = self.call_groq()
        self.update_conversation_history(role="assistant", text_interaction=final_message.content)
        return final_message.content


if __name__ == "__main__":
    conversation_agent_object = ConversationAgent()
    while True:
        question = input("\nToi : ")
        if question == "stop":
            break
        print("Jarvis :", conversation_agent_object.ask_llm(question))