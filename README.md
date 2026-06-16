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

VirtualAlloc 

VirtualAllocEx

VirtualProtect

CreateProcessInternalW (per intercettare eventuale Process Hollowing)

WriteProcessMemory

ResumeThread

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


Fase 2: Analisi Dinamica e Bypass Anti-Debugging (In corso)
🎯 Obiettivo della Fase
Intercettare il processo di spacchettamento (unpacking) del payload dannoso in memoria, analizzando il comportamento della DLL infetta (log.dll) caricata tramite tecnica di DLL Sideloading dall'eseguibile esca (bluetoothservice.exe).


📝 Diario di Analisi e Ostacoli Incontrati
1. Primo Tentativo: Software Breakpoints sulle API Standard
Azione: Piazzati Software Breakpoint (SetBPX) sulle principali funzioni di iniezione di Windows (VirtualAlloc, VirtualProtect, CreateProcessInternalW, ecc.) all'Entry Point del programma.

Risultato: Fallimento. Il debugger ha segnalato Terminated prima di raggiungere le funzioni monitorate.

Analisi Procmon: Escludendo il rumore del Registro di Sistema, l'analisi ha rivelato che l'eseguibile ha caricato correttamente log.dll ma si è poi chiuso improvvisamente. Successivamente, è emerso un rapido cambio di PID, con la comparsa di cloni del processo principale e conseguenti errori di SHARING VIOLATION.

Conclusione: Il malware ha rilevato la presenza del debugger (o la modifica della RAM dovuta ai byte 0xCC dei breakpoint software) e ha eseguito una tecnica di evasione clonando se stesso in background (Bait and Switch/Process Spawning).

2. Secondo Tentativo: Potenziamento ScyllaHide
Azione: Ripristino dello snapshot della VM. Configurazione del profilo ScyllaHide su VMProtect x86/x64 aggiungendo spunte mirate:

Timing Hooks: (GetTickCount, NtQueryPerf.Counter) per impedire al malware di misurare il tempo di esecuzione.

DRx Protection: Per nascondere la presenza di breakpoint hardware alla CPU.

Hide from PEB / System Info: Per rendere invisibile x32dbg alla lista dei processi attivi.

Risultato: Fallimento. Il debugger si è arrestato nuovamente senza far scattare le trappole.

3. Terzo Tentativo: Breakpoint Hardware (HWBP) sulle API Native
Azione: Sostituzione dei Software Breakpoint (visibili nella RAM) con Hardware Breakpoint (bph), invisibili al malware in quanto salvati direttamente nei registri della CPU (limite massimo di 4 slot).

Target Spostato a livello Kernel: Sono state monitorate le API non documentate (Native) di Windows per intercettare le chiamate di livello più basso:

NtAllocateVirtualMemory

NtWriteVirtualMemory

NtResumeThread

CreateProcessInternalW

