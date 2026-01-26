use dioxus::prelude::*;
use lazy_static::lazy_static;
use std::collections::HashMap;
use unicode_normalization::UnicodeNormalization;

// --- Data Structures ---

type CodeMap = HashMap<u32, String>;

lazy_static! {
    static ref MAP_0: CodeMap = parse_tsv(include_str!("../../uni2tipa/uni2tipa0.tsv"));
    static ref MAP_1: CodeMap = parse_tsv(include_str!("../../uni2tipa/uni2tipa1.tsv"));
    static ref MAP_2: CodeMap = parse_tsv(include_str!("../../uni2tipa/uni2tipa2.tsv"));
    static ref MAP_TONE: CodeMap = parse_tsv(include_str!("../../uni2tipa/uni2tipa-tone.tsv"));
}

fn parse_tsv(content: &str) -> CodeMap {
    content.lines()
        .filter(|l| !l.is_empty())
        .filter_map(|line| {
            let mut parts = line.split('\t');
            let hex = parts.next()?;
            let val = parts.next()?;
            let code = u32::from_str_radix(hex, 16).ok()?;
            Some((code, val.to_string()))
        })
        .collect()
}

#[derive(Clone, Debug, PartialEq)]
pub enum Token {
    Known(String),
    Unknown(char),
}

struct Unit {
    base: u32,
    modifiers: Vec<u32>,
}

// --- Converter Logic ---

struct IpaConverter;

impl IpaConverter {
    pub fn convert(input: &str) -> Vec<Token> {
        // decompose
        let codes: Vec<u32> = input.chars()
            .flat_map(|c| c.nfd())
            .map(|c| c as u32)
            .collect();
        
        // group unicodes (base + modifiers)
        let units = Self::group_units(codes);
        
        // translate units to TIPA tokens
        let mut tokens = Self::translate_units(units);
        
        // process binary modifiers (tie bars)
        Self::post_process(&mut tokens);
        
        tokens
    }

    fn group_units(codes: Vec<u32>) -> Vec<Unit> {
        let mut units = Vec::new();
        let mut i = codes.len() as isize - 1;

        while i >= 0 {
            let curr = codes[i as usize];
            let mut modifiers = Vec::new();

            if MAP_TONE.contains_key(&curr) {
                // Tonal grouping
                let base = curr;
                i -= 1;
                while i >= 0 && MAP_TONE.contains_key(&codes[i as usize]) {
                    modifiers.push(codes[i as usize]);
                    i -= 1;
                }
                modifiers.reverse();
                units.push(Unit { base, modifiers });
            } else {
                // Standard grouping
                while i >= 0 && MAP_1.contains_key(&codes[i as usize]) {
                    modifiers.push(codes[i as usize]);
                    i -= 1;
                }
                modifiers.reverse();
                
                if i >= 0 {
                    let base = codes[i as usize];
                    i -= 1;
                    units.push(Unit { base, modifiers });
                } else {
                    // Dangling modifiers
                    for m in modifiers.into_iter().rev() {
                        units.push(Unit { base: m, modifiers: Vec::new() });
                    }
                }
            }
        }
        units.reverse();
        units
    }

    fn translate_units(units: Vec<Unit>) -> Vec<Token> {
        units.into_iter().map(|u| {
            if MAP_TONE.contains_key(&u.base) {
                let mut tone_str = u.modifiers.iter()
                    .filter_map(|m| MAP_TONE.get(m))
                    .cloned()
                    .collect::<String>();
                tone_str.push_str(MAP_TONE.get(&u.base).unwrap());
                Token::Known(format!("\\tone{{{}}}", tone_str))
            } else {
                match MAP_0.get(&u.base) {
                    Some(base_tipa) => {
                        let res = u.modifiers.iter()
                            .filter_map(|m| MAP_1.get(m))
                            .fold(base_tipa.clone(), |acc, mod_tipa| {
                                format!("{}{{{}}}", mod_tipa, acc)
                            });
                        Token::Known(res)
                    }
                    None => Token::Unknown(std::char::from_u32(u.base).unwrap_or('?')),
                }
            }
        }).collect()
    }

