import os
import asyncio
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("API_KEY")
genai.configure(api_key=api_key)

async def get_answer_from_context(context: list[str], question: str) -> str:

    #Add parameters: context and a question.
    try:
        system_instruction = (
            "You are a highly precise and reliable assistant. "
            "Answer the user’s question using ONLY the provided context. "
            "Do NOT guess, infer, or use outside knowledge. "
            "When giving an answer, provide it in a detailed and structured manner, explaining each relevant part clearly. "
            "Use complete sentences, examples, and step-by-step explanations where helpful so that even someone with no prior knowledge can fully understand. "
            "If multiple context passages are provided, carefully integrate them into a single coherent and thorough answer without assuming anything beyond what is written. "
            "If you notice minor typos or spelling errors in the context, silently correct them in your answer, but do not alter or replace entire words."
        )

        # Context and question is just for testing, will be replaced later when previous tickets are ready.
        prompt = f"""{system_instruction}
        CONTEXT: {context}
        QUESTION:{question}
        """

        def call_gemini():
            model = genai.GenerativeModel("gemini-2.5-flash-lite")
            return model.generate_content(prompt)

        response = await asyncio.to_thread(call_gemini)

        print(response.text)

        return response.text.strip()

    except TimeoutError:
        return "The server is busy. Please try again shortly."
    except Exception as e:
        print(f"Error calling Gemini: {e}")
        return "Something went wrong while generating the answer."