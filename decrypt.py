import sys

# --- CONFIGURAZIONE ---
# Inserisci qui il nome del tuo dump originario (quello non toccato)
INPUT_FILE = "bluetoothservice2.bin" 
OUTPUT_FILE = "payload_ghidra.bin"
KEY = b"gQ2JR&9;"

# L'offset esatto calcolato dai tuoi log (053C601F - 053C401F)
OFFSET = 0x2000 

def process_file():
    try:
        with open(INPUT_FILE, "rb") as f:
            data = bytearray(f.read())
    except FileNotFoundError:
        print(f"[!] Errore: File '{INPUT_FILE}' non trovato. Controlla il nome.")
        return

    print(f"[*] File caricato: {len(data)} byte.")

    if len(data) <= OFFSET:
        print("[!] Errore: Il file è più piccolo dell'offset. Sicuro di avere il dump completo?")
        return

    print(f"[*] Preservo i primi {hex(OFFSET)} byte (codice in chiaro)...")
    print(f"[*] Applico l'algoritmo XOR alla backdoor...")

    key_len = len(KEY)

    # Ciclo di decrittazione: replica esatta dell'Assembly del malware
    for i in range(OFFSET, len(data)):
        al = data[i]
        cl = KEY[(i - OFFSET) % key_len]

        # add al, cl
        al = (al + cl) & 0xFF
        # xor al, cl
        al = (al ^ cl) & 0xFF
        # sub al, cl
        al = (al - cl) & 0xFF

        data[i] = al

    with open(OUTPUT_FILE, "wb") as f:
        f.write(data)

    print(f"\n[+] VITTORIA! Payload decrittato e salvato come: {OUTPUT_FILE}")

if __name__ == "__main__":
    process_file()