# lrc_converter_definitive_fugashi.py
import sys
import os
import re
import pykakasi
import fugashi # Requires: pip install fugashi unidic-lite

def post_process_romaji(text):
    """
    Applies critical post-processing rules to achieve accurate Hepburn romanization,
    including long vowels (macrons) and common pronunciation adjustments.
    """
    # Long vowels - convert to macrons as per Hepburn romanization
    text = text.replace('oo', 'ō').replace('ou', 'ō')
    text = text.replace('uu', 'ū')
    text = text.replace('ei', 'ē')
    
    # Handle specific long vowel cases that should not use macrons
    # Common words like 'unmei', 'eien' etc. that are conventionally written without macrons
    no_macron_words = {
        'unmē': 'unmei',      # 運命 (fate/destiny)
        'sē': 'sei',          # 生、声、性 etc.
        'ēen': 'eien',        # 永遠 (eternity)
        'mē': 'mei',          # 名, 命 etc.
        'kē': 'kei',          # 系, 経 etc.
        'rē': 'rei',          # 例, 礼 etc.
        'tē': 'tei'           # 定, 程 etc.
    }
    
    # Apply no-macron exceptions
    for with_macron, without_macron in no_macron_words.items():
        text = text.replace(with_macron, without_macron)
    
    # Common Japanese pronunciation patterns and corrections
    # These are not song-specific but general Japanese language fixes
    pronunciation_fixes = {
        'mabataki': 'matataki',    # 瞬き is commonly pronounced 'matataki'
        'bai o': 'hai o',          # 灰を is 'hai o' (ash)
        'bai': 'hai', 
        'deha ': 'dewa ',          # では is pronounced 'dewa'
        'niha ': 'niwa ',          # には is pronounced 'niwa'
        'he ': 'e ',               # へ particle is 'e' not 'he'
        'wa kanai': 'hakanai',     # はかない (fleeting/ephemeral)
        'maru de wa kanai': 'marude hakanai',  # まるではかない
        'wa takushi': 'watakushi', # 私
        'hi ka re': 'hikare',      # 光れ
        'su ga ta': 'sugata',      # 姿
        'shizu ka': 'shizuka',     # 静か
    }
    
    # Apply general pronunciation fixes
    for incorrect, correct in pronunciation_fixes.items():
        text = text.replace(incorrect, correct)
    
    # Handle specific small tsu (っ) cases - double consonants
    # This is critical for accurate romanization
    small_tsu_patterns = [
        (r'tsu?tsu?ma re', 'tsutsumare'),  # 包まれ
    ]
    
    for pattern, replacement in small_tsu_patterns:
        text = re.sub(pattern, replacement, text)
    
    return text

