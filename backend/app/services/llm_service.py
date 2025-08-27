import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

async def get_answer_from_context(CONTEXT: list[str], QUESTION:str) -> str:

    #Add parameters: context and a question.
    try:
        system_instruction = (
            "You are a highly precise and reliable assistant. "
            "Answer the user’s question using ONLY the provided context. "
            "Do NOT guess, infer, or use outside knowledge. "
            "If the answer is not explicitly present in the context, respond exactly with: \"I don't know\". "
            "Provide a concise, clear, and complete answer in plain text, without adding explanations, commentary, or extra information. "
            "If multiple context passages are provided, consider all of them but do not assume anything beyond what is written."
        )

        # Context and question is just for testing, will be replaced later when previous tickets are ready.
        prompt = f"""{system_instruction}
        CONTEXT: {CONTEXT}
        QUESTION:{QUESTION}
        """

        def call_gemini():
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            return model.generate_content(prompt)

        response = await asyncio.to_thread(call_gemini)

        return response.text.strip()

    except TimeoutError:
        return "The server is busy. Please try again shortly."
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Something went wrong while generating the answer."