export type LangCode = "mr" | "hi" | "en";

export const SUPPORTED_LANGUAGES: Record<LangCode, { name: string }> = {
  mr: { name: "मराठी" },
  hi: { name: "हिंदी" },
  en: { name: "English" },
};

type Dict = Record<string, string>;

export const I18N: Record<LangCode, Dict> = {
  en: {
    "landing.login": "Log in",
    "landing.signup": "Sign up",
    "hero.headline": "Report it in your language. It gets read in theirs.",
    "hero.sub":
      "JanMitra AI turns your voice into a complaint your local worker can read — translated automatically, no matter which language either of you speaks.",
    "hero.cta.primary": "Get started",
    "hero.cta.secondary": "Log in",
    "auth.field.phone": "Phone number",
    "auth.field.name": "Full name",
    "auth.field.password": "Password",
    "auth.login.button": "Log in",
    "auth.signup.button": "Create account",
    "auth.login.switch": "New here?",
    "auth.login.switchlink": "Create an account",
    "auth.signup.switch": "Already have an account?",
    "auth.signup.switchlink": "Log in",
    "auth.signup.langlocked": "Signing up in",
    "auth.signup.changelang": "change",
    "auth.signup.workernote":
      "Sanitation worker? Worker accounts are created by your ward's Super Admin — ask them for your login details.",
  },
  mr: {
    "landing.login": "लॉग इन",
    "landing.signup": "साइन अप",
    "hero.headline": "तुमच्या भाषेत तक्रार करा. त्यांच्या भाषेत वाचली जाईल.",
    "hero.sub":
      "JanMitra AI तुमचा आवाज तक्रारीत बदलतो — तुमचा स्थानिक कर्मचारी ती स्वतःच्या भाषेत आपोआप भाषांतरित वाचू शकतो.",
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
    "auth.signup.langlocked": "भाषा निवडली:",
    "auth.signup.changelang": "बदला",
    "auth.signup.workernote":
      "सफाई कर्मचारी आहात? कर्मचारी खाती तुमच्या वॉर्डच्या सुपर अ‍ॅडमिनद्वारे तयार केली जातात — त्यांच्याकडून लॉगिन तपशील घ्या.",
  },
  hi: {
    "landing.login": "लॉग इन",
    "landing.signup": "साइन अप",
    "hero.headline": "अपनी भाषा में शिकायत करें। उनकी भाषा में पढ़ी जाएगी।",
    "hero.sub":
      "JanMitra AI आपकी आवाज़ को शिकायत में बदल देता है — आपका स्थानीय कर्मचारी उसे अपनी भाषा में अपने आप अनुवादित पढ़ सकता है।",
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
    "auth.signup.langlocked": "चुनी गई भाषा:",
    "auth.signup.changelang": "बदलें",
    "auth.signup.workernote":
      "सफाई कर्मचारी हैं? कर्मचारी खाते आपके वार्ड के सुपर एडमिन द्वारा बनाए जाते हैं — उनसे अपनी लॉगिन जानकारी लें।",
  },
};

export function t(lang: LangCode, key: string): string {
  return I18N[lang]?.[key] ?? I18N.en[key] ?? key;
}
