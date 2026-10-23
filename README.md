# CodeAlpha AI Internship Projects

This repository contains my Artificial Intelligence internship tasks completed under CodeAlpha — upgraded from the original submissions into tools that are useful beyond the internship.

## Task 1: Language Translation Tool
A Python translator built on `deep-translator` (Google Translate).

```bash
cd Task1_Translator
python translator.py "Hello, how are you?"            # -> Hindi (default)
python translator.py --to es "Good morning"           # -> Spanish
python translator.py --from en --to hi "Thank you"    # explicit source
python translator.py --file phrases.txt --to hi       # translate a file, line by line
python translator.py --list-languages                 # supported language codes
python translator.py                                  # interactive mode
```

## Task 2: Cybersecurity FAQ Chatbot
An offline chatbot that answers cybersecurity questions from a built-in
knowledge base of 20 topics (phishing, ransomware, 2FA, SQL injection,
XSS, incident response, careers…). Matching ignores case/punctuation,
understands synonyms (OTP → 2FA), scores partial matches, and suggests
topics when it cannot answer.

```bash
cd Task2_Chatbot
python chatbot.py                          # interactive chat
python chatbot.py "what is phishing?"      # one-shot question
python chatbot.py --topics                 # list all topics
```

No internet needed for the chatbot — the knowledge base is built in.

## Technologies Used
- Python
- deep-translator (Task 1 only)

## Setup & Tests
```bash
pip install -r requirements.txt
python -m pytest tests/ -q   # 8 offline tests, no network needed
```

## Output
Screenshots from the original internship submission are included in the respective task folders (`Task1_Output.png`, `Task2_FAQ_Chatbot_Output.png`).

## License
MIT