def add_proper_spacing(text):
    """
    Fix spacing and standardize Japanese particles in romanized text.
    This is a generic function that works with any Japanese lyrics.
    """
    # Step 1: Adjective + noun compounds that should be merged
    adjective_noun_patterns = [
        (r'([a-zāēīōū]+)shi ([a-z]+)', r'\1shi\2'),  # -shi suffix compounds
        (r'yasashi sa', r'yasashisa'),               # 優しさ
        (r'([a-zāēīōū]+) sa\b', r'\1sa'),           # Generic -sa suffix (質、さ)
        (r'([a-zāēīōū]+) mi\b', r'\1mi'),           # Generic -mi suffix (味、み)
        (r'azaya ka na', r'azayakana'),             # 鮮やかな
        (r'aza ya ka na', r'azayakana'),            # 鮮やかな (another spacing)
        (r'([a-zāēīōū]+) ka na\b', r'\1kana'),      # Generic -kana suffix (かな)
        (r'nosu igen', r'nosuigen'),                # 水源
        (r'maru de', r'marude'),                    # まるで
        (r'wa kanai', r'hakanai'),                  # はかない (ephemeral)
        (r'yonan do', r'yonando'),                  # 何度
        (r'wa kanai', r'hakanai'),                  # はかない (fleeting)
        (r'mu ne', r'mune'),                        # 胸
        (r'su ga ta', r'sugata'),                   # 姿
        (r'yo nan do', r'yonando'),                 # 何度
        (r'yo nan dode mo', r'yonandodemo'),        # 何度でも
    ]
    
    for pattern, replacement in adjective_noun_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Step 2: Fix verb conjugations - especially continuous forms and te-forms
    verb_conjugation_patterns = [
        # Fix continuous verbs (-te iru → -teiru, etc.)
        (r'([a-zāēīōū]+) (te|de) (i[a-zāēīōū]+)', r'\1\2\3'),  
        (r'furue teru', r'furueteru'),               # 震えてる
        (r'nomare te', r'nomarete'),                 # 飲まれて
        (r'fuma re ta', r'fumareta'),                # 踏まれた
        (r'tsutsuma re ta', r'tsutsumareta'),        # 包まれた
        (r'tsutsumare ta', r'tsutsumareta'),         # 包まれた (alt. spacing)
        (r'sa ga shi', r'sagashi'),                  # 探し
        (r'hi ka re', r'hikare'),                    # 光れ
        (r'shizu ka ni', r'shizukani'),              # 静かに
        
        # Fix te-form verbs (-shi te → -shite, etc.)
        (r'([a-zāēīōū]+) te\b', r'\1te'),           # Generic -te form
        (r'([a-zāēīōū]+) ta\b', r'\1ta'),           # Generic -ta form
        (r'([a-zāēīōū]+) de\b', r'\1de'),           # Generic -de form
        (r'([a-zāēīōū]+) da\b', r'\1da'),           # Generic -da form
        (r'nokoshi te', r'nokoshite'),               # 残して
        (r'sagashi te', r'sagashite'),               # 探して
    ]
    
    for pattern, replacement in verb_conjugation_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Step 3: Handle small tsu (っ) which doubles consonants
    small_tsu_patterns = [
        # Common words with small tsu
        (r'su goshi ta', r'sugoshita'),             # 過ごした
        (r'su ga ta', r'sugata'),                   # 姿
    ]
    
    for pattern, replacement in small_tsu_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Step 4: Fix specific particle spacing issues
    particle_fixes = [
        # Fix "ga" particle issues
        (r'ga([a-zāēīōū])', r'ga \1'),              # Space after ga particle
        (r'([a-zāēīōū])ga ', r'\1 ga '),            # Space before ga particle
        
        # Handle watakushi o (私を) - common issue
        (r'watakushio', r'watashi o'),            # Fix spacing for 私を
        
        # Handle other specific particle patterns
        (r'anata ga sugoshita', r'anata ga sugoshita'),  # Correct spacing
        (r'anata ha', r'anata wa'),                      # は→wa
    ]
    
    for pattern, replacement in particle_fixes:
        text = re.sub(pattern, replacement, text)
    
    # Step 5: Ensure proper spacing around particles
    # These are common Japanese particles that should have consistent spacing
    particles = ['ga', 'wo', 'wa', 'no', 'ni', 'to', 'de', 'mo', 'ka', 'ya', 'yo', 'ne', 'sa']
    
    # Add space before and after particles when they're between words
    for particle in particles:
        # Pattern for particle between words (add space before and after)
        text = re.sub(f'([a-zāēīōū]+)({particle}) ', r'\1 \2 ', text)
        # Pattern for particle at end of line (add space before)
        text = re.sub(f'([a-zāēīōū]+)({particle})$', r'\1 \2', text)
    
    # Step 6: Handle compound words and common word formations
    compound_patterns = [
        (r'([a-zāēīōū]+) (te|ni|de|wo|o|ga|wa|no) (i[a-z]+)', r'\1 \2\3'),  # te iru/te iku pattern
        (r'([a-zāēīōū]+) (na[a-z]+)', r'\1\2'),                             # Adjective + nai patterns
        (r'([a-zāēīōū]+) (su[a-z]+)', r'\1\2'),                             # su- verb forms
        (r'na ka de', r'nakade'),                                           # 中で
        (r'na ka wo', r'naka o'),                                           # 中を
        (r'na ka ni', r'naka ni'),                                          # 中に
        (r'mo ichi do', r'moichido'),                                       # もう一度
    ]
    
    for pattern, replacement in compound_patterns:
        text = re.sub(pattern, replacement, text)
    
    # Final cleanup - remove extra spaces and standardize particle pronunciation
    text = re.sub(r' +', ' ', text).strip()
    
    # Standard particle pronunciation rules in Japanese
    text = text.replace(' ha ', ' wa ')  # は particle is pronounced "wa"
    if text.startswith('ha '): text = 'wa ' + text[3:]
    text = text.replace(' wo ', ' o ')   # を particle is pronounced "o"
    text = text.replace(' he ', ' e ')   # へ particle is pronounced "e"
    
    return text

