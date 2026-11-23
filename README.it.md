[English](README.md)

# docs-index-for-agents

Qui ci sono tre cose: un indice della documentazione che l'agente di programmazione legge per primo, uno script che controlla che l'indice non dimentichi nessun file, e una skill di Claude Code che spiega all'agente come costruirlo e tenerlo aggiornato.

Autore: Lorenzo Algeri. Licenza: MIT.

## Un indice che l'agente legge prima di tutto

In un progetto su cui Claude Code lavora ogni giorno i file Markdown si accumulano: piani, decisioni, note per chi riprende il lavoro, procedure. Quando parte una sessione, l'agente non sa quali sono ancora validi. Si mette a elencare cartelle, apre i file sbagliati o ne legge troppi, e consuma contesto prima ancora di cominciare.

Per questo nella radice di ogni progetto tengo un file, `_INDEX.md`, che dice cos'è il progetto, da dove partire e cosa contiene davvero ogni documento. All'agente chiedo di leggere quello prima di tutto.

L'indice lo controlla uno script. "Ogni file `.md` è linkato, ogni link funziona, ogni link è relativo" si conta facilmente, quindi lo conta lo script. Quello che lo script non può dirmi è se le frasi di riassunto sono vere, e quella parte la faccio rivedere a un modello.

| Percorso | Cos'è |
|---|---|
| `verify_index.py` | Il controllo. Solo libreria standard di Python. |
| `tests/test_verify_index.py` | 30 test pytest, scritti prima del codice. |
| `example/brindle/` | Un progetto inventato (8 file `.md`) con un indice corretto. |
| `example/brindle-with-errors/` | Lo stesso progetto, con l'indice rotto apposta. |
| `skill/SKILL.md` | Skill di Claude Code: come leggere, costruire e rinfrescare un indice, e quale fase gira su quale fascia di modello. |
| `skill/INDEX_CONTRACT.md` | Una pagina: cosa impone lo script e cosa controlla il revisore. |

## Provarlo in 5 minuti

Ti serve Python 3.9 o più recente (io l'ho sviluppato e provato solo sul 3.13). Su macOS e Linux il comando potrebbe essere `python3`.

```text
python -m pip install pytest
python -m pytest
python verify_index.py example/brindle
python verify_index.py example/brindle-with-errors
```

Sull'esempio giusto esce con codice 0:

```text
Project: example/brindle
Index: _INDEX.md
Coverage: 8/8 .md files linked (100.0%)
PASS
```

Su quello rotto esce con codice 1:

```text
Project: example/brindle-with-errors
Index: _INDEX.md
Coverage: 5/8 .md files linked (62.5%)
Errors (6):
  [absolute-link] _INDEX.md:32 -> /srv/brindle/docs/api.md
  [broken-link] _INDEX.md:33 -> docs/run-book.md
  [outside-project] _INDEX.md:39 -> ../brindle/README.md
  [not-linked] CHANGELOG.md
  [not-linked] docs/api.md
  [not-linked] docs/runbook.md
FAIL
```

Gli errori che ho messo apposta sono quattro: un link assoluto, un link con un refuso, un link a un altro progetto e un file dimenticato. Il link assoluto e quello con il refuso lasciano anche il loro file senza link, ed è per questo che le righe sono sei.

Con `--index NAME` si usa un file indice con un altro nome, con `--exclude DIR` (ripetibile) si salta una cartella. Se il file indice non c'è, il codice di uscita è 2.

La copertura compare come percentuale arrotondata per difetto, accanto ai conteggi, così un controllo che fallisce non mostra mai `100.0%`. Nei link contano anche maiuscole e minuscole: se un link funziona su Windows ma non su Linux, qui fallisce.

## I numeri del sistema originale

Il sistema originale lo uso sulle mie cartelle di lavoro. Questi numeri vengono da lì, e li ha misurati il verificatore originale, che fa più cose della versione ridotta che trovi qui. Da questo repository non si possono riprodurre, e non sono un benchmark.

| Misura | Valore | Data |
|---|---|---|
| Prima generazione | 59 indici, 3876 file `.md` mappati | 5-7 ott 2026 |
| Perimetro | 80 progetti e 3 contenitori, 6585 file `.md` | 20 nov 2026 |
| Copertura | 4684 file `.md` linkati su 5316 attesi (88%), contati sulle voci che hanno un indice | 20 nov 2026 |
| Voci con errori | 24 su 83, di cui 16 senza indice (alcune sono cartelle di servizio, non progetti) | 20 nov 2026 |
| Tempo risparmiato a inizio sessione | non misurato | |
| Costo in token per generare gli indici | non misurato | |

L'88% è la cosa che mi ha insegnato di più. Tra le mie regole globali per l'agente c'è "aggiorna l'indice quando cambi la documentazione", e il verificatore dice che la regola da sola non basta: gli indici restano indietro. Probabilmente mancano i file scritti dopo l'ultima rigenerazione, ma non l'ho controllato file per file.

## Cosa fa in più il verificatore originale

Il verificatore originale gestisce anche i sotto-indici per i progetti molto grandi e controlla front matter e titoli delle sezioni: qui quei controlli non ci sono. Manca anche lo script che nell'originale coordina le fasi. La skill descrive a parole le fasi e le fasce di modello, quindi la applichi come metodo con i tuoi subagenti. Non è un flusso che ho testato.

## Limiti

- Il controllo guarda solo la struttura: se una riga dell'indice descrive male un file, passa lo stesso. Accorgersene tocca al revisore, che è un modello.
- Legge un solo file indice nella radice del progetto.
- Segue i link in linea `[testo](percorso)`. I link in stile riferimento non li legge.
- Non ho nessuna misura che dica che un indice fa risparmiare tempo o token. Che senza indice una sessione sprechi contesto è l'idea da cui sono partito, e non l'ho dimostrata.
- Manca ancora un hook che lanci il controllo a fine sessione, in modo da non dipendere da una regola scritta.

## Licenza

MIT. Vedi `LICENSE`.