Risultato: Il debugger ha correttamente intercettato NtAllocateVirtualMemory durante le fasi iniziali di caricamento di Windows (creazione dell'Heap tramite RtlCreateHeap), ma il malware è sfuggito nuovamente creando un processo clone (es. PID 240) bypassando l'Entry Point dell'eseguibile.

4. La Rivelazione Architetturale: Esecuzione in DllMain
Azione: Analisi del flusso di caricamento.

Conclusione Fondamentale: Il malware non attende l'Entry Point ufficiale (OptionalHeader.AddressOfEntryPoint) dell'eseguibile per avviare il suo codice. Sfruttando la logica di Windows, il codice malevolo viene eseguito all'interno della funzione di inizializzazione della libreria stessa (DllMain) nel millisecondo esatto in cui il sistema operativo carica log.dll in memoria.

Stato Attuale: Arrivando all'Entry Point, il debugger giunge in ritardo sulla "scena del crimine", quando il processo di iniezione è già avvenuto e il malware ha già spostato l'esecuzione nel nuovo PID.

Per neutralizzare questa strategia di evasione, è necessario spostare la linea di difesa prima dell'Entry Point.

Attivare l'opzione User DLL Entry nelle preferenze (Events) di x32dbg.

Eseguire il programma un modulo alla volta (F9 progressivo).

Congelare l'esecuzione nell'istante esatto in cui il debugger notifica il caricamento del modulo log.dll, prima che venga eseguita la sua DllMain.

5. Quinto Tentativo: Congelamento in DllMain e Mascheramento Avanzato

Azione: Disattivazione dei breakpoint software. Attivazione dell'opzione User DLL Entry in x32dbg per intercettare il caricamento pre-Entry Point. Utilizzo simultaneo di ScyllaHide con spunte mirate su Timing Hooks (per falsificare l'orologio di sistema e ingannare l'istruzione RDTSC) e DRx Protection (per nascondere i Breakpoint Hardware).

Risultato: Fallimento "a scoppio ritardato". Il malware evade sistematicamente al secondo tentativo di esecuzione.

Conclusione: Il malware implementa un controllo di persistenza o verifica lo stato ambientale/PEB (BeingDebugged). Rileva i residui della sessione precedente, rendendo necessario operare in Clean State continuo (tramite ripristino snapshot VM) ed escludendo l'uso di breakpoint temporali che alterano il normale flusso di caricamento.

6. Sesto Tentativo: Intercettazione API Crittografiche Native (Il pensiero laterale)

Azione: Tentativo di bypassare la logica anti-debug estraendo il payload a valle della decrittazione. 
Ispezione della scheda Simboli di x32dbg per individuare le librerie crittografiche caricate. 
Posizionamento di Breakpoint Hardware in Esecuzione (HWBP) sulle API native di decrittazione: CryptDecrypt (advapi32.dll) e BCryptDecrypt (bcrypt.dll).  
Risultato: Evasione completa. 
I breakpoint sulle API crittografiche non sono mai scattati.  
Conclusione Fondamentale: L'autore del malware non si affida alle librerie crittografiche di Windows (CryptoAPI/CNG).
log.dll integra un algoritmo di decrittazione custom (es. XOR, RC4) compilato staticamente nel proprio codice.  

7. Settimo Tentativo: Memory Allocation Trap (La "Tela Vuota")  
Obiettivo: Dato che il metodo di decrittazione è sconosciuto, intercettare la destinazione finale del payload decrittato.

Azione:

Ripristino in Clean State.

Piazzamento HWBP su NtAllocateVirtualMemory (Ring 0).

Utilizzo dello stepping Execute till Return (Ctrl+F9) per far completare la richiesta di memoria al sistema operativo.

Analisi dello Stack: poiché l'API è nativa, l'indirizzo della memoria allocata non viene restituito in EAX (che contiene solo lo STATUS_SUCCESS), ma tramite un puntatore letto nel parametro [esp+8].

Filtraggio del Rumore: L'analisi del Call Stack ha evidenziato la necessità di filtrare le normali allocazioni di sistema. Molte interruzioni iniziali su NtAllocateVirtualMemory ritornavano a ntdll.RtlCreateHeap (il sistema operativo che prepara l'Heap). La procedura richiede di ignorare queste chiamate legittime eseguendo cicli continui, fermandosi solo quando il return address nello Stack punterà direttamente a log.dll o a un modulo sconosciuto.

8. Ottavo Tentativo: La Trappola su ZwProtectVirtualMemory e Scansione Progressiva

Azione: Abbandonata l'allocazione di memoria a causa dell'eccessivo "rumore" di sistema. Posizionato un Hardware Breakpoint su ZwProtectVirtualMemory (usata dai packer per rendere eseguibile la memoria appena scritta). Ad ogni hit del breakpoint (F9), è stata eseguita una Ricerca Globale (Pattern Search) nella RAM per l'intestazione esadecimale PE: 4D 5A 90 00 03 00 00 00.

Risultato: Successo parziale. Dopo svariati cicli, la scansione ha individuato un nuovo blocco dinamico (es. 006C0000) contenente i Magic Bytes e la dicitura This program cannot be run in DOS mode. Il blocco è stato estratto tramite "Dump Memory to File".

9. Nono Tentativo: Riparazione in PE-bear e la Falsa Pista (Decoy PE)

Azione: Il file binario estratto dalla RAM non veniva riconosciuto da IDA Free a causa del disallineamento della memoria (Virtual vs Raw). Il file è stato caricato in PE-bear per correggere chirurgicamente i Section Headers, sovrascrivendo i campi Raw Addr e Raw size con i valori corrispondenti alle colonne Virtual Addr e Virtual Size.

Risultato: IDA ha riconosciuto l'eseguibile riparato, ma il disassemblaggio forzato (tasto 'C') e l'ispezione delle stringhe (Shift+F12) hanno svelato un inganno. La sezione .text conteneva solo 176 byte. Non c'era traccia di codice Assembly eseguibile, ma esclusivamente informazioni sui metadati (es. ProductVersion, en-US).

