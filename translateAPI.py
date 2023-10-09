from google.cloud import translate
import config


def translate_text(text: str, target_language_code: str) -> translate.Translation:
    PROJECT_ID = config.PROJECT_ID
    PARENT = f"projects/{PROJECT_ID}"
    client = translate.TranslationServiceClient()
    response = client.translate_text(
        parent=PARENT,
        contents=[text],
        target_language_code=target_language_code,
    )
    return response.translations[0]


