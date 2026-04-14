# RAGForge
Generatore di una pipeline multimodale di estrazione e normalizzazione contenuti (OCR + ASR + captioning + document parsing + export testuale per ingestion).
Il programma permette di estrarre testi da una directory di input contenente vari tipi di file: docx,pdf,mp4,wav,m4a,jpg,png, ecc..
In una cartella di output sono scritti tutti le parti testuali in file nominati come i file originali ma con estensione TXT.
Il programma inserisce anche la descrizione dei frame di un filmato, la descrizione di un'immagine, la trascrizione audio, ecc..
Una volta che la cartella di output si è popolata, allora si può usarla come directory di RAG, per programmi come open-webui, ecc.ecc..

INSTALLAZIONE
Si consiglia sempre di creare un ambiente Python dedicato, es. 
python -m venv ragforge
Attivare l'environment (per Windows: ragforge\Scripts\activate)
pip install -r requirements.txt

Bisogna installare il software Tesseract (ATTENTI AD INCLUDERE LA LINGUA ITALIANA), per il riconoscimento OCR, si consiglia di scegliere le lingue italiano ed inglese durante l'istallazione.

Se si hanno problemi col Tkinter, in Windows il pacchetto arriva con l'istallazione di Python (https://www.python.org/)

Lanciare il file install.bat (istalla Tesseract e FFMpeg) - RIAVVIARE IL COMPUTER O APRIRE UN'ALTRA FINESTRA CMD.


