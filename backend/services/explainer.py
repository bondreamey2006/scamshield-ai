import os
import asyncio
import google.generativeai as genai
from typing import List

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

try:
    model = genai.GenerativeModel("gemini-1.5-flash")
except Exception:
    model = None

async def generate_explanation(verdict: str, score: int, signals: List[str]) -> str:
    """
    Calls Gemini API to explain the verdict, enforcing a 2-second timeout.
    Falls back to deterministic templates if the LLM fails or times out.
    """
    fallbacks = {
        "green": "No strong risk signals found. Proceed if you are comfortable.",
        "yellow": "Unknown or cautionary evidence exists. Please verify through an official channel.",
        "red": f"High risk detected due to: {', '.join(signals)}. Do not proceed."
    }

    if not model or not os.getenv("GEMINI_API_KEY"):
        return fallbacks.get(verdict, "Unable to verify risk level.")

    prompt = (
        f"You are a pre-payment safety assistant. The backend scored this transaction {score}/100 "
        f"and gave a {verdict.upper()} verdict based on these signals: {signals}. "
        f"Write exactly 1-2 short, plain-language sentences explaining to a non-technical user "
        f"why they received this verdict. Do NOT state the numerical score. Do NOT change the verdict."
    )

    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(model.generate_content, prompt),
            timeout=2.0
        )
        return response.text.strip()
    except asyncio.TimeoutError:
        return fallbacks.get(verdict, "Transaction flagged by internal heuristics.")
    except Exception:
        return fallbacks.get(verdict, "Error communicating with AI explainer.")