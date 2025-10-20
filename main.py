from main import process_lrc_file
if __name__ == "__main__":
    if len(sys.argv) > 1:
        for audio_filepath in sys.argv[1:]:
            base, _ = os.path.splitext(audio_filepath)
            lrc_filepath = f"{base}.lrc"
            process_lrc_file(lrc_filepath)
    else:
        print("Usage: Pass audio file paths to this script.")
        input("Press Enter to exit...")