I tool sono suddivisi in base alla fase operativa. Ogni strumento ha uno scopo specifico per intercettare, decodificare e sconfiggere i meccanismi di evasione del malware.

1. Triage e Analisi Statica Preliminare
PEstudio / PEview: Utilizzati per ispezionare gli header del formato PE (Portable Executable), controllare le dipendenze, cercare stringhe sospette in chiaro e verificare l'entropia (per confermare l'offuscamento) senza eseguire il file.

capa: Fondamentale per la "capability analysis". Legge le API importate e le routine di base del file per fornire un quadro immediato di cosa il malware è in grado di fare (es. leggere il registro, aprire socket di rete) prima del debugging.

2. Monitoraggio Comportamentale e Simulazione di Rete
Procmon (Sysinternals): Registra in tempo reale ogni operazione sui file, sul registro di sistema e sui processi. Cruciale per individuare i meccanismi di persistenza (es. chiavi in Run o servizi creati) utilizzati dalla backdoor.

FakeNet-NG: Strumento di simulazione di rete. Finge di essere Internet (rispondendo alle richieste DNS e HTTP) per ingannare il malware facendogli credere di essere connesso al suo server C2. Questo spinge la backdoor a rivelare le sue piene funzionalità.

Wireshark: Utilizzato in modo differito per analizzare i file .pcap generati da FakeNet e studiare il formato dei pacchetti inviati al C2 per l'esfiltrazione dati.

3. Debugging, Memory Dumping ed Evasione
x32dbg: Necessario per eseguire il malware passo-passo e intercettare il momento in cui il payload decrittato viene scritto nella memoria RAM.

ScyllaHide: Chrysalis possiede routine anti-analisi; questo plugin nasconde la presenza di x32dbg al processo in esecuzione, impedendo al malware di bloccarsi o autodistruggersi.

Scylla e PE-bear: Utilizzati nella fase di post-dumping per ricostruire la IAT (Import Address Table) e riallineare le sezioni del file .bin estratto dalla memoria. Senza questo passaggio, i decompilatori non riescono a leggere il file.

4. Reverse Engineering ed Estrazione IoC
IDA Freeware 8.2: Il disassemblatore e decompilatore principale. Verrà utilizzato sul binario dumpato e riparato per tradurre il codice macchina in linguaggio Assembly o pseudocodice, permettendo di analizzare la logica esatta dei comandi operativi della backdoor.

FLOSS (FireEye Labs Obfuscated String Solver): A differenza dei classici tool per le stringhe, FLOSS automatizza il de-offuscamento delle stringhe nascoste negli stack o protette da semplici algoritmi, portando alla luce URL, IP e percorsi critici.

yarGen: Analizza il payload finale isolando le stringhe uniche e creando automaticamente regole YARA, pronte per essere usate in sistemi di rilevamento e threat hunting.

🗺️ Roadmap di Analisi Operativa
Fase 1: Preparazione dell'Ambiente e dei File
Estrazione: Inserire la password dell'archivio (es. infected) per estrarre update.exe (dropper), log.dll (payload iniettrice) e BluetoothService (shellcode offuscato).

Sanificazione: Rimuovere qualsiasi estensione difensiva di sicurezza (come .infected) aggiunta dalle piattaforme di intelligence.

Ripristino Nomi: Rinominare i file basandosi sui metadati per ricreare la catena di sideloading:

Eseguibile vulnerabile: BluetoothService.exe

Libreria malevola: log.dll

File payload offuscato: BluetoothService

Allestimento Directory: Creare il percorso fittizio bersaglio (es. %appdata%\Bluetooth) e posizionarvi i tre file.