Conclusione: Il malware ha ingannato l'analista iniettando una "DLL fantasma" o un mini-eseguibile esca per simulare un avvenuto unpacking. Il payload vero e proprio, di dimensioni nettamente superiori, è ancora celato all'interno del processo originale.

Next Step (In corso): Ripristinare la Macchina Virtuale, lanciare nuovamente la trappola su ZwProtectVirtualMemory in x32dbg e analizzare la Memory Map filtrata per Dimensione (Size) per individuare grandi blocchi (es. 200+ KB) allocati dinamicamente (PRV/MAP) con permessi ERW/RW, isolando così il vero payload.


10. Decimo Tentativo: Frammentazione della Memoria (Memory Spraying) e Fallimento HWBP in Scrittura
Azione: A seguito della scoperta del falso payload, si è tentato di monitorare in tempo reale i blocchi di memoria allocati dinamicamente (con permessi ERW) utilizzando la Memory Map di x32dbg. 
È stato piazzato un Breakpoint Hardware in Accesso/Scrittura su un blocco candidato per intercettare l'istante esatto della decrittazione.  
Risultato: Evasione. Il malware genera un "rumore" ambientale estremo attraverso una tecnica di Memory Spraying, allocando decine di piccoli frammenti (es. 4 KB) per disorientare l'analista. 
Inoltre, sfrutta una decrittazione in-place, sovrascrivendo e rilasciando continuamente i buffer, non lasciando tracce contigue nella RAM.Conclusione: L'architettura di Chrysalis (attribuita all'APT Lotus Blossom) rende l'analisi dinamica in memoria strutturalmente inefficace e incline a falsi positivi.  

11. Undicesimo Tentativo: Analisi Statica su log.dll e Scoperta dell'API Hashing
Azione: Abbandono del debugging dinamico in favore dell'analisi statica della libreria iniettrice log.dll tramite IDA Freeware 8.2. 
Ricerca delle routine di base responsabili del caricamento.  
Risultato: Individuazione di un denso blocco matematico all'interno della sequenza di innesco, inizialmente scambiato per l'algoritmo di decrittazione (LCG). L'analisi delle costanti esadecimali (811C9DC5h e 85EBCA6Bh) ha rivelato che il malware sta in realtà implementando un sofisticato sistema combinato di hashing (FNV-1a e MurmurHash3).
Conclusione: Il malware protegge le proprie intenzioni tramite API Hashing. Non importa o chiama le funzioni di sistema (come VirtualAlloc o ReadFile) in chiaro. Al contrario, risolve i loro indirizzi in memoria confrontando gli hash e li salva all'interno di una tabella di Puntatori a Funzione nascosta nella sezione .rdata (dati in sola lettura).




🎯 Next Step: La Caccia all'Algoritmo di Decrittazione (Analisi Statica Avanzata)
Obiettivo Attuale:
Superata la barriera dell'API Hashing, sappiamo che la backdoor Chrysalis compila la sua "rubrica" di funzioni nascoste tramite una specifica routine (rinominata in Setup_API_Table). Il vero motore di decrittazione del payload si trova inevitabilmente a valle di questa inizializzazione. Dobbiamo individuare il punto esatto in cui il malware apre fisicamente il file dormiente per tradurre il suo codice.  Azioni Operative in IDA Freeware 8.2:  Ispezione delle Stringhe (Il Cecchino):Aprire la finestra delle stringhe (Shift + F12).Ricercare la stringa corrispondente al nome del file contenente il payload crittato: BluetoothService.  Riferimenti Incrociati (Cross-References):Fare doppio clic sulla stringa individuata.Selezionarla e premere il tasto X per visualizzare tutte le funzioni che vi accedono.Questo teletrasporterà la visuale esattamente nel punto in cui il malware prepara i parametri per l'apertura del file.Individuazione del Cuore Matematico:Analizzare il codice Assembly immediatamente successivo al caricamento della stringa.Cercare chiamate indirette (call dword ptr [...]) che indicano l'uso dell'API ReadFile mascherata.Individuare il ciclo iterativo (while/for a livello Assembly, riconoscibile dai salti condizionati come jb o jnz verso l'alto) contenente le istruzioni XOR, ADD o IMUL. Quello sarà l'effettivo algoritmo LCG di decrittazione.