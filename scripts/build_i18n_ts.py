"""Assembles the final frontend-react/src/lib/i18n.ts from:
- ENGLISH_SOURCE in generate_i18n_translations.py (single source of truth for all keys)
- the hand-reviewed existing hi/mr translations (kept as-is, not regenerated)
- scripts/i18n_translations_output.json (freshly generated hi/mr new-keys + or/gu/bn all-keys)

Run after generate_i18n_translations.py. Writes directly to i18n.ts.
"""

import json

from generate_i18n_translations import ENGLISH_SOURCE, EXISTING_KEYS

# Hand-reviewed, already in the repo -- preserved verbatim, not regenerated.
EXISTING_HI = {
    "landing.login": "लॉग इन",
    "landing.signup": "साइन अप",
    "hero.headline": "अपनी भाषा में शिकायत करें। उनकी भाषा में पढ़ी जाएगी।",
    "hero.sub": "JanMitra AI आपकी आवाज़ को शिकायत में बदल देता है — आपका स्थानीय कर्मचारी उसे अपनी भाषा में अपने आप अनुवादित पढ़ सकता है।",
    "hero.cta.primary": "शुरू करें",
    "hero.cta.secondary": "लॉग इन",
    "auth.field.phone": "फ़ोन नंबर",
    "auth.field.name": "पूरा नाम",
    "auth.field.password": "पासवर्ड",
    "auth.login.button": "लॉग इन",
    "auth.signup.button": "खाता बनाएं",
    "auth.login.switch": "नए हैं?",
    "auth.login.switchlink": "खाता बनाएं",
    "auth.signup.switch": "पहले से खाता है?",
    "auth.signup.switchlink": "लॉग इन",
    "auth.signup.workernote": "सफाई कर्मचारी हैं? कर्मचारी खाते आपके वार्ड के सुपर एडमिन द्वारा बनाए जाते हैं — उनसे अपनी लॉगिन जानकारी लें।",
}
EXISTING_MR = {
    "landing.login": "लॉग इन",
    "landing.signup": "साइन अप",
    "hero.headline": "तुमच्या भाषेत तक्रार करा. त्यांच्या भाषेत वाचली जाईल.",
    "hero.sub": "JanMitra AI तुमचा आवाज तक्रारीत बदलतो — तुमचा स्थानिक कर्मचारी ती स्वतःच्या भाषेत आपोआप भाषांतरित वाचू शकतो.",
    "hero.cta.primary": "सुरुवात करा",
    "hero.cta.secondary": "लॉग इन",
    "auth.field.phone": "फोन नंबर",
    "auth.field.name": "पूर्ण नाव",
    "auth.field.password": "पासवर्ड",
    "auth.login.button": "लॉग इन",
    "auth.signup.button": "खाते तयार करा",
    "auth.login.switch": "नवीन आहात?",
    "auth.login.switchlink": "खाते तयार करा",
    "auth.signup.switch": "आधीच खाते आहे?",
    "auth.signup.switchlink": "लॉग इन",
    "auth.signup.workernote": "सफाई कर्मचारी आहात? कर्मचारी खाती तुमच्या वॉर्डच्या सुपर अ‍ॅडमिनद्वारे तयार केली जातात — त्यांच्याकडून लॉगिन तपशील घ्या.",
}

NATIVE_NAMES = {
    "en": ("English", "English"),
    "hi": ("हिन्दी", "Hindi"),
    "mr": ("मराठी", "Marathi"),
    "or": ("ଓଡ଼ିଆ", "Odia"),
    "gu": ("ગુજરાતી", "Gujarati"),
    "bn": ("বাংলা", "Bengali"),
}

LANG_ORDER = ["en", "hi", "mr", "or", "gu", "bn"]


def ts_string(s: str) -> str:
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def main() -> None:
    with open("scripts/i18n_translations_output.json", encoding="utf-8") as f:
        generated = json.load(f)

    full: dict[str, dict[str, str]] = {lang: {} for lang in LANG_ORDER}
    full["en"] = dict(ENGLISH_SOURCE)
    for key in EXISTING_KEYS:
        full["hi"][key] = EXISTING_HI[key]
        full["mr"][key] = EXISTING_MR[key]
    for lang in ["hi", "mr", "or", "gu", "bn"]:
        for key, text in generated.get(lang, {}).items():
            full[lang][key] = text

    # Sanity check: every language must have every key before we write anything.
    missing = {
        lang: [k for k in ENGLISH_SOURCE if k not in full[lang]]
        for lang in LANG_ORDER
    }
    missing = {k: v for k, v in missing.items() if v}
    if missing:
        raise SystemExit(f"Missing translations, aborting: {missing}")

    lines = []
    lines.append('export type LangCode = "en" | "hi" | "mr" | "or" | "gu" | "bn";')
    lines.append("")
    lines.append("export const SUPPORTED_LANGUAGES: Record<LangCode, { name: string; gloss: string }> = {")
    for lang in LANG_ORDER:
        native, gloss = NATIVE_NAMES[lang]
        lines.append(f'  {lang}: {{ name: {ts_string(native)}, gloss: {ts_string(gloss)} }},')
    lines.append("};")
    lines.append("")
    lines.append("type Dict = Record<string, string>;")
    lines.append("")
    lines.append("export const I18N: Record<LangCode, Dict> = {")
    for lang in LANG_ORDER:
        lines.append(f"  {lang}: {{")
        for key in ENGLISH_SOURCE:  # stable key order across all languages
            lines.append(f"    {ts_string(key)}: {ts_string(full[lang][key])},")
        lines.append("  },")
    lines.append("};")
    lines.append("")
    lines.append("export function t(lang: LangCode, key: string): string {")
    lines.append("  return I18N[lang]?.[key] ?? I18N.en[key] ?? key;")
    lines.append("}")
    lines.append("")

    out_path = "frontend-react/src/lib/i18n.ts"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Wrote {out_path}: {len(ENGLISH_SOURCE)} keys x {len(LANG_ORDER)} languages")


if __name__ == "__main__":
    main()
