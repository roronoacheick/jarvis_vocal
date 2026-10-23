from groq import Groq
from dotenv import load_dotenv
import os


class ConversationAgent:
    def __init__(self):
        load_dotenv()
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
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


if __name__ == "__main__":
    conversation_agent_object = ConversationAgent()
    conversation_agent_object.update_conversation_history(role="user", text_interaction="bonjour")
    conversation_agent_object.update_conversation_history(role="assistant", text_interaction="salut !")
    print(conversation_agent_object.get_conversation_history())