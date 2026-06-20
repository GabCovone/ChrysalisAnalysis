Estrai l'archivio di ScyllaHide.

All'interno della cartella estratta, naviga nel seguente percorso:
ScyllaHide > x64dbg > x32

Troverai diversi file. Copia i seguenti tre file specifici:

HookLibraryx86.dll

scylla_hide.ini

ScyllaHideX64DBGPlugin.dp32

Apri la cartella principale in cui hai installato/estratto la tua suite x64dbg.

Naviga nel percorso dedicato alla versione a 32-bit:
release > x32

Cerca una cartella chiamata plugins.

Nota: Se hai appena scaricato x32dbg e non lo hai mai avviato, questa cartella non esisterà. In tal caso, fai clic destro, seleziona "Nuovo > Cartella" e nominala esattamente plugins (tutto minuscolo).

Entra nella cartella plugins.

Incolla i tre file copiati in precedenza direttamente nella radice di questa cartella (non creare ulteriori sottocartelle).

Il percorso finale dei file dovrà essere esattamente questo:

[Tua_Cartella_x64dbg]\release\x32\plugins\ScyllaHideX64DBGPlugin.dp32

[Tua_Cartella_x64dbg]\release\x32\plugins\HookLibraryx86.dll

[Tua_Cartella_x64dbg]\release\x32\plugins\scylla_hide.ini


Per assicurarti che l'integrazione sia andata a buon fine:

Avvia l'eseguibile x32dbg.exe.

Guarda la barra dei menu in alto e clicca su Plugins.

Se l'installazione è corretta, vedrai ScyllaHide apparire nel menu a tendina. Da lì potrai accedere alle opzioni del plugin e configurare i profili di evasione necessari per la tua analisi.