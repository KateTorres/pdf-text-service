from src.utils.text_cleaning import process_extracted_text

sample_cyrillic = """
Это пример текста.
Следующая строка -
с переносом слов.
Hello world text in Latin.
"""

sample_english = """
This is a test text.
It con-
tinues on the next line.
123 456
Пример текста на кириллице.
"""

print("\n--- Cyrillic mode ---")
print(process_extracted_text(sample_cyrillic, language="cyrillic"))

print("\n--- English mode ---")
print(process_extracted_text(sample_english, language="english"))
