"""Cybersecurity FAQ Chatbot.

Ask questions about cybersecurity topics and get plain-English answers.
The knowledge base and matching engine are pure Python — no internet
needed. Matching is forgiving: it ignores case/punctuation, understands
a few synonyms, scores partial matches, and suggests the closest topic
when it cannot answer directly.

Run interactively:   python chatbot.py
Ask one question:    python chatbot.py "what is phishing?"
List topics:         python chatbot.py --topics
"""
from __future__ import annotations

import argparse
import re
import sys

# topic -> (keywords, answer). Keywords drive matching; keep them natural.
KNOWLEDGE_BASE: dict[str, tuple[list[str], str]] = {
    "hacking": (["hacking", "hacker", "hack"],
        "Hacking is the practice of finding and exploiting weaknesses in systems. "
        "Ethical hackers do it with permission to make systems safer; doing it "
        "without permission is a crime."),
    "ethical hacking": (["ethical hacking", "white hat", "penetration testing", "pentest"],
        "Ethical hacking (penetration testing) means attacking a system with the "
        "owner's written permission to find flaws before criminals do. Always work "
        "inside an agreed scope and rules of engagement."),
    "bug bounty": (["bug bounty", "bounty", "hackerone", "bugcrowd"],
        "Bug bounty programs pay security researchers for responsibly reporting "
        "real vulnerabilities. Platforms like HackerOne and Bugcrowd list programs "
        "with clear scope and payout rules."),
    "phishing": (["phishing", "fake email", "scam email", "spear phishing"],
        "Phishing is a fake message (email, SMS, call) that tricks you into giving "
        "up passwords, OTPs or money. Check the sender address, never share OTPs, "
        "and open the real app/website yourself instead of tapping links."),
    "sql injection": (["sql injection", "sqli", "sql attack"],
        "SQL injection tricks a website into running attacker SQL by putting code "
        "in input fields (like ' OR '1'='1). The defence is prepared statements / "
        "parameterised queries — never build SQL with string concatenation."),
    "xss": (["xss", "cross site scripting", "cross-site scripting"],
        "Cross-Site Scripting (XSS) lets attackers inject JavaScript into pages "
        "other users view, stealing sessions or defacing sites. Defend with output "
        "encoding, input validation and a Content-Security-Policy header."),
    "malware": (["malware", "virus", "trojan", "worm", "spyware"],
        "Malware is malicious software: viruses, worms, trojans, spyware. It spreads "
        "through cracked software, fake updates and malicious attachments. Keep "
        "systems updated and download only from official sources."),
    "ransomware": (["ransomware", "files encrypted", "locked files"],
        "Ransomware encrypts your files and demands payment for the key. Protect "
        "yourself with offline backups (3-2-1 rule), updates, and by never opening "
        "unknown attachments. Paying rarely guarantees recovery."),
    "password": (["password", "strong password", "password manager", "passphrase"],
        "Use a long, unique passphrase for every account (16+ characters) and store "
        "them in a password manager like Bitwarden. Reused passwords are the #1 way "
        "accounts get taken over after a breach."),
    "2fa": (["2fa", "two factor", "two-factor", "mfa", "otp", "authenticator"],
        "Two-factor authentication (2FA/MFA) adds a second proof — usually an "
        "authenticator app code — on top of your password. Prefer app-based codes "
        "or security keys over SMS, which attackers can intercept via SIM swap."),
    "vpn": (["vpn", "virtual private network"],
        "A VPN encrypts your traffic and routes it through a server, hiding it from "
        "the local network and your ISP. It helps on public Wi-Fi, but it does not "
        "make you anonymous or protect you from phishing and malware."),
    "firewall": (["firewall"],
        "A firewall filters network traffic by rules — allowing trusted connections "
        "and blocking the rest. Every OS has one built in; keep it on, and only open "
        "the ports you actually need."),
    "encryption": (["encryption", "encrypt", "https", "tls"],
        "Encryption scrambles data so only someone with the key can read it. HTTPS "
        "(TLS) encrypts web traffic in transit; tools like BitLocker/LUKS encrypt "
        "data at rest on your disk."),
    "social engineering": (["social engineering", "manipulation", "pretexting"],
        "Social engineering manipulates people — not machines — into giving access "
        "or information: fake IT calls, authority pressure, urgency. The defence is "
        "verifying requests through a separate, known channel."),
    "zero day": (["zero day", "zero-day", "0day"],
        "A zero-day is a vulnerability the vendor does not know about yet (zero days "
        "to fix it). They are rare and valuable; fast patching and defence-in-depth "
        "limit the damage once one is used."),
    "brute force": (["brute force", "password cracking", "dictionary attack"],
        "Brute force means trying passwords until one works. Defences: rate "
        "limiting, account lockout, strong passwords, 2FA, and breached-password "
        "blocklists."),
    "ddos": (["ddos", "denial of service", "dos attack"],
        "A DDoS attack floods a service with traffic from many machines (a botnet) "
        "until real users cannot reach it. Mitigation uses rate limiting, CDNs and "
        "upstream filtering."),
    "public wifi": (["public wifi", "public wi-fi", "free wifi", "wifi safety"],
        "Public Wi-Fi can be spied on or faked (evil-twin hotspots). Avoid banking "
        "on it, prefer mobile data or a VPN, turn off auto-connect, and check that "
        "sites use HTTPS."),
    "career": (["career", "job", "start cybersecurity", "learn cybersecurity", "roadmap"],
        "A practical path: learn networking + Linux basics, then security "
        "fundamentals (try TryHackMe/HackTheBox), build projects on GitHub, and "
        "certify when ready (Security+ / CEH are common first steps). Consistency "
        "beats speed."),
    "incident response": (["incident response", "breach", "hacked", "account hacked"],
        "If an account is hacked: change the password from a clean device, enable "
        "2FA, revoke other sessions, check recovery email/phone, and warn contacts. "
        "For companies, incident response follows: identify, contain, eradicate, "
        "recover, learn."),
}

