import os
from openai import OpenAI

client = OpenAI(
    api_key=os.getenv("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1"
)

def generar_respuesta(texto):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "Sos un vendedor de un negocio online en Argentina. Respondé corto, amable y profesional."
                },
                {
                    "role": "user",
                    "content": texto
                }
            ],
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        print("ERROR IA:", e)
        return "Gracias por tu mensaje 🙌"