    fn post_process(tokens: &mut Vec<Token>) {
        let mut i = 0;
        while i + 1 < tokens.len() {
            let mut merged = false;
            if let Token::Unknown(c) = tokens[i] {
                if let Some(cmd) = MAP_2.get(&(c as u32)) {
                    if i > 0 && i + 1 < tokens.len() {
                        let prev = tokens[i-1].raw();
                        let next = tokens[i+1].raw();
                        tokens[i-1] = Token::Known(format!("{}{{{}{}}}", cmd, prev, next));
                        tokens.remove(i);
                        tokens.remove(i);
                        merged = true;
                    }
                }
            }
            if !merged { i += 1; }
        }
    }
}

impl Token {
    fn raw(&self) -> String {
        match self {
            Token::Known(s) => s.clone(),
            Token::Unknown(c) => c.to_string(),
        }
    }
}

// --- UI Components ---

fn main() {
    wasm_logger::init(wasm_logger::Config::default());
    launch(App);
}

#[component]
fn App() -> Element {
    let mut ipa_input = use_signal(|| "ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː".to_string());
    let tokens = use_memo(move || IpaConverter::convert(&ipa_input.read()));
    
    rsx! {
        div {
            style: "padding: 20px; max-width: 800px; margin: 0 auto; font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;",
            h1 { style: "color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; margin-top: 0;", "IPA to TIPA" }
            
            div { style: "margin: 25px 0;",
                label { display: "block", margin_bottom: "10px", font_weight: "600", color: "#34495e", "IPA Input" }
                textarea {
                    value: "{ipa_input}",
                    oninput: move |evt| ipa_input.set(evt.value()),
                    // Font set to Gentium Book Plus
                    style: "width: 100%; height: 120px; padding: 15px; border: 1px solid #bdc3c7; border-radius: 8px; font-size: 20px; box-sizing: border-box; transition: border-color 0.2s; outline: none; font-family: 'Gentium Book Plus', serif;",
                }
            }

            div { style: "margin: 25px 0;",
                label { display: "block", margin_bottom: "10px", font_weight: "600", color: "#34495e", "TIPA Output" }
                div {
                    style: "width: 100%; min-height: 100px; padding: 15px; border: 1px solid #bdc3c7; border-radius: 8px; background: #fdfdfd; font-size: 18px; white-space: pre-wrap; font-family: 'Cascadia Code', 'Fira Code', 'Courier New', monospace; line-height: 1.6;",
                    for token in tokens.read().iter() {
                        match token {
                            Token::Known(s) => rsx! { span { "{s}" } },
                            Token::Unknown(c) => rsx! { span { style: "color: #e74c3c; font-weight: bold; background: #fee2e2; padding: 1px 3px; border-radius: 3px; font-family: 'Gentium Book Plus', serif;", "{c}" } },
                        }
                    }
                }
            }
        }
    }
}

// --- Tests ---

#[cfg(test)]
mod tests {
    use super::*;

    fn to_str(tokens: Vec<Token>) -> String {
        tokens.iter().map(|t| t.raw()).collect()
    }

    #[test]
    fn test_basics() {
        assert!(to_str(IpaConverter::convert("ti")).contains("t"));
    }

    #[test]
    fn test_super() {
        let ipa = "ˈtʰiː ˌnãɪ̃ɾ̃iˈtʰu̟ː ˈd͡ʒeɪ ˈpʰiː";
        let expected = r#""t\super{h}i: ""n\~{a}\~{I}\~{R}i"t\super{h}\|+{u}: "\t{dZ}eI "p\super{h}i:"#;
        assert_eq!(to_str(IpaConverter::convert(ipa)), expected);
    }

    #[test]
    fn test_tone() {
        let ipa = "tʰjɛn˧˥ ʈʂʊŋ˥ pɑŋ˥ pʰɤŋ˧˥";
        let expected = r#"t\super{h}jEn\tone{35} \:t{}\:s{}UN\tone{5} pAN\tone{5} p\super{h}7N\tone{35}"#;
        assert_eq!(to_str(IpaConverter::convert(ipa)), expected);
    }
}