SYNONYMS = {"otp": "2fa", "mfa": "2fa", "two factor": "2fa", "phish": "phishing",
            "ransom": "ransomware", "wifi": "public wifi", "wi-fi": "public wifi"}

FALLBACK = ("Sorry, I don't know that one yet. Type 'topics' to see what I can "
            "answer, or try rephrasing with a keyword like 'phishing' or 'vpn'.")


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s-]", " ", text.lower()).strip()


def find_answer(question: str) -> tuple[str, str | None]:
    """Return (answer, matched_topic). Topic is None when nothing matched."""
    q = _normalize(question)
    if not q:
        return FALLBACK, None
    for phrase, topic in SYNONYMS.items():
        if phrase in q:
            q_topic = topic
            if q_topic in KNOWLEDGE_BASE:
                return KNOWLEDGE_BASE[q_topic][1], q_topic
    best_topic, best_score = None, 0
    for topic, (keywords, _answer) in KNOWLEDGE_BASE.items():
        score = 0
        for kw in keywords:
            if kw in q:
                score += 10 + len(kw)          # full phrase hit
            else:
                words = set(q.split())
                score += 2 * sum(1 for w in kw.split() if w in words)
        if topic in q:
            score += 15
        if score > best_score:
            best_topic, best_score = topic, score
    if best_topic is not None and best_score >= 10:
        return KNOWLEDGE_BASE[best_topic][1], best_topic
    return FALLBACK, None


def list_topics() -> str:
    return "I can answer questions about:\n" + "\n".join(
        f" - {topic}" for topic in KNOWLEDGE_BASE)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Cybersecurity FAQ chatbot.")
    parser.add_argument("question", nargs="*", help="Ask a single question and exit.")
    parser.add_argument("--topics", action="store_true", help="List answerable topics.")
    args = parser.parse_args(argv)

    if args.topics:
        print(list_topics())
        return 0
    if args.question:
        answer, _ = find_answer(" ".join(args.question))
        print(answer)
        return 0

    print("=== Cybersecurity FAQ Chatbot (type 'exit' to quit, 'topics' to list) ===")
    while True:
        try:
            question = input("Ask: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        if question.lower() in ("exit", "quit", "bye"):
            print("Goodbye! Stay safe online.")
            break
        if question.lower() == "topics":
            print(list_topics())
            continue
        answer, _ = find_answer(question)
        print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