Fase 2: Esecuzione, Intercettazione e Memory Dumping
Avvio Monitoraggio: Lanciare in background FakeNet-NG (per il traffico) e Procmon (per l'attività di sistema).

Configurazione Debugger: Aprire x32dbg, caricare BluetoothService.exe e assicurarsi che il plugin ScyllaHide sia attivo.

Impostazione Breakpoint: Inserire breakpoint hardware o software sulle seguenti chiamate API cruciali:

VirtualAlloc / VirtualAllocEx

VirtualProtect

CreateProcessInternalW (per intercettare eventuale Process Hollowing)

Esecuzione: Avviare l'esecuzione. Quando il debugger si ferma su VirtualAlloc/VirtualProtect, ispezionare l'indirizzo di memoria appena manipolato.

Dumping: Verificare la presenza dei Magic Bytes (MZ e intestazione PE) nella Memory Map. Cliccare con il tasto destro sulla regione allocata ed eseguire un "Dump Memory to File" salvandolo come payload_dumped.bin.

Fase 3: Riparazione PE e Reverse Engineering
Ricostruzione IAT: Aprire payload_dumped.bin con PE-bear (o utilizzare Scylla) per sistemare le intestazioni, le sezioni sfalsate e ricostruire la Import Address Table.

Estrazione Automatica: Dare in pasto il binario riparato a FLOSS e yarGen per mappare tutte le stringhe de-offuscate (C2, percorsi di rete, chiavi di persistenza).

Analisi Statica Approfondita: Caricare il binario finale in IDA Freeware 8.2. Utilizzare le stringhe estratte al punto precedente o le chiamate API sospette come Cross-References per navigare il codice e studiare le funzioni specifiche della backdoor Chrysalis (es. reverse shell, esfiltrazione dati, auto-cancellazione).


Fase 1: Preparazione dell'Ambiente e dei File
Obiettivo: Allestire l'ambiente di analisi isolato, eludere i controlli anti-sandbox impostando percorsi realistici e ricostruire la catena di infezione necessaria per innescare la tecnica del DLL Sideloading.

🛡️ 1. Prerequisiti di Sicurezza
Prima di manipolare i campioni malevoli, è vitale garantire che il malware non possa infettare la macchina host o comunicare con l'infrastruttura reale dell'attaccante.

Isolamento di Rete: Assicurarsi che la scheda di rete della Macchina Virtuale sia fisicamente disabilitata dalle impostazioni dell'hypervisor o impostata su un rigido Host-Only (nessun bridge, nessun NAT).

Visibilità Estensioni: Verificare che Esplora File di Windows sia configurato per mostrare le estensioni di tutti i file (Scheda Visualizza > spunta su Estensioni nomi file). Questo previene errori critici durante la rinominazione (es. creare un file.exe.exe).

Snapshot Iniziale: Creare uno Snapshot della VM pulita prima di procedere, fungendo da punto di ripristino sicuro.

📂 2. Allestimento della Directory Bersaglio
Per ingannare i meccanismi anti-analisi del malware che verificano il percorso di esecuzione, si ricrea la directory di sistema attesa dalla backdoor:

Aprire la finestra "Esegui" di Windows (Tasto Windows + R).

Digitare %appdata% e premere Invio per accedere alla cartella nascosta Roaming.

Creare una nuova cartella nominata esattamente Bluetooth.

Percorso finale: C:\Users\[NomeUtente]\AppData\Roaming\Bluetooth\

🏷️ 3. Estrazione e Ripristino della Catena
I campioni scaricati dalle piattaforme di intelligence sono archiviati per sicurezza (password: infected), rinominati con il loro hash SHA-256 e resi inoffensivi tramite finte estensioni. È necessario ricostruire la triade originale per attivare il sideloading.

Rinominare i tre file estratti seguendo questo schema esatto:

L'Esca (Eseguibile Legittimo ma Vulnerabile):

File originale: a511be5164dc... (Tipo: Application, ~681 KB)

Azione: Rinominare in BluetoothService.exe

L'Iniettore (Libreria Malevola):

File originale: 3bdc4c063759... (Tipo: Application extension, ~84 KB)

Azione: Rinominare in log.dll

Il Payload (Dati Criptati / Shellcode):

File originale: _77bfea78def...infected (Tipo: INFECTED File, ~197 KB)

Azione: Eliminare l'underscore iniziale (_) e cancellare completamente l'estensione finale (.infected). Confermare l'avviso di sicurezza di Windows.

Rinominare in: BluetoothService (privo di estensione).

✅ 4. Assemblaggio Finale e Check-Off
Selezionare i tre file appena ripristinati.

Spostarli all'interno della cartella di sistema preparata al punto 2.