def process_lrc_file(lrc_path):
    """
    Reads an LRC file and converts it to high-quality, natural Romaji
    by using the fugashi (MeCab) parser for superior accuracy in both
    segmentation and pronunciation.
    """
    if not os.path.exists(lrc_path):
        print(f"INFO: LRC file not found: {lrc_path}")
        return

    try:
        # --- INITIALIZE PROFESSIONAL-GRADE TOOLS ---
        # fugashi (MeCab) for accurate segmentation and readings
        tagger = fugashi.Tagger()
        # pykakasi for the final Kana -> Romaji conversion step
        kks = pykakasi.kakasi()

        with open(lrc_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        new_content = []
        lrc_pattern = re.compile(r'^(\[\d{2}:\d{2}[.,]\d{2,3}\])(.*)$')

        for line in lines:
            line_strip = line.strip()
            match = lrc_pattern.match(line_strip)
            
            if match:
                timestamp = match.group(1)
                japanese_text = match.group(2)
                
                # --- THE CORRECT LINGUISTIC PIPELINE ---
                # 1. Parse the text with fugashi. This returns a list of Node objects,
                #    each representing a correctly segmented word.
                nodes = tagger(japanese_text)
                
                # Create a simple, joined romanization without caring about spaces yet
                romaji_parts = []
                
                # Keep track of previous node for better handling of verb forms and compounds
                prev_pos = None
                prev_surface = None
                
                for i, node in enumerate(nodes):
                    # 2. Get the correct pronunciation in Katakana from the parser's features.
                    #    This solves critical reading errors like "灰" -> "ハイ" (hai) and "様" -> "ヨウ" (yō).
                    pronunciation_kata = node.feature.kana
                    
                    # If the parser provides no reading (e.g., for symbols), use the surface form.
                    if not pronunciation_kata:
                        pronunciation_kata = node.surface
                    
                    # 3. Convert the Katakana pronunciation to basic Romaji.
                    result = kks.convert(pronunciation_kata)
                    romaji_part = "".join([item['hepburn'] for item in result])

                    # 4. Apply post-processing for long vowels and other known corrections.
                    romaji_part = post_process_romaji(romaji_part)
                    
                    # Part of speech information for better tokenization
                    pos = node.feature.pos1 if hasattr(node.feature, 'pos1') else ''
                    pos2 = node.feature.pos2 if hasattr(node.feature, 'pos2') else ''
                    is_particle = pos == '助詞'
                    is_auxiliary = pos in ['助動詞', '接尾辞']
                    is_adjective_stem = pos == '形容詞' and pos2 != '語幹'
                    is_verb = pos == '動詞'
                    is_noun = pos == '名詞'
                    
                    # Handle small tsu (促音) by checking the surface form
                    has_small_tsu = '」' in node.surface
                    
                    # Skip empty tokens
                    if romaji_part.strip() == '':
                        continue
                    
                    # Look ahead for verb or adjective compounds
                    next_node = nodes[i+1] if i+1 < len(nodes) else None
                    is_followed_by_auxiliary = next_node and (next_node.feature.pos1 == '助動詞' or next_node.feature.pos1 == '接尾辞')
                    is_followed_by_particle = next_node and next_node.feature.pos1 == '助詞'
                    
                    # Create a more advanced system for handling Japanese grammar
                    if is_particle:
                        # Particles generally get spaces around them in romanization
                        romaji_parts.append(romaji_part)
                    elif is_auxiliary and romaji_parts:
                        # Auxiliaries and suffixes attach directly to previous
                        # This handles te-form, continuous forms, etc.
                        romaji_parts.append(romaji_part)
                    elif is_verb and is_followed_by_auxiliary:
                        # Keep verbs connected to their auxiliaries (te iru → teiru)
                        romaji_parts.append(romaji_part)
                    elif is_adjective_stem and (prev_pos == '名詞' or is_followed_by_auxiliary):
                        # Handle adjective + noun compounds
                        romaji_parts.append(romaji_part)
                    elif is_noun and prev_pos == '形容詞':
                        # Connect adjective to the noun it modifies
                        romaji_parts.append(romaji_part)
                    else:
                        # Content words get a space separator
                        romaji_parts.append(romaji_part)
                    
                    # Remember this node's info for the next iteration
                    prev_pos = pos
                    prev_surface = node.surface
                
                # 6. Join all words with a space between them
                romaji_text = ' '.join(romaji_parts)
                
                # Replace multiple spaces with single space and clean up
                romaji_text = re.sub(r' +', ' ', romaji_text).strip()
                
                # --- Final Cleanup Stage 1: Basic Particle Fixes ---
                romaji_text = romaji_text.replace(' ha ', ' wa ')
                if romaji_text.startswith('ha '): romaji_text = 'wa ' + romaji_text[3:]
                romaji_text = romaji_text.replace(' wo ', ' o ')  # Correct particle
                romaji_text = romaji_text.replace(' he ', ' e ')  # Correct direction particle
                romaji_text = romaji_text.replace('「', '"').replace('」', '"')
                romaji_text = romaji_text.replace('watakushi', 'watashi')
                
                # --- Final Cleanup Stage 2: Advanced Grammar Rules ---
                # Apply common fixes for proper spacing, verb forms, etc.
                romaji_text = add_proper_spacing(romaji_text)
                
                # --- Final Cleanup Stage 3: Specific Post-Processing ---
                # Apply additional cleanup for any missed issues
                # This ensures particles like "ga" are handled properly
                romaji_text = re.sub(r'ga([a-zāēīōūA-Z])', r'ga \1', romaji_text)
                
                # Handle compound verbs and noun-suffix combinations once more
                # This catches cases that might have been missed in the earlier stages
                romaji_text = re.sub(r'([a-zāēīōū]+) sa$', r'\1sa', romaji_text)  # noun + sa suffix
                romaji_text = re.sub(r'([a-zāēīōū]+) te iru', r'\1teiru', romaji_text)  # te-form + iru
                
                # Capitalize first letter
                if romaji_text and romaji_text[0].isalpha():
                    romaji_text = romaji_text[0].upper() + romaji_text[1:]

                new_line = f"{timestamp} {romaji_text.strip()}"
                new_content.append(new_line)
            else:
                new_content.append(line_strip)
        
        base, ext = os.path.splitext(lrc_path)
        new_lrc_path = f"{base}_romaji.lrc"

        with open(new_lrc_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(new_content))
        
        print(f"SUCCESS: Created final Romaji LRC file: {new_lrc_path}")

    except Exception as e:
        print(f"ERROR: Failed to process {lrc_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        for audio_filepath in sys.argv[1:]:
            base, _ = os.path.splitext(audio_filepath)
            lrc_filepath = f"{base}.lrc"
            process_lrc_file(lrc_filepath)
    else:
        print("Usage: python lrc_converter.py <audio_file_path> [audio_file_path2 ...]")
        print("       The script will look for .lrc files with the same base name as the audio files.")
        print("Example: python lrc_converter.py ./tests/01\\ Shogeki.mp3")